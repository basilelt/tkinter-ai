import { randomUUID } from "node:crypto";
import {
  ENEMY_ARCHETYPES,
  GAME_TICK_RATE,
  MAX_ACTIVE_ENEMIES,
  MAX_PLAYERS_PER_ROOM,
  PLAYER_DEFAULTS,
  SNAPSHOT_RATE,
  WAVE_CONFIG,
  WORLD_BOUNDS,
  calculateDamage,
  clamp,
  computeMatchXp,
  createDeterministicRng,
  distance,
  hashStringSeed,
  isCriticalHit,
  mergeProgression,
  normalize,
  randomInt,
  scale,
  sub,
  type EnemyArchetype,
  type GameSnapshot,
  type MatchPhase,
  type MatchPlayerStats,
  type NetEnemyState,
  type NetPickupState,
  type NetPlayerState,
  type NetProjectileState,
  type PlayerInputFrame,
  type PlayerProfile,
  type RoomCode,
  type Vec3
} from "@silent-hillberg/shared";
import type { ProfileStore } from "../storage/profile-store";

interface PlayerRuntime {
  socketId: string;
  profile: PlayerProfile;
  ready: boolean;
  connected: boolean;
  state: NetPlayerState;
  input: PlayerInputFrame;
  stats: MatchPlayerStats;
  nextPrimaryAtMs: number;
  nextSecondaryAtMs: number;
  reloadEndAtMs: number;
  dashEndAtMs: number;
  nextDashAtMs: number;
  ackTick: number;
}

interface EnemyRuntime extends NetEnemyState {
  archetypeData: EnemyArchetype;
  lastAttackAtMs: number;
  removedAtMs: number;
}

interface ProjectileRuntime extends NetProjectileState {
  removedAtMs: number;
}

export interface RoomStatePayload {
  roomCode: RoomCode;
  phase: MatchPhase;
  players: {
    playerId: string;
    nickname: string;
    ready: boolean;
    connected: boolean;
    level: number;
  }[];
}

interface RoomEmitter {
  toRoom(roomCode: string, event: "room:state" | "game:snapshot" | "game:event" | "match:end", payload: unknown): void;
  toSocket(socketId: string, event: "progression:update", payload: unknown): void;
}

const SPAWN_POINTS: Vec3[] = [
  { x: -8, y: 0, z: -10 },
  { x: 8, y: 0, z: -10 },
  { x: -8, y: 0, z: 10 },
  { x: 8, y: 0, z: 10 }
];

const PICKUP_POSITIONS: Vec3[] = [
  { x: -20, y: 0, z: 12 },
  { x: 18, y: 0, z: -18 },
  { x: 0, y: 0, z: 32 }
];

const DEFAULT_INPUT: PlayerInputFrame = {
  seq: 0,
  dtMs: 16,
  moveX: 0,
  moveZ: 0,
  yaw: 0,
  pitch: 0,
  jump: false,
  sprint: false,
  dash: false,
  firePrimary: false,
  fireSecondary: false,
  reload: false
};

const SNAPSHOT_EVERY_TICKS = Math.max(1, Math.floor(GAME_TICK_RATE / SNAPSHOT_RATE));

export class GameRoom {
  public readonly roomCode: RoomCode;

  private readonly playersBySocket = new Map<string, PlayerRuntime>();
  private readonly socketByPlayerId = new Map<string, string>();
  private readonly enemies = new Map<string, EnemyRuntime>();
  private readonly projectiles = new Map<string, ProjectileRuntime>();
  private readonly pickups: NetPickupState[];
  private readonly rng: () => number;

  private readonly phaseState: {
    phase: MatchPhase;
    wave: number;
    tick: number;
    startedAtMs: number;
    endedAtMs: number;
    pendingWaveAtMs: number;
    extraction: {
      center: Vec3;
      radius: number;
      progress: number;
      requiredProgress: number;
      active: boolean;
    };
  };

  private finalizing = false;

