# Oasira Home Assistant Add-on

The Oasira Cloud Bridge connects your Home Assistant installation to Oasira
Cloud. It pairs the installation with an Oasira Care facility, retrieves the
Home Assistant connection details provisioned for that facility, and starts a
Cloudflare Tunnel when one is available.

Your Home Assistant installation and the bridge credentials remain on your own
hardware.

## Requirements

- An existing Home Assistant installation
- A supported add-on architecture: `aarch64` or `amd64`
- An Oasira account with access to Oasira Care
- A one-time enrollment code for the Home Assistant node
- Home Assistant connection details provisioned in the facility's Hub
  Provisioning panel

## Installation

1. In Home Assistant, open **Settings > Add-ons > Add-on Store**.
2. Open the menu and choose **Repositories**.
3. Add:
   `https://github.com/EffortlessHome/oasira_addon`
4. Find and install **Oasira Cloud Bridge**.
5. Enter the configuration options below, save, and start the add-on.

## Configuration

Configure these values in the add-on's **Configuration** tab:

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `api_endpoint` | Yes | `careapi` | Oasira API endpoint. Choose `careapi`, `propertyapi`, or `homeapi`. |
| `api_url` | No | Empty | Optional custom API base URL. When set, it overrides the selected endpoint. |
| `enrollment_code` | No on subsequent starts | Empty | One-time pairing code issued by Oasira Care. |
| `node_name` | No | `Home Assistant add-on` | Display name used for the enrolled Home Assistant node. |

The supported endpoint selections resolve as follows:

- `careapi` -> `https://careapi.oasira.ai`
- `propertyapi` -> `https://propertyapi.oasira.ai`
- `homeapi` -> `https://homeapi.oasira.ai`

## First startup

At startup, the bridge exchanges the enrollment code for a revocable node API
key. The code is consumed during enrollment, and the resulting node credentials
are stored in `/data/care_node.json`.

The bridge then retrieves the Home Assistant URL and token configured in
Oasira Care. If Hub Provisioning has not supplied that connection information,
the bridge will report that it cannot start and you must configure it in
Oasira Care.

After enrollment, the saved node key is reused, verified with Oasira Cloud, and
the spent enrollment code is no longer required. The key can be revoked from
Oasira Care; if revoked, issue a new enrollment code and enroll the node again.

## Remote access

When Oasira Care provides a Cloudflare Tunnel token for the enrolled node, the
add-on downloads the matching `cloudflared` binary if needed and starts the
tunnel. If no tunnel is configured yet, the bridge continues checking and can
start it after tunnel provisioning is completed.

## Runtime details

- The add-on starts automatically with Home Assistant.
- It supports `aarch64` and `amd64`.
- Enrollment credentials persist in `/data` across restarts and updates.
- Add-on options are stored by Home Assistant in `/data/options.json`.
- The bridge configuration is defined in
  [config.yaml](oasira_cloud_bridge/config.yaml).

## Support

For product information and help, visit
[Oasira](https://www.Oasira.ai/). To report an add-on issue, open an issue in
this repository.
