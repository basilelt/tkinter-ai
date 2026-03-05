import type { MatchPlayerStats, PlayerProfile } from "./types";
import { UNLOCK_CATALOG } from "./constants";

export function xpForLevel(level: number): number {
  if (level <= 1) {
    return 0;
  }

  return Math.floor(100 * Math.pow(level - 1, 1.25));
}

export function levelFromXp(xp: number): number {
  let level = 1;

  while (xpForLevel(level + 1) <= xp) {
    level += 1;
  }

  return level;
}

export function computeMatchXp(stats: MatchPlayerStats): number {
  const killXp = stats.kills * 16;
  const damageXp = Math.floor(stats.damageDone * 0.25);
  const surviveBonus = stats.survived ? 90 : 0;
  const reviveBonus = stats.revives * 50;
  const waveBonus = stats.waveReached * 32;
  const penalty = Math.floor(stats.damageTaken * 0.05);

  return Math.max(50, killXp + damageXp + surviveBonus + reviveBonus + waveBonus - penalty);
}

export function mergeProgression(profile: PlayerProfile, gainedXp: number): PlayerProfile {
  const nextXp = Math.max(0, profile.xp + gainedXp);
  const nextLevel = levelFromXp(nextXp);

  const unlockedWeaponIds = UNLOCK_CATALOG.weapons
    .filter((weapon) => weapon.requiredLevel <= nextLevel)
    .map((weapon) => weapon.id);

  const unlockedPerkIds = UNLOCK_CATALOG.perks
    .filter((perk) => perk.requiredLevel <= nextLevel)
    .map((perk) => perk.id);

  return {
    ...profile,
    xp: nextXp,
    level: nextLevel,
    unlockedWeaponIds,
    unlockedPerkIds,
    equippedWeaponId: unlockedWeaponIds.includes(profile.equippedWeaponId)
      ? profile.equippedWeaponId
      : unlockedWeaponIds[0],
    equippedPerkIds: profile.equippedPerkIds.filter((perkId) => unlockedPerkIds.includes(perkId))
  };
}