  public constructor(
    roomCode: RoomCode,
    private readonly profileStore: ProfileStore,
    private readonly emitter: RoomEmitter
  ) {
    this.roomCode = roomCode;
    this.rng = createDeterministicRng(hashStringSeed(roomCode));
    this.pickups = [
      {
        id: `pickup-ammo-${randomUUID()}`,
        kind: "ammo",
        position: PICKUP_POSITIONS[0],
        active: true
      },
      {
        id: `pickup-medkit-${randomUUID()}`,
        kind: "medkit",
        position: PICKUP_POSITIONS[1],
        active: true
      },
      {
        id: `pickup-armor-${randomUUID()}`,
        kind: "armor",
        position: PICKUP_POSITIONS[2],
        active: true
      }
    ];

    this.phaseState = {
      phase: "lobby",
      wave: 0,
      tick: 0,
      startedAtMs: 0,
      endedAtMs: 0,
      pendingWaveAtMs: 0,
      extraction: {
        center: { x: 0, y: 0, z: 58 },
        radius: 8,
        progress: 0,
        requiredProgress: WAVE_CONFIG.extractionRequiredMs,
        active: false
      }
    };
  }

  public addPlayer(socketId: string, profile: PlayerProfile): { ok: true } | { ok: false; reason: string } {
    if (this.phaseState.phase !== "lobby") {
      return { ok: false, reason: "Room already started" };
    }

    if (this.playersBySocket.size >= MAX_PLAYERS_PER_ROOM) {
      return { ok: false, reason: "Room is full" };
    }

    const spawn = SPAWN_POINTS[this.playersBySocket.size % SPAWN_POINTS.length];

    const runtime: PlayerRuntime = {
      socketId,
      profile,
      ready: false,
      connected: true,
      state: {
        id: profile.playerId,
        nickname: profile.nickname,
        position: { ...spawn },
        velocity: { x: 0, y: 0, z: 0 },
        yaw: 0,
        pitch: 0,
        hp: PLAYER_DEFAULTS.maxHp,
        armor: 0,
        ammoPrimary: PLAYER_DEFAULTS.primaryAmmoMax,
        ammoSecondary: PLAYER_DEFAULTS.secondaryAmmoMax,
        sprinting: false,
        grounded: true,
        isReloading: false,
        kills: 0,
        alive: true,
        level: profile.level
      },
      input: { ...DEFAULT_INPUT },
      stats: {
        kills: 0,
        damageDone: 0,
        damageTaken: 0,
        revives: 0,
        survived: true,
        waveReached: 0
      },
      nextPrimaryAtMs: 0,
      nextSecondaryAtMs: 0,
      reloadEndAtMs: 0,
      dashEndAtMs: 0,
      nextDashAtMs: 0,
      ackTick: 0
    };

    this.playersBySocket.set(socketId, runtime);
    this.socketByPlayerId.set(profile.playerId, socketId);
    this.broadcastRoomState();

    return { ok: true };
  }

  public markDisconnected(socketId: string): void {
    const runtime = this.playersBySocket.get(socketId);
    if (!runtime) {
      return;
    }

    runtime.connected = false;
    runtime.ready = false;

    if (this.phaseState.phase === "lobby") {
      this.playersBySocket.delete(socketId);
      this.socketByPlayerId.delete(runtime.profile.playerId);
    } else {
      runtime.state.alive = false;
      runtime.state.hp = 0;
      runtime.stats.survived = false;
    }

    this.broadcastRoomState();
  }

  public setReady(socketId: string, ready: boolean): boolean {
    const runtime = this.playersBySocket.get(socketId);
    if (!runtime || this.phaseState.phase !== "lobby") {
      return false;
    }

    runtime.ready = ready;
    this.broadcastRoomState();
    return true;
  }

  public setInput(socketId: string, input: PlayerInputFrame): void {
    const runtime = this.playersBySocket.get(socketId);
    if (!runtime) {
      return;
    }

    runtime.input = input;
  }

  public setAckTick(socketId: string, tick: number): void {
    const runtime = this.playersBySocket.get(socketId);
    if (!runtime) {
      return;
    }

    runtime.ackTick = tick;
  }

