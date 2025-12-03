# Multi-stage build for oasira-matter
FROM node:22-alpine AS matter-builder

WORKDIR /build

# Copy oasira-matter workspace files
COPY oasira-matter/package.json oasira-matter/pnpm-lock.yaml oasira-matter/pnpm-workspace.yaml ./
COPY oasira-matter/biome.json ./
COPY oasira-matter/packages ./packages

# Install pnpm and build
RUN npm install -g pnpm@10.20.0 && \
    pnpm install --frozen-lockfile && \
    pnpm run build:app

# Main runtime image
FROM ghcr.io/home-assistant/aarch64-base:latest

# Install Node.js runtime and Python
RUN apk add --no-cache python3 py3-pip nodejs npm

COPY run.py /run.py
RUN chmod +x /run.py

COPY run.sh /run.sh
RUN chmod +x /run.sh

COPY cert.pem /root/.cloudflared/cert.pem
COPY cert.pem /cert.pem

# Copy requirements and install Python packages
COPY requirements.txt /requirements.txt

# Create and use a virtual environment for Python packages
RUN python3 -m venv /venv \
    && . /venv/bin/activate \
    && pip install --no-cache-dir -r /requirements.txt \
    && pip install --no-cache-dir aiohttp websockets==12.0 Brotli

# Copy dashboard dist folder (includes .gitkeep if empty)
COPY dist /app/dist

# Copy built oasira-matter backend and frontend from builder stage
COPY --from=matter-builder /build/packages/backend/dist /app/matter-backend
COPY --from=matter-builder /build/packages/frontend/dist /app/matter-frontend

# Copy necessary node_modules for runtime
# The backend needs its dependencies and the common package
COPY --from=matter-builder /build/node_modules /app/matter-node_modules
COPY --from=matter-builder /build/packages/backend/node_modules /app/matter-backend/node_modules
COPY --from=matter-builder /build/packages/common/dist /app/matter-backend/node_modules/@oasira-matter/common

# Set NODE_PATH so Node.js can find workspace dependencies
ENV PATH="/venv/bin:$PATH"
ENV NODE_ENV=production
ENV NODE_PATH=/app/matter-node_modules

CMD ["/run.sh"]
