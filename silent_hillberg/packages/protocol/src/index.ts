import { z } from "zod";

const nicknameRegex = /^[a-zA-Z0-9_-]{2,24}$/;

export const guestAuthRequestSchema = z.object({
  nickname: z.string().regex(nicknameRegex, "Nickname must be 2-24 chars [a-zA-Z0-9_-]"),
  deviceFingerprint: z.string().min(8).max(128)
});

export const playerProfileSchema = z.object({
  playerId: z.string(),
  nickname: z.string(),
  level: z.number().int().min(1),
  xp: z.number().int().min(0),
  unlockedWeaponIds: z.array(z.enum(["rusty-rifle", "campus-shotgun", "illberg-rail"])),
  unlockedPerkIds: z.array(z.enum(["adrenaline", "iron-lung", "fog-hunter"])),
  equippedWeaponId: z.enum(["rusty-rifle", "campus-shotgun", "illberg-rail"]),
  equippedPerkIds: z.array(z.enum(["adrenaline", "iron-lung", "fog-hunter"]))
});

export const guestAuthResponseSchema = z.object({
  playerId: z.string(),
  token: z.string(),
  profile: playerProfileSchema
});

export const updateLoadoutSchema = z.object({
  equippedWeaponId: z.enum(["rusty-rifle", "campus-shotgun", "illberg-rail"]),
  equippedPerkIds: z.array(z.enum(["adrenaline", "iron-lung", "fog-hunter"])).max(2)
});

export const roomCreateSchema = z.object({
  token: z.string()
});

export const roomJoinSchema = z.object({
  token: z.string(),
  roomCode: z.string().length(6)
});

export const roomReadySchema = z.object({
  ready: z.boolean()
});

export const playerInputFrameSchema = z.object({
  seq: z.number().int().min(0),
  dtMs: z.number().min(1).max(100),
  moveX: z.number().min(-1).max(1),
  moveZ: z.number().min(-1).max(1),
  yaw: z.number(),
  pitch: z.number().min(-1.45).max(1.45),
  jump: z.boolean(),
  sprint: z.boolean(),
  dash: z.boolean(),
  firePrimary: z.boolean(),
  fireSecondary: z.boolean(),
  reload: z.boolean()
});

export const ackSnapshotSchema = z.object({
  tick: z.number().int().nonnegative()
});

export const clientToServerSchemaMap = {
  "room:create": roomCreateSchema,
  "room:join": roomJoinSchema,
  "room:ready": roomReadySchema,
  "player:input": playerInputFrameSchema,
  "player:ackSnapshot": ackSnapshotSchema
} as const;

export const vec3Schema = z.object({
  x: z.number(),
  y: z.number(),
  z: z.number()
});

export const roomStateSchema = z.object({
  roomCode: z.string(),
  phase: z.enum(["lobby", "running", "extraction", "ended"]),
  players: z.array(
    z.object({
      playerId: z.string(),
      nickname: z.string(),
      ready: z.boolean(),
      connected: z.boolean(),
      level: z.number().int().min(1)
    })
  )
});

export const gameEventSchema = z.object({
  type: z.enum(["hit", "kill", "wave-start", "wave-cleared", "extraction-open", "match-result", "damage", "reload"]),
  atMs: z.number(),
  payload: z.record(z.any())
});

export const gameSnapshotSchema = z.object({
  tick: z.number().int().nonnegative(),
  serverTimeMs: z.number(),
  phase: z.enum(["lobby", "running", "extraction", "ended"]),
  wave: z.number().int().nonnegative(),
  players: z.array(
    z.object({
      id: z.string(),
      nickname: z.string(),
      position: vec3Schema,
      velocity: vec3Schema,
      yaw: z.number(),
      pitch: z.number(),
      hp: z.number(),
      armor: z.number(),
      ammoPrimary: z.number(),
      ammoSecondary: z.number(),
      sprinting: z.boolean(),
      grounded: z.boolean(),
      isReloading: z.boolean(),
      kills: z.number(),
      alive: z.boolean(),
      level: z.number()
    })
  ),
  enemies: z.array(
    z.object({
      id: z.string(),
      archetype: z.string(),
      spriteAsset: z.string(),
      position: vec3Schema,
      velocity: vec3Schema,
      hp: z.number(),
      maxHp: z.number(),
      alive: z.boolean(),
      targetPlayerId: z.string().nullable(),
      elite: z.boolean()
    })
  ),
  projectiles: z.array(
    z.object({
      id: z.string(),
      ownerId: z.string(),
      position: vec3Schema,
      velocity: vec3Schema,
      ttlMs: z.number(),
      damage: z.number()
    })
  ),
  pickups: z.array(
    z.object({
      id: z.string(),
      kind: z.enum(["ammo", "medkit", "armor"]),
      position: vec3Schema,
      active: z.boolean()
    })
  ),
  extraction: z.object({
    center: vec3Schema,
    radius: z.number(),
    progress: z.number(),
    requiredProgress: z.number(),
    active: z.boolean()
  })
});

export const progressionUpdateSchema = z.object({
  profile: playerProfileSchema,
  gainedXp: z.number().int().min(0)
});

export const matchEndSchema = z.object({
  roomCode: z.string(),
  success: z.boolean(),
  waveReached: z.number().int().min(0),
  durationSec: z.number().min(0),
  leaderboard: z.array(
    z.object({
      playerId: z.string(),
      nickname: z.string(),
      kills: z.number().int(),
      xpGained: z.number().int(),
      survived: z.boolean()
    })
  )
});

export const serverToClientSchemaMap = {
  "room:state": roomStateSchema,
  "game:snapshot": gameSnapshotSchema,
  "game:event": gameEventSchema,
  "progression:update": progressionUpdateSchema,
  "match:end": matchEndSchema
} as const;

export type ClientToServerEvent = keyof typeof clientToServerSchemaMap;
export type ServerToClientEvent = keyof typeof serverToClientSchemaMap;