  public tick(nowMs: number, dtSec: number): void {
    this.phaseState.tick += 1;

    if (this.phaseState.phase === "lobby") {
      this.tryStartMatch(nowMs);
    }

    if (this.phaseState.phase === "running" || this.phaseState.phase === "extraction") {
      this.tickPlayers(nowMs, dtSec);
      this.tickProjectiles(nowMs, dtSec);
      this.tickEnemies(nowMs, dtSec);
      this.tickPickups(nowMs);
      this.tickWaves(nowMs);
      this.tickExtraction(nowMs, dtSec);
      this.checkFailure(nowMs);
    }

    this.cleanupEntities(nowMs);

    if (this.phaseState.tick % SNAPSHOT_EVERY_TICKS === 0) {
      this.emitter.toRoom(this.roomCode, "game:snapshot", this.createSnapshot(nowMs));
    }
  }

  public toRoomState(): RoomStatePayload {
    return {
      roomCode: this.roomCode,
      phase: this.phaseState.phase,
      players: [...this.playersBySocket.values()].map((runtime) => ({
        playerId: runtime.state.id,
        nickname: runtime.profile.nickname,
        ready: runtime.ready,
        connected: runtime.connected,
        level: runtime.profile.level
      }))
    };
  }

  public isDisposable(nowMs: number): boolean {
    if (this.playersBySocket.size === 0) {
      return true;
    }

    if (this.phaseState.phase !== "ended") {
      return false;
    }

    const anyConnected = [...this.playersBySocket.values()].some((runtime) => runtime.connected);
    if (!anyConnected && nowMs - this.phaseState.endedAtMs > 5000) {
      return true;
    }

    return false;
  }

  private broadcastRoomState(): void {
    this.emitter.toRoom(this.roomCode, "room:state", this.toRoomState());
  }

  private emitGameEvent(type: string, payload: Record<string, unknown>): void {
    this.emitter.toRoom(this.roomCode, "game:event", {
      type,
      atMs: Date.now(),
      payload
    });
  }

  private tryStartMatch(nowMs: number): void {
    if (this.playersBySocket.size === 0) {
      return;
    }

    const connectedPlayers = [...this.playersBySocket.values()].filter((runtime) => runtime.connected);
    if (connectedPlayers.length === 0) {
      return;
    }

    const everyoneReady = connectedPlayers.every((runtime) => runtime.ready);
    if (!everyoneReady) {
      return;
    }

    this.phaseState.phase = "running";
    this.phaseState.startedAtMs = nowMs;
    this.phaseState.wave = 1;
    this.phaseState.pendingWaveAtMs = 0;
    this.phaseState.extraction.progress = 0;
    this.phaseState.extraction.active = false;

    let spawnIndex = 0;
    for (const runtime of this.playersBySocket.values()) {
      const spawn = SPAWN_POINTS[spawnIndex % SPAWN_POINTS.length];
      spawnIndex += 1;
      runtime.state.position = { ...spawn };
      runtime.state.velocity = { x: 0, y: 0, z: 0 };
      runtime.state.yaw = 0;
      runtime.state.pitch = 0;
      runtime.state.hp = PLAYER_DEFAULTS.maxHp;
      runtime.state.armor = 25;
      runtime.state.ammoPrimary = PLAYER_DEFAULTS.primaryAmmoMax;
      runtime.state.ammoSecondary = PLAYER_DEFAULTS.secondaryAmmoMax;
      runtime.state.sprinting = false;
      runtime.state.grounded = true;
      runtime.state.isReloading = false;
      runtime.state.kills = 0;
      runtime.state.alive = true;
      runtime.ready = false;
      runtime.stats = {
        kills: 0,
        damageDone: 0,
        damageTaken: 0,
        revives: 0,
        survived: true,
        waveReached: 1
      };
      runtime.nextPrimaryAtMs = 0;
      runtime.nextSecondaryAtMs = 0;
      runtime.reloadEndAtMs = 0;
      runtime.nextDashAtMs = 0;
      runtime.dashEndAtMs = 0;
      runtime.input = { ...DEFAULT_INPUT };
    }

    this.spawnWave(this.phaseState.wave);
    this.broadcastRoomState();
    this.emitGameEvent("wave-start", {
      wave: this.phaseState.wave,
      enemies: this.enemies.size
    });
  }

