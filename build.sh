#!/bin/bash

# Build script for Oasira addon with dashboard

set -e

echo "🔨 Building Oasira Dashboard..."
cd ../oasira-dashboard
npm install
npm run build

echo "🔨 Building Oasira Addon..."
cd ../oasira_addon

# Use the simple Dockerfile that copies pre-built files
docker build -f Dockerfile.simple -t oasira-addon:latest ..

echo "✅ Build complete!"
echo "Dashboard will be available at http://[addon-ip]:8080"
