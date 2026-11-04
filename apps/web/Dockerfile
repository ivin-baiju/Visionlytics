FROM node:24-alpine
WORKDIR /repo
RUN corepack enable
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml tsconfig.base.json ./
COPY packages/ui packages/ui
COPY packages/shared-types packages/shared-types
COPY apps/web apps/web
RUN pnpm install --frozen-lockfile
WORKDIR /repo/apps/web
EXPOSE 5173
HEALTHCHECK --interval=10s --timeout=3s CMD wget -qO- http://127.0.0.1:5173/ || exit 1
CMD ["pnpm", "dev"]
