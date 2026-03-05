import { describe, expect, it } from "vitest";
import { InMemoryProfileStore } from "../storage/in-memory-profile-store";
import { GameRoom } from "./game-room";

describe("GameRoom", () => {
  it("starts when player is ready", async () => {
    const events: Array<{ event: string; payload: unknown }> = [];
    const store = new InMemoryProfileStore();
    const profile = await store.upsertGuest("RoomPlayer", "room-player-fingerprint");

    const room = new GameRoom("ABC123", store, {
      toRoom: (_roomCode, event, payload) => {
        events.push({ event, payload });
      },
      toSocket: () => {
        return;
      }
    });

    const added = room.addPlayer("socket-1", profile);
    expect(added.ok).toBe(true);

    room.setReady("socket-1", true);
    room.tick(Date.now(), 1 / 30);

    expect(room.toRoomState().phase).toBe("running");
    expect(events.some((entry) => entry.event === "game:event")).toBe(true);
  });
});
