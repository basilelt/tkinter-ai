import {
  guestAuthResponseSchema,
  playerProfileSchema,
  updateLoadoutSchema
} from "@silent-hillberg/protocol";
import type { PerkId, PlayerProfile, UnlockCatalog, WeaponId } from "@silent-hillberg/shared";

export interface GuestSession {
  playerId: string;
  token: string;
  profile: PlayerProfile;
}

export class ApiClient {
  public constructor(private readonly baseUrl = "") {}

  public async authGuest(nickname: string, deviceFingerprint: string): Promise<GuestSession> {
    const response = await fetch(`${this.baseUrl}/api/auth/guest`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ nickname, deviceFingerprint })
    });

    if (!response.ok) {
      throw new Error(`Auth failed (${response.status})`);
    }

    const payload = guestAuthResponseSchema.parse(await response.json());

    return {
      playerId: payload.playerId,
      token: payload.token,
      profile: payload.profile
    };
  }

  public async getProfile(token: string): Promise<PlayerProfile> {
    const response = await fetch(`${this.baseUrl}/api/profile/me`, {
      headers: {
        authorization: `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error(`Profile fetch failed (${response.status})`);
    }

    return playerProfileSchema.parse(await response.json());
  }

  public async updateLoadout(
    token: string,
    payload: { equippedWeaponId: WeaponId; equippedPerkIds: PerkId[] }
  ): Promise<PlayerProfile> {
    const parsedPayload = updateLoadoutSchema.parse(payload);

    const response = await fetch(`${this.baseUrl}/api/profile/loadout`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        authorization: `Bearer ${token}`
      },
      body: JSON.stringify(parsedPayload)
    });

    if (!response.ok) {
      throw new Error(`Loadout update failed (${response.status})`);
    }

    return playerProfileSchema.parse(await response.json());
  }

  public async getUnlockCatalog(): Promise<UnlockCatalog> {
    const response = await fetch(`${this.baseUrl}/api/unlocks/catalog`);
    if (!response.ok) {
      throw new Error(`Catalog fetch failed (${response.status})`);
    }

    return (await response.json()) as UnlockCatalog;
  }

  public async getLeaderboard(limit = 20): Promise<Array<{ playerId: string; nickname: string; level: number; xp: number }>> {
    const response = await fetch(`${this.baseUrl}/api/leaderboard?limit=${limit}`);
    if (!response.ok) {
      throw new Error(`Leaderboard fetch failed (${response.status})`);
    }

    const payload = (await response.json()) as {
      entries: Array<{ playerId: string; nickname: string; level: number; xp: number }>;
    };

    return payload.entries;
  }
}
