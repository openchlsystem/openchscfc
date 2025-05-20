# Build stage - Native ARM architecture
FROM node:20-bookworm-slim as build-stage

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source
COPY . .

# Build
RUN which node && node --version && \
    npm install -g vite && \
    node node_modules/vite/bin/vite.js build

# Production stage
FROM nginx:stable as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]