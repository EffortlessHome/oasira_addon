#!/bin/sh
set -e

CONFIG_FILE="/data/options.json"

if [ -f "$CONFIG_FILE" ]; then
  echo "Loading configuration from $CONFIG_FILE"
  
  # Parse JSON and export as environment variables
  export EMAIL=$(jq -r '.email // ""' "$CONFIG_FILE")
  export PASSWORD=$(jq -r '.password // ""' "$CONFIG_FILE")
  export SYSTEM_ID=$(jq -r '.system_id // ""' "$CONFIG_FILE")
  export MATTER_LABEL=$(jq -r '.matter_label // "favorite"' "$CONFIG_FILE")
  export DASHBOARD_PORT=$(jq -r '.dashboard_port // 8080' "$CONFIG_FILE")
  
  echo "Configuration loaded:"
  echo "  EMAIL: ${EMAIL:0:3}***"
  echo "  SYSTEM_ID: $SYSTEM_ID"
  echo "  MATTER_LABEL: $MATTER_LABEL"
  echo "  DASHBOARD_PORT: $DASHBOARD_PORT"
else
  echo "No options.json found at $CONFIG_FILE; using environment variables"
  
  # Debug: Show what we have before mapping
  echo "DEBUG - Before mapping:"
  echo "  OASIRA_EMAIL: ${OASIRA_EMAIL:-not set}"
  echo "  OASIRA_PASSWORD: ${OASIRA_PASSWORD:+set}"
  echo "  EMAIL: ${EMAIL:-not set}"
  echo "  PASSWORD: ${PASSWORD:+set}"
  
  # Map OASIRA_* environment variables to expected names
  # Use := to set default if unset or empty
  export EMAIL="${OASIRA_EMAIL:-$EMAIL}"
  export PASSWORD="${OASIRA_PASSWORD:-$PASSWORD}"
  
  # Debug: Show what we have after mapping
  echo "DEBUG - After mapping:"
  echo "  EMAIL: ${EMAIL:-not set}"
  echo "  PASSWORD: ${PASSWORD:+set}"
  
  echo "Configuration from environment:"
  echo "  EMAIL: ${EMAIL:0:3}***"
  echo "  PASSWORD: ***"
  echo "  SYSTEM_ID: ${SYSTEM_ID:-not set}"
  echo "  MATTER_LABEL: ${MATTER_LABEL:-favorite}"
  echo "  DASHBOARD_PORT: ${DASHBOARD_PORT:-8080}"
fi

# Expose SUPERVISOR_TOKEN to the script (it's already available as env, but be explicit)
export SUPERVISOR_TOKEN="${SUPERVISOR_TOKEN:-}"

echo "Starting Oasira Cloud Bridge..."

# Activate virtual environment and run Python
. /venv/bin/activate

# Set Python to unbuffered mode for immediate log output
export PYTHONUNBUFFERED=1

exec python3 /run.py
