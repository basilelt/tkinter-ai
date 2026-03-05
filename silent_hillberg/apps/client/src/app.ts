import type { GameSnapshot, NetPlayerState, PlayerProfile } from "@silent-hillberg/shared";
import { AudioEngine } from "./audio/audio-engine";
import { InputController } from "./game/input-controller";
import { WorldRenderer } from "./game/world-renderer";
import { ApiClient } from "./net/api-client";
import { GameSocketClient } from "./net/game-socket";

function createDeviceFingerprint(): string {
  const key = "silent-hillberg-device-id";
  const existing = localStorage.getItem(key);
  if (existing) {
    return existing;
  }

  const created = `${Date.now().toString(36)}-${crypto.randomUUID()}`;
  localStorage.setItem(key, created);
  return created;
}

function byId<T extends HTMLElement>(root: ParentNode, id: string): T {
  const node = root.querySelector<T>(`#${id}`);
  if (!node) {
    throw new Error(`Missing element #${id}`);
  }
  return node;
}

interface RoomState {
  roomCode: string;
  phase: "lobby" | "running" | "extraction" | "ended";
  players: Array<{
    playerId: string;
    nickname: string;
    ready: boolean;
    connected: boolean;
    level: number;
  }>;
}

export class SilentHillbergApp {
  private readonly api = new ApiClient("");
  private readonly socket = new GameSocketClient();
  private readonly audio = new AudioEngine();

  private readonly canvas: HTMLCanvasElement;
  private readonly menuScreen: HTMLDivElement;
  private readonly statusLine: HTMLDivElement;
  private readonly lobbyList: HTMLDivElement;
  private readonly matchOverlay: HTMLDivElement;
  private readonly matchTitle: HTMLHeadingElement;
  private readonly matchRows: HTMLTableSectionElement;

  private readonly inputNickname: HTMLInputElement;
  private readonly inputRoomCode: HTMLInputElement;
  private readonly createRoomButton: HTMLButtonElement;
  private readonly joinRoomButton: HTMLButtonElement;
  private readonly readyButton: HTMLButtonElement;

  private readonly waveLabel: HTMLSpanElement;
  private readonly roomLabel: HTMLSpanElement;
  private readonly hpFill: HTMLDivElement;
  private readonly armorFill: HTMLDivElement;
  private readonly hpText: HTMLSpanElement;
  private readonly armorText: HTMLSpanElement;
  private readonly ammoText: HTMLSpanElement;
  private readonly levelText: HTMLSpanElement;
  private readonly phaseText: HTMLSpanElement;
  private readonly extractionText: HTMLSpanElement;
  private readonly feedList: HTMLDivElement;

  private readonly masterSlider: HTMLInputElement;
  private readonly musicSlider: HTMLInputElement;
  private readonly sfxSlider: HTMLInputElement;
  private readonly voiceSlider: HTMLInputElement;

  private readonly renderer: WorldRenderer;
  private readonly input: InputController;

  private session: { token: string; profile: PlayerProfile } | null = null;
  private roomState: RoomState | null = null;
  private snapshot: GameSnapshot | null = null;

  private inputSeq = 0;
  private lastFrameAt = performance.now();
  private rafId = 0;
  private hasGameFocus = false;
  private readyState = false;
  private lastAckTick = -1;

  private frameBudgetSample = 0;
  private frameBudgetCount = 0;

  public constructor(private readonly root: HTMLElement) {
    root.innerHTML = this.template();

    this.canvas = byId<HTMLCanvasElement>(root, "game-canvas");
    this.menuScreen = byId<HTMLDivElement>(root, "menu-screen");
    this.statusLine = byId<HTMLDivElement>(root, "status-line");
    this.lobbyList = byId<HTMLDivElement>(root, "lobby-list");
    this.matchOverlay = byId<HTMLDivElement>(root, "match-overlay");
    this.matchTitle = byId<HTMLHeadingElement>(root, "match-title");
    this.matchRows = byId<HTMLTableSectionElement>(root, "match-rows");

    this.inputNickname = byId<HTMLInputElement>(root, "nickname-input");
    this.inputRoomCode = byId<HTMLInputElement>(root, "room-code-input");
    this.createRoomButton = byId<HTMLButtonElement>(root, "create-room-button");
    this.joinRoomButton = byId<HTMLButtonElement>(root, "join-room-button");
    this.readyButton = byId<HTMLButtonElement>(root, "ready-button");

    this.waveLabel = byId<HTMLSpanElement>(root, "wave-label");
    this.roomLabel = byId<HTMLSpanElement>(root, "room-label");
    this.hpFill = byId<HTMLDivElement>(root, "hp-fill");
    this.armorFill = byId<HTMLDivElement>(root, "armor-fill");
    this.hpText = byId<HTMLSpanElement>(root, "hp-text");
    this.armorText = byId<HTMLSpanElement>(root, "armor-text");
    this.ammoText = byId<HTMLSpanElement>(root, "ammo-text");
    this.levelText = byId<HTMLSpanElement>(root, "level-text");
    this.phaseText = byId<HTMLSpanElement>(root, "phase-text");
    this.extractionText = byId<HTMLSpanElement>(root, "extraction-text");
    this.feedList = byId<HTMLDivElement>(root, "feed-list");

    this.masterSlider = byId<HTMLInputElement>(root, "master-slider");
    this.musicSlider = byId<HTMLInputElement>(root, "music-slider");
    this.sfxSlider = byId<HTMLInputElement>(root, "sfx-slider");
    this.voiceSlider = byId<HTMLInputElement>(root, "voice-slider");

    this.renderer = new WorldRenderer(this.canvas);
    this.input = new InputController(this.canvas);

    this.bindUi();
    this.bindSocket();

    this.rafId = requestAnimationFrame((timestamp) => this.loop(timestamp));
  }

