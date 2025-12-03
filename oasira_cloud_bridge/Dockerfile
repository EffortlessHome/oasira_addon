# Multi-stage build for oasira-matter frontend
FROM node:22-alpine AS matter-builder

WORKDIR /build

# Copy oasira-matter workspace files
COPY oasira-matter/package.json oasira-matter/pnpm-lock.yaml ./
COPY oasira-matter/biome.json ./
COPY oasira-matter/packages/common ./packages/common
COPY oasira-matter/packages/frontend ./packages/frontend

# Create modified pnpm-workspace.yaml without apps directory
RUN echo 'packages:' > pnpm-workspace.yaml && \
    echo '  - "packages/*"' >> pnpm-workspace.yaml

# Create stub apps/oasira-matter/package.json for frontend version import
RUN mkdir -p apps/oasira-matter && \
    echo '{"name":"@oasira-matter/oasira-matter","version":"1.0.0"}' > apps/oasira-matter/package.json

# Install pnpm and build frontend (only common and frontend packages)
RUN npm install -g pnpm@10.20.0 && \
    pnpm install --no-frozen-lockfile --filter @oasira-matter/common --filter @oasira-matter/frontend && \
    pnpm --filter @oasira-matter/common run build && \
    pnpm --filter @oasira-matter/frontend run build

# Main runtime image
FROM ghcr.io/home-assistant/aarch64-base:latest

# Install Python only
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

# Copy built oasira-matter frontend from builder stage
COPY --from=matter-builder /build/packages/frontend/dist /app/matter-frontend

ENV PATH="/venv/bin:$PATH"

CMD ["/run.sh"]
