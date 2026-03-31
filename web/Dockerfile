FROM node:22-alpine AS build

WORKDIR /app
RUN corepack enable

# Copy root monorepo config + web package
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY web/ web/

# Install only web workspace deps
RUN pnpm install --filter lucid-web

# Build from web directory
WORKDIR /app/web
RUN npx vite build

FROM nginx:alpine
COPY --from=build /app/web/dist /usr/share/nginx/html
COPY web/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