  private template(): string {
    return `
      <div id="game-root">
        <canvas id="game-canvas"></canvas>

        <section id="menu-screen" class="menu-screen">
          <div class="menu-panel">
            <h1 class="title">Silent Hillberg</h1>
            <p class="subtitle">FPS horror coop 1-4 sur le campus UHA Illberg.</p>

            <div class="menu-grid">
              <div>
                <label for="nickname-input">Pseudo</label>
                <input id="nickname-input" value="IllbergRunner" maxlength="24" />
              </div>
              <div>
                <label for="room-code-input">Code room</label>
                <input id="room-code-input" placeholder="ABC123" maxlength="6" />
              </div>
            </div>

            <div class="menu-actions">
              <button id="create-room-button" class="primary">Créer room</button>
              <button id="join-room-button">Rejoindre room</button>
            </div>

            <div class="menu-actions">
              <button id="ready-button">Ready</button>
            </div>

            <div id="status-line" class="status-line"></div>
            <div id="lobby-list" class="lobby-list"></div>
          </div>
        </section>

        <section class="hud" id="hud">
          <div class="crosshair"></div>

          <div class="hud-top">
            <div class="wave-pill" id="wave-label">Wave 0</div>
            <div class="wave-pill" id="phase-text">Lobby</div>
            <div class="wave-pill" id="extraction-text">Extraction: 0%</div>
            <div class="room-pill" id="room-label">Room: ----</div>
          </div>

          <div class="hud-bottom">
            <div class="player-card">
              <img src="/assets/joueur.jpeg" alt="Portrait joueur" />
              <div class="player-stats">
                <div>
                  <strong id="level-text">Lvl 1</strong>
                  <span id="ammo-text" style="float:right">Ammo 0 / 0</span>
                </div>
                <div class="bars">
                  <div>
                    <div>Vie <span id="hp-text">100</span></div>
                    <div class="bar"><div id="hp-fill" class="bar-fill hp"></div></div>
                  </div>
                  <div>
                    <div>Armure <span id="armor-text">0</span></div>
                    <div class="bar"><div id="armor-fill" class="bar-fill armor"></div></div>
                  </div>
                </div>
              </div>
            </div>

            <div class="hud-right">
              <div class="audio-card">
                <div class="audio-row"><span>Master</span><input id="master-slider" type="range" min="0" max="1" step="0.01" value="0.82" /></div>
                <div class="audio-row"><span>Music</span><input id="music-slider" type="range" min="0" max="1" step="0.01" value="0.62" /></div>
                <div class="audio-row"><span>SFX</span><input id="sfx-slider" type="range" min="0" max="1" step="0.01" value="0.75" /></div>
                <div class="audio-row"><span>Voice</span><input id="voice-slider" type="range" min="0" max="1" step="0.01" value="0.55" /></div>
              </div>
              <div class="feed-card" id="feed-list"></div>
            </div>
          </div>

          <div class="vignette"></div>
          <div class="grain"></div>
        </section>

        <section id="match-overlay" class="match-overlay">
          <div class="match-panel">
            <h2 id="match-title" class="match-title">Résultat</h2>
            <table class="match-table">
              <thead>
                <tr>
                  <th>Player</th>
                  <th>Kills</th>
                  <th>XP</th>
                  <th>Survie</th>
                </tr>
              </thead>
              <tbody id="match-rows"></tbody>
            </table>
          </div>
        </section>
      </div>
    `;
  }

