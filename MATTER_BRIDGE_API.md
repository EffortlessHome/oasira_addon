# Matter Bridge API Examples

## Create a Vacuum-Only Bridge

### PowerShell
```powershell
# Run the included script
.\create_vacuum_bridge.ps1

# Or inline command:
$body = @{
    name = "Vacuum Bridge"
    port = 5541
    filter = @{
        include = @(@{ type = "domain"; value = "vacuum" })
        exclude = @()
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8482/api/matter/bridges" -Method POST -ContentType "application/json" -Body $body
```

### cURL
```bash
curl -X POST http://localhost:8482/api/matter/bridges \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Vacuum Bridge",
    "port": 5541,
    "filter": {
      "include": [
        {
          "type": "domain",
          "value": "vacuum"
        }
      ],
      "exclude": []
    }
  }'
```

### Python
```python
import requests

bridge_config = {
    "name": "Vacuum Bridge",
    "port": 5541,
    "filter": {
        "include": [
            {
                "type": "domain",
                "value": "vacuum"
            }
        ],
        "exclude": []
    }
}

response = requests.post(
    "http://localhost:8482/api/matter/bridges",
    json=bridge_config
)

print(response.json())
```

## Other Filter Examples

### Filter by Area
```json
{
  "name": "Living Room Bridge",
  "port": 5542,
  "filter": {
    "include": [
      {
        "type": "area",
        "value": "living_room"
      }
    ],
    "exclude": []
  }
}
```

### Filter by Label
```json
{
  "name": "Favorites Bridge",
  "port": 5543,
  "filter": {
    "include": [
      {
        "type": "label",
        "value": "favorite"
      }
    ],
    "exclude": []
  }
}
```

### Filter by Entity Pattern
```json
{
  "name": "Specific Vacuums",
  "port": 5544,
  "filter": {
    "include": [
      {
        "type": "pattern",
        "value": "vacuum.roborock_*"
      }
    ],
    "exclude": []
  }
}
```

### Multiple Domains
```json
{
  "name": "Cleaning Bridge",
  "port": 5545,
  "filter": {
    "include": [
      {
        "type": "domain",
        "value": "vacuum"
      },
      {
        "type": "domain",
        "value": "switch"
      }
    ],
    "exclude": []
  }
}
```

### Include Domain, Exclude Specific Entity
```json
{
  "name": "Most Vacuums",
  "port": 5546,
  "filter": {
    "include": [
      {
        "type": "domain",
        "value": "vacuum"
      }
    ],
    "exclude": [
      {
        "type": "pattern",
        "value": "vacuum.old_broken_vacuum"
      }
    ]
  }
}
```

## Available Filter Types

- **domain**: Filter by Home Assistant domain (e.g., "vacuum", "light", "switch")
- **pattern**: Glob pattern matching entity IDs (e.g., "vacuum.roborock_*")
- **label**: Filter by Home Assistant label
- **area**: Filter by Home Assistant area name
- **platform**: Filter by integration platform
- **entity_category**: Filter by entity category (config, diagnostic)

## Get All Bridges
```powershell
Invoke-RestMethod -Uri "http://localhost:8482/api/matter/bridges"
```

## Get Specific Bridge
```powershell
$bridgeId = "your-bridge-id-here"
Invoke-RestMethod -Uri "http://localhost:8482/api/matter/bridges/$bridgeId"
```

## Update Bridge
```powershell
$bridgeId = "your-bridge-id-here"
$updateBody = @{
    id = $bridgeId
    name = "Updated Vacuum Bridge"
    port = 5541
    filter = @{
        include = @(@{ type = "domain"; value = "vacuum" })
        exclude = @()
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8482/api/matter/bridges/$bridgeId" -Method PUT -ContentType "application/json" -Body $updateBody
```

## Delete Bridge
```powershell
$bridgeId = "your-bridge-id-here"
Invoke-RestMethod -Uri "http://localhost:8482/api/matter/bridges/$bridgeId" -Method DELETE
```

## Factory Reset Bridge
```powershell
$bridgeId = "your-bridge-id-here"
Invoke-RestMethod -Uri "http://localhost:8482/api/matter/bridges/$bridgeId/actions/factory-reset"
```

## Notes

- Each bridge requires a unique port number
- The default bridge typically uses port 5540
- After creating a bridge, use the QR code or manual pairing code to add it to your Matter controller
- Bridges will automatically discover and add entities matching the filter
