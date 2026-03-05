import { env } from "../config/env";
import { InMemoryProfileStore } from "./in-memory-profile-store";
import type { ProfileStore } from "./profile-store";
import { PrismaProfileStore } from "./prisma-profile-store";

export async function createProfileStore(): Promise<ProfileStore> {
  if (env.useInMemoryDb) {
    return new InMemoryProfileStore();
  }

  const store = new PrismaProfileStore();
  try {
    await store.connect();
    return store;
  } catch (error) {
    console.warn("Prisma unavailable, using in-memory profile store", error);
    await store.disconnect();
    return new InMemoryProfileStore();
  }
}
