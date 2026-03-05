import jwt from "jsonwebtoken";
import { env } from "../config/env";

export interface AuthTokenPayload {
  playerId: string;
  nickname: string;
}

export function signAuthToken(payload: AuthTokenPayload): string {
  return jwt.sign(payload, env.jwtSecret, {
    algorithm: "HS256",
    expiresIn: "30d"
  });
}

export function verifyAuthToken(token: string): AuthTokenPayload | null {
  try {
    const decoded = jwt.verify(token, env.jwtSecret);
    if (typeof decoded !== "object" || decoded === null) {
      return null;
    }

    if (typeof decoded.playerId !== "string" || typeof decoded.nickname !== "string") {
      return null;
    }

    return {
      playerId: decoded.playerId,
      nickname: decoded.nickname
    };
  } catch {
    return null;
  }
}

export function parseBearerToken(header: string | undefined): string | null {
  if (!header) {
    return null;
  }

  if (!header.startsWith("Bearer ")) {
    return null;
  }

  return header.slice("Bearer ".length).trim();
}
