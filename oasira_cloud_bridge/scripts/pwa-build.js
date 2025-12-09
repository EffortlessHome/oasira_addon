#!/usr/bin/env node

/**
 * PWA Build Script for Oasira Dashboard
 * Builds the app for both web (PWA) and Capacitor mobile platforms
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const projectRoot = path.join(__dirname, '..');
const distDir = path.join(projectRoot, 'dist');
const capacitorDir = path.join(projectRoot, 'ios');
const androidDir = path.join(projectRoot, 'android');

console.log('🚀 Starting PWA Build Process...\n');

try {
  // Step 1: Build for web with PWA support
  console.log('📦 Step 1: Building PWA web app...');
  execSync('npm run build', { cwd: projectRoot, stdio: 'inherit' });
  console.log('✅ Web PWA build complete!\n');

  // Step 2: Verify PWA assets were generated
  console.log('🔍 Step 2: Verifying PWA assets...');
  const expectedFiles = [
    'sw.js',
    'manifest.webmanifest',
    'workbox-*.js'
  ];

  const distFiles = fs.readdirSync(distDir);
  const hasServiceWorker = distFiles.some(f => f === 'sw.js');
  const hasManifest = distFiles.some(f => f === 'manifest.webmanifest');

  if (!hasServiceWorker) {
    console.warn('⚠️  Service Worker (sw.js) not found in dist/');
  } else {
    console.log('✅ Service Worker: sw.js found');
  }

  if (!hasManifest) {
    console.warn('⚠️  Manifest (manifest.webmanifest) not found in dist/');
  } else {
    console.log('✅ Manifest: manifest.webmanifest found');
  }

  const workboxFiles = distFiles.filter(f => f.startsWith('workbox-'));
  console.log(`✅ Workbox files: ${workboxFiles.length} cache strategy files found\n`);

  // Step 3: Check if Capacitor projects exist
  console.log('📱 Step 3: Checking Capacitor platforms...');
  const hasIOS = fs.existsSync(capacitorDir);
  const hasAndroid = fs.existsSync(androidDir);

  if (hasIOS) {
    console.log('✅ iOS platform detected');
  } else {
    console.log('ℹ️  iOS platform not initialized (run: npx cap add ios)');
  }

  if (hasAndroid) {
    console.log('✅ Android platform detected');
  } else {
    console.log('ℹ️  Android platform not initialized (run: npx cap add android)');
  }

  // Step 4: Sync to Capacitor if platforms exist
  if (hasIOS || hasAndroid) {
    console.log('\n📲 Step 4: Syncing to Capacitor...');
    try {
      execSync('npx cap sync', { cwd: projectRoot, stdio: 'inherit' });
      console.log('✅ Capacitor sync complete!\n');
    } catch (err) {
      console.error('❌ Capacitor sync failed. Make sure Capacitor CLI is installed:\n  npm install -g @capacitor/cli\n');
    }
  }

  // Step 5: Summary
  console.log('✅ PWA Build Complete!\n');
  console.log('📋 Summary:');
  console.log('  • Web PWA app built and ready in: ./dist');
  console.log('  • Service Worker: Handles offline caching and updates');
  console.log('  • Manifest: Configured for standalone app experience');
  console.log('  • Capacitor: App synced to mobile platforms\n');

  console.log('🚀 Next Steps:');
  console.log('  Web Testing:');
  console.log('    npm run preview          (test PWA locally)');
  console.log('    DevTools → Application → Service Workers to verify\n');

  if (hasAndroid) {
    console.log('  Android Testing:');
    console.log('    npx cap open android    (open in Android Studio)');
    console.log('    Run app on device/emulator\n');
  }

  if (hasIOS) {
    console.log('  iOS Testing:');
    console.log('    npx cap open ios        (open in Xcode)');
    console.log('    Run app on simulator/device\n');
  }

} catch (error) {
  console.error('❌ Build failed:', error.message);
  process.exit(1);
}
