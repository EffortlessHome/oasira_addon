# Local Docker Development

## Quick Start

1. **Copy environment template:**
   ```powershell
   Copy-Item .env.example .env
   ```

2. **Edit `.env` file with your Oasira credentials:**
   - `OASIRA_EMAIL`: Your Oasira account email
   - `OASIRA_PASSWORD`: Your Oasira account password
   - `SYSTEM_ID`: Your system ID (optional - will auto-select if you have only one system)
   - `MATTER_LABEL`: Home Assistant label for Matter devices (default: "favorite")
   
   **Note:** HA_URL, HA_TOKEN, and CLOUDFLARE_TOKEN are automatically fetched from the Oasira API.

3. **Build and run:**
   ```powershell
   docker-compose up --build
   ```

4. **Access the dashboard:**
   - Main Dashboard: http://localhost:8080
   - Matter API: http://localhost:8080/api/matter/bridges

## Create Matter Bridge

```powershell
Invoke-RestMethod -Uri "http://localhost:8080/api/matter/bridges" -Method POST -ContentType "application/json" -Body '{"name": "My Bridge", "port": 5540, "filter": {"include": [{"type": "label", "value": "favorite"}], "exclude": []}}'
```

## Get Bridge Info (with pairing code)

```powershell
$bridges = Invoke-RestMethod -Uri "http://localhost:8080/api/matter/bridges"
$bridgeId = $bridges[0].id
Invoke-RestMethod -Uri "http://localhost:8080/api/matter/bridges/$bridgeId"
```

## Persistent Data

All configuration is stored in `./data/` directory:
- `./data/options.json` - Addon configuration
- `./data/matter/` - Matter bridge configurations and storage

## Rebuild

```powershell
docker-compose down
docker-compose up --build
```

## View Logs

```powershell
docker-compose logs -f oasira-bridge
```

## Architecture

- **Port 8080**: Python web server (dashboard + API proxy)
- **Port 8482**: Matter.js backend (internal, proxied through 8080)
- **Volumes**: `./data` mapped to `/data` for persistence
