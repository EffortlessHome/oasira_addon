# Multi-stage build for oasira-matter backend
FROM node:22-alpine AS matter-builder

WORKDIR /build

# Copy oasira-matter workspace files
COPY oasira_cloud_bridge/oasira-matter/package.json oasira_cloud_bridge/oasira-matter/pnpm-lock.yaml ./
COPY oasira_cloud_bridge/oasira-matter/biome.json ./
COPY oasira_cloud_bridge/oasira-matter/packages/common ./packages/common
COPY oasira_cloud_bridge/oasira-matter/packages/backend ./packages/backend

# Create modified pnpm-workspace.yaml without apps and frontend
RUN echo 'packages:' > pnpm-workspace.yaml && \
    echo '  - "packages/common"' >> pnpm-workspace.yaml && \
    echo '  - "packages/backend"' >> pnpm-workspace.yaml

# Install pnpm and build backend
RUN npm install -g pnpm@10.20.0 && \
    pnpm install --no-frozen-lockfile --filter @oasira-matter/common --filter @oasira-matter/backend && \
    pnpm --filter @oasira-matter/common run build && \
    pnpm --filter @oasira-matter/backend run build

# Main runtime image
FROM ghcr.io/home-assistant/aarch64-base:latest

# Install Python and Node.js runtime
RUN apk add --no-cache python3 py3-pip nodejs npm

COPY oasira_cloud_bridge/run.py /run.py
RUN chmod +x /run.py

COPY oasira_cloud_bridge/run.sh /run.sh
RUN chmod +x /run.sh

COPY oasira_cloud_bridge/cert.pem /root/.cloudflared/cert.pem
COPY oasira_cloud_bridge/cert.pem /cert.pem

# Copy requirements and install Python packages
COPY oasira_cloud_bridge/requirements.txt /requirements.txt

# Create and use a virtual environment for Python packages
RUN python3 -m venv /venv \
    && . /venv/bin/activate \
    && pip install --no-cache-dir -r /requirements.txt \
    && pip install --no-cache-dir aiohttp websockets==12.0 Brotli

# Copy dashboard dist folder (includes .gitkeep if empty)
COPY oasira_cloud_bridge/dist /app/dist

# Copy built Matter backend from builder stage (bundle.js is self-contained)
COPY --from=matter-builder /build/packages/backend/bundle.js /app/matter-backend/bundle.js

ENV PATH="/venv/bin:$PATH"

CMD ["/run.sh"]
