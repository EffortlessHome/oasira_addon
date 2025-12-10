#!/bin/bash
# Manual build and push script for Oasira Cloud Bridge Docker images
# This is useful for testing or when GitHub Actions is not available

set -e

# Configuration
DOCKER_USERNAME="${DOCKER_USERNAME:-effortlesshome}"
IMAGE_NAME="${DOCKER_USERNAME}/oasira-cloud-bridge"

# Extract version from config.yaml
VERSION=$(grep "^version:" oasira_cloud_bridge/config.yaml | cut -d'"' -f2)

echo "Building Oasira Cloud Bridge v${VERSION}"
echo "Image: ${IMAGE_NAME}"
echo ""

# Ensure logged in to Docker Hub
echo "Checking Docker Hub login..."
if ! docker info | grep -q "Username"; then
    echo "Please login to Docker Hub:"
    docker login
fi

cd oasira_cloud_bridge

# Build for amd64
echo ""
echo "==================================="
echo "Building for linux/amd64..."
echo "==================================="
docker buildx build \
    --platform linux/amd64 \
    --tag ${IMAGE_NAME}:${VERSION}-amd64 \
    --tag ${IMAGE_NAME}:latest-amd64 \
    --push \
    --file Dockerfile \
    .

# Build for arm64/aarch64
echo ""
echo "==================================="
echo "Building for linux/arm64..."
echo "==================================="
docker buildx build \
    --platform linux/arm64 \
    --tag ${IMAGE_NAME}:${VERSION}-aarch64 \
    --tag ${IMAGE_NAME}:latest-aarch64 \
    --push \
    --file Dockerfile \
    .

cd ..

# Create multi-arch manifest
echo ""
echo "==================================="
echo "Creating multi-arch manifest..."
echo "==================================="

docker buildx imagetools create \
    --tag ${IMAGE_NAME}:${VERSION} \
    ${IMAGE_NAME}:${VERSION}-amd64 \
    ${IMAGE_NAME}:${VERSION}-aarch64

docker buildx imagetools create \
    --tag ${IMAGE_NAME}:latest \
    ${IMAGE_NAME}:latest-amd64 \
    ${IMAGE_NAME}:latest-aarch64

echo ""
echo "✅ Successfully built and pushed:"
echo "   ${IMAGE_NAME}:${VERSION}"
echo "   ${IMAGE_NAME}:latest"
echo ""
echo "Architecture-specific tags:"
echo "   ${IMAGE_NAME}:${VERSION}-amd64"
echo "   ${IMAGE_NAME}:${VERSION}-aarch64"
echo "   ${IMAGE_NAME}:latest-amd64"
echo "   ${IMAGE_NAME}:latest-aarch64"
