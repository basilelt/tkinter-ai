export function calculateDamage(baseDamage: number, isHeadshot: boolean, distance: number, maxRange: number): number {
  const clampedDistance = Math.max(0, Math.min(distance, maxRange));
  const falloff = 1 - 0.55 * (clampedDistance / maxRange);
  const headshotMultiplier = isHeadshot ? 1.85 : 1;

  return Math.max(1, Math.round(baseDamage * falloff * headshotMultiplier));
}

export function isCriticalHit(normalizedHitHeight: number): boolean {
  return normalizedHitHeight > 0.72;
}
