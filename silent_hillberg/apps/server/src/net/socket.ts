import {
  ackSnapshotSchema,
  playerInputFrameSchema,
  roomCreateSchema,
  roomJoinSchema,
  roomReadySchema
} from "@silent-hillberg/protocol";
import { Server, type Socket } from "socket.io";
import { verifyAuthToken } from "../auth/token";
import { RoomManager } from "../game/room-manager";
import type { ProfileStore } from "../storage/profile-store";

type AckResponse = {
  ok: boolean;
  roomCode?: string;
  reason?: string;
};

type AckFn = (response: AckResponse) => void;

export function registerSocketHandlers(io: Server, roomManager: RoomManager, profileStore: ProfileStore): void {
  io.on("connection", (socket) => {
    socket.on("room:create", async (payload, ack?: AckFn) => {
      const parsed = roomCreateSchema.safeParse(payload);
      if (!parsed.success) {
        ack?.({ ok: false, reason: "Invalid payload" });
        return;
      }

      const auth = verifyAuthToken(parsed.data.token);
      if (!auth) {
        ack?.({ ok: false, reason: "Invalid token" });
        return;
      }

      const profile = await profileStore.getById(auth.playerId);
      if (!profile) {
        ack?.({ ok: false, reason: "Profile not found" });
        return;
      }

      const result = roomManager.createRoom(socket.id, profile);
      if (!result.ok) {
        ack?.({ ok: false, reason: result.reason });
        return;
      }

      socket.data.playerId = profile.playerId;
      socket.data.nickname = profile.nickname;
      socket.data.roomCode = result.roomCode;

      socket.join(result.roomCode);
      roomManager.emitRoomState(result.roomCode);
      ack?.({ ok: true, roomCode: result.roomCode });
    });

    socket.on("room:join", async (payload, ack?: AckFn) => {
      const parsed = roomJoinSchema.safeParse(payload);
      if (!parsed.success) {
        ack?.({ ok: false, reason: "Invalid payload" });
        return;
      }

      const auth = verifyAuthToken(parsed.data.token);
      if (!auth) {
        ack?.({ ok: false, reason: "Invalid token" });
        return;
      }

      const profile = await profileStore.getById(auth.playerId);
      if (!profile) {
        ack?.({ ok: false, reason: "Profile not found" });
        return;
      }

      const roomCode = parsed.data.roomCode.toUpperCase();
      const joined = roomManager.joinRoom(socket.id, profile, roomCode);
      if (!joined.ok) {
        ack?.({ ok: false, reason: joined.reason });
        return;
      }

      socket.data.playerId = profile.playerId;
      socket.data.nickname = profile.nickname;
      socket.data.roomCode = roomCode;

      socket.join(roomCode);
      roomManager.emitRoomState(roomCode);
      ack?.({ ok: true, roomCode });
    });

    socket.on("room:ready", (payload) => {
      const parsed = roomReadySchema.safeParse(payload);
      if (!parsed.success) {
        return;
      }

      roomManager.setReady(socket.id, parsed.data.ready);
      const roomCode = roomManager.getRoomCodeBySocket(socket.id);
      if (roomCode) {
        roomManager.emitRoomState(roomCode);
      }
    });

    socket.on("player:input", (payload) => {
      const parsed = playerInputFrameSchema.safeParse(payload);
      if (!parsed.success) {
        return;
      }

      roomManager.pushInput(socket.id, parsed.data);
    });

    socket.on("player:ackSnapshot", (payload) => {
      const parsed = ackSnapshotSchema.safeParse(payload);
      if (!parsed.success) {
        return;
      }

      roomManager.ackSnapshot(socket.id, parsed.data.tick);
    });

    socket.on("disconnect", () => {
      const roomCode = roomManager.getRoomCodeBySocket(socket.id);
      roomManager.disconnect(socket.id);

      if (roomCode) {
        roomManager.emitRoomState(roomCode);
      }
    });
  });
}
