# Oasira Matter Integration

This document describes how the Oasira Matter functionality has been integrated into the Oasira Cloud Bridge addon.

## Architecture Overview

The integration combines two main components into a single unified addon:

1. **Oasira Cloud Bridge** (Python/aiohttp) - The main dashboard and cloud connectivity service
2. **Oasira Matter Hub** (Node.js/Express) - Matter protocol bridge for Home Assistant

Both services run on the **same port (8080)** but are accessible at different paths:

- **Main Dashboard**: `http://[addon-ip]:8080/`
- **Matter Hub**: `http://[addon-ip]:8080/matter/`

## Technical Implementation

### 1. Build Process (Dockerfile)

The Dockerfile uses a multi-stage build approach:

**Stage 1: Matter Builder**
- Uses Node.js 22 Alpine image
- Installs pnpm package manager
- Builds the oasira-matter workspace:
  - Backend (TypeScript → JavaScript bundle)
  - Frontend (React app)
  - Common shared library

**Stage 2: Runtime**
- Based on Home Assistant's aarch64-base image
- Installs Python 3 and Node.js runtime
- Copies built Matter artifacts from builder stage
- Sets up Python virtual environment for dependencies

### 2. Runtime Architecture

**Process Structure:**
```
run.py (Python)
├── Oasira Cloud Bridge (aiohttp web server on port 8080)
│   ├── Main Dashboard (/)
│   └── Reverse Proxy (/matter/*)
└── Matter Hub (Node.js subprocess on port 8481)
    ├── Matter API (/api/matter/*)
    └── Matter UI (served via proxy)
```

**Request Routing:**
- `/` → Main Oasira Dashboard (static files)
- `/matter/api/*` → Proxied to Node.js backend (http://localhost:8481)
- `/matter/*` → Matter UI (static files with base path rewriting)

### 3. Code Changes

#### `run.py` Modifications

**New Function: `start_matterhub()`**
- Starts the Node.js Matter backend as a subprocess
- Runs on internal port 8481 (not exposed externally)
- Passes Home Assistant URL and token from addon config
- Logs output to console with "matter-out" prefix
- Stores Matter data in `/data/matter` for persistence

**Enhanced Function: `serve_dashboard()`**
- Creates unified aiohttp web application
- Implements reverse proxy for `/matter/*` requests
- Adds `X-Forwarded-Prefix: /matter` header for proper URL handling
- Serves Matter UI with base path rewriting
- Maintains separate static file serving for both UIs

#### Dockerfile Updates

**Multi-stage Build:**
```dockerfile
FROM node:22-alpine AS matter-builder
# Build oasira-matter packages
FROM ghcr.io/home-assistant/aarch64-base:latest
# Install runtime and copy built artifacts
```

**Key Changes:**
- Installs Node.js and npm in runtime stage
- Copies built Matter backend and frontend
- Copies node_modules for runtime dependencies
- Sets NODE_PATH environment variable

### 4. Proxy Implementation

The Python reverse proxy:
- Strips `/matter` prefix before forwarding to Node.js
- Preserves query strings and request bodies
- Adds `X-Forwarded-Prefix` header for Matter backend
- Handles errors gracefully with 503 responses

The Matter backend recognizes the `X-Forwarded-Prefix` header (via `proxy-support.ts`) and adjusts its URL generation accordingly.

## Configuration

No additional configuration is needed for users. The Matter integration uses the same Home Assistant credentials as the main addon:

- `ha_url`: Home Assistant URL
- `ha_token`: Automatically obtained from Oasira API
- Storage: `/data/matter` (persistent across restarts)

## Benefits of This Integration

1. **Single Port**: Both UIs accessible on the same port - easier for users
2. **Unified Management**: One addon to install and configure
3. **Shared Authentication**: Uses the same Oasira credentials
4. **Efficient**: Matter Hub runs only when the addon is running
5. **Clean URLs**: `/` for main dashboard, `/matter/` for Matter features

## File Structure

```
oasira_cloud_bridge/
├── run.py                          # Main Python server (modified)
├── Dockerfile                      # Multi-stage build (modified)
├── oasira-matter/                  # Matter source code
│   ├── packages/
│   │   ├── backend/                # Node.js Express server
│   │   ├── frontend/               # React UI
│   │   └── common/                 # Shared TypeScript library
│   └── package.json                # Workspace config
└── dist/                           # Main dashboard (pre-built)

# After Docker build:
/app/
├── dist/                           # Main dashboard files
├── matter-backend/                 # Built Node.js server
│   ├── cli.js                      # Entry point
│   ├── bootstrap.js
│   └── node_modules/               # Runtime dependencies
├── matter-frontend/                # Built React app
└── matter-node_modules/            # Workspace dependencies
```

## Testing the Integration

1. **Build the addon:**
   ```bash
   ./build.sh   # or build.bat on Windows
   ```

2. **Access the UIs:**
   - Main Dashboard: `http://localhost:8080/`
   - Matter Hub: `http://localhost:8080/matter/`

3. **Check logs:**
   - Python server: Main log output
   - Matter backend: Lines prefixed with "matter-out:" or "matter-err:"

## Troubleshooting

**Matter Hub not accessible:**
- Check logs for "matter-out:" messages
- Verify Node.js process started (look for PID in logs)
- Ensure `/app/matter-backend/cli.js` exists in container

**API requests failing:**
- Check reverse proxy logs for errors
- Verify Matter backend is running on port 8481
- Check `X-Forwarded-Prefix` header in requests

**Build failures:**
- Ensure oasira-matter submodule is initialized
- Check pnpm installation in builder stage
- Verify Node.js 22 compatibility

## Future Enhancements

Potential improvements to consider:

1. **Health Checks**: Add endpoint to verify Matter backend status
2. **Configuration UI**: Allow Matter-specific settings in addon config
3. **Metrics**: Expose Matter device count and status
4. **Dynamic Loading**: Start Matter Hub only when needed
5. **WebSocket Support**: Handle WebSocket connections in proxy

## References

- [Oasira Matter Documentation](oasira-matter/README.md)
- [Matter Protocol Specification](https://buildwithmatter.com/)
- [Home Assistant Add-on Development](https://developers.home-assistant.io/docs/add-ons)
