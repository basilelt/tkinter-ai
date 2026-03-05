FROM node:22-alpine

WORKDIR /app
RUN corepack enable

COPY package.json pnpm-workspace.yaml tsconfig.base.json ./
COPY apps/server ./apps/server
COPY packages ./packages

RUN pnpm install --no-frozen-lockfile
RUN pnpm --filter @silent-hillberg/shared build
RUN pnpm --filter @silent-hillberg/protocol build
RUN pnpm --filter @silent-hillberg/server prisma:generate
RUN pnpm --filter @silent-hillberg/server build

EXPOSE 3001
WORKDIR /app/apps/server
CMD ["sh", "-c", "pnpm prisma:push && node dist/index.js"]
