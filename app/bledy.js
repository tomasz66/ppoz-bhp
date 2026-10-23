// "Znajdź błąd": własne zdjęcia z terenu jako zadania. Do zdjęcia zaznaczasz naruszenia z listy obchodu
// (data/warsztat.json), więc odpowiedź ma od razu zalecenie i paragraf. Tryb ćwiczeń losuje zdjęcie
// i pyta "co tu jest nie tak?". Zdjęcia leżą w IndexedDB telefonu (localStorage jest na nie za mały).

TRASY.push(
  [/^#\/bledy$/, () => widokBledow()],
  [/^#\/bledy\/cwicz$/, () => widokCwiczenia()],
  [/^#\/blad\/(\w+)$/, (m) => widokBledu(m[1])],
);

const BAZA_ZDJEC = { nazwa: "ppoz-bhp", wersja: 1, magazyn: "zdjecia" };
const MAX_BOK_PX = 1280;
const MINIATURA_PX = 320;
const JAKOSC_JPEG = 0.8;
const PROMPT_ZDJECIA = `Jesteś inspektorem ochrony przeciwpożarowej i BHP. Popatrz na zdjęcie i wskaż, które punkty z listy kontrolnej mogą być tu naruszone.
Odpowiedz po polsku, krótko, każdy punkt w osobnej linii w formacie: identyfikator - co widać na zdjęciu.
Wypisz tylko punkty, które naprawdę widać. Jeśli nic nie widać, napisz to wprost. Nie zgaduj tego, czego nie widać.`;

stan.bledy = { cwiczenie: null, odslonieto: false, filtr: "" };

// ── IndexedDB ──

function bazaZdjec() {
  if (!stan.bazaZdjec) {
    stan.bazaZdjec = new Promise((ok, blad) => {
      const r = indexedDB.open(BAZA_ZDJEC.nazwa, BAZA_ZDJEC.wersja);
      r.onupgradeneeded = () => r.result.createObjectStore(BAZA_ZDJEC.magazyn, { keyPath: "id" });
      r.onsuccess = () => ok(r.result);
      r.onerror = () => blad(r.error);
    });
  }
  return stan.bazaZdjec;
}

async function operacjaZdjec(tryb, dzialanie) {
  const db = await bazaZdjec();
  return new Promise((ok, blad) => {
    const r = dzialanie(db.transaction(BAZA_ZDJEC.magazyn, tryb).objectStore(BAZA_ZDJEC.magazyn));
    r.onsuccess = () => ok(r.result);
    r.onerror = () => blad(r.error);
  });
}

const wszystkieZdjecia = () => operacjaZdjec("readonly", (s) => s.getAll());
const jednoZdjecie = (id) => operacjaZdjec("readonly", (s) => s.get(id));
const zapiszZdjecie = (z) => operacjaZdjec("readwrite", (s) => s.put(z));
const usunZdjecieZBazy = (id) => operacjaZdjec("readwrite", (s) => s.delete(id));

// Zmniejsza zdjęcie z aparatu (kilka MB) do rozsądnego JPEG-a.
function zmniejsz(plik, bok) {
  return new Promise((ok, blad) => {
    const img = new Image();
    img.onload = () => {
      const skala = Math.min(1, bok / Math.max(img.width, img.height));
      const c = document.createElement("canvas");
      c.width = Math.round(img.width * skala);
      c.height = Math.round(img.height * skala);
      c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
      URL.revokeObjectURL(img.src);
      ok(c.toDataURL("image/jpeg", JAKOSC_JPEG));
    };
    img.onerror = blad;
    img.src = URL.createObjectURL(plik);
  });
}

async function dodajZdjecie(input) {
  const plik = input.files && input.files[0];
  if (!plik) {
    return;
  }
  pokazKomunikat("Zapisuję zdjęcie…");
  if (navigator.storage && navigator.storage.persist) {
    navigator.storage.persist().catch(() => {});
  }
  const [zdjecie, miniatura] = await Promise.all([zmniejsz(plik, MAX_BOK_PX), zmniejsz(plik, MINIATURA_PX)]);
  const z = { id: Date.now().toString(36), zdjecie, miniatura, punkty: [], notatka: "", data: dzisIso() };
  await zapiszZdjecie(z);
  location.hash = `#/blad/${z.id}`;
}

function wszystkiePunkty() {
  return stan.warsztat.obchod.flatMap((sek) => sek.punkty.map((p) => ({ ...p, sek: sek.tytul, ikona: sek.ikona })));
}

// ── Lista ──

async function widokBledow() {
  ustawNaglowek("Znajdź błąd", "back");
  ustawZakladke("nauka");
  await wczytajWarsztat();
  const zdjecia = (await wszystkieZdjecia()).sort((a, b) => b.id.localeCompare(a.id));
  const gotowe = zdjecia.filter((z) => z.punkty.length);
  widok.innerHTML = `
    <div class="section-header"><div class="section-title">Znajdź błąd</div>
    <div class="section-sub">${tekst("Rób zdjęcia zastawionych gaśnic, zaklinowanych drzwi i bałaganu przy piecach. Zaznacz, co jest nie tak - podstawę prawną aplikacja doda sama. Potem ćwicz na własnych zdjęciach.")}</div></div>
    <label class="btn" style="margin:12px 16px 0;width:auto">📷 Dodaj zdjęcie<input type="file" accept="image/*" hidden onchange="dodajZdjecie(this)"></label>
    ${gotowe.length ? `<div class="btn-row"><a class="btn secondary" href="#/bledy/cwicz">🎯 Ćwicz (${gotowe.length} ${gotowe.length === 1 ? "zdjęcie" : "zdjęć"})</a></div>` : ""}
    ${zdjecia.length ? `<div class="section-label">Moje zdjęcia · ${zdjecia.length}</div>
      <div class="galeria">${zdjecia.map((z) => `<a href="#/blad/${z.id}" class="miniatura"><img src="${z.miniatura}" alt="">
        <span class="${z.punkty.length ? "ok" : ""}">${z.punkty.length ? `${z.punkty.length} błąd/y` : "opisz"}</span></a>`).join("")}</div>`
      : `<div class="empty">${tekst("Nie masz jeszcze zdjęć. Zrób pierwsze - na służbie, w sklepie, w garażu.")}</div>`}
    <div class="foot">${tekst("Zdjęcia zapisują się tylko w tym telefonie. Nie fotografuj ludzi ani tablic rejestracyjnych - wystarczy sam problem.")}</div>`;
}

// ── Opis zdjęcia ──

async function widokBledu(id) {
  ustawNaglowek("Opisz zdjęcie", "#/bledy");
  ustawZakladke("nauka");
  await wczytajWarsztat();
  const z = await jednoZdjecie(id);
  if (!z) {
    location.replace("#/bledy");
    return;
  }
  stan.bledy.id = id;
  const filtr = bezOgonkow(stan.bledy.filtr || "");
  const punkty = wszystkiePunkty().filter((p) => z.punkty.includes(p.id) || !filtr || bezOgonkow(p.co + " " + p.sek).includes(filtr));
  const jestKlucz = !!czytaj(KLUCZ_A.klucz, "");
  widok.innerHTML = `
    <img class="zdjecie" src="${z.zdjecie}" alt="">
    <div class="card"><label class="pole"><span>Co widać (własnymi słowami)</span><textarea oninput="zmienBlad('notatka', this.value)" placeholder="np. gaśnica za kartonami przy kasie">${esc(z.notatka)}</textarea></label></div>
    ${jestKlucz ? `<div class="btn-row"><button class="btn secondary" id="btn-podpowiedz" onclick="podpowiedzAI()">🤖 Podpowiedź AI - co tu może być nie tak?</button></div><div id="podpowiedz"></div>` : ""}
    <div class="section-label">Zaznacz naruszenia · ${z.punkty.length}</div>
    <div class="search-wrap"><div class="search-box"><input class="search-input" placeholder="Filtruj: gaśnica, drzwi, piec…" value="${esc(stan.bledy.filtr || "")}" oninput="stan.bledy.filtr=this.value;filtrujPunkty()"></div></div>
    <div id="punkty-bledu">${punkty.map((p) => wierszPunktu(p, z.punkty.includes(p.id))).join("")}</div>
    <div class="btn-row"><a class="btn" href="#/bledy">Gotowe</a></div>
    <div class="btn-row"><button class="btn secondary" onclick="usunZdjecie('${id}')">Usuń zdjęcie</button></div>`;
}

function wierszPunktu(p, zaznaczony) {
  return `<label class="card punkt-wybor${zaznaczony ? " on" : ""}"><input type="checkbox" ${zaznaczony ? "checked" : ""} onchange="przelaczPunkt('${p.id}', this.checked)">
    <span><span class="punkt-sek">${p.ikona} ${esc(p.sek)}</span>${tekst(p.co)}</span></label>`;
}

async function filtrujPunkty() {
  const z = await jednoZdjecie(stan.bledy.id);
  const filtr = bezOgonkow(stan.bledy.filtr || "");
  document.getElementById("punkty-bledu").innerHTML = wszystkiePunkty()
    .filter((p) => z.punkty.includes(p.id) || !filtr || bezOgonkow(p.co + " " + p.sek).includes(filtr))
    .map((p) => wierszPunktu(p, z.punkty.includes(p.id))).join("");
}

async function zmienBlad(pole, wartosc) {
  const z = await jednoZdjecie(stan.bledy.id);
  z[pole] = wartosc;
  await zapiszZdjecie(z);
}

async function przelaczPunkt(pid, wlacz) {
  const z = await jednoZdjecie(stan.bledy.id);
  z.punkty = wlacz ? [...new Set([...z.punkty, pid])] : z.punkty.filter((x) => x !== pid);
  await zapiszZdjecie(z);
  const etykieta = document.querySelector(`input[onchange*="'${pid}'"]`);
  if (etykieta) {
    etykieta.closest(".punkt-wybor").classList.toggle("on", wlacz);
  }
  document.querySelector(".section-label").textContent = `Zaznacz naruszenia · ${z.punkty.length}`;
}

async function usunZdjecie(id) {
  if (!confirm("Usunąć to zdjęcie z aplikacji?")) {
    return;
  }
  await usunZdjecieZBazy(id);
  location.replace("#/bledy");
}

// AI ogląda zdjęcie i wskazuje możliwe punkty z listy kontrolnej - Ty decydujesz, co zaznaczyć.
async function podpowiedzAI() {
  const b = document.getElementById("btn-podpowiedz");
  const pole = document.getElementById("podpowiedz");
  const z = await jednoZdjecie(stan.bledy.id);
  b.disabled = true;
  pole.innerHTML = `<div class="spinner">AI ogląda zdjęcie…</div>`;
  const lista = wszystkiePunkty().map((p) => `${p.id}: ${p.co}`).join("\n");
  try {
    const odp = await zapytajJednorazowo([
      { type: "image", source: { type: "base64", media_type: "image/jpeg", data: z.zdjecie.split(",")[1] } },
      { type: "text", text: `${PROMPT_ZDJECIA}\n\nLista kontrolna:\n${lista}` },
    ]);
    const ids = wszystkiePunkty().map((p) => p.id).filter((pid) => new RegExp(`(^|\\s)${pid}\\b`, "m").test(odp));
    pole.innerHTML = `<div class="card"><div class="fun-label">🤖 Podpowiedź AI</div><p>${nbsp(esc(odp)).replace(/\n+/g, "<br>")}</p>
      ${ids.length ? `<div class="btn-row" style="margin:12px 0 0"><button class="btn small" onclick="zaznaczSugerowane(${esc(JSON.stringify(ids))})">Zaznacz sugerowane (${ids.length})</button></div>` : ""}
      <p class="pomoc">${tekst("AI może się mylić - zaznacz tylko to, co sam widzisz na zdjęciu.")}</p></div>`;
  } catch (e) {
    pole.innerHTML = `<div class="card amber"><p>${tekst(opisBledu(e))}</p></div>`;
  } finally {
    b.disabled = false;
  }
}

async function zaznaczSugerowane(ids) {
  const z = await jednoZdjecie(stan.bledy.id);
  z.punkty = [...new Set([...z.punkty, ...ids])];
  await zapiszZdjecie(z);
  widokBledu(stan.bledy.id);
}

// ── Ćwiczenie ──

async function widokCwiczenia(nastepne) {
  ustawNaglowek("Co tu jest nie tak?", "#/bledy");
  ustawZakladke("nauka");
  await wczytajWarsztat();
  const gotowe = (await wszystkieZdjecia()).filter((z) => z.punkty.length);
  if (!gotowe.length) {
    location.replace("#/bledy");
    return;
  }
  const b = stan.bledy;
  if (nastepne || !b.cwiczenie || !gotowe.some((z) => z.id === b.cwiczenie)) {
    const inne = gotowe.filter((z) => z.id !== b.cwiczenie);
    b.cwiczenie = (inne.length ? inne : gotowe)[Math.floor(Math.random() * (inne.length || gotowe.length))].id;
    b.odslonieto = false;
  }
  const z = gotowe.find((x) => x.id === b.cwiczenie);
  const punkty = wszystkiePunkty().filter((p) => z.punkty.includes(p.id));
  widok.innerHTML = `
    <img class="zdjecie" src="${z.zdjecie}" alt="">
    <p class="opis-trybu">${tekst(`Znajdź ${punkty.length === 1 ? "naruszenie" : `${punkty.length} naruszenia`} i powiedz na głos, jaki przepis łamią. Potem sprawdź.`)}</p>
    ${b.odslonieto ? `
      ${z.notatka ? `<div class="card"><div class="fun-label">📝 Twoja notatka</div><p>${tekst(z.notatka)}</p></div>` : ""}
      ${punkty.map((p) => `<div class="card punkt uw"><p><b>${tekst(p.co)}</b></p><p class="zal"><b>Zalecenie:</b> ${tekst(p.zal)}</p><div class="links">${zrodloCiekawostki(p.zr)}</div></div>`).join("")}
      <div class="btn-row"><button class="btn" onclick="widokCwiczenia(true)">Następne zdjęcie ›</button></div>`
    : `<div class="btn-row"><button class="btn" onclick="stan.bledy.odslonieto=true;widokCwiczenia()">Pokaż odpowiedź</button></div>`}`;
}
