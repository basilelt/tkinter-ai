FROM node:22-alpine AS builder

WORKDIR /app
RUN corepack enable

COPY package.json pnpm-workspace.yaml tsconfig.base.json ./
COPY apps/client ./apps/client
COPY packages ./packages

RUN pnpm install --no-frozen-lockfile
RUN pnpm --filter @silent-hillberg/shared build
RUN pnpm --filter @silent-hillberg/protocol build
RUN pnpm --filter @silent-hillberg/client build

FROM nginx:1.27-alpine

COPY --from=builder /app/apps/client/dist /usr/share/nginx/html
COPY apps/client/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
