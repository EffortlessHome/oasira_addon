# Oasira Cloud Add-on

Connect your Home Assistant instance to Oasira Cloud services with integrated Matter Hub support.

## About

This add-on provides:
- **Cloudflare Tunnel** - Secure remote access to your Home Assistant
- **Matter Hub** - Native Matter protocol bridge for smart home devices
- **Cloud Dashboard** - Hosted interface for managing your Oasira services
- **Bundled Web App Hosting** - Serves the local `web` app on a separate configurable port (default `8099`)

## Features

## Plan Requirements

This add-on requires a subscribed Oasira plan.
Systems on the Basic plan do not include this feature, so the add-on will not start.
Upgrade to a plan higher than Basic to use the Oasira add-on.

## Installation

1. Add this repository to your Home Assistant add-on store
2. Install the "Oasira Cloud" add-on
3. Configure your credentials
4. Start the add-on


## Data Persistence

The add-on stores data in `/data`:
- `/data/matter` - Matter device configurations and pairings
- `/data/options.json` - Add-on configuration

This data persists across add-on restarts and updates.


## Technical Details

See [MATTER_INTEGRATION.md](../MATTER_INTEGRATION.md) for technical documentation about the Matter integration architecture.

## Support

For support, visit [Oasira](https://Oasira.co)