  private tickPlayers(nowMs: number, dtSec: number): void {
    for (const runtime of this.playersBySocket.values()) {
      if (!runtime.connected || !runtime.state.alive) {
        continue;
      }

      const state = runtime.state;
      const input = runtime.input;

      state.yaw = input.yaw;
      state.pitch = clamp(input.pitch, -1.45, 1.45);

      const forward = { x: Math.sin(state.yaw), y: 0, z: Math.cos(state.yaw) };
      const right = { x: Math.cos(state.yaw), y: 0, z: -Math.sin(state.yaw) };

      const moveVector = {
        x: right.x * input.moveX + forward.x * input.moveZ,
        y: 0,
        z: right.z * input.moveX + forward.z * input.moveZ
      };

      const moveDir = normalize(moveVector);
      const isDashing = nowMs < runtime.dashEndAtMs;

      if (input.dash && nowMs >= runtime.nextDashAtMs) {
        runtime.nextDashAtMs = nowMs + PLAYER_DEFAULTS.dashCooldownMs;
        runtime.dashEndAtMs = nowMs + PLAYER_DEFAULTS.dashDurationMs;
      }

      const baseSpeed = input.sprint ? PLAYER_DEFAULTS.sprintSpeed : PLAYER_DEFAULTS.walkSpeed;
      const targetSpeed = isDashing ? PLAYER_DEFAULTS.dashSpeedBoost : baseSpeed;

      const targetVelocityX = moveDir.x * targetSpeed;
      const targetVelocityZ = moveDir.z * targetSpeed;

      const blend = Math.min(1, dtSec * PLAYER_DEFAULTS.friction);
      state.velocity.x += (targetVelocityX - state.velocity.x) * blend;
      state.velocity.z += (targetVelocityZ - state.velocity.z) * blend;

      if (input.jump && state.grounded) {
        state.velocity.y = PLAYER_DEFAULTS.jumpVelocity;
        state.grounded = false;
      }

      state.velocity.y -= PLAYER_DEFAULTS.gravity * dtSec;

      state.position.x += state.velocity.x * dtSec;
      state.position.y += state.velocity.y * dtSec;
      state.position.z += state.velocity.z * dtSec;

      state.position.x = clamp(state.position.x, WORLD_BOUNDS.minX, WORLD_BOUNDS.maxX);
      state.position.z = clamp(state.position.z, WORLD_BOUNDS.minZ, WORLD_BOUNDS.maxZ);

      if (state.position.y <= 0) {
        state.position.y = 0;
        state.velocity.y = 0;
        state.grounded = true;
      }

      state.sprinting = input.sprint;

      state.isReloading = false;
      state.ammoPrimary = PLAYER_DEFAULTS.primaryAmmoMax;
      state.ammoSecondary = PLAYER_DEFAULTS.secondaryAmmoMax;

      if (input.firePrimary && nowMs >= runtime.nextPrimaryAtMs) {
        runtime.nextPrimaryAtMs = nowMs + PLAYER_DEFAULTS.primaryFireIntervalMs;
        this.handlePrimaryShot(runtime, nowMs);
      }

      if (input.fireSecondary && nowMs >= runtime.nextSecondaryAtMs) {
        runtime.nextSecondaryAtMs = nowMs + PLAYER_DEFAULTS.secondaryFireIntervalMs;
        this.spawnProjectile(runtime);
      }
    }
  }

