import { randomUUID } from "node:crypto";
import type { PerkId, PlayerProfile, WeaponId } from "@silent-hillberg/shared";
import type { LeaderboardEntry, MatchHistoryEntry, ProfileStore } from "./profile-store";
import { createBaseProfile } from "./utils";

export class InMemoryProfileStore implements ProfileStore {
  private readonly profilesById = new Map<string, PlayerProfile>();
  private readonly profileIdByFingerprint = new Map<string, string>();
  private readonly histories: MatchHistoryEntry[] = [];

  public async upsertGuest(nickname: string, deviceFingerprint: string): Promise<PlayerProfile> {
    const knownId = this.profileIdByFingerprint.get(deviceFingerprint);

    if (knownId) {
      const existing = this.profilesById.get(knownId);
      if (existing) {
        const updated: PlayerProfile = {
          ...existing,
          nickname
        };
        this.profilesById.set(updated.playerId, updated);
        return updated;
      }
    }

    const profileId = randomUUID();
    const profile = createBaseProfile(profileId, nickname);

    this.profilesById.set(profile.playerId, profile);
    this.profileIdByFingerprint.set(deviceFingerprint, profile.playerId);

    return profile;
  }

  public async getById(playerId: string): Promise<PlayerProfile | null> {
    return this.profilesById.get(playerId) ?? null;
  }

  public async updateLoadout(
    playerId: string,
    equippedWeaponId: WeaponId,
    equippedPerkIds: PerkId[]
  ): Promise<PlayerProfile | null> {
    const profile = this.profilesById.get(playerId);
    if (!profile) {
      return null;
    }

    const updated: PlayerProfile = {
      ...profile,
      equippedWeaponId,
      equippedPerkIds
    };

    this.profilesById.set(playerId, updated);
    return updated;
  }

  public async saveProfile(profile: PlayerProfile): Promise<PlayerProfile> {
    this.profilesById.set(profile.playerId, profile);
    return profile;
  }

  public async getLeaderboard(limit = 20): Promise<LeaderboardEntry[]> {
    return [...this.profilesById.values()]
      .sort((a, b) => (b.xp === a.xp ? b.level - a.level : b.xp - a.xp))
      .slice(0, limit)
      .map((profile) => ({
        playerId: profile.playerId,
        nickname: profile.nickname,
        level: profile.level,
        xp: profile.xp
      }));
  }

  public async appendMatchHistory(entry: MatchHistoryEntry): Promise<void> {
    this.histories.push(entry);
  }

  public async disconnect(): Promise<void> {
    return;
  }
}
