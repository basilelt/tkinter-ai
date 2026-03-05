import { PrismaClient } from "@prisma/client";
import { type PerkId, type PlayerProfile, type WeaponId } from "@silent-hillberg/shared";
import type { LeaderboardEntry, MatchHistoryEntry, ProfileStore } from "./profile-store";
import { createBaseProfile } from "./utils";

function toProfile(record: {
  id: string;
  nickname: string;
  level: number;
  xp: number;
  unlockedWeaponIds: unknown;
  unlockedPerkIds: unknown;
  equippedWeaponId: string;
  equippedPerkIds: unknown;
}): PlayerProfile {
  return {
    playerId: record.id,
    nickname: record.nickname,
    level: record.level,
    xp: record.xp,
    unlockedWeaponIds: (record.unlockedWeaponIds as WeaponId[]) ?? ["rusty-rifle"],
    unlockedPerkIds: (record.unlockedPerkIds as PerkId[]) ?? [],
    equippedWeaponId: record.equippedWeaponId as WeaponId,
    equippedPerkIds: (record.equippedPerkIds as PerkId[]) ?? []
  };
}

export class PrismaProfileStore implements ProfileStore {
  public readonly prisma: PrismaClient;

  public constructor() {
    this.prisma = new PrismaClient();
  }

  public async connect(): Promise<void> {
    await this.prisma.$connect();
  }

  public async upsertGuest(nickname: string, deviceFingerprint: string): Promise<PlayerProfile> {
    const existing = await this.prisma.playerProfile.findUnique({
      where: {
        deviceFingerprint
      }
    });

    if (existing) {
      const updated = await this.prisma.playerProfile.update({
        where: {
          id: existing.id
        },
        data: {
          nickname
        }
      });

      return toProfile(updated);
    }

    const base = createBaseProfile("new-player", nickname);

    const created = await this.prisma.playerProfile.create({
      data: {
        nickname,
        deviceFingerprint,
        xp: base.xp,
        level: base.level,
        unlockedWeaponIds: base.unlockedWeaponIds,
        unlockedPerkIds: base.unlockedPerkIds,
        equippedWeaponId: base.equippedWeaponId,
        equippedPerkIds: base.equippedPerkIds
      }
    });

    return toProfile(created);
  }

  public async getById(playerId: string): Promise<PlayerProfile | null> {
    const profile = await this.prisma.playerProfile.findUnique({
      where: {
        id: playerId
      }
    });

    return profile ? toProfile(profile) : null;
  }

  public async updateLoadout(
    playerId: string,
    equippedWeaponId: WeaponId,
    equippedPerkIds: PerkId[]
  ): Promise<PlayerProfile | null> {
    try {
      const updated = await this.prisma.playerProfile.update({
        where: {
          id: playerId
        },
        data: {
          equippedWeaponId,
          equippedPerkIds
        }
      });

      return toProfile(updated);
    } catch {
      return null;
    }
  }

  public async saveProfile(profile: PlayerProfile): Promise<PlayerProfile> {
    const saved = await this.prisma.playerProfile.update({
      where: {
        id: profile.playerId
      },
      data: {
        nickname: profile.nickname,
        level: profile.level,
        xp: profile.xp,
        unlockedWeaponIds: profile.unlockedWeaponIds,
        unlockedPerkIds: profile.unlockedPerkIds,
        equippedWeaponId: profile.equippedWeaponId,
        equippedPerkIds: profile.equippedPerkIds
      }
    });

    return toProfile(saved);
  }

  public async getLeaderboard(limit = 20): Promise<LeaderboardEntry[]> {
    const players = await this.prisma.playerProfile.findMany({
      take: limit,
      orderBy: [{ xp: "desc" }, { level: "desc" }],
      select: {
        id: true,
        nickname: true,
        xp: true,
        level: true
      }
    });

    return players.map((player) => ({
      playerId: player.id,
      nickname: player.nickname,
      level: player.level,
      xp: player.xp
    }));
  }

  public async appendMatchHistory(entry: MatchHistoryEntry): Promise<void> {
    await this.prisma.matchHistory.create({
      data: {
        playerId: entry.playerId,
        roomCode: entry.roomCode,
        success: entry.success,
        kills: entry.stats.kills,
        damageDone: entry.stats.damageDone,
        damageTaken: entry.stats.damageTaken,
        waveReached: entry.waveReached,
        xpGained: entry.xpGained
      }
    });
  }

  public async disconnect(): Promise<void> {
    await this.prisma.$disconnect();
  }
}
