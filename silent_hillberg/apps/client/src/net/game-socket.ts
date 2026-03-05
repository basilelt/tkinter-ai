import type {
  GameSnapshot,
  PlayerInputFrame,
  PlayerProfile
} from "@silent-hillberg/shared";
import type { Socket } from "socket.io-client";
import { io } from "socket.io-client";

interface RoomStatePayload {
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

interface MatchEndPayload {
  roomCode: string;
  success: boolean;
  waveReached: number;
  durationSec: number;
  leaderboard: Array<{
    playerId: string;
    nickname: string;
    kills: number;
    xpGained: number;
    survived: boolean;
  }>;
}

interface GameEventPayload {
  type: string;
  atMs: number;
  payload: Record<string, unknown>;
}

interface ProgressionPayload {
  profile: PlayerProfile;
  gainedXp: number;
}

export class GameSocketClient {
  private socket: Socket | null = null;

  public onRoomState?: (payload: RoomStatePayload) => void;
  public onSnapshot?: (payload: GameSnapshot) => void;
  public onGameEvent?: (payload: GameEventPayload) => void;
  public onProgressionUpdate?: (payload: ProgressionPayload) => void;
  public onMatchEnd?: (payload: MatchEndPayload) => void;
  public onDisconnect?: () => void;

  public connect(): void {
    if (this.socket && this.socket.connected) {
      return;
    }

    this.socket = io({
      transports: ["websocket", "polling"]
    });

    this.socket.on("room:state", (payload: RoomStatePayload) => {
      this.onRoomState?.(payload);
    });

    this.socket.on("game:snapshot", (payload: GameSnapshot) => {
      this.onSnapshot?.(payload);
    });

    this.socket.on("game:event", (payload: GameEventPayload) => {
      this.onGameEvent?.(payload);
    });

    this.socket.on("progression:update", (payload: ProgressionPayload) => {
      this.onProgressionUpdate?.(payload);
    });

    this.socket.on("match:end", (payload: MatchEndPayload) => {
      this.onMatchEnd?.(payload);
    });

    this.socket.on("disconnect", () => {
      this.onDisconnect?.();
    });
  }

  public disconnect(): void {
    this.socket?.disconnect();
    this.socket = null;
  }

  public isConnected(): boolean {
    return Boolean(this.socket?.connected);
  }

  public async createRoom(token: string): Promise<{ ok: true; roomCode: string } | { ok: false; reason: string }> {
    if (!this.socket) {
      return { ok: false, reason: "Socket unavailable" };
    }

    return new Promise((resolve) => {
      this.socket!.emit("room:create", { token }, (ack: { ok: boolean; roomCode?: string; reason?: string }) => {
        if (ack.ok && ack.roomCode) {
          resolve({ ok: true, roomCode: ack.roomCode });
          return;
        }

        resolve({ ok: false, reason: ack.reason ?? "Unable to create room" });
      });
    });
  }

  public async joinRoom(token: string, roomCode: string): Promise<{ ok: true } | { ok: false; reason: string }> {
    if (!this.socket) {
      return { ok: false, reason: "Socket unavailable" };
    }

    return new Promise((resolve) => {
      this.socket!.emit(
        "room:join",
        {
          token,
          roomCode
        },
        (ack: { ok: boolean; reason?: string }) => {
          if (ack.ok) {
            resolve({ ok: true });
            return;
          }

          resolve({ ok: false, reason: ack.reason ?? "Unable to join room" });
        }
      );
    });
  }

  public setReady(ready: boolean): void {
    this.socket?.emit("room:ready", { ready });
  }

  public sendInput(frame: PlayerInputFrame): void {
    this.socket?.emit("player:input", frame);
  }

  public ackSnapshot(tick: number): void {
    this.socket?.emit("player:ackSnapshot", { tick });
  }
}
