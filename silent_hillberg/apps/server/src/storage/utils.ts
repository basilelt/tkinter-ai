import { levelFromXp, UNLOCK_CATALOG, type PlayerProfile } from "@silent-hillberg/shared";

export function createBaseProfile(playerId: string, nickname: string): PlayerProfile {
  const level = 1;
  const unlockedWeaponIds = UNLOCK_CATALOG.weapons.filter((weapon) => weapon.requiredLevel <= level).map((weapon) => weapon.id);
  const unlockedPerkIds = UNLOCK_CATALOG.perks.filter((perk) => perk.requiredLevel <= level).map((perk) => perk.id);

  return {
    playerId,
    nickname,
    level,
    xp: 0,
    unlockedWeaponIds,
    unlockedPerkIds,
    equippedWeaponId: unlockedWeaponIds[0],
    equippedPerkIds: []
  };
}

export function clampLevelFromXp(xp: number): number {
  return Math.max(1, levelFromXp(xp));
}
