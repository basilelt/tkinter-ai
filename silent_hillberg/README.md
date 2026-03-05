# Silent Hillberg

Silent Hillberg est un FPS horreur coop (1-4 joueurs) inspiré de Doom, sur navigateur web desktop, construit avec Three.js + Socket.IO + Fastify.

## Stack

- Monorepo TypeScript (`pnpm workspaces`)
- Client: Vite + Three.js + audio procédural Tone.js
- Serveur: Fastify + Socket.IO (serveur autoritaire 30 Hz)
- Progression persistante: Prisma + PostgreSQL
- Déploiement: Docker Compose + Nginx reverse proxy

## Arborescence

- `apps/client`: jeu web FPS, HUD, audio, lobby
- `apps/server`: API REST + simulation multijoueur + progression
- `packages/shared`: types, constantes gameplay, utilitaires progression/combat
- `packages/protocol`: validation runtime Zod des payloads API/socket
- `assets`: sources visuelles du projet

## Lancer en local (dev)

```bash
pnpm install
pnpm --filter @silent-hillberg/server prisma:generate
pnpm --filter @silent-hillberg/server prisma:push
pnpm dev
```

Services:
- client: http://localhost:5173
- server: http://localhost:3001

## Lancer avec Docker

```bash
docker compose up --build
```

Service web:
- http://localhost:8080

## Contrôles

- `WASD`: déplacement
- `Shift`: sprint
- `Space`: saut
- `Q`: dash
- `Click gauche`: tir principal hitscan
- `Click droit`: projectile secondaire
- `R`: reload

## API publique

- `POST /api/auth/guest`
- `GET /api/profile/me`
- `POST /api/profile/loadout`
- `GET /api/unlocks/catalog`
- `GET /api/leaderboard`

## Événements WebSocket

Client -> serveur:
- `room:create`
- `room:join`
- `room:ready`
- `player:input`
- `player:ackSnapshot`

Serveur -> client:
- `room:state`
- `game:snapshot`
- `game:event`
- `progression:update`
- `match:end`
