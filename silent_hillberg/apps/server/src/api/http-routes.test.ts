import Fastify from "fastify";
import { describe, expect, it, beforeEach, afterEach } from "vitest";
import { registerHttpRoutes } from "./http-routes";
import { InMemoryProfileStore } from "../storage/in-memory-profile-store";
import type { FastifyInstance } from "fastify";

describe("http routes", () => {
  const store = new InMemoryProfileStore();
  let app: FastifyInstance;

  beforeEach(async () => {
    app = Fastify();
    await registerHttpRoutes(app, store);
    await app.ready();
  });

  afterEach(async () => {
    await app.close();
  });

  it("creates guest profile and fetches me", async () => {
    const auth = await app.inject({
      method: "POST",
      url: "/api/auth/guest",
      payload: {
        nickname: "Tester",
        deviceFingerprint: "fingerprint-12345"
      }
    });

    expect(auth.statusCode).toBe(200);
    const body = auth.json() as { token: string; playerId: string };

    const me = await app.inject({
      method: "GET",
      url: "/api/profile/me",
      headers: {
        authorization: `Bearer ${body.token}`
      }
    });

    expect(me.statusCode).toBe(200);
    const meBody = me.json() as { nickname: string };
    expect(meBody.nickname).toBe("Tester");
  });
});
