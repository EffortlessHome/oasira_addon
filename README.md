# Oasira Home Assistant Add-on

Oasira adds a simpler household experience on top of your existing Home
Assistant setup. Install this add-on to connect Home Assistant to Oasira
services; your Home Assistant installation stays on your own hardware.

## What it provides

Oasira's current offering includes:

- Remote access using Cloudflare Tunnel infrastructure
- A unified dashboard and household app experience
- Guest access with controls for device categories
- Camera support, Matter support, entity management, and drag-and-drop
  configuration
- iOS, Android, and TV apps, currently in beta

See [Oasira.AI](https://www.Oasira.ai/) for current product
details.

## Requirements

- An existing Home Assistant installation
- A supported add-on architecture: `aarch64` or `amd64`
- An Oasira account and an active plan or trial


## Install

1. In Home Assistant, open **Settings > Add-ons > Add-on Store**.
2. Open the menu and choose **Repositories**.
3. Add this repository:
   `https://github.com/EffortlessHome/Oasira_addon`
4. Find and install **Oasira **.
5. Configure the add-on, save the options, and start it.

## Add-on options

Configure these in the add-on's **Configuration** tab:

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `email` | Yes | Not set | Email address for your Oasira account |
| `password` | Yes | Not set | Password for your Oasira account |
| `ha_url` | No | Empty | Optional Home Assistant URL |
| `ha_token` | No | Empty | Optional Home Assistant token |
| `matter_label` | No | `favorite` | Matter label option |
| `send_on_start` | No | `true` | Whether to send on add-on startup |
| `interval_seconds` | No | `3600` | Send interval, in seconds |

The add-on runs automatically at startup. Its configuration schema and
supported architectures are defined in
[config.yaml](Oasira_cloud_bridge/config.yaml).

## Support

For product information and help, visit
[Oasira.co](https://www.Oasira.ai/). For add-on issues, open an
issue in this repository.