  private handlePrimaryShot(runtime: PlayerRuntime, nowMs: number): void {
    const playerState = runtime.state;
    const aimDirection = this.getAimDirection(playerState.yaw, playerState.pitch);

    let bestTarget: EnemyRuntime | null = null;
    let bestScore = -Infinity;
    let bestDistance = Number.POSITIVE_INFINITY;

    for (const enemy of this.enemies.values()) {
      if (!enemy.alive) {
        continue;
      }

      const toEnemy = {
        x: enemy.position.x - playerState.position.x,
        y: enemy.position.y + 1.6 - (playerState.position.y + 1.6),
        z: enemy.position.z - playerState.position.z
      };

      const enemyDistance = Math.sqrt(toEnemy.x * toEnemy.x + toEnemy.y * toEnemy.y + toEnemy.z * toEnemy.z);
      if (enemyDistance > PLAYER_DEFAULTS.primaryRange) {
        continue;
      }

      const toEnemyDir = normalize(toEnemy);
      const alignment = aimDirection.x * toEnemyDir.x + aimDirection.y * toEnemyDir.y + aimDirection.z * toEnemyDir.z;
      if (alignment < 0.93) {
        continue;
      }

      const score = alignment * 2 - enemyDistance * 0.01;
      if (score > bestScore) {
        bestScore = score;
        bestDistance = enemyDistance;
        bestTarget = enemy;
      }
    }

    if (!bestTarget) {
      return;
    }

    const critical = isCriticalHit(bestScore / 2);
    const damage = calculateDamage(PLAYER_DEFAULTS.primaryDamage, critical, bestDistance, PLAYER_DEFAULTS.primaryRange);

    this.applyDamageToEnemy(bestTarget, runtime, damage, nowMs, critical, "primary");
  }

  private spawnProjectile(runtime: PlayerRuntime): void {
    const player = runtime.state;
    const direction = this.getAimDirection(player.yaw, player.pitch);

    const projectile: ProjectileRuntime = {
      id: `projectile-${randomUUID()}`,
      ownerId: player.id,
      position: {
        x: player.position.x + direction.x * 1.3,
        y: player.position.y + 1.5,
        z: player.position.z + direction.z * 1.3
      },
      velocity: scale(direction, PLAYER_DEFAULTS.projectileSpeed),
      ttlMs: 1500,
      damage: PLAYER_DEFAULTS.secondaryDamage,
      removedAtMs: 0
    };

    this.projectiles.set(projectile.id, projectile);
  }

  private tickProjectiles(nowMs: number, dtSec: number): void {
    for (const projectile of this.projectiles.values()) {
      if (projectile.removedAtMs > 0) {
        continue;
      }

      projectile.ttlMs -= dtSec * 1000;
      if (projectile.ttlMs <= 0) {
        projectile.removedAtMs = nowMs;
        continue;
      }

      projectile.position.x += projectile.velocity.x * dtSec;
      projectile.position.y += projectile.velocity.y * dtSec;
      projectile.position.z += projectile.velocity.z * dtSec;

      for (const enemy of this.enemies.values()) {
        if (!enemy.alive) {
          continue;
        }

        const hitDistance = distance(projectile.position, enemy.position);
        if (hitDistance > 1.5 * enemy.archetypeData.scale * 0.5) {
          continue;
        }

        const ownerSocket = this.socketByPlayerId.get(projectile.ownerId);
        if (!ownerSocket) {
          projectile.removedAtMs = nowMs;
          break;
        }

        const owner = this.playersBySocket.get(ownerSocket);
        if (!owner) {
          projectile.removedAtMs = nowMs;
          break;
        }

        this.applyDamageToEnemy(enemy, owner, projectile.damage, nowMs, false, "secondary");
        projectile.removedAtMs = nowMs;
        break;
      }
    }
  }

  private tickEnemies(nowMs: number, dtSec: number): void {
    const alivePlayers = [...this.playersBySocket.values()].filter((runtime) => runtime.connected && runtime.state.alive);

    for (const enemy of this.enemies.values()) {
      if (!enemy.alive) {
        continue;
      }

      if (alivePlayers.length === 0) {
        continue;
      }

      let target: PlayerRuntime | null = null;
      let nearestDistance = Number.POSITIVE_INFINITY;

      for (const player of alivePlayers) {
        const currentDistance = distance(enemy.position, player.state.position);
        if (currentDistance < nearestDistance) {
          nearestDistance = currentDistance;
          target = player;
        }
      }

      if (!target) {
        continue;
      }

      enemy.targetPlayerId = target.state.id;

      if (nearestDistance > enemy.archetypeData.attackRange) {
        const direction = normalize(sub(target.state.position, enemy.position));
        enemy.velocity = scale(direction, enemy.archetypeData.speed);
        enemy.position.x += enemy.velocity.x * dtSec;
        enemy.position.z += enemy.velocity.z * dtSec;
        enemy.position.y = 0;
      } else {
        enemy.velocity = { x: 0, y: 0, z: 0 };
        if (nowMs - enemy.lastAttackAtMs >= enemy.archetypeData.attackCooldownMs) {
          enemy.lastAttackAtMs = nowMs;
          this.damagePlayer(target, enemy.archetypeData.damage, nowMs, enemy.id);
        }
      }
    }
  }

