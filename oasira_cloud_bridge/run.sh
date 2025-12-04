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
else
  echo "No options.json found at $CONFIG_FILE; using environment variables"
fi

# Expose SUPERVISOR_TOKEN to the script (it's already available as env, but be explicit)
export SUPERVISOR_TOKEN="${SUPERVISOR_TOKEN:-}"

# Activate virtual environment and run Python
. /venv/bin/activate
exec python3 /run.py
