/**
 * Service Worker for Trading Bot Dashboard
 * Provides offline capability and caching strategy
 */

const CACHE_NAME = 'trading-dashboard-v1';
const STATIC_CACHE = 'static-v1';

// Assets to cache on install
const STATIC_ASSETS = [
    '/',
    '/static/css/dashboard.css',
    '/static/js/dashboard.js',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
    'https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    console.log('Service Worker: Installing...');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('Service Worker: Caching static assets');
                // Try to cache, but don't fail if CDN is blocked
                return cache.addAll(STATIC_ASSETS.filter(url => !url.includes('http')))
                    .catch(err => console.log('Some assets failed to cache:', err));
            })
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker: Activating...');
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cache) => {
                        if (cache !== CACHE_NAME && cache !== STATIC_CACHE) {
                            console.log('Service Worker: Clearing old cache:', cache);
                            return caches.delete(cache);
                        }
                    })
                );
            })
            .then(() => self.clients.claim())
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Handle API requests differently
    if (url.pathname.startsWith('/api/')) {
        // Network first for API calls
        event.respondWith(
            fetch(request)
                .then((response) => {
                    // Clone the response
                    const responseToCache = response.clone();
                    
                    // Cache the API response for short time
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(request, responseToCache);
                    });
                    
                    return response;
                })
                .catch(() => {
                    // If network fails, try cache
                    return caches.match(request)
                        .then((cachedResponse) => {
                            if (cachedResponse) {
                                console.log('Service Worker: Serving API from cache:', url.pathname);
                                return cachedResponse;
                            }
                            // Return offline response
                            return new Response(JSON.stringify({
                                error: 'Offline',
                                message: 'You are offline. Showing cached data.'
                            }), {
                                headers: { 'Content-Type': 'application/json' }
                            });
                        });
                })
        );
    } else {
        // Cache first for static assets
        event.respondWith(
            caches.match(request)
                .then((cachedResponse) => {
                    if (cachedResponse) {
                        // Return cached version and update in background
                        fetch(request).then((response) => {
                            caches.open(STATIC_CACHE).then((cache) => {
                                cache.put(request, response);
                            });
                        }).catch(() => {});
                        
                        return cachedResponse;
                    }
                    
                    // Not in cache, fetch from network
                    return fetch(request)
                        .then((response) => {
                            // Cache the response
                            if (request.method === 'GET') {
                                const responseToCache = response.clone();
                                caches.open(STATIC_CACHE).then((cache) => {
                                    cache.put(request, responseToCache);
                                });
                            }
                            return response;
                        });
                })
        );
    }
});

// Message event - for manual cache updates
self.addEventListener('message', (event) => {
    if (event.data.action === 'skipWaiting') {
        self.skipWaiting();
    }
    
    if (event.data.action === 'clearCache') {
        event.waitUntil(
            caches.keys().then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cache) => caches.delete(cache))
                );
            })
        );
    }
});
