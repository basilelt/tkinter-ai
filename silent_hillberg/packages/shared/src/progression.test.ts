import { describe, expect, it } from "vitest";
import { computeMatchXp, levelFromXp, mergeProgression } from "./progression";
import type { PlayerProfile } from "./types";

describe("progression", () => {
  it("should compute a minimum xp reward", () => {
    const xp = computeMatchXp({
      kills: 0,
      damageDone: 0,
      damageTaken: 999,
      revives: 0,
      survived: false,
      waveReached: 1
    });

    expect(xp).toBe(50);
  });

  it("should update level based on xp", () => {
    expect(levelFromXp(0)).toBe(1);
    expect(levelFromXp(100)).toBe(2);
    expect(levelFromXp(1000)).toBeGreaterThan(3);
  });

  it("should merge and unlock progression", () => {
    const profile: PlayerProfile = {
      playerId: "player-1",
      nickname: "test",
      level: 1,
      xp: 0,
      unlockedWeaponIds: ["rusty-rifle"],
      unlockedPerkIds: [],
      equippedWeaponId: "rusty-rifle",
      equippedPerkIds: []
    };

    const updated = mergeProgression(profile, 1000);

    expect(updated.level).toBeGreaterThan(1);
    expect(updated.unlockedWeaponIds.length).toBeGreaterThan(1);
  });
});
