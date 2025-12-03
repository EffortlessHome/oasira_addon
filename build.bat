@echo off
REM Build script for Oasira addon with dashboard

echo Building Oasira Addon...
cd oasira_cloud_bridge

REM Build the addon
docker build -t oasira-addon:latest .

echo Build complete!
echo To test locally, run: docker run -p 8080:8080 oasira-addon:latest