  private tickPickups(nowMs: number): void {
    for (const pickup of this.pickups) {
      if (!pickup.active) {
        continue;
      }

      for (const player of this.playersBySocket.values()) {
        if (!player.connected || !player.state.alive) {
          continue;
        }

        const pickupDistance = distance(player.state.position, pickup.position);
        if (pickupDistance > 1.8) {
          continue;
        }

        if (pickup.kind === "ammo") {
          player.state.ammoPrimary = PLAYER_DEFAULTS.primaryAmmoMax;
          player.state.ammoSecondary = PLAYER_DEFAULTS.secondaryAmmoMax;
        } else if (pickup.kind === "medkit") {
          player.state.hp = Math.min(PLAYER_DEFAULTS.maxHp, player.state.hp + 35);
        } else {
          player.state.armor = Math.min(PLAYER_DEFAULTS.maxArmor, player.state.armor + 25);
        }

        pickup.active = false;
        setTimeout(() => {
          pickup.active = true;
        }, 9000);
      }
    }

    if (this.phaseState.phase === "ended") {
      return;
    }

    const elapsed = nowMs - this.phaseState.startedAtMs;
    if (elapsed < 1) {
      return;
    }
  }

  private tickWaves(nowMs: number): void {
    if (this.phaseState.phase !== "running" && this.phaseState.phase !== "extraction") {
      return;
    }

    const aliveEnemies = [...this.enemies.values()].filter((enemy) => enemy.alive).length;

    if (aliveEnemies > 0) {
      return;
    }

    if (this.phaseState.phase === "running") {
      if (this.phaseState.wave >= WAVE_CONFIG.extractionWave) {
        this.phaseState.phase = "extraction";
        this.phaseState.extraction.active = true;
        this.phaseState.extraction.progress = 0;
        this.phaseState.pendingWaveAtMs = 0;
        this.emitGameEvent("extraction-open", {
          center: this.phaseState.extraction.center,
          radius: this.phaseState.extraction.radius
        });
        this.broadcastRoomState();
        return;
      }

      if (this.phaseState.pendingWaveAtMs === 0) {
        this.phaseState.pendingWaveAtMs = nowMs + WAVE_CONFIG.interWaveDelayMs;
        this.emitGameEvent("wave-cleared", {
          wave: this.phaseState.wave
        });
      }

      if (nowMs >= this.phaseState.pendingWaveAtMs) {
        this.phaseState.pendingWaveAtMs = 0;
        this.phaseState.wave += 1;
        this.spawnWave(this.phaseState.wave);
        this.emitGameEvent("wave-start", {
          wave: this.phaseState.wave,
          enemies: this.enemies.size
        });
      }
    }
  }

  private tickExtraction(nowMs: number, dtSec: number): void {
    if (!this.phaseState.extraction.active || this.phaseState.phase !== "extraction") {
      return;
    }

    const alivePlayers = [...this.playersBySocket.values()].filter((runtime) => runtime.connected && runtime.state.alive);
    if (alivePlayers.length === 0) {
      void this.finalizeMatch(false, nowMs);
      return;
    }

    let insideCount = 0;
    for (const player of alivePlayers) {
      const extractionDistance = distance(player.state.position, this.phaseState.extraction.center);
      if (extractionDistance <= this.phaseState.extraction.radius) {
        insideCount += 1;
      }
    }

    if (insideCount > 0) {
      this.phaseState.extraction.progress += dtSec * 1000 * (insideCount / alivePlayers.length);
    } else {
      this.phaseState.extraction.progress = Math.max(0, this.phaseState.extraction.progress - dtSec * 1000 * 0.35);
    }

    if (this.phaseState.extraction.progress >= this.phaseState.extraction.requiredProgress) {
      void this.finalizeMatch(true, nowMs);
    }
  }

