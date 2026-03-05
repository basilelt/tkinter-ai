import { levelFromXp, UNLOCK_CATALOG, type PlayerProfile, type WeaponId } from "@silent-hillberg/shared";

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

export function ensureDefaultWeapon(profile: PlayerProfile): PlayerProfile {
  const defaultWeapon: WeaponId = "rusty-rifle";
  const unlockedWeaponIds = profile.unlockedWeaponIds.length > 0 ? profile.unlockedWeaponIds : [defaultWeapon];
  const equippedWeaponId = unlockedWeaponIds.includes(profile.equippedWeaponId) ? profile.equippedWeaponId : unlockedWeaponIds[0];

  return {
    ...profile,
    unlockedWeaponIds,
    equippedWeaponId
  };
}
