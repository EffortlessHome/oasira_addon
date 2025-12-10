@echo off
REM Build script for Oasira addon with dashboard

echo Copying dashboard dist folder...
if exist "..\oasira-dashboard\dist" (
    REM Clean old dist folder first
    if exist "oasira_cloud_bridge\dist" rmdir /S /Q "oasira_cloud_bridge\dist"
    xcopy /E /I /Y "..\oasira-dashboard\dist" "oasira_cloud_bridge\dist"
    echo Dashboard dist copied successfully
) else (
    echo WARNING: Dashboard dist folder not found at ..\oasira-dashboard\dist
    echo Build will continue but dashboard may not be available
)

echo.
echo Building Oasira Addon with optimizations...
cd oasira_cloud_bridge

REM Build the addon with BuildKit for better caching
set DOCKER_BUILDKIT=1
docker build --build-arg BUILDKIT_INLINE_CACHE=1 --progress=plain -t oasira-addon:latest .

cd ..
echo.
echo Build complete!
echo To test locally, run: docker run -p 8080:8080 oasira-addon:latest
