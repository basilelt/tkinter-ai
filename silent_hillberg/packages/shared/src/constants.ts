import type { EnemyArchetype, UnlockCatalog } from "./types";

export const GAME_TICK_RATE = 30;
export const SNAPSHOT_RATE = 10;
export const MAX_PLAYERS_PER_ROOM = 4;
export const MAX_ACTIVE_ENEMIES = 42;
export const ROOM_CODE_LENGTH = 6;

export const WORLD_BOUNDS = {
  minX: -120,
  maxX: 120,
  minY: 0,
  maxY: 20,
  minZ: -120,
  maxZ: 120
} as const;

export const PLAYER_DEFAULTS = {
  maxHp: 100,
  maxArmor: 50,
  walkSpeed: 7.2,
  sprintSpeed: 11.2,
  dashSpeedBoost: 18,
  dashDurationMs: 170,
  dashCooldownMs: 1400,
  jumpVelocity: 5.6,
  gravity: 18,
  friction: 10,
  primaryDamage: 18,
  primaryHeadshotMultiplier: 1.85,
  primaryRange: 45,
  primaryAmmoMax: 999,
  primaryFireIntervalMs: 120,
  reloadDurationMs: 1500,
  secondaryDamage: 35,
  secondaryAmmoMax: 999,
  secondaryFireIntervalMs: 900,
  projectileSpeed: 26
} as const;

export const WAVE_CONFIG = {
  baseEnemies: 6,
  enemiesPerWaveGrowth: 2,
  interWaveDelayMs: 3000,
  extractionWave: 3,
  extractionRequiredMs: 8500
} as const;

export const UNLOCK_CATALOG: UnlockCatalog = {
  weapons: [
    {
      id: "rusty-rifle",
      requiredLevel: 1,
      displayName: "Rusty Rifle",
      description: "Arme fiable et rapide, style Doom classique."
    },
    {
      id: "campus-shotgun",
      requiredLevel: 3,
      displayName: "Campus Shotgun",
      description: "Très puissant à courte portée avec spread large."
    },
    {
      id: "illberg-rail",
      requiredLevel: 6,
      displayName: "Illberg Rail",
      description: "Tir perçant longue portée pour cibles alignées."
    }
  ],
  perks: [
    {
      id: "adrenaline",
      requiredLevel: 2,
      displayName: "Adrenaline",
      description: "Bonus de vitesse temporaire après une élimination."
    },
    {
      id: "iron-lung",
      requiredLevel: 4,
      displayName: "Iron Lung",
      description: "Réduit la perte de stamina en sprint."
    },
    {
      id: "fog-hunter",
      requiredLevel: 5,
      displayName: "Fog Hunter",
      description: "Augmente la visibilité des silhouettes ennemies."
    }
  ]
};

export const ENEMY_ARCHETYPES: EnemyArchetype[] = [
  {
    id: "maigreur",
    asset: "cyril_maigreur.jpeg",
    hp: 60,
    damage: 8,
    speed: 4.2,
    xpReward: 24,
    scale: 2.1,
    attackRange: 1.5,
    attackCooldownMs: 1150,
    elite: false
  },
  {
    id: "hassen",
    asset: "hassen.jpg",
    hp: 78,
    damage: 10,
    speed: 3.8,
    xpReward: 28,
    scale: 2.05,
    attackRange: 1.6,
    attackCooldownMs: 1100,
    elite: false
  },
  {
    id: "jw2",
    asset: "jw2.jpeg",
    hp: 72,
    damage: 11,
    speed: 4.5,
    xpReward: 30,
    scale: 2.2,
    attackRange: 1.5,
    attackCooldownMs: 980,
    elite: false
  },
  {
    id: "jw3",
    asset: "jw3.jpg",
    hp: 80,
    damage: 12,
    speed: 4.1,
    xpReward: 32,
    scale: 2.2,
    attackRange: 1.7,
    attackCooldownMs: 1000,
    elite: false
  },
  {
    id: "jw4",
    asset: "jw4.webp",
    hp: 95,
    damage: 14,
    speed: 4.0,
    xpReward: 36,
    scale: 2.4,
    attackRange: 1.8,
    attackCooldownMs: 940,
    elite: false
  },
  {
    id: "perronne",
    asset: "perronne.jpeg",
    hp: 110,
    damage: 16,
    speed: 3.7,
    xpReward: 40,
    scale: 2.45,
    attackRange: 1.8,
    attackCooldownMs: 1020,
    elite: false
  },
  {
    id: "chat",
    asset: "le_chat_mange_la_souris.webp",
    hp: 65,
    damage: 9,
    speed: 5.2,
    xpReward: 34,
    scale: 1.9,
    attackRange: 1.3,
    attackCooldownMs: 760,
    elite: false
  },
  {
    id: "jw-boss",
    asset: "JW.png",
    hp: 600,
    damage: 26,
    speed: 3.4,
    xpReward: 350,
    scale: 3.8,
    attackRange: 2.4,
    attackCooldownMs: 900,
    elite: true
  }
];
