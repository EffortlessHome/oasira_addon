# Oasira Cloud Bridge Add-on

Connect your Home Assistant instance to Oasira Cloud services with integrated Matter Hub support.

## About

This add-on provides:
- **Cloudflare Tunnel** - Secure remote access to your Home Assistant
- **Matter Hub** - Native Matter protocol bridge for smart home devices
- **Unified Web Dashboard** - Single interface accessible on one port

## Features

### Main Dashboard
- Monitor Oasira Cloud connection status
- View system information
- Manage tunnel configuration
- Accessible at: `http://[addon-ip]:8080/`

### Matter Hub
- Add and manage Matter devices
- Configure Matter bridges
- View device status and capabilities
- Accessible at: `http://[addon-ip]:8080/matter/`

Both interfaces run on the **same port (8080)** for simplified access.

## Configuration

```yaml
care_api_url: https://your-oasira-care-api.example.com
enrollment_code: ABCD-EFGH-JKLM
node_name: Front Desk Hub
dashboard_port: 8080
```

### Configuration Options

- `care_api_url` (required): Base URL of your Oasira Care API
- `enrollment_code` (required for first start): One-time pairing code issued by a facility admin in Oasira Care. It is exchanged for a revocable node key stored in `/data/care_node.json`, so the code can be cleared afterwards.
- `node_name` (optional): Name shown for this node in Oasira Care
- `ha_url` / `ha_token` (optional): Override the Home Assistant URL and token. By default both are supplied by Oasira Care (set per hub in the facility's Hub Provisioning panel).
- `dashboard_port` (optional): Port for web interface (default: 8080)

## Installation

1. Add this repository to your Home Assistant add-on store
2. Install the "Oasira Cloud Bridge" add-on
3. Enter the Care API URL and a pairing code from Oasira Care
4. Start the add-on
5. Access the dashboard at `http://[homeassistant-ip]:8080/`
6. Access Matter Hub at `http://[homeassistant-ip]:8080/matter/`

## Data Persistence

The add-on stores data in `/data`:
- `/data/matter` - Matter device configurations and pairings
- `/data/options.json` - Add-on configuration

This data persists across add-on restarts and updates.

## Technical Details

See [MATTER_INTEGRATION.md](../MATTER_INTEGRATION.md) for technical documentation about the Matter integration architecture.

## Support

For support, visit [Oasira](https://oasira.com)
