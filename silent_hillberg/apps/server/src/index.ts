import cors from "@fastify/cors";
import Fastify from "fastify";
import { Server } from "socket.io";
import { env } from "./config/env";
import { registerHttpRoutes } from "./api/http-routes";
import { createProfileStore } from "./storage/create-profile-store";
import { registerSocketHandlers } from "./net/socket";
import { RoomManager } from "./game/room-manager";

async function bootstrap() {
  const app = Fastify({
    logger: true
  });

  await app.register(cors, {
    origin: env.clientOrigin,
    credentials: true
  });

  const profileStore = await createProfileStore();
  await registerHttpRoutes(app, profileStore);

  const io = new Server(app.server, {
    cors: {
      origin: env.clientOrigin,
      credentials: true
    }
  });

  const roomManager = new RoomManager(io, profileStore);
  roomManager.start();
  registerSocketHandlers(io, roomManager, profileStore);

  app.addHook("onClose", async () => {
    roomManager.stop();
    io.close();
    await profileStore.disconnect();
  });

  const stopSignals: NodeJS.Signals[] = ["SIGINT", "SIGTERM"];
  for (const signal of stopSignals) {
    process.on(signal, async () => {
      app.log.info({ signal }, "Shutting down Silent Hillberg server");
      await app.close();
      process.exit(0);
    });
  }

  await app.listen({
    host: env.host,
    port: env.port
  });

  app.log.info(`Silent Hillberg server running at http://${env.host}:${env.port}`);
}

bootstrap().catch((error) => {
  console.error(error);
  process.exit(1);
});
