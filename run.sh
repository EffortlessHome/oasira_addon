#!/bin/sh
set -e

CONFIG_FILE="/data/options.json"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "No options.json found at $CONFIG_FILE; using defaults in config.json"
fi

# Expose SUPERVISOR_TOKEN to the script (it's already available as env, but be explicit)
export SUPERVISOR_TOKEN="${SUPERVISOR_TOKEN:-}"

# Activate virtual environment and run Python
. /venv/bin/activate
exec python3 /run.py
