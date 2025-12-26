var staticCacheName = "django-pwa-v1";

var filesToCache = [
    '/static/images/favicon.ico',
    '/static/images/android-chrome-192x192.png', 
    '/static/images/android-chrome-512x512.png',
    '/static/images/apple-touch-icon.png',
];

self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(staticCacheName).then(function (cache) {
      return cache.addAll(filesToCache);
    })
  );
});

self.addEventListener("fetch", function (event) {
  event.respondWith(
    fetch(event.request)
      .then(function (response) {
        return caches.open(staticCacheName).then(function (cache) {
             return response;
        });
      })
      .catch(function () {
        return caches.match(event.request);
      })
  );
});