export type PlayerId = string;
export type RoomCode = string;
export type EntityId = string;

export interface Vec3 {
  x: number;
  y: number;
  z: number;
}

export interface PlayerInputFrame {
  seq: number;
  dtMs: number;
  moveX: number;
  moveZ: number;
  yaw: number;
  pitch: number;
  jump: boolean;
  sprint: boolean;
  dash: boolean;
  firePrimary: boolean;
  fireSecondary: boolean;
  reload: boolean;
}

export interface NetPlayerState {
  id: PlayerId;
  nickname: string;
  position: Vec3;
  velocity: Vec3;
  yaw: number;
  pitch: number;
  hp: number;
  armor: number;
  ammoPrimary: number;
  ammoSecondary: number;
  sprinting: boolean;
  grounded: boolean;
  isReloading: boolean;
  kills: number;
  alive: boolean;
  level: number;
}

export interface NetEnemyState {
  id: EntityId;
  archetype: EnemyArchetypeId;
  spriteAsset: string;
  position: Vec3;
  velocity: Vec3;
  hp: number;
  maxHp: number;
  alive: boolean;
  targetPlayerId: PlayerId | null;
  elite: boolean;
}

export interface NetProjectileState {
  id: EntityId;
  ownerId: PlayerId;
  position: Vec3;
  velocity: Vec3;
  ttlMs: number;
  damage: number;
}

export interface NetPickupState {
  id: EntityId;
  kind: "ammo" | "medkit" | "armor";
  position: Vec3;
  active: boolean;
}

export interface ExtractionZone {
  center: Vec3;
  radius: number;
  progress: number;
  requiredProgress: number;
  active: boolean;
}

export interface GameSnapshot {
  tick: number;
  serverTimeMs: number;
  phase: MatchPhase;
  wave: number;
  players: NetPlayerState[];
  enemies: NetEnemyState[];
  projectiles: NetProjectileState[];
  pickups: NetPickupState[];
  extraction: ExtractionZone;
}

export interface PlayerProfile {
  playerId: PlayerId;
  nickname: string;
  level: number;
  xp: number;
  unlockedWeaponIds: WeaponId[];
  unlockedPerkIds: PerkId[];
  equippedWeaponId: WeaponId;
  equippedPerkIds: PerkId[];
}

export interface UnlockNode<TId extends string> {
  id: TId;
  requiredLevel: number;
  displayName: string;
  description: string;
}

export interface UnlockCatalog {
  weapons: UnlockNode<WeaponId>[];
  perks: UnlockNode<PerkId>[];
}

export type WeaponId = "rusty-rifle" | "campus-shotgun" | "illberg-rail";
export type PerkId = "adrenaline" | "iron-lung" | "fog-hunter";

export type MatchPhase = "lobby" | "running" | "extraction" | "ended";

export type EnemyArchetypeId =
  | "maigreur"
  | "hassen"
  | "jw2"
  | "jw3"
  | "jw4"
  | "perronne"
  | "chat"
  | "jw-boss";

export interface EnemyArchetype {
  id: EnemyArchetypeId;
  asset: string;
  hp: number;
  damage: number;
  speed: number;
  xpReward: number;
  scale: number;
  attackRange: number;
  attackCooldownMs: number;
  elite: boolean;
}

export interface MatchPlayerStats {
  kills: number;
  damageDone: number;
  damageTaken: number;
  revives: number;
  survived: boolean;
  waveReached: number;
}