  private bindUi(): void {
    this.createRoomButton.addEventListener("click", async () => {
      await this.ensureAudio();
      await this.createRoom();
    });

    this.joinRoomButton.addEventListener("click", async () => {
      await this.ensureAudio();
      await this.joinRoom();
    });

    this.readyButton.addEventListener("click", () => {
      this.readyState = !this.readyState;
      this.readyButton.textContent = this.readyState ? "Unready" : "Ready";
      this.socket.setReady(this.readyState);
    });

    const onSlider = () => {
      this.audio.setMix({
        master: Number(this.masterSlider.value),
        music: Number(this.musicSlider.value),
        sfx: Number(this.sfxSlider.value),
        voice: Number(this.voiceSlider.value)
      });
    };

    this.masterSlider.addEventListener("input", onSlider);
    this.musicSlider.addEventListener("input", onSlider);
    this.sfxSlider.addEventListener("input", onSlider);
    this.voiceSlider.addEventListener("input", onSlider);
  }

  private bindSocket(): void {
    this.socket.onRoomState = (state) => {
      this.roomState = state;
      this.roomLabel.textContent = `Room: ${state.roomCode}`;
      this.phaseText.textContent = state.phase.toUpperCase();
      this.renderLobby(state);

      const gameActive = state.phase === "running" || state.phase === "extraction";
      this.hasGameFocus = gameActive;
      this.menuScreen.style.display = gameActive ? "none" : "flex";
      this.input.setEnabled(gameActive);

      if (state.phase === "lobby") {
        this.readyState = false;
        this.readyButton.textContent = "Ready";
      }
    };

    this.socket.onSnapshot = (snapshot) => {
      this.snapshot = snapshot;
      this.waveLabel.textContent = `Wave ${snapshot.wave}`;
      if (this.lastAckTick !== snapshot.tick) {
        this.socket.ackSnapshot(snapshot.tick);
        this.lastAckTick = snapshot.tick;
      }

      if (snapshot.extraction.active) {
        const percent = Math.floor((snapshot.extraction.progress / Math.max(1, snapshot.extraction.requiredProgress)) * 100);
        this.extractionText.textContent = `Extraction: ${percent}%`;
      } else {
        this.extractionText.textContent = "Extraction: 0%";
      }
    };

    this.socket.onGameEvent = (event) => {
      switch (event.type) {
        case "wave-start": {
          const wave = Number(event.payload.wave ?? 0);
          this.pushFeed(`Wave ${wave} commence`);
          this.audio.onWaveStart(wave);
          break;
        }
        case "wave-cleared": {
          this.pushFeed(`Wave ${event.payload.wave ?? "?"} nettoyée`);
          break;
        }
        case "hit": {
          this.audio.onHit();
          break;
        }
        case "kill": {
          const playerId = String(event.payload.playerId ?? "");
          if (this.session && playerId === this.session.profile.playerId) {
            this.audio.onKill();
            this.pushFeed("Kill confirmé");
          }
          break;
        }
        case "damage": {
          const playerId = String(event.payload.playerId ?? "");
          if (this.session && playerId === this.session.profile.playerId) {
            this.audio.onDamage();
          }
          break;
        }
        case "reload": {
          this.pushFeed("Reload terminé");
          break;
        }
        case "extraction-open": {
          this.pushFeed("Extraction ouverte! Rejoignez la zone.");
          this.audio.onExtractionOpen();
          break;
        }
        default:
          break;
      }
    };

    this.socket.onProgressionUpdate = ({ profile, gainedXp }) => {
      if (this.session) {
        this.session.profile = profile;
      }

      this.levelText.textContent = `Lvl ${profile.level}`;
      this.pushFeed(`+${gainedXp} XP`);
    };

    this.socket.onMatchEnd = (result) => {
      this.hasGameFocus = false;
      this.input.setEnabled(false);
      this.menuScreen.style.display = "flex";

      this.matchTitle.textContent = result.success
        ? `Victoire - Wave ${result.waveReached}`
        : `Défaite - Wave ${result.waveReached}`;
      this.matchRows.innerHTML = "";

      for (const row of result.leaderboard) {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${row.nickname}</td>
          <td>${row.kills}</td>
          <td>${row.xpGained}</td>
          <td>${row.survived ? "Oui" : "Non"}</td>
        `;
        this.matchRows.appendChild(tr);
      }

      this.matchOverlay.classList.add("visible");
      window.setTimeout(() => {
        this.matchOverlay.classList.remove("visible");
      }, 9000);
    };

    this.socket.onDisconnect = () => {
      this.statusLine.textContent = "Déconnecté du serveur.";
      this.hasGameFocus = false;
      this.input.setEnabled(false);
      this.menuScreen.style.display = "flex";
    };
  }

  private async createRoom(): Promise<void> {
    try {
      const session = await this.ensureSession();
      this.socket.connect();

      const created = await this.socket.createRoom(session.token);
      if (!created.ok) {
        this.statusLine.textContent = created.reason;
        return;
      }

      this.statusLine.textContent = `Room ${created.roomCode} créée.`;
      this.inputRoomCode.value = created.roomCode;
      this.matchOverlay.classList.remove("visible");
    } catch (error) {
      this.statusLine.textContent = error instanceof Error ? error.message : "Erreur inconnue";
    }
  }

  private async joinRoom(): Promise<void> {
    const roomCode = this.inputRoomCode.value.trim().toUpperCase();
    if (roomCode.length !== 6) {
      this.statusLine.textContent = "Code room invalide (6 caractères).";
      return;
    }

    try {
      const session = await this.ensureSession();
      this.socket.connect();

      const joined = await this.socket.joinRoom(session.token, roomCode);
      if (!joined.ok) {
        this.statusLine.textContent = joined.reason;
        return;
      }

      this.statusLine.textContent = `Connecté à ${roomCode}.`;
      this.matchOverlay.classList.remove("visible");
    } catch (error) {
      this.statusLine.textContent = error instanceof Error ? error.message : "Erreur inconnue";
    }
  }

  private async ensureSession(): Promise<{ token: string; profile: PlayerProfile }> {
    const nickname = this.inputNickname.value.trim() || "IllbergRunner";

    if (this.session) {
      return this.session;
    }

    const fingerprint = createDeviceFingerprint();
    const auth = await this.api.authGuest(nickname, fingerprint);

    this.session = {
      token: auth.token,
      profile: auth.profile
    };

    this.levelText.textContent = `Lvl ${auth.profile.level}`;
    return this.session;
  }

  private renderLobby(state: RoomState): void {
    if (state.players.length === 0) {
      this.lobbyList.innerHTML = "Aucun joueur";
      return;
    }

    this.lobbyList.innerHTML = state.players
      .map(
        (player) =>
          `<div class="lobby-player"><span>${player.nickname} (Lvl ${player.level})</span><span>${
            player.connected ? (player.ready ? "READY" : "WAIT") : "DC"
          }</span></div>`
      )
      .join("");
  }

  private renderHud(localPlayer: NetPlayerState | null): void {
    if (!localPlayer) {
      return;
    }

    this.hpText.textContent = `${Math.max(0, Math.floor(localPlayer.hp))}`;
    this.armorText.textContent = `${Math.max(0, Math.floor(localPlayer.armor))}`;
    this.ammoText.textContent = `Ammo ${localPlayer.ammoPrimary} / ${localPlayer.ammoSecondary}`;
    this.levelText.textContent = `Lvl ${localPlayer.level}`;

    this.hpFill.style.width = `${Math.max(0, Math.min(100, localPlayer.hp))}%`;
    this.armorFill.style.width = `${Math.max(0, Math.min(100, (localPlayer.armor / 50) * 100))}%`;
  }

  private pushFeed(text: string): void {
    const line = document.createElement("div");
    line.className = "feed-line";
    line.textContent = `[${new Date().toLocaleTimeString()}] ${text}`;

    this.feedList.prepend(line);

    while (this.feedList.children.length > 8) {
      this.feedList.removeChild(this.feedList.lastChild as Node);
    }
  }

  private async ensureAudio(): Promise<void> {
    await this.audio.start();
  }

  private loop(timestamp: number): void {
    const dtMs = Math.max(1, Math.min(60, timestamp - this.lastFrameAt));
    this.lastFrameAt = timestamp;

    this.frameBudgetSample += dtMs;
    this.frameBudgetCount += 1;
    if (this.frameBudgetCount >= 60) {
      const avg = this.frameBudgetSample / this.frameBudgetCount;
      this.audio.setLowAudioMode(avg > 26);
      this.frameBudgetSample = 0;
      this.frameBudgetCount = 0;
    }

    if (this.hasGameFocus && this.session && this.snapshot) {
      const local = this.snapshot.players.find((player) => player.id === this.session!.profile.playerId) ?? null;
      if (local) {
        const inputFrame = this.input.buildFrame(this.inputSeq, dtMs);
        this.inputSeq += 1;
        this.socket.sendInput(inputFrame);

        if (inputFrame.firePrimary) {
          this.audio.onPrimaryShot();
        }
      }

      this.renderHud(local);
    }

    this.renderer.render(this.snapshot, this.session?.profile.playerId ?? null);

    this.rafId = requestAnimationFrame((next) => this.loop(next));
  }

  public destroy(): void {
    cancelAnimationFrame(this.rafId);
    this.input.dispose();
    this.renderer.dispose();
    this.socket.disconnect();
  }
}
