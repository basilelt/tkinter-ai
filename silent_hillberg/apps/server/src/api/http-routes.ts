import {
  UNLOCK_CATALOG,
  type PerkId,
  type PlayerProfile,
  type WeaponId
} from "@silent-hillberg/shared";
import {
  guestAuthRequestSchema,
  guestAuthResponseSchema,
  playerProfileSchema,
  updateLoadoutSchema
} from "@silent-hillberg/protocol";
import type { FastifyInstance, FastifyReply, FastifyRequest } from "fastify";
import { parseBearerToken, signAuthToken, verifyAuthToken } from "../auth/token";
import type { ProfileStore } from "../storage/profile-store";

async function requireAuthenticatedProfile(
  request: FastifyRequest,
  reply: FastifyReply,
  profileStore: ProfileStore
): Promise<PlayerProfile | null> {
  const bearerToken = parseBearerToken(request.headers.authorization);
  if (!bearerToken) {
    reply.status(401).send({ error: "Missing bearer token" });
    return null;
  }

  const authPayload = verifyAuthToken(bearerToken);
  if (!authPayload) {
    reply.status(401).send({ error: "Invalid token" });
    return null;
  }

  const profile = await profileStore.getById(authPayload.playerId);
  if (!profile) {
    reply.status(404).send({ error: "Profile not found" });
    return null;
  }

  return profile;
}

export async function registerHttpRoutes(app: FastifyInstance, profileStore: ProfileStore): Promise<void> {
  app.get("/", async () => ({
    service: "silent-hillberg-server",
    ok: true,
    docs: {
      health: "/health",
      authGuest: "/api/auth/guest",
      profileMe: "/api/profile/me",
      unlockCatalog: "/api/unlocks/catalog",
      leaderboard: "/api/leaderboard"
    }
  }));

  app.get("/favicon.ico", async (_request, reply) => {
    reply.status(204).send();
  });

  app.get("/health", async () => ({ ok: true, service: "silent-hillberg-server" }));

  app.post("/api/auth/guest", async (request, reply) => {
    const parsed = guestAuthRequestSchema.safeParse(request.body);
    if (!parsed.success) {
      reply.status(400).send({ error: parsed.error.flatten() });
      return;
    }

    const profile = await profileStore.upsertGuest(parsed.data.nickname, parsed.data.deviceFingerprint);

    const token = signAuthToken({
      playerId: profile.playerId,
      nickname: profile.nickname
    });

    const response = {
      playerId: profile.playerId,
      token,
      profile
    };

    const validated = guestAuthResponseSchema.parse(response);
    reply.status(200).send(validated);
  });

  app.get("/api/profile/me", async (request, reply) => {
    const profile = await requireAuthenticatedProfile(request, reply, profileStore);
    if (!profile) {
      return;
    }

    reply.status(200).send(playerProfileSchema.parse(profile));
  });

  app.post("/api/profile/loadout", async (request, reply) => {
    const profile = await requireAuthenticatedProfile(request, reply, profileStore);
    if (!profile) {
      return;
    }

    const parsed = updateLoadoutSchema.safeParse(request.body);
    if (!parsed.success) {
      reply.status(400).send({ error: parsed.error.flatten() });
      return;
    }

    const equippedWeaponId = parsed.data.equippedWeaponId as WeaponId;
    const equippedPerkIds = parsed.data.equippedPerkIds as PerkId[];

    if (!profile.unlockedWeaponIds.includes(equippedWeaponId)) {
      reply.status(403).send({ error: "Weapon not unlocked" });
      return;
    }

    if (!equippedPerkIds.every((perkId) => profile.unlockedPerkIds.includes(perkId))) {
      reply.status(403).send({ error: "Perk not unlocked" });
      return;
    }

    const updated = await profileStore.updateLoadout(profile.playerId, equippedWeaponId, equippedPerkIds);
    if (!updated) {
      reply.status(404).send({ error: "Profile not found" });
      return;
    }

    reply.status(200).send(playerProfileSchema.parse(updated));
  });

  app.get("/api/unlocks/catalog", async () => {
    return UNLOCK_CATALOG;
  });

  app.get("/api/leaderboard", async (request) => {
    const query = request.query as { limit?: string };
    const limit = query.limit ? Number(query.limit) : 20;

    return {
      entries: await profileStore.getLeaderboard(Number.isFinite(limit) ? limit : 20)
    };
  });
}
