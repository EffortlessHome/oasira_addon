@echo off
REM Build script for Oasira addon with dashboard

echo Building Oasira Dashboard...
cd ..\oasira-dashboard
call npm install
call npm run build

echo Building Oasira Addon...
cd ..\oasira_addon

REM Use the simple Dockerfile that copies pre-built files
docker build -f Dockerfile.simple -t oasira-addon:latest ..

echo Build complete!
echo Dashboard will be available at http://[addon-ip]:8080
