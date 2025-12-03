# Oasira Matter Setup Guide

After rebranding from Home-Assistant-Matter-Hub to Oasira Matter, follow these steps to set up your development environment:

## Step 1: Clean Old Dependencies

Remove all existing node_modules and build artifacts:

```powershell
pnpm run cleanup
```

## Step 2: Install Dependencies

Reinstall all dependencies with the updated package names:

```powershell
pnpm install
```

This will resolve the workspace references to the newly named packages:
- `@oasira-matter/common`
- `@oasira-matter/backend`
- `@oasira-matter/frontend`

## Step 3: Build Packages

Build all packages in the correct order:

```powershell
# Build common package first (required by others)
pnpm run build:minimum

# Build all packages
pnpm run build
```

## Step 4: Run Tests

Verify everything works correctly:

```powershell
pnpm test
```

## Step 5: Local Development

To run the application in development mode:

```powershell
pnpm run serve
```

Or to run in production mode:

```powershell
pnpm run production
```

## Step 6: Build Distribution Package

To create the distributable package:

```powershell
# Build and pack
pnpm run release:pack
```

This creates `apps/oasira-matter/package.tgz` which can be published to npm.

## Common Issues

### Module Resolution Errors

If you see errors like "Cannot find module '@oasira-matter/...'", make sure:
1. You've run `pnpm install` after the rebranding
2. The workspace packages are properly linked
3. You've built the common package: `pnpm run build:minimum`

### TypeScript Errors

Build errors in TypeScript files are normal until dependencies are installed and packages are built.

## Development Workflow

### 1. Frontend Development
```powershell
cd packages/frontend
pnpm run dev
```

### 2. Backend Development
```powershell
cd packages/backend
pnpm run serve
```

### 3. Full Stack Development
From the root:
```powershell
pnpm run serve
```

## Docker Build

To build the Docker images locally:

```powershell
# For standalone image
docker build -f apps/oasira-matter/standalone.Dockerfile -t oasira:local .

# For addon image
docker build -f apps/oasira-matter/addon.Dockerfile -t oasira-addon:local .
```

## Testing Docker Image Locally

```powershell
docker run -d `
  --name oasira-matter-test `
  --network host `
  -e OASIRA_MATTER_MATTER_HOME_ASSISTANT_URL="http://192.168.1.100:8123/" `
  -e OASIRA_MATTER_MATTER_HOME_ASSISTANT_ACCESS_TOKEN="your-token-here" `
  -e OASIRA_MATTER_MATTER_LOG_LEVEL="debug" `
  -v ${PWD}/oasira-data:/data `
  oasira:local
```

## Publishing to NPM

Once ready to publish:

```powershell
# Update version (optional)
pnpm run release:version

# Build and pack
pnpm run release:pack

# Publish (requires npm credentials)
pnpm run release:publish
```

## Environment Variables for Development

Create a `.env` file in the root directory:

```env
OASIRA_MATTER_MATTER_HOME_ASSISTANT_URL=http://192.168.1.100:8123/
OASIRA_MATTER_MATTER_HOME_ASSISTANT_ACCESS_TOKEN=your_long_lived_access_token
OASIRA_MATTER_MATTER_LOG_LEVEL=debug
OASIRA_MATTER_MATTER_HTTP_PORT=8482
OASIRA_MATTER_MATTER_STORAGE_LOCATION=./.local-storage
```

## VS Code Integration

The workspace is already configured for VS Code. Key features:
- TypeScript compilation on save
- ESLint/Biome linting
- Debugging configurations
- Recommended extensions

## Next Steps

After successful setup:
1. Review the [REBRANDING_SUMMARY.md](./REBRANDING_SUMMARY.md) for all changes
2. Update any local configurations or scripts
3. Test the application thoroughly
4. Update documentation as needed
5. Consider creating Oasira-specific branding assets (logos, etc.)

## Getting Help

If you encounter issues:
1. Check that all packages are properly installed: `pnpm list`
2. Verify TypeScript compilation: `pnpm run build`
3. Review build logs for specific errors
4. Check GitHub issues in the repository

---

**Note:** The first build after rebranding may take longer as all packages need to be rebuilt with new names.
