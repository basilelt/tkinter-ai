import type { MatchPlayerStats, PlayerProfile, WeaponId, PerkId } from "@silent-hillberg/shared";

export interface LeaderboardEntry {
  playerId: string;
  nickname: string;
  level: number;
  xp: number;
}

export interface MatchHistoryEntry {
  playerId: string;
  roomCode: string;
  success: boolean;
  waveReached: number;
  stats: MatchPlayerStats;
  xpGained: number;
}

export interface ProfileStore {
  upsertGuest(nickname: string, deviceFingerprint: string): Promise<PlayerProfile>;
  getById(playerId: string): Promise<PlayerProfile | null>;
  updateLoadout(playerId: string, equippedWeaponId: WeaponId, equippedPerkIds: PerkId[]): Promise<PlayerProfile | null>;
  saveProfile(profile: PlayerProfile): Promise<PlayerProfile>;
  getLeaderboard(limit?: number): Promise<LeaderboardEntry[]>;
  appendMatchHistory(entry: MatchHistoryEntry): Promise<void>;
  disconnect(): Promise<void>;
}