  private checkFailure(nowMs: number): void {
    if (this.phaseState.phase === "ended") {
      return;
    }

    const alivePlayers = [...this.playersBySocket.values()].filter((runtime) => runtime.connected && runtime.state.alive);
    if (alivePlayers.length === 0) {
      void this.finalizeMatch(false, nowMs);
    }
  }

  private async finalizeMatch(success: boolean, nowMs: number): Promise<void> {
    if (this.finalizing || this.phaseState.phase === "ended") {
      return;
    }

    this.finalizing = true;
    this.phaseState.phase = "ended";
    this.phaseState.endedAtMs = nowMs;
    this.phaseState.extraction.active = false;
    this.broadcastRoomState();

    const leaderboard: {
      playerId: string;
      nickname: string;
      kills: number;
      xpGained: number;
      survived: boolean;
    }[] = [];

    for (const runtime of this.playersBySocket.values()) {
      const survived = runtime.connected && runtime.state.alive;
      runtime.stats.survived = survived;
      runtime.stats.waveReached = this.phaseState.wave;

      const gainedXp = computeMatchXp(runtime.stats);

      try {
        const profile = (await this.profileStore.getById(runtime.profile.playerId)) ?? runtime.profile;
        const updatedProfile = mergeProgression(profile, gainedXp);
        await this.profileStore.saveProfile(updatedProfile);
        await this.profileStore.appendMatchHistory({
          playerId: runtime.profile.playerId,
          roomCode: this.roomCode,
          success,
          waveReached: this.phaseState.wave,
          stats: runtime.stats,
          xpGained: gainedXp
        });

        runtime.profile = updatedProfile;
        runtime.state.level = updatedProfile.level;

        this.emitter.toSocket(runtime.socketId, "progression:update", {
          profile: updatedProfile,
          gainedXp
        });
      } catch (error) {
        console.error("Progression persistence failed", error);
      }

      leaderboard.push({
        playerId: runtime.profile.playerId,
        nickname: runtime.profile.nickname,
        kills: runtime.stats.kills,
        xpGained: gainedXp,
        survived
      });
    }

    const durationSec = this.phaseState.startedAtMs
      ? Math.max(0, Math.floor((nowMs - this.phaseState.startedAtMs) / 1000))
      : 0;

    this.emitter.toRoom(this.roomCode, "match:end", {
      roomCode: this.roomCode,
      success,
      waveReached: this.phaseState.wave,
      durationSec,
      leaderboard: leaderboard.sort((a, b) => (b.kills === a.kills ? b.xpGained - a.xpGained : b.kills - a.kills))
    });

    this.finalizing = false;
  }

  private spawnWave(wave: number): void {
    const waveBase = WAVE_CONFIG.baseEnemies + (wave - 1) * WAVE_CONFIG.enemiesPerWaveGrowth;
    const enemiesToSpawn = Math.min(MAX_ACTIVE_ENEMIES, waveBase);

    const normalArchetypes = ENEMY_ARCHETYPES.filter((archetype) => !archetype.elite);
    const shouldSpawnBoss = wave >= WAVE_CONFIG.extractionWave;

    for (let index = 0; index < enemiesToSpawn; index += 1) {
      const archetype = normalArchetypes[randomInt(this.rng, 0, normalArchetypes.length - 1)];
      this.spawnEnemy(archetype);
    }

    if (shouldSpawnBoss) {
      const boss = ENEMY_ARCHETYPES.find((entry) => entry.id === "jw-boss");
      if (boss) {
        this.spawnEnemy(boss);
      }
    }

    for (const runtime of this.playersBySocket.values()) {
      runtime.stats.waveReached = wave;
    }
  }

