# Quick Reference: Oasira Matter Integration

## URL Structure
- **Main Dashboard**: `http://localhost:8080/`
- **Matter Hub**: `http://localhost:8080/matter/`
- **Matter API**: `http://localhost:8080/matter/api/*`

## Ports
- **External**: 8080 (configurable via `dashboard_port`)
- **Internal Matter Backend**: 8481 (not exposed)

## File Locations (Container)
```
/app/
├── dist/                  # Main dashboard (pre-built)
├── matter-backend/        # Node.js server
│   ├── cli.js            # Entry point
│   └── node_modules/     # Dependencies
├── matter-frontend/       # React UI
└── matter-node_modules/   # Workspace deps

/data/
├── matter/               # Matter device storage (persistent)
└── options.json          # Addon config
```

## Process Tree
```
run.py (Python)
├── aiohttp server (port 8080)
│   ├── Main dashboard (/)
│   └── Reverse proxy (/matter/*)
└── node cli.js (port 8481)
    └── Matter backend (Express)
```

## Key Code Sections

### Start Matter Backend
**File**: `run.py`
**Function**: `start_matterhub()`
```python
proc_matter = await asyncio.create_subprocess_exec(
    "node",
    "/app/matter-backend/cli.js",
    "start",
    f"--home-assistant-url={ha_url}",
    f"--home-assistant-access-token={ha_token}",
    "--http-port=8481",
    f"--storage-location=/data/matter",
)
```

### Reverse Proxy
**File**: `run.py`
**Function**: `matter_proxy_handler()`
```python
# Strip /matter prefix
proxied_path = request.path.replace('/matter', '', 1)
target_url = f"http://localhost:8481{proxied_path}"

# Add forwarded prefix header
headers['X-Forwarded-Prefix'] = '/matter'
```

### Route Registration
**File**: `run.py`
**Function**: `serve_dashboard()`
```python
# Order matters!
app.router.add_route('*', '/matter/api/{path:.*}', matter_proxy_handler)
app.router.add_static('/matter/', path=matter_frontend_path)
app.router.add_static('/', path=dashboard_path)
```

## Docker Build Stages

### Stage 1: Builder
```dockerfile
FROM node:22-alpine AS matter-builder
# Install pnpm
# Copy workspace files
# Build all packages
```

### Stage 2: Runtime
```dockerfile
FROM ghcr.io/home-assistant/aarch64-base:latest
# Install Python + Node.js
# Copy built artifacts
# Set environment
```

## Environment Variables
- `NODE_ENV=production` - Node.js production mode
- `NODE_PATH=/app/matter-node_modules` - Module resolution
- `PATH=/venv/bin:$PATH` - Python virtual env

## Logs
- **Main**: Direct stdout/stderr
- **Matter**: Prefixed with "matter-out:" or "matter-err:"
- **Cloudflare**: Prefixed with "cloudflared-out:" or "cloudflared-err:"

## Common Commands

### Build
```bash
./build.sh    # Linux/Mac
build.bat     # Windows
```

### Local Test
```bash
docker run -p 8080:8080 oasira-addon:latest
```

### Check Logs
```bash
docker logs [container-id]
# Look for:
# - "✅ Oasira Matter server started"
# - "✅ Unified server running"
# - "matter-out:" prefixed lines
```

## Debugging

### Matter Backend Not Starting
1. Check `/app/matter-backend/cli.js` exists
2. Verify Node.js installed: `node --version`
3. Check for "matter-out:" in logs
4. Verify port 8481 not in use

### UI Not Loading
1. Check `/app/matter-frontend/` exists
2. Verify static route registered
3. Check browser console for 404s
4. Verify base path in HTML

### API Not Responding
1. Check Matter backend on port 8481: `curl http://localhost:8481/api/matter/bridges`
2. Verify proxy forwards requests
3. Check X-Forwarded-Prefix header
4. Look for proxy errors in logs

## Configuration (config.yaml)
```yaml
options:
  email: ""
  password: ""
  system_id: ""
  ha_url: "http://homeassistant.local:8123"
  dashboard_port: 8080
```

## Dependencies

### Build Time
- pnpm 10.20.0
- Node.js 22
- TypeScript (via pnpm)

### Runtime
- Python 3 + venv
- Node.js runtime
- aiohttp (Python)
- Express (Node.js)
- @matter/* packages

## Header Flow

### Request: `/matter/api/bridges`
1. Client → aiohttp (port 8080)
2. Python proxy strips `/matter`
3. Adds `X-Forwarded-Prefix: /matter`
4. Forwards to `http://localhost:8481/api/bridges`
5. Matter backend processes with prefix awareness
6. Response flows back through proxy
7. Client receives response

## Quick Fixes

### Rebuild Everything
```bash
cd oasira_cloud_bridge
docker build --no-cache -t oasira-addon:latest .
```

### Check Matter Build
```bash
docker run --rm -it oasira-addon:latest ls -la /app/matter-backend/
docker run --rm -it oasira-addon:latest node /app/matter-backend/cli.js --help
```

### Test Proxy
```bash
# Inside container
curl http://localhost:8481/api/matter/bridges  # Direct
curl http://localhost:8080/matter/api/bridges  # Through proxy
```

## Success Indicators

✅ Build succeeds without errors  
✅ Logs show "Oasira Matter server started with PID"  
✅ Logs show "Unified server running at http://0.0.0.0:8080"  
✅ Both URLs accessible in browser  
✅ No 404 errors in browser console  
✅ Matter API returns JSON responses  

## Support Files
- `MATTER_INTEGRATION.md` - Full technical documentation
- `INTEGRATION_SUMMARY.md` - Change summary
- `oasira_cloud_bridge/README.md` - User documentation
