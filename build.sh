#!/bin/bash

# Build script for Oasira addon

set -e

echo "🔨 Building Oasira Addon..."
cd oasira_cloud_bridge

# Build the addon
docker build -t oasira-addon:latest .

echo "✅ Build complete!"
echo "To test locally, run: docker run -p 8080:8080 oasira-addon:latest"