  private spawnEnemy(archetype: EnemyArchetype): void {
    const angle = this.rng() * Math.PI * 2;
    const radius = 45 + this.rng() * 55;

    const position: Vec3 = {
      x: Math.cos(angle) * radius,
      y: 0,
      z: Math.sin(angle) * radius
    };

    const enemy: EnemyRuntime = {
      id: `enemy-${randomUUID()}`,
      archetype: archetype.id,
      spriteAsset: archetype.asset,
      position,
      velocity: { x: 0, y: 0, z: 0 },
      hp: archetype.hp,
      maxHp: archetype.hp,
      alive: true,
      targetPlayerId: null,
      elite: archetype.elite,
      archetypeData: archetype,
      lastAttackAtMs: 0,
      removedAtMs: 0
    };

    this.enemies.set(enemy.id, enemy);
  }

  private applyDamageToEnemy(
    enemy: EnemyRuntime,
    attacker: PlayerRuntime,
    damage: number,
    nowMs: number,
    critical: boolean,
    source: "primary" | "secondary"
  ): void {
    if (!enemy.alive) {
      return;
    }

    enemy.hp -= damage;
    attacker.stats.damageDone += damage;

    if (enemy.hp <= 0) {
      enemy.hp = 0;
      enemy.alive = false;
      enemy.removedAtMs = nowMs + 900;
      attacker.stats.kills += 1;
      attacker.state.kills += 1;

      this.emitGameEvent("kill", {
        playerId: attacker.state.id,
        enemyId: enemy.id,
        archetype: enemy.archetype
      });
    }
  }

  private damagePlayer(target: PlayerRuntime, incomingDamage: number, nowMs: number, enemyId: string): void {
    if (!target.state.alive) {
      return;
    }

    let remaining = incomingDamage;

    if (target.state.armor > 0) {
      const absorbed = Math.min(target.state.armor, Math.ceil(incomingDamage * 0.5));
      target.state.armor -= absorbed;
      remaining -= absorbed;
    }

    target.state.hp -= remaining;
    target.stats.damageTaken += remaining;

    if (target.state.hp <= 0) {
      target.state.hp = 0;
      target.state.alive = false;
      target.stats.survived = false;
    }

    if (nowMs % 997 === 0) {
      this.phaseState.tick += 0;
    }
  }

  private getAimDirection(yaw: number, pitch: number): Vec3 {
    const cosPitch = Math.cos(pitch);
    return normalize({
      x: Math.sin(yaw) * cosPitch,
      y: Math.sin(pitch),
      z: Math.cos(yaw) * cosPitch
    });
  }

  private cleanupEntities(nowMs: number): void {
    for (const [enemyId, enemy] of this.enemies.entries()) {
      if (!enemy.alive && enemy.removedAtMs > 0 && nowMs >= enemy.removedAtMs) {
        this.enemies.delete(enemyId);
      }
    }

    for (const [projectileId, projectile] of this.projectiles.entries()) {
      if (projectile.removedAtMs > 0 && nowMs >= projectile.removedAtMs + 100) {
        this.projectiles.delete(projectileId);
      }
    }
  }

  private createSnapshot(nowMs: number): GameSnapshot {
    return {
      tick: this.phaseState.tick,
      serverTimeMs: nowMs,
      phase: this.phaseState.phase,
      wave: this.phaseState.wave,
      players: [...this.playersBySocket.values()].map((runtime) => runtime.state),
      enemies: [...this.enemies.values()].map((enemy) => ({
        id: enemy.id,
        archetype: enemy.archetype,
        spriteAsset: enemy.spriteAsset,
        position: enemy.position,
        velocity: enemy.velocity,
        hp: enemy.hp,
        maxHp: enemy.maxHp,
        alive: enemy.alive,
        targetPlayerId: enemy.targetPlayerId,
        elite: enemy.elite
      })),
      projectiles: [...this.projectiles.values()].map((projectile) => ({
        id: projectile.id,
        ownerId: projectile.ownerId,
        position: projectile.position,
        velocity: projectile.velocity,
        ttlMs: projectile.ttlMs,
        damage: projectile.damage
      })),
      pickups: this.pickups,
      extraction: {
        center: this.phaseState.extraction.center,
        radius: this.phaseState.extraction.radius,
        progress: this.phaseState.extraction.progress,
        requiredProgress: this.phaseState.extraction.requiredProgress,
        active: this.phaseState.extraction.active
      }
    };
  }
}
