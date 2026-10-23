// Działanie offline: najpierw sieć (świeże dane), a bez internetu - kopia z pamięci telefonu.
const CACHE = "ppoz-bhp-v13";
const PLIKI = ["./", "index.html", "style.css", "app.js", "warsztat.js", "asystent.js", "pojecia.js", "mapa.js", "bledy.js", "manifest.json",
  "data/akty.json", "data/sciagi.json", "data/pytania.json", "data/obserwowane.json", "data/nowosci.json", "data/aktualnosci.json", "data/ciekawostki.json", "data/warsztat.json", "data/pojecia.json", "data/liczby.json", "icons/icon-180.png"];

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
  // "no-cache": zawsze pytamy serwer, czy plik się zmienił (serwer pozwala trzymać kopię 10 minut,
  // przez co nowa wersja aplikacji pojawiała się z opóźnieniem).
  const swiezy = e.request.method === "GET" ? new Request(e.request.url, { cache: "no-cache" }) : e.request;
  e.respondWith(
    fetch(swiezy)
      .then((r) => {
        const kopia = r.clone();
        caches.open(CACHE).then((c) => c.put(e.request, kopia));
        return r;
      })
      .catch(() => caches.match(e.request))
  );
});
