@echo off
REM Manual build and push script for Oasira Cloud Bridge Docker images
REM This is useful for testing or when GitHub Actions is not available

setlocal enabledelayedexpansion

REM Configuration
if "%DOCKER_USERNAME%"=="" set DOCKER_USERNAME=effortlesshome
set IMAGE_NAME=%DOCKER_USERNAME%/oasira-cloud-bridge

REM Extract version from config.yaml
for /f "tokens=2 delims=:" %%a in ('findstr "^version:" oasira_cloud_bridge\config.yaml') do (
    set VERSION=%%a
    set VERSION=!VERSION:"=!
    set VERSION=!VERSION: =!
)

echo Building Oasira Cloud Bridge v%VERSION%
echo Image: %IMAGE_NAME%
echo.

REM Ensure logged in to Docker Hub
echo Checking Docker Hub login...
docker info | findstr /C:"Username" >nul
if errorlevel 1 (
    echo Please login to Docker Hub:
    docker login
    if errorlevel 1 exit /b 1
)

cd oasira_cloud_bridge

REM Build for amd64
echo.
echo ===================================
echo Building for linux/amd64...
echo ===================================
docker buildx build ^
    --platform linux/amd64 ^
    --tag %IMAGE_NAME%:%VERSION%-amd64 ^
    --tag %IMAGE_NAME%:latest-amd64 ^
    --push ^
    --file Dockerfile ^
    .

if errorlevel 1 (
    echo Build failed for amd64
    cd ..
    exit /b 1
)

REM Build for arm64/aarch64
echo.
echo ===================================
echo Building for linux/arm64...
echo ===================================
docker buildx build ^
    --platform linux/arm64 ^
    --tag %IMAGE_NAME%:%VERSION%-aarch64 ^
    --tag %IMAGE_NAME%:latest-aarch64 ^
    --push ^
    --file Dockerfile ^
    .

if errorlevel 1 (
    echo Build failed for arm64
    cd ..
    exit /b 1
)

cd ..

REM Create multi-arch manifest
echo.
echo ===================================
echo Creating multi-arch manifest...
echo ===================================

docker buildx imagetools create ^
    --tag %IMAGE_NAME%:%VERSION% ^
    %IMAGE_NAME%:%VERSION%-amd64 ^
    %IMAGE_NAME%:%VERSION%-aarch64

docker buildx imagetools create ^
    --tag %IMAGE_NAME%:latest ^
    %IMAGE_NAME%:latest-amd64 ^
    %IMAGE_NAME%:latest-aarch64

echo.
echo Successfully built and pushed:
echo    %IMAGE_NAME%:%VERSION%
echo    %IMAGE_NAME%:latest
echo.
echo Architecture-specific tags:
echo    %IMAGE_NAME%:%VERSION%-amd64
echo    %IMAGE_NAME%:%VERSION%-aarch64
echo    %IMAGE_NAME%:latest-amd64
echo    %IMAGE_NAME%:latest-aarch64
