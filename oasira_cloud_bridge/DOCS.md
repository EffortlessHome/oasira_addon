# Oasira Cloud Bridge Documentation

## Configuration Options

### Required Settings

- **care_api_url**: Base URL of your Oasira Care API
- **enrollment_code**: One-time pairing code issued by a facility admin in Oasira Care (needed on first start only; the add-on stores its own node key)

### Optional Settings

- **node_name**: Name shown for this node in Oasira Care
- **ha_url** / **ha_token**: Override the Home Assistant URL and token. By default both are supplied by Oasira Care for this node.
- **dashboard_port**: Port for the web dashboard (default: `8080`)

## Features

### Cloudflare Tunnel
Automatically establishes a secure Cloudflare tunnel for remote access to your Home Assistant instance.
Everything comes from one pairing code: in Oasira Care (Hub Provisioning) enter the Home Assistant URL/token and a remote-access subdomain, generate the code, and paste it into `enrollment_code`. Redeeming it creates the node key, stores the HA connection and provisions the tunnel. If a tunnel is added later, the add-on picks it up within a minute. The add-on stops if the node is revoked in Oasira Care.

### Matter
Adds Matter device export support to Home Assistant.

### Web Dashboard
Provides a web interface for monitoring and managing your Oasira services.

## Troubleshooting

### Add-on won't start
1. Check that the pairing code is unused and unexpired (issue a new one if needed)
2. If the node key was revoked, enter a new pairing code
3. Check the add-on logs for specific error messages

### Services not connecting
- Ensure your internet connection is stable
- Verify your Oasira account has active services
- Check that the required ports are not blocked by your firewall

## Support

For additional help, contact Oasira support at https://oasira.com
