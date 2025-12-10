# Docker Hub Image Distribution

The Oasira Cloud Bridge addon now uses pre-built Docker images from Docker Hub instead of building locally. This significantly speeds up installation and updates.

## Image Information

- **Docker Hub Repository**: `effortlesshome/oasira-cloud-bridge`
- **Tags**: 
  - `{version}` - Specific version (e.g., `1.1.33`)
  - `latest` - Latest stable version
  - `{version}-{arch}` - Architecture-specific (e.g., `1.1.33-amd64`, `1.1.33-aarch64`)

## Automated Builds (GitHub Actions)

Images are automatically built and pushed to Docker Hub when:
- Code is pushed to the `main` branch
- A new release is published
- Manually triggered via workflow dispatch

### Setup Requirements

Add the following secrets to your GitHub repository:
1. `DOCKERHUB_USERNAME` - Your Docker Hub username
2. `DOCKERHUB_TOKEN` - Docker Hub access token (create at https://hub.docker.com/settings/security)

### Workflow Details

The workflow (`.github/workflows/build-push.yml`) does the following:
1. Builds images for both `amd64` and `aarch64` architectures
2. Pushes architecture-specific tags
3. Creates multi-arch manifests for version and latest tags
4. Uses GitHub Actions cache for faster subsequent builds

## Manual Build and Push

If you need to build and push images manually:

### Linux/Mac:
```bash
chmod +x build-push.sh
./build-push.sh
```

### Windows:
```cmd
build-push.bat
```

**Prerequisites**:
- Docker buildx enabled
- Logged in to Docker Hub (`docker login`)

## Addon Configuration

The addon's `config.yaml` and `config.json` now include:
```yaml
image: "effortlesshome/oasira-cloud-bridge:{version}-{arch}"
```

Home Assistant will automatically:
1. Pull the correct image for the system's architecture
2. Use the version specified in the config
3. Skip the local build process entirely

## Benefits

- ✅ **Faster Installation**: No local compilation needed
- ✅ **Faster Updates**: Pull pre-built images instead of rebuilding
- ✅ **Consistent Builds**: All users get identical images
- ✅ **Reduced Resource Usage**: No CPU/memory intensive builds on user systems
- ✅ **Better Testing**: CI/CD pipeline ensures builds succeed before distribution

## Version Management

To release a new version:
1. Update version in `oasira_cloud_bridge/config.yaml` and `config.json`
2. Commit and push to `main` branch
3. GitHub Actions will automatically build and push new images
4. Users will receive the update through Home Assistant addon updates

## Troubleshooting

### Image Pull Failures
If users experience pull failures:
- Check Docker Hub repository is public
- Verify the version tag exists on Docker Hub
- Check architecture matches (`amd64` or `aarch64`)

### Force Rebuild
To force a rebuild without version change:
1. Use workflow dispatch in GitHub Actions
2. Or manually run `build-push.sh`/`build-push.bat`

### Check Available Tags
```bash
# List all tags
docker search effortlesshome/oasira-cloud-bridge --limit 100

# Or use Docker Hub API
curl https://hub.docker.com/v2/repositories/effortlesshome/oasira-cloud-bridge/tags
```
