import { PrismaClient } from "@prisma/client";
import { UNLOCK_CATALOG } from "@silent-hillberg/shared";

const prisma = new PrismaClient();

async function run() {
  await prisma.playerProfile.upsert({
    where: {
      deviceFingerprint: "seed-local-player"
    },
    update: {},
    create: {
      nickname: "HillbergSeed",
      deviceFingerprint: "seed-local-player",
      xp: 200,
      level: 2,
      unlockedWeaponIds: UNLOCK_CATALOG.weapons.filter((w) => w.requiredLevel <= 2).map((w) => w.id),
      unlockedPerkIds: UNLOCK_CATALOG.perks.filter((p) => p.requiredLevel <= 2).map((p) => p.id),
      equippedWeaponId: "rusty-rifle",
      equippedPerkIds: []
    }
  });
}

run()
  .then(async () => {
    await prisma.$disconnect();
  })
  .catch(async (error) => {
    console.error(error);
    await prisma.$disconnect();
    process.exit(1);
  });
