# Multi-stage build for oasira-matter frontend only
FROM node:22-alpine AS matter-builder

WORKDIR /build

# Copy oasira-matter workspace files
COPY oasira-matter/package.json oasira-matter/pnpm-lock.yaml oasira-matter/pnpm-workspace.yaml ./
COPY oasira-matter/biome.json ./
COPY oasira-matter/packages/common ./packages/common
COPY oasira-matter/packages/frontend ./packages/frontend

# Install pnpm and build frontend only
RUN npm install -g pnpm@10.20.0 && \
    (pnpm install --no-frozen-lockfile --no-optional || \
     pnpm install --no-frozen-lockfile --force) && \
    pnpm --filter @oasira-matter/common run build && \
    pnpm --filter @oasira-matter/frontend run build

# Main runtime image
FROM ghcr.io/home-assistant/aarch64-base:latest

# Install Python only (Node.js no longer needed at runtime)
RUN apk add --no-cache python3 py3-pip

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

# Copy built oasira-matter frontend only (static files)
COPY --from=matter-builder /build/packages/frontend/dist /app/matter-frontend

ENV PATH="/venv/bin:$PATH"

CMD ["/run.sh"]
