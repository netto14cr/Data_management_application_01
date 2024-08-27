const CACHE_NAME = 'data-management-app-v1';
const urlsToCache = [
    '/',
    'static/pwa/image/favicon.ico',
    'static/pwa/image/ios-splash-1170x2532.jpg',
    'static/pwa/image/logo144.png',
    'static/pwa/image/logo192.png',
    'static/pwa/image/logo48.png',
    'static/pwa/image/logo512.png',
    'static/pwa/image/logo96.png',
    '/static/js/script.js',
    '/static/js/install_app.js',
    'static/pwa/service/manifest.json',
    'static/pwa/service/service-worker.js',
    'templates/cloud/cloud_data.html',
    'templates/cloud/edit_cloud_data.html',
    'templates/cloud/view_row.html',
    'templates/form/data_entry.html',
    'templates/form/data_entry_mysql.html',
    'templates/form/data_entry_sheets.html',
    'templates/header/navbar.html',
    'templates/main/base.html',
    'templates/main/error_404.html',
    'templates/main/error_500.html',
    'templates/main/index.html',
    'templates/sheets/edit_sheet_data.html',
    'templates/sheets/manage_sheets.html',
    'templates/sheets/view_sheet_data.html',
    '/offline.html' // Fallback page
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
            .catch((error) => {
                console.error('Failed to open cache:', error);
            })
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                if (response) {
                    return response;
                }
                return fetch(event.request).catch(() => {
                    return caches.match('/offline.html'); // Fallback page
                });
            })
    );
});
