import { GAME_TICK_RATE, ROOM_CODE_LENGTH, type PlayerInputFrame, type PlayerProfile } from "@silent-hillberg/shared";
import { Server } from "socket.io";
import type { ProfileStore } from "../storage/profile-store";
import { GameRoom } from "./game-room";

export class RoomManager {
  private readonly roomsByCode = new Map<string, GameRoom>();
  private readonly roomCodeBySocket = new Map<string, string>();
  private loopHandle: NodeJS.Timeout | null = null;

  public constructor(
    private readonly io: Server,
    private readonly profileStore: ProfileStore
  ) {}

  public start(): void {
    if (this.loopHandle) {
      return;
    }

    this.loopHandle = setInterval(() => {
      const nowMs = Date.now();
      const dtSec = 1 / GAME_TICK_RATE;

      for (const [roomCode, room] of this.roomsByCode.entries()) {
        room.tick(nowMs, dtSec);

        if (room.isDisposable(nowMs)) {
          this.roomsByCode.delete(roomCode);
        }
      }
    }, 1000 / GAME_TICK_RATE);
  }

  public stop(): void {
    if (!this.loopHandle) {
      return;
    }

    clearInterval(this.loopHandle);
    this.loopHandle = null;
  }

  public createRoom(socketId: string, profile: PlayerProfile): { ok: true; roomCode: string } | { ok: false; reason: string } {
    if (this.roomCodeBySocket.has(socketId)) {
      return { ok: false, reason: "Socket is already in a room" };
    }

    const roomCode = this.generateRoomCode();
    const room = new GameRoom(roomCode, this.profileStore, {
      toRoom: (targetRoomCode, event, payload) => {
        this.io.to(targetRoomCode).emit(event, payload);
      },
      toSocket: (targetSocketId, event, payload) => {
        this.io.to(targetSocketId).emit(event, payload);
      }
    });

    const joined = room.addPlayer(socketId, profile);
    if (!joined.ok) {
      return joined;
    }

    this.roomsByCode.set(roomCode, room);
    this.roomCodeBySocket.set(socketId, roomCode);

    return { ok: true, roomCode };
  }

  public joinRoom(socketId: string, profile: PlayerProfile, roomCode: string): { ok: true } | { ok: false; reason: string } {
    if (this.roomCodeBySocket.has(socketId)) {
      return { ok: false, reason: "Socket is already in a room" };
    }

    const room = this.roomsByCode.get(roomCode);
    if (!room) {
      return { ok: false, reason: "Room not found" };
    }

    const joined = room.addPlayer(socketId, profile);
    if (!joined.ok) {
      return joined;
    }

    this.roomCodeBySocket.set(socketId, roomCode);
    return { ok: true };
  }

  public setReady(socketId: string, ready: boolean): boolean {
    const room = this.getRoomBySocket(socketId);
    if (!room) {
      return false;
    }

    return room.setReady(socketId, ready);
  }

  public pushInput(socketId: string, input: PlayerInputFrame): void {
    const room = this.getRoomBySocket(socketId);
    if (!room) {
      return;
    }

    room.setInput(socketId, input);
  }

  public ackSnapshot(socketId: string, tick: number): void {
    const room = this.getRoomBySocket(socketId);
    if (!room) {
      return;
    }

    room.setAckTick(socketId, tick);
  }

  public disconnect(socketId: string): void {
    const roomCode = this.roomCodeBySocket.get(socketId);
    if (!roomCode) {
      return;
    }

    const room = this.roomsByCode.get(roomCode);
    if (room) {
      room.markDisconnected(socketId);
    }

    this.roomCodeBySocket.delete(socketId);
  }

  public getRoomCodeBySocket(socketId: string): string | null {
    return this.roomCodeBySocket.get(socketId) ?? null;
  }

  public emitRoomState(roomCode: string): void {
    const room = this.roomsByCode.get(roomCode);
    if (!room) {
      return;
    }

    this.io.to(roomCode).emit("room:state", room.toRoomState());
  }

  private getRoomBySocket(socketId: string): GameRoom | null {
    const roomCode = this.roomCodeBySocket.get(socketId);
    if (!roomCode) {
      return null;
    }

    return this.roomsByCode.get(roomCode) ?? null;
  }

  private generateRoomCode(): string {
    const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";

    let roomCode = "";
    do {
      roomCode = "";
      for (let index = 0; index < ROOM_CODE_LENGTH; index += 1) {
        roomCode += alphabet[Math.floor(Math.random() * alphabet.length)];
      }
    } while (this.roomsByCode.has(roomCode));

    return roomCode;
  }
}
