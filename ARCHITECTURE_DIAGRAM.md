# Oasira Matter Integration - Visual Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User's Browser                          │
└───────────────┬───────────────────────┬─────────────────────────┘
                │                       │
                │ http://host:8080/     │ http://host:8080/matter/
                ▼                       ▼
┌───────────────────────────────────────────────────────────────────┐
│                    Home Assistant Addon                           │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Python Process (run.py)                        │ │
│  │                                                              │ │
│  │  ┌────────────────────────────────────────────────────────┐ │ │
│  │  │        aiohttp Web Server (Port 8080)                  │ │ │
│  │  │                                                         │ │ │
│  │  │  Route: /                                               │ │ │
│  │  │  ├─ Serve: /app/dist/* (Main Dashboard)               │ │ │
│  │  │  └─ Static files, SPA routing                          │ │ │
│  │  │                                                         │ │ │
│  │  │  Route: /matter/                                        │ │ │
│  │  │  ├─ Serve: /app/matter-frontend/* (Matter UI)         │ │ │
│  │  │  └─ Base path rewriting, static files                  │ │ │
│  │  │                                                         │ │ │
│  │  │  Route: /matter/api/*                                   │ │ │
│  │  │  └─ Reverse Proxy ─────────────────────┐               │ │ │
│  │  │     • Strip /matter prefix             │               │ │ │
│  │  │     • Add X-Forwarded-Prefix header    │               │ │ │
│  │  │     • Forward to localhost:8481        │               │ │ │
│  │  └─────────────────────────────────────────┼───────────────┘ │ │
│  │                                            │                 │ │
│  │  ┌─────────────────────────────────────────▼───────────────┐ │ │
│  │  │     Node.js Process (subprocess)                        │ │ │
│  │  │                                                          │ │ │
│  │  │     Express Server (Port 8481 - Internal)               │ │ │
│  │  │     • Matter API endpoints                              │ │ │
│  │  │     • Home Assistant integration                        │ │ │
│  │  │     • Matter device management                          │ │ │
│  │  │     • Storage: /data/matter                             │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │             Other Services (asyncio tasks)                    │ │
│  │  • Cloudflare Tunnel (cloudflared)                           │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  Home Assistant  │
                  │   (localhost)    │
                  └──────────────────┘
```

## Request Flow Diagram

### Main Dashboard Request
```
Browser → http://host:8080/
    │
    ▼
aiohttp Server
    │
    ├─ Match route: /
    │
    ▼
Serve: /app/dist/index.html
    │
    ▼
Browser ← HTML + Assets
```

### Matter UI Request
```
Browser → http://host:8080/matter/
    │
    ▼
aiohttp Server
    │
    ├─ Match route: /matter/
    │
    ▼
Serve: /app/matter-frontend/index.html
    │   (with base href="/matter/")
    │
    ▼
Browser ← HTML + Assets
```

### Matter API Request
```
Browser → http://host:8080/matter/api/bridges
    │
    ▼
aiohttp Server
    │
    ├─ Match route: /matter/api/{path}
    │
    ▼
matter_proxy_handler()
    │
    ├─ Strip prefix: /matter
    ├─ Add header: X-Forwarded-Prefix: /matter
    │
    ▼
Forward → http://localhost:8481/api/bridges
    │
    ▼
Node.js Express Server
    │
    ├─ Process request with prefix awareness
    ├─ Query Home Assistant
    │
    ▼
Response ← JSON data
    │
    ▼
aiohttp Proxy
    │
    ▼
Browser ← JSON response
```

## Docker Build Flow

```
┌─────────────────────────────────────────────────────────────┐
│              Stage 1: matter-builder                        │
│              (node:22-alpine)                               │
│                                                             │
│  1. Copy oasira-matter source                               │
│  2. Install pnpm                                            │
│  3. pnpm install (dependencies)                             │
│  4. pnpm run build:app                                      │
│     ├─ Build: packages/common                               │
│     ├─ Build: packages/backend (TypeScript → JavaScript)    │
│     └─ Build: packages/frontend (React → optimized bundle)  │
│                                                             │
│  Output:                                                    │
│  ├─ /build/packages/backend/dist/                           │
│  ├─ /build/packages/frontend/dist/                          │
│  └─ /build/node_modules/                                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ COPY --from=matter-builder
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Stage 2: runtime                               │
│              (ghcr.io/home-assistant/aarch64-base:latest)   │
│                                                             │
│  1. Install Python 3 + Node.js                              │
│  2. Copy run.py, run.sh, cert.pem                           │
│  3. Install Python packages (venv)                          │
│  4. Copy pre-built dashboard (dist/)                        │
│  5. Copy Matter artifacts from builder:                     │
│     ├─ backend → /app/matter-backend/                       │
│     ├─ frontend → /app/matter-frontend/                     │
│     └─ node_modules → /app/matter-node_modules/             │
│                                                             │
│  Final Image:                                               │
│  ├─ Python runtime with deps                                │
│  ├─ Node.js runtime                                         │
│  ├─ Main dashboard (pre-built)                              │
│  └─ Matter Hub (built in stage 1)                           │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌────────────────────────────────────────────────────────────┐
│                  Addon Configuration                       │
│  /data/options.json                                        │
│  ├─ email, password, system_id                             │
│  ├─ ha_url                                                 │
│  └─ dashboard_port                                         │
└──────────────┬─────────────────────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────────────────────┐
│            Python Process (run.py)                         │
│                                                            │
│  1. Authenticate with Oasira API                           │
│  2. Get ha_token from API                                  │
│  3. Start services:                                        │
│     ├─ Cloudflare Tunnel                                   │
│     ├─ Matter Hub (pass ha_url + ha_token)                 │
│     └─ Web Server (unified interface)                      │
└──────┬─────────────────────────┬───────────────────────────┘
       │                         │
       ▼                         ▼
┌─────────────────┐    ┌──────────────────────┐
│ Cloudflare      │    │ Node.js Matter Hub   │
│ (port dynamic)  │    │ (port 8481)          │
└─────────────────┘    │                      │
                       │ Connects to:         │
                       │ • Home Assistant     │
                       │ • Matter devices     │
                       │                      │
                       │ Stores in:           │
                       │ /data/matter/        │
                       └──────────────────────┘
```

## Port Mapping

```
External            Internal             Service
──────────          ────────             ───────
:8080          →    :8080           aiohttp (Python)
                    :8481           Express (Node.js)
                                    ↓
                                    localhost only
```

## File Structure After Build

```
Container Filesystem:
/
├── app/
│   ├── dist/                         # Main Oasira Dashboard
│   │   ├── index.html
│   │   ├── assets/
│   │   └── ...
│   │
│   ├── matter-backend/               # Node.js server (built)
│   │   ├── cli.js                    # Entry point
│   │   ├── bootstrap.js
│   │   ├── node_modules/             # Backend dependencies
│   │   │   └── @oasira-matter/
│   │   │       └── common/           # Shared library
│   │   └── ...
│   │
│   ├── matter-frontend/              # React UI (built)
│   │   ├── index.html
│   │   ├── assets/
│   │   └── ...
│   │
│   └── matter-node_modules/          # Workspace dependencies
│       └── ...
│
├── data/                             # Persistent storage
│   ├── matter/                       # Matter device configs
│   │   ├── storage/
│   │   └── ...
│   └── options.json                  # Addon config
│
├── venv/                             # Python virtual environment
│   └── ...
│
└── run.py                            # Main Python script
```

## Startup Sequence

```
1. Container starts
    │
    ▼
2. run.sh executes
    │
    ▼
3. run.py begins
    │
    ├─ Load /data/options.json
    ├─ Authenticate with Oasira API
    └─ Get credentials & tokens
    │
    ▼
4. Start Cloudflare Tunnel (background task)
    │
    ▼
5. Start Matter Hub (background task)
    │   │
    │   └─ node /app/matter-backend/cli.js start
    │       --home-assistant-url=...
    │       --home-assistant-access-token=...
    │       --http-port=8481
    │       --storage-location=/data/matter
    │
    ▼
6. Start Web Server (background task)
    │   │
    │   └─ aiohttp server on port 8080
    │       ├─ Register routes
    │       ├─ Start listening
    │       └─ Log "Unified server running..."
    │
    ▼
7. Keep main loop running
    │
    └─ await asyncio.Event().wait()
```

## Success Indicators in Logs

```
Starting OAuth authentication...
✅ Firebase authentication successful
✅ Found X system(s)
✅ Login successful!
🌩️ Starting Cloudflare tunnel...
cloudflared-out: ...
🔗 Starting Matter Hub...
✅ Oasira Matter server started with PID XXXX
matter-out: ...
📊 Starting Dashboard...
✅ Matter UI integrated at /matter/
✅ Unified server running at http://0.0.0.0:8080
   - Main Dashboard: http://0.0.0.0:8080/
   - Matter Hub: http://0.0.0.0:8080/matter/
```
