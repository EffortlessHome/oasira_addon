# Oasira Home Assistant Add-ons

Home Assistant add-ons repository for Oasira Cloud services.

## Installation

Add this repository to your Home Assistant instance:

1. Navigate to **Settings** → **Add-ons** → **Add-on Store**
2. Click the **⋮** (three dots) in the top right
3. Select **Repositories**
4. Add this URL: `https://github.com/EffortlessHome/oasira_addon`
5. Click **Add**

## Available Add-ons

### Oasira Cloud Bridge

Connect your Home Assistant to Oasira Cloud services with:
- **Cloudflare Tunnel** - Secure remote access
- **Matter Hub Integration** - Matter protocol bridge for smart home devices
- **Unified Web Dashboard** - Single interface for all features

#### Features

- **Main Dashboard** (accessible at `/`) - Monitor and manage Oasira services
- **Matter Hub UI** (accessible at `/matter/`) - Configure and manage Matter devices
- Single port (8080) for both interfaces
- Automatic authentication using Oasira credentials
- Persistent storage for Matter devices

See [MATTER_INTEGRATION.md](MATTER_INTEGRATION.md) for technical details about the Matter integration.

## Support

For support and questions, visit [Oasira](https://oasira.com)
