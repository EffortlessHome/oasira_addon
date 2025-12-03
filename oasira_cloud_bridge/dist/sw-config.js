/**
 * PWA Service Worker Configuration for Oasira Dashboard
 * 
 * This file provides enhanced offline support and caching strategies
 * for the Oasira Dashboard PWA running on both web and Capacitor.
 * 
 * Key Features:
 * - Automatic cache versioning
 * - Smart offline fallbacks
 * - Background sync for pending actions
 * - Update notifications
 */

// Cache version - increment this when updating cache strategy
const CACHE_VERSION = 'v1';
const CACHE_NAME = `oasira-cache-${CACHE_VERSION}`;
const API_CACHE = `oasira-api-${CACHE_VERSION}`;
const OFFLINE_CACHE = `oasira-offline-${CACHE_VERSION}`;

// Assets to cache on install
const CRITICAL_ASSETS = [
  '/',
  '/index.html',
  '/manifest.webmanifest',
];

// API routes to cache (read-only operations)
const CACHEABLE_API_ROUTES = [
  '/api/states',
  '/api/config/entries',
  '/api/areas',
  '/api/devices',
];

// Self-destruct old caches
self.addEventListener('activate', (event) => {
  console.log('[PWA-SW] Activating service worker...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && cacheName !== API_CACHE && cacheName !== OFFLINE_CACHE) {
            console.log(`[PWA-SW] Deleting old cache: ${cacheName}`);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Handle fetch requests with intelligent caching
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests and same-site POST/PUT/DELETE for API modifications
  if (request.method !== 'GET') {
    return;
  }

  // Handle different request types
  if (url.origin === location.origin) {
    // Same-origin requests (app assets)
    event.respondWith(handleSameOriginRequest(request));
  } else {
    // Cross-origin requests (external APIs)
    event.respondWith(handleCrossOriginRequest(request));
  }
});

async function handleSameOriginRequest(request) {
  // Try network first, fallback to cache
  try {
    const response = await fetch(request);
    
    if (response.ok) {
      // Cache successful responses
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.log(`[PWA-SW] Network request failed for ${request.url}, using cache`);
    
    // Try cache as fallback
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    // Return offline page if available
    if (request.mode === 'navigate') {
      const offlineResponse = await caches.match('/offline.html');
      if (offlineResponse) {
        return offlineResponse;
      }
    }

    // Return error response
    return new Response(
      JSON.stringify({ error: 'Offline: Unable to load resource' }),
      { status: 503, statusText: 'Service Unavailable' }
    );
  }
}

async function handleCrossOriginRequest(request) {
  // Cache first, fallback to network for external APIs
  try {
    const cache = await caches.open(API_CACHE);
    const cachedResponse = await cache.match(request);

    if (cachedResponse) {
      console.log(`[PWA-SW] Using cached response for ${request.url}`);
      return cachedResponse;
    }

    // Not in cache, try network
    const response = await fetch(request);

    if (response.ok) {
      // Cache successful API responses
      cache.put(request, response.clone());
    }

    return response;
  } catch (error) {
    console.log(`[PWA-SW] API request failed: ${request.url}`);
    
    // Try stale cache
    const cache = await caches.open(API_CACHE);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      console.log(`[PWA-SW] Returning stale cached data for ${request.url}`);
      return cachedResponse;
    }

    // Return error response
    return new Response(
      JSON.stringify({ error: 'API unavailable' }),
      { status: 503, statusText: 'Service Unavailable' }
    );
  }
}

// Handle messages from app
self.addEventListener('message', (event) => {
  const { type, payload } = event.data;

  console.log(`[PWA-SW] Received message: ${type}`);

  switch (type) {
    case 'SKIP_WAITING':
      console.log('[PWA-SW] Forcing service worker update');
      self.skipWaiting();
      break;

    case 'CLEAR_CACHE':
      console.log('[PWA-SW] Clearing all caches');
      caches.keys().then((names) => {
        names.forEach((name) => caches.delete(name));
      });
      break;

    case 'CACHE_URLS':
      console.log('[PWA-SW] Caching URLs:', payload.urls);
      caches.open(CACHE_NAME).then((cache) => {
        cache.addAll(payload.urls).catch(err => 
          console.error('[PWA-SW] Failed to cache URLs:', err)
        );
      });
      break;

    default:
      console.log(`[PWA-SW] Unknown message type: ${type}`);
  }
});

// Periodic background sync for pending updates
self.addEventListener('sync', (event) => {
  console.log('[PWA-SW] Background sync event:', event.tag);
  
  if (event.tag === 'sync-pending-updates') {
    event.waitUntil(syncPendingUpdates());
  }
});

async function syncPendingUpdates() {
  try {
    console.log('[PWA-SW] Syncing pending updates...');
    
    // Get pending updates from IndexedDB or localStorage
    const pending = await getPendingUpdates();
    
    if (pending.length > 0) {
      console.log(`[PWA-SW] Found ${pending.length} pending updates to sync`);
      
      // Send each pending update
      for (const update of pending) {
        try {
          const response = await fetch(update.url, {
            method: update.method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(update.data)
          });

          if (response.ok) {
            console.log(`[PWA-SW] Successfully synced: ${update.url}`);
            await removePendingUpdate(update.id);
          }
        } catch (err) {
          console.error(`[PWA-SW] Failed to sync update:`, err);
          // Keep in pending queue for next sync
        }
      }
    }
  } catch (err) {
    console.error('[PWA-SW] Background sync failed:', err);
    throw err; // Retry sync
  }
}

// Placeholder functions for pending updates (implement with actual storage)
async function getPendingUpdates() {
  // TODO: Implement with IndexedDB or localStorage
  return [];
}

async function removePendingUpdate(id) {
  // TODO: Implement with IndexedDB or localStorage
}

console.log('[PWA-SW] Service Worker loaded');
