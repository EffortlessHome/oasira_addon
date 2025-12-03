# Hosting Oasira Dashboard in the Addon

This addon now includes the Oasira Dashboard web UI.

## Overview

The addon serves the oasira-dashboard React application as a web interface accessible through Home Assistant's addon panel or directly via port 8080.

## Build Options

### Option 1: Multi-stage Build (Dockerfile)
Builds the dashboard from source inside Docker:
```bash
docker build -t oasira-addon:latest .
```

**Pros:** Self-contained, no need to pre-build
**Cons:** Longer build time, requires Node.js in Docker

### Option 2: Pre-built Copy (Dockerfile.simple) - RECOMMENDED
Copies pre-built dashboard files:
```bash
# First build the dashboard
cd ../oasira-dashboard
npm install
npm run build

# Then build the addon
cd ../oasira_addon
docker build -f Dockerfile.simple -t oasira-addon:latest ..
```

**Pros:** Faster builds, simpler
**Cons:** Requires manual dashboard build first

### Option 3: Use Build Scripts
Automated build process:
```bash
# Linux/Mac
./build.sh

# Windows
build.bat
```

## Configuration

The addon exposes the following new options in `config.yaml`:

```yaml
dashboard_port: 8080  # Port for the dashboard web server
```

## Accessing the Dashboard

1. **Through Home Assistant Ingress:**
   - Go to Settings → Add-ons
   - Click on "Oasira Cloud Bridge"
   - Click "OPEN WEB UI" or "Oasira Dashboard" panel

2. **Direct Access:**
   - Navigate to `http://[home-assistant-ip]:8080`
   - Or `http://[addon-ip]:8080` if using host_network mode

## How It Works

1. The dashboard is built using Vite (React + TypeScript)
2. Built files are copied to `/var/www/dashboard` in the container
3. Python's aiohttp serves the static files on the configured port
4. The addon's `run.py` starts both the dashboard server and the existing Oasira services

## Files Modified

- `Dockerfile` - Multi-stage build with Node.js
- `Dockerfile.simple` - Simple copy of pre-built files (recommended)
- `config.yaml` - Added dashboard_port, ingress support, and panel config
- `run.py` - Added `serve_dashboard()` function using aiohttp
- `build.sh` / `build.bat` - Automated build scripts

## Development Workflow

1. Make changes to oasira-dashboard
2. Build the dashboard: `cd oasira-dashboard && npm run build`
3. Rebuild the addon: `cd oasira_addon && docker build -f Dockerfile.simple -t oasira-addon:latest ..`
4. Restart the addon in Home Assistant

## Troubleshooting

**Dashboard not loading:**
- Check if `/var/www/dashboard` exists in the container
- Verify port 8080 is not blocked by firewall
- Check addon logs: `docker logs [container-id]`

**Build fails:**
- Ensure oasira-dashboard builds successfully standalone first
- Check Docker has enough memory (Node builds can be memory-intensive)
- Verify file paths in Dockerfile are correct relative to build context

## Architecture

```
oasira_addon/
├── Dockerfile (multi-stage with Node)
├── Dockerfile.simple (copy pre-built)
├── config.yaml (addon config + ingress)
├── run.py (Python server + dashboard server)
└── build.sh/bat (build automation)

oasira-dashboard/
└── dist/ (built files copied to addon)
```

## Future Enhancements

- [ ] Add WebSocket proxy to connect dashboard to Home Assistant API
- [ ] Enable HTTPS support with SSL certificates
- [ ] Add authentication layer
- [ ] Implement API endpoints for dashboard-specific features
- [ ] Add custom branding/theming options
