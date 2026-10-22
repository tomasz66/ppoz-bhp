// Działanie offline: najpierw sieć (świeże dane), a bez internetu - kopia z pamięci telefonu.
const CACHE = "ppoz-bhp-v4";
const PLIKI = ["./", "index.html", "style.css", "app.js", "manifest.json",
  "data/akty.json", "data/sciagi.json", "data/pytania.json", "data/obserwowane.json", "data/nowosci.json", "data/aktualnosci.json", "data/ciekawostki.json", "icons/icon-180.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(PLIKI)));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((k) => Promise.all(k.filter((n) => n !== CACHE).map((n) => caches.delete(n)))));
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) {
    return;
  }
  e.respondWith(
    fetch(e.request)
      .then((r) => {
        const kopia = r.clone();
        caches.open(CACHE).then((c) => c.put(e.request, kopia));
        return r;
      })
      .catch(() => caches.match(e.request))
  );
});
