// PPOŻ BHP - kompendium przepisów i nauka do egzaminu inspektora ppoż.
// Widoki sterowane adresem po "#" (np. #/akt/rozp-ochrona-budynkow/p32), dane z data/*.json.
// Postęp nauki i ustawienia w localStorage telefonu.

const API_SEJM = "https://api.sejm.gov.pl/eli/acts/";
const INTERWALY_DNI = [1, 2, 4, 7, 14, 30, 60, 120];
const PYTAN_W_LEKCJI = 10;
const PYTAN_W_EGZAMINIE = 60;
const PROG_EGZAMINU = 0.7;
const WAZNOSC_SPRAWDZENIA_H = 12;
const LIMIT_ZAPYTANIA_MS = 30000;
const NA_STRONE = 15;
const NAJWAZNIEJSZYCH = 6;
const CIEKAWOSTKA_CO = 3;
const DZIEN_MS = 86400000;
const KLUCZ = { motyw: "bhp-motyw", nauka: "bhp-nauka", zmiany: "bhp-zmiany", tematy: "bhp-tematy", wizyta: "bhp-wizyta-czytnik" };

const stan = { spis: [], dok: {}, artykuly: null, akty: [], aktyMapa: {}, sciagi: [], pytania: [], obserwowane: null, nowosci: [], aktualnosci: { wpisy: [] }, ciekawostki: { przypadki: [], ciekawostki: [] }, sesja: null };
const widok = document.getElementById("widok");

// ── Pomocnicze ──

function czytaj(klucz, domyslna) {
  try {
    const v = localStorage.getItem(klucz);
    return v ? JSON.parse(v) : domyslna;
  } catch (e) {
    return domyslna;
  }
}

function zapisz(klucz, wartosc) {
  try {
    localStorage.setItem(klucz, JSON.stringify(wartosc));
  } catch (e) {
    // Tryb prywatny - postęp zostanie tylko do zamknięcia karty.
  }
}

function esc(s) {
  return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

// Twarda spacja po jednoliterowych spójnikach, żeby nie zostawały na końcu wiersza.
function nbsp(s) {
  return s.replace(/(^|[\s(„])([aiouwzAIOUWZ])\s/g, "$1$2 ");
}

function tekst(s) {
  return nbsp(esc(s));
}

function bezOgonkow(s) {
  return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/ł/g, "l");
}

function data(iso) {
  if (!iso) {
    return "";
  }
  const [r, m, d] = iso.split("-");
  return `${d}.${m}.${r}`;
}

function kafel(napis, kolor) {
  const emotka = /\p{Extended_Pictographic}/u.test(napis) ? " big" : "";
  return `<span class="row-icon${emotka}" style="background-color:${kolor}">${esc(napis)}</span>`;
}

// Link do prawdziwego źródła (ISAP, PDF, strona wydawcy) - otwiera się poza aplikacją.
function linkISAP(url, etykieta = "Oryginał w ISAP") {
  return `<a class="chip red" href="${url}" target="_blank" rel="noopener">${etykieta} ↗</a>`;
}

// Akt prawny z adresu ISAP otwieramy w czytniku aplikacji, jeśli mamy jego tekst.
const ROK_NOWYCH_ISAP = 2012;
const W_APLIKACJI = {
  "DU/1991/351": "ustawa-ppoz", "DU/2025/188": "ustawa-ppoz",
  "DU/2010/719": "rozp-ochrona-budynkow", "DU/2023/822": "rozp-ochrona-budynkow",
  "DU/2009/1030": "rozp-woda-drogi",
};

function eliZIsap(url) {
  const m = String(url).match(/WDU(\d{4})(\d{7})/);
  if (!m) {
    return null;
  }
  const rok = Number(m[1]);
  return `DU/${rok}/${rok < ROK_NOWYCH_ISAP ? Number(m[2].slice(3)) : Number(m[2])}`;
}

function adresDokumentu(url) {
  const eli = eliZIsap(url);
  if (eli && W_APLIKACJI[eli]) {
    return `#/akt/${W_APLIKACJI[eli]}`;
  }
  if (eli && stan.spis.includes(eli)) {
    return `#/dok/${eli.replaceAll("/", "_")}`;
  }
  return null;
}

function linkDok(url, etykieta) {
  const wew = adresDokumentu(url);
  return wew ? `<a class="chip red" href="${wew}">${esc(etykieta)} ›</a>` : linkISAP(url, esc(etykieta));
}

function chipZrodla(zr) {
  const akt = stan.aktyMapa[zr.a];
  const j = akt && akt.jednostki.find((x) => x.id === zr.j);
  if (!j) {
    return "";
  }
  const u = zr.u && zr.u !== "uwaga" ? " " + zr.u : "";
  return `<a class="chip" href="#/akt/${zr.a}/${zr.j}">${esc(j.etykieta + u)} · ${esc(akt.skrot)}</a> ${linkISAP(akt.tekst.isap, "ISAP")}`;
}

// ── Nawigacja ──

function ustawNaglowek(tytul, wstecz) {
  document.getElementById("nav-title").textContent = tytul;
  const b = document.getElementById("btn-back");
  b.hidden = !wstecz;
  b.onclick = () => (wstecz === "back" && history.length > 1 ? history.back() : (location.hash = wstecz === "back" ? "#/start" : wstecz));
}

function ustawZakladke(nazwa) {
  document.querySelectorAll(".tab-item").forEach((t) => t.classList.toggle("active", t.dataset.tab === nazwa));
}

const TRASY = [
  [/^#\/przepisy$/, () => widokPrzepisy()],
  [/^#\/akt\/([\w-]+)$/, (m) => widokAkt(m[1])],
  [/^#\/akt\/([\w-]+)\/(\w+)$/, (m) => widokJednostka(m[1], m[2])],
  [/^#\/szukaj$/, () => widokSzukaj()],
  [/^#\/sciagi$/, () => widokSciagi()],
  [/^#\/sciaga\/([\w-]+)$/, (m) => widokSciaga(m[1])],
  [/^#\/nauka$/, () => widokNauka()],
  [/^#\/lekcja$/, () => widokPytanie()],
  [/^#\/egzamin$/, () => widokPytanie()],
  [/^#\/wynik$/, () => widokWynik()],
  [/^#\/(zmiany|nowosci)$/, () => widokZmiany()],
  [/^#\/(czywiesz|luz)$/, () => widokCzyWiesz()],
  [/^#\/news\/(\w+)$/, (m) => widokNews(m[1])],
  [/^#\/dok\/(\w+)$/, (m) => widokDok(m[1])],
  [/^#\/dok\/(\w+)\/(\w+)$/, (m) => widokDokJednostka(m[1], m[2])],
  [/^#\/czytnik$/, () => {
    // "Nowe" = opublikowane po poprzednim wejściu do czytnika.
    stan.poprzedniaWizyta = czytaj(KLUCZ.wizyta, 0);
    zapisz(KLUCZ.wizyta, Date.now());
    widokCzytnik();
  }],
];

function trasa() {
  const h = location.hash || "#/start";
  window.scrollTo(0, 0);
  for (const [wzor, fn] of TRASY) {
    const m = h.match(wzor);
    if (m) {
      fn(m);
      return;
    }
  }
  widokStart();
}

// ── Start ──

function widokStart() {
  ustawNaglowek("PPOŻ BHP");
  ustawZakladke("start");
  const n = statystykiNauki();
  const nowe = noweZmiany();
  const jednostek = stan.akty.reduce((s, a) => s + a.jednostki.length, 0);
  widok.innerHTML = `
    <div class="section-header">
      <div class="section-title">PPOŻ BHP</div>
      <div class="section-sub">${tekst("Przepisy, ściągi i nauka do egzaminu inspektora ochrony przeciwpożarowej. Każdy przepis z linkiem do oryginału.")}</div>
    </div>
    ${poleSzukania("")}
    <div class="list-group"><a class="row" href="#/asystent">${kafel("🎙", "#5e35b1")}<span class="row-main"><span class="row-title">Asystent - zapytaj lub przepytaj mnie</span><span class="row-sub">${tekst("Objaśnienia z paragrafów, lektor i mikrofon")}</span></span><span class="row-chev">›</span></a></div>
    ${kartaAktualnosci()}
    ${nowe.length ? `<div class="section-label">Uwaga</div><a class="card alert" style="display:block" href="#/nowosci"><h3>${nowe.length} ${nowe.length === 1 ? "nowa zmiana" : "nowe zmiany"} w prawie</h3><p>${tekst("Sejm opublikował zmianę w akcie, który obserwujesz. Dotknij, żeby zobaczyć.")}</p></a>` : ""}
    <div class="section-label">Nauka</div>
    <div class="tiles">
      <a class="tile" href="#/nauka"><div class="tile-num">${n.doPowtorki}</div><div class="tile-label">do powtórki dziś</div></a>
      <a class="tile" href="#/nauka"><div class="tile-num">${n.opanowane}/${stan.pytania.length}</div><div class="tile-label">pytań opanowanych</div></a>
    </div>
    <div class="btn-row"><button class="btn" onclick="startLekcji()">Lekcja - ${PYTAN_W_LEKCJI} pytań</button></div>
    <div class="section-label">Warsztat</div>
    <div class="list-group">
      <a class="row" href="#/obchod/nowy">${kafel("🔍", "#c0392b")}<span class="row-main"><span class="row-title">Obchód obiektu</span><span class="row-sub">${tekst("Lista kontrolna ppoż i BHP → zalecenia z paragrafami")}</span></span><span class="row-chev">›</span></a>
      <a class="row" href="#/warsztat">${kafel("📄", "#2f5d8a")}<span class="row-main"><span class="row-title">Wzory dokumentów i zapisane obchody</span><span class="row-sub">${tekst("IBP, wypadek przy pracy, ocena ryzyka")}</span></span><span class="row-chev">›</span></a>
    </div>
    <div class="section-label">Czy wiesz, że… · dziś</div>
    ${kartaCiekawostki(ciekawostkaDnia())}
    <div class="list-group"><a class="row" href="#/czywiesz">${kafel("💡", "#e8a200")}<span class="row-main"><span class="row-title">Czy wiesz, że…</span><span class="row-sub">${wszystkieCiekawostki().length} sytuacji z życia z podstawą prawną</span></span><span class="row-chev">›</span></a></div>
    ${najblizszeTerminy()}
    <div class="section-label">Z branży</div>
    <div class="list-group">${najwazniejsze(3).map(wierszAktualnosci).join("")}
      <a class="row" href="#/czytnik">${kafel("NEWS", "#2f5d8a")}<span class="row-main"><span class="row-title">Więcej wiadomości</span><span class="row-sub">${nowychOdWizyty()} nowych od ostatniego czytania · dziś, wczoraj, cały tydzień</span></span><span class="row-chev">›</span></a></div>
    <div class="section-label">Na skróty</div>
    <div class="list-group">
      ${stan.sciagi.slice(0, 4).map((s) => wierszSciagi(s)).join("")}
      <a class="row" href="#/sciagi">${kafel("WSZ", "#3a3a3c")}<span class="row-main"><span class="row-title">Wszystkie ściągi</span></span><span class="row-chev">›</span></a>
    </div>
    <div class="foot">${tekst(`W aplikacji: ${stan.akty.length} akty ppoż (${jednostek} artykułów i paragrafów). Stan prawny na ${data(stan.stanNa)}. Teksty z oficjalnej bazy Sejmu (ISAP). Aplikacja nie zastępuje oryginału - w razie wątpliwości otwórz link do ISAP.`)}</div>`;
  podepnijSzukanie();
}

// "Czy wiesz, że…": przypadki z życia (sytuacja + co mówi prawo) i ciekawostki - każdy z podstawą prawną.
function wszystkieCiekawostki() {
  return stan.ciekawostki.przypadki.concat(stan.ciekawostki.ciekawostki);
}

function ciekawostkaDnia() {
  const lista = wszystkieCiekawostki();
  return lista[Math.floor(Date.now() / DZIEN_MS) % lista.length];
}

function losowaPrzerwa() {
  const lista = wszystkieCiekawostki();
  return lista[Math.floor(Math.random() * lista.length)];
}

function zrodloCiekawostki(zr) {
  if (zr.dok) {
    const o = stan.obserwowane.akty.find((x) => x.eli === zr.dok.replace(/^DU_(\d+)_(\d+)$/, "DU/$1/$2"));
    const nazwa = o ? o.nazwa : zr.dok.replace(/^DU_(\d+)_(\d+)$/, "Dz.U. $1 poz. $2");
    return `<a class="chip red" href="#/dok/${zr.dok}/${zr.j}">${esc(zr.u ? zr.u + " · " : "")}${esc(nazwa)} ›</a>`;
  }
  if (zr.url) {
    return linkZrodla({ url: zr.url, opis: zr.opis });
  }
  return chipZrodla(zr);
}

function kartaCiekawostki(c, slowa) {
  const pod = (t) => (slowa ? podswietl(t, slowa) : tekst(t));
  return `<div class="card fun">
    ${c.s ? `<div class="fun-label">💡 Sytuacja</div><p class="case-s">${pod(c.s)}</p><div class="fun-label" style="margin-top:10px">⚖️ Co mówi prawo</div>` : `<div class="fun-label">💡 Czy wiesz, że…</div>`}
    <p>${pod(c.t)}</p><div class="links">${zrodloCiekawostki(c.zr)}</div></div>`;
}

function widokCzyWiesz() {
  ustawNaglowek("Czy wiesz, że…");
  ustawZakladke("czywiesz");
  const d = stan.filtrCzyWiesz || "all";
  const lista = wszystkieCiekawostki().filter((c) => d === "all" || c.d === d);
  widok.innerHTML = `
    <div class="section-header"><div class="section-title">Czy wiesz, że…</div>
    <div class="section-sub">${tekst(`Sytuacje z życia firm i domów przełożone na przepisy - ${wszystkieCiekawostki().length} przypadków, każdy z podstawą prawną. Przydadzą się w rozmowie z klientem.`)}</div></div>
    <div class="seg">${[["all", "Wszystko"], ["bhp", "BHP"], ["ppoz", "PPOŻ"]].map(([k, n]) => `<button class="${d === k ? "on" : ""}" onclick="stan.filtrCzyWiesz='${k}';widokCzyWiesz()">${n}</button>`).join("")}</div>
    <div class="section-label">${lista.length} pozycji</div>
    ${lista.map((c) => kartaCiekawostki(c)).join("")}
    <div class="foot">${tekst("Każdy przypadek jest sprawdzony z brzmieniem przepisu. Dotknij źródła, żeby przeczytać cały artykuł lub paragraf.")}</div>`;
}

function najblizszeTerminy() {
  const terminy = [];
  for (const n of stan.nowosci) {
    if (dniDo(n.od) > 0) {
      terminy.push({ data: n.od, opis: "wchodzi w życie", n });
    }
    if (n.termin && dniDo(n.termin.data) > 0) {
      terminy.push({ data: n.termin.data, opis: n.termin.opis, n });
    }
  }
  terminy.sort((a, b) => a.data.localeCompare(b.data));
  if (!terminy.length) {
    return "";
  }
  return `<div class="section-label">Najbliższe terminy</div><div class="list-group">${terminy.slice(0, 3).map((t) => `
    <a class="row" href="#/nowosci">${kafel(String(dniDo(t.data)) + "\ndni", t.n.dziedzina === "bhp" ? "#2f5d8a" : "#c0392b")}
    <span class="row-main"><span class="row-title small">${tekst(t.n.tytul)}</span><span class="row-sub">${tekst(t.opis)} · ${data(t.data)}</span></span><span class="row-chev">›</span></a>`).join("")}</div>`;
}

function poleSzukania(wartosc) {
  return `<div class="search-wrap"><label class="search-box big">
    <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
    <input class="search-input" id="szukaj" type="search" placeholder="Szukaj: smoła, gałęzie, gaśnica…" value="${esc(wartosc)}" autocomplete="off" enterkeyhint="search">
  </label></div>`;
}

// Na Start wpisanie pierwszej litery przenosi do pełnego wyszukiwania (wyniki na żywo).
function podepnijSzukanie() {
  const pole = document.getElementById("szukaj");
  pole.addEventListener("input", () => {
    sessionStorage.setItem("bhp-q", pole.value);
    location.hash = "#/szukaj";
  });
  pole.addEventListener("focus", wczytajWszystkieDok, { once: true });
}

// ── Wyszukiwarka "wszystko naraz": przypadki, ściągi, przepisy ppoż i BHP, nowości, pytania, wiadomości ──
// Bez polskich znaków i odmiany: "smola" znajdzie "smoły", "galezie" - "gałęzi", "gasnica" - "gaśnic".

const MIN_RDZEN = 4;
const KONCOWKA = 3;
const NA_GRUPE = 6;
const STOP = new Set(["i", "w", "z", "na", "do", "o", "a", "oraz", "czy", "jak", "sie", "to", "od", "po", "za", "dla", "przy", "co", "nie", "jest", "sa"]);
// Słowa, które w przepisach występują pod inną nazwą.
const SYNONIMY = {
  galez: ["galez", "chrust", "pozostalosci roslin"], galaz: ["galez", "chrust", "pozostalosci roslin"], chrus: ["chrust", "galez"],
  czad: ["czad", "tlenku wegla"], dym: ["dym"], upal: ["upal", "niewyzsza niz 35", "przekroczy 28"], goraco: ["upal", "niewyzsza niz 35", "przekroczy 28"],
  komputer: ["komputer", "monitor"], monito: ["monitor", "komputer"], kask: ["kask", "helm"], okular: ["okular", "szkla kontaktowe"],
  butl: ["butl"], grill: ["grill", "butl"], komin: ["komin", "przewod"], wypadek: ["wypad"], ploty: ["plot", "granicy dzialki"],
  plot: ["plot", "ploc", "ogrodz", "granicy dzialki"], ploc: ["plot", "ploc", "ogrodz", "granicy dzialki"], sasiad: ["sasiad", "granicy dzialki"], ogrodz: ["ogrodz", "granicy dzialki", "plot"], drabin: ["drabin"],
  probn: ["probn", "praktyczne sprawdzenie"], cwicze: ["cwicze", "praktyczne sprawdzenie"],
  pijan: ["nietrzezw", "alkohol"], alkohol: ["alkohol", "nietrzezw"], l4: ["zwolnien", "niezdolnosci do pracy"],
};

function rdzen(w) {
  return w.length <= MIN_RDZEN ? w : w.slice(0, Math.max(MIN_RDZEN, w.length - KONCOWKA));
}

function warianty(slowo) {
  const r = rdzen(slowo);
  const klucz = Object.keys(SYNONIMY).find((k) => r.startsWith(k) || k.startsWith(r));
  return klucz ? [r, ...SYNONIMY[klucz]] : [r];
}

async function wczytajWszystkieDok() {
  if (stan.wszystkieDok) {
    return stan.wszystkieDok;
  }
  stan.wszystkieDok = Promise.all(stan.spis.map((eli) => wczytajDok(eli.replaceAll("/", "_")).catch(() => null)));
  return stan.wszystkieDok;
}

function indeks() {
  // Każdy element: grupa, tekst do przeszukania, HTML wyniku (funkcja) i waga grupy.
  const el = [];
  for (const c of wszystkieCiekawostki()) {
    el.push({ g: "case", txt: (c.s || "") + " " + c.t + " " + (c.tagi || []).join(" "), c });
  }
  for (const s of stan.sciagi) {
    for (const w of s.wiersze) {
      el.push({ g: "sciaga", txt: s.tytul + " " + w[0] + " " + w[1], s, w });
    }
  }
  for (const a of stan.akty) {
    for (const j of a.jednostki) {
      j.linie.forEach((l, i) => el.push({ g: "ppoz", txt: l.t, a, j, i }));
    }
  }
  for (const d of stan.dokZaladowane || []) {
    if (!d) {
      continue;
    }
    const grupa = d.rola === "akt" ? "bhp" : "zmiany";
    for (const j of d.jednostki) {
      j.linie.forEach((l, i) => el.push({ g: grupa, txt: l.t, d, j, i }));
    }
  }
  for (const n of stan.nowosci) {
    el.push({ g: "nowosci", txt: n.tytul + " " + n.co.join(" ") + " " + n.szansa, n });
  }
  for (const q of stan.pytania) {
    el.push({ g: "pytania", txt: q.q + " " + q.odp[q.ok], q });
  }
  for (const w of stan.aktualnosci.wpisy) {
    if (w.d !== "luz") {
      el.push({ g: "news", txt: w.t + " " + (w.lead || ""), w });
    }
  }
  for (const e of el) {
    e.norm = bezOgonkow(e.txt);
  }
  return el;
}

const GRUPY_SZUKANIA = [
  ["case", "💡 Czy wiesz, że… - przypadki z życia"],
  ["sciaga", "☰ Ściągi"],
  ["ppoz", "§ Przepisy ppoż"],
  ["bhp", "§ Przepisy BHP i warunki techniczne"],
  ["nowosci", "✦ Nowości w prawie"],
  ["zmiany", "§ Akty zmieniające"],
  ["pytania", "✎ Pytania do nauki"],
  ["news", "📰 Wiadomości z branży"],
];

function wynikSzukania(e, slowa) {
  if (e.g === "case") {
    return kartaCiekawostki(e.c, slowa);
  }
  if (e.g === "sciaga") {
    return `<div class="card"><div class="cheat-k">${esc(e.s.tytul)} · ${podswietl(e.w[0], slowa)}</div><div class="cheat-v">${podswietl(e.w[1], slowa)}</div><div class="cheat-src">${chipZrodla(e.w[2])}</div></div>`;
  }
  if (e.g === "ppoz") {
    return `<a class="row" href="#/akt/${e.a.id}/${e.j.id}" onclick="sessionStorage.setItem('bhp-hit','${e.i}')"><span class="row-main">
      <span class="row-title small">${esc(e.j.etykieta)} · ${esc(e.a.skrot)}</span><span class="row-sub">${podswietl(wycinek(e.txt, slowa), slowa)}</span></span><span class="row-chev">›</span></a>`;
  }
  if (e.g === "bhp" || e.g === "zmiany") {
    const plik = e.d.eli.replaceAll("/", "_");
    return `<a class="row" href="#/dok/${plik}/${e.j.id}" onclick="sessionStorage.setItem('bhp-hit','${e.i}')"><span class="row-main">
      <span class="row-title small">${esc(e.j.etykieta)} · ${esc(nazwaDok(e.d))}</span><span class="row-sub">${podswietl(wycinek(e.txt, slowa), slowa)}</span></span><span class="row-chev">›</span></a>`;
  }
  if (e.g === "nowosci") {
    return `<a class="row" href="#/nowosci"><span class="row-main"><span class="row-title small">${podswietl(e.n.tytul, slowa)}</span>
      <span class="row-sub">${podswietl(wycinek(e.n.co.join(" "), slowa), slowa)}</span></span><span class="row-chev">›</span></a>`;
  }
  if (e.g === "pytania") {
    return `<div class="card"><p><b>${podswietl(e.q.q, slowa)}</b></p><p>Odpowiedź: ${podswietl(e.q.odp[e.q.ok], slowa)}</p><div class="links">${chipZrodla(e.q.zr)}</div></div>`;
  }
  return wierszAktualnosci(e.w);
}

function widokSzukaj() {
  const q = sessionStorage.getItem("bhp-q") || "";
  ustawNaglowek("Szukaj wszędzie", "#/start");
  ustawZakladke("start");
  widok.innerHTML = `${poleSzukania(q)}<div id="wyniki"></div>`;
  const pole = document.getElementById("szukaj");
  let czasomierz;
  const pokaz = () => {
    sessionStorage.setItem("bhp-q", pole.value);
    clearTimeout(czasomierz);
    czasomierz = setTimeout(() => (document.getElementById("wyniki").innerHTML = wynikiSzukania(pole.value)), 120);
  };
  pole.addEventListener("input", pokaz);
  pole.focus();
  pole.setSelectionRange(pole.value.length, pole.value.length);
  document.getElementById("wyniki").innerHTML = wynikiSzukania(q);
  // Akty BHP (duże pliki) dociągamy w tle; gdy dojdą, odświeżamy wyniki.
  if (!stan.dokZaladowane) {
    wczytajWszystkieDok().then((lista) => {
      stan.dokZaladowane = lista;
      stan.indeks = null;
      if (location.hash === "#/szukaj") {
        document.getElementById("wyniki").innerHTML = wynikiSzukania(pole.value);
      }
    });
  }
}

function wynikiSzukania(q) {
  const slowa = bezOgonkow(q).split(/[\s,.;]+/).filter((s) => s.length > 1 && !STOP.has(s));
  if (!slowa.length) {
    return `<div class="empty">${tekst("Wpisz, czego szukasz - np. smoła, gałęzie przy płocie, gaśnica, drabina, upał, badania. Przeszukam przypadki, ściągi, przepisy ppoż i BHP, nowości, pytania i wiadomości.")}</div>`;
  }
  stan.indeks = stan.indeks || indeks();
  const grupySlow = slowa.map(warianty);
  const pasujace = [];
  for (const e of stan.indeks) {
    let pkt = 0;
    let wszystkie = true;
    for (const war of grupySlow) {
      const ile = war.reduce((s, w) => s + (e.norm.split(w).length - 1), 0);
      if (!ile) {
        wszystkie = false;
        break;
      }
      pkt += Math.min(ile, 3);
    }
    if (wszystkie) {
      pasujace.push({ e, pkt });
    }
  }
  const podswietlane = grupySlow.flat();
  const ladowanie = !stan.dokZaladowane ? `<div class="spinner">Doczytuję przepisy BHP…</div>` : "";
  if (!pasujace.length) {
    return `${ladowanie}<div class="empty">${tekst("Nic nie znaleziono. Spróbuj krótszego słowa albo innego określenia.")}</div>`;
  }
  return ladowanie + GRUPY_SZUKANIA.map(([g, nazwa]) => {
    const lista = pasujace.filter((x) => x.e.g === g).sort((a, b) => b.pkt - a.pkt);
    if (!lista.length) {
      return "";
    }
    const limit = (stan.limitySzukania || {})[g] || NA_GRUPE;
    const lista2 = lista.slice(0, limit).map((x) => wynikSzukania(x.e, podswietlane)).join("");
    const kontener = ["case", "sciaga", "pytania"].includes(g) ? lista2 : `<div class="list-group">${lista2}</div>`;
    return `<div class="section-label">${nazwa} · ${lista.length}</div>${kontener}
      ${lista.length > limit ? `<div class="btn-row"><button class="btn secondary" onclick="pokazWiecej('${g}')">Pokaż więcej (${lista.length - limit})</button></div>` : ""}`;
  }).join("");
}

function pokazWiecej(g) {
  stan.limitySzukania = stan.limitySzukania || {};
  stan.limitySzukania[g] = ((stan.limitySzukania[g]) || NA_GRUPE) + 10;
  document.getElementById("wyniki").innerHTML = wynikiSzukania(document.getElementById("szukaj").value);
}

function wycinek(t, slowa) {
  const norm = bezOgonkow(t);
  const lista = Array.isArray(slowa) ? slowa.flatMap(warianty) : [slowa];
  const i = Math.max(0, Math.min(...lista.map((s) => norm.indexOf(s)).filter((x) => x >= 0).concat([0])));
  const od = Math.max(0, i - 60);
  return (od > 0 ? "…" : "") + t.slice(od, od + 220) + (t.length > od + 220 ? "…" : "");
}

// Podświetla wszystkie wystąpienia szukanych rdzeni (bez względu na polskie znaki).
function podswietl(t, slowa) {
  const zrodlo = nbsp(String(t));
  const norm = bezOgonkow(zrodlo);
  const znaczniki = new Array(zrodlo.length).fill(false);
  for (const s of slowa.flatMap((x) => (x.length > 1 ? [x] : []))) {
    let i = norm.indexOf(s);
    while (i >= 0) {
      for (let k = i; k < i + s.length; k++) {
        znaczniki[k] = true;
      }
      i = norm.indexOf(s, i + s.length);
    }
  }
  let wynik = "";
  let otwarty = false;
  for (let k = 0; k < zrodlo.length; k++) {
    if (znaczniki[k] && !otwarty) {
      wynik += "<mark>";
      otwarty = true;
    }
    if (!znaczniki[k] && otwarty) {
      wynik += "</mark>";
      otwarty = false;
    }
    wynik += esc(zrodlo[k]);
  }
  return wynik + (otwarty ? "</mark>" : "");
}

// ── Przepisy ──

function widokPrzepisy() {
  ustawNaglowek("Przepisy");
  ustawZakladke("przepisy");
  const bhp = stan.obserwowane ? stan.obserwowane.akty.filter((o) => o.dziedzina === "bhp") : [];
  const wt = stan.obserwowane && stan.obserwowane.akty.find((o) => o.eli === "DU/2002/690");
  widok.innerHTML = `
    <div class="section-header"><div class="section-title">Przepisy</div>
    <div class="section-sub">${tekst("Pełny tekst aktów z naniesionymi zmianami. Zmienione fragmenty mają żółty pasek.")}</div></div>
    ${poleSzukania("")}
    <div class="section-label">Ochrona przeciwpożarowa</div>
    <div class="list-group">${stan.akty.filter((a) => a.dziedzina === "ppoz").map((a) => `
      <a class="row" href="#/akt/${a.id}">${kafel(a.kafel, a.kolor)}<span class="row-main">
      <span class="row-title">${esc(a.skrot)}</span><span class="row-sub">${tekst(a.nazwa)}</span></span><span class="row-chev">›</span></a>`).join("")}
      ${wt ? `<a class="row" href="${adresDokumentu(wt.isap) || wt.isap}">${kafel("WT", "#b25000")}<span class="row-main">
      <span class="row-title">Warunki techniczne (WT 2002)</span><span class="row-sub">${tekst("Uchylone od 20.09.2026, nowych nie ogłoszono. Okres przejściowy - zobacz zakładkę Nowości.")}</span></span><span class="row-chev">›</span></a>` : ""}
    </div>
    <div class="section-label">Bezpieczeństwo i higiena pracy</div>
    <div class="list-group">${bhp.map((o) => `
      <a class="row" href="${adresDokumentu(o.isap) || o.isap}">${kafel("BHP", "#2f5d8a")}<span class="row-main">
      <span class="row-title">${esc(o.nazwa)}</span><span class="row-sub">${tekst(o.tytul)}</span></span><span class="row-chev">›</span></a>`).join("")}
    </div>
    <div class="foot">${tekst("Akty BHP: aktualny tekst jednolity z bazy Sejmu. Zmiany ogłoszone po tekście jednolitym są wypisane na górze każdego aktu.")}</div>`;
  podepnijSzukanie();
}

function widokAkt(id) {
  const a = stan.aktyMapa[id];
  if (!a) {
    return widokPrzepisy();
  }
  ustawNaglowek(a.skrot, "#/przepisy");
  ustawZakladke("przepisy");
  const rozdzialy = [];
  for (const j of a.jednostki) {
    let r = rozdzialy[rozdzialy.length - 1];
    if (!r || r.nazwa !== j.rozdzial) {
      r = { nazwa: j.rozdzial, jedn: [] };
      rozdzialy.push(r);
    }
    r.jedn.push(j);
  }
  widok.innerHTML = `
    <div class="section-header"><div class="section-sub" style="color:var(--text)">${tekst(a.nazwa)}</div></div>
    <div class="card info">
      <p><b>Podstawa tekstu:</b> ${tekst(a.tekst.opis)}${a.zmiany.length ? `, z naniesionymi zmianami: ${a.zmiany.map((z) => `<a href="${adresDokumentu(z.isap) || z.isap}">${esc(z.opis)}</a> (od ${data(z.od)})`).join(", ")}` : ""}.</p>
      ${a.pominiete ? `<p>${tekst(a.pominiete)}</p>` : ""}
    </div>
    ${rozdzialy.map((r) => `
      <div class="section-label">${esc(r.nazwa || "Przepisy")}</div>
      <div class="list-group">${r.jedn.map((j) => `
        <a class="row" href="#/akt/${a.id}/${j.id}"><span class="row-main"><span class="row-title">${esc(j.etykieta)}${j.zm ? ' <span class="zm-tag">zmieniony</span>' : ""}</span>
        <span class="row-sub">${tekst(j.linie[0] ? j.linie[0].t.slice(0, 110) : "")}…</span></span><span class="row-chev">›</span></a>`).join("")}
      </div>`).join("")}
    ${kartaZrodla("Dziennik Ustaw / ISAP", "stan prawny na " + data(stan.stanNa), `<p class="url">${tekst(a.tekst.opis)}</p>
      <div class="links">${linkISAP(a.isap, "Akt w ISAP")} ${linkISAP(a.tekst.isap, "Tekst jednolity w ISAP")} ${linkISAP(a.tekst.pdf, "PDF")}</div>`)}`;
}

function widokJednostka(aktId, jId) {
  const a = stan.aktyMapa[aktId];
  const idx = a ? a.jednostki.findIndex((j) => j.id === jId) : -1;
  if (idx < 0) {
    return widokPrzepisy();
  }
  const j = a.jednostki[idx];
  const hit = sessionStorage.getItem("bhp-hit");
  sessionStorage.removeItem("bhp-hit");
  ustawNaglowek(`${j.etykieta} · ${a.skrot}`, `#/akt/${a.id}`);
  ustawZakladke("przepisy");
  const poprz = a.jednostki[idx - 1];
  const nast = a.jednostki[idx + 1];
  widok.innerHTML = `
    <div class="unit-head"><div class="unit-label">${esc(j.etykieta)}</div>
    <div class="unit-chapter">${esc(j.rozdzial)}</div><div class="unit-act">${tekst(a.nazwa)}</div></div>
    <div class="law">${j.linie.map((l, i) => `<p id="l${i}" class="l${l.p}${l.zm ? " zm" : ""}${String(i) === hit ? " hit" : ""}">${tekst(l.t)}${l.zm ? ` <span class="zm-tag">${esc(l.zm)}</span>` : ""}</p>`).join("")}</div>
    ${j.uwaga ? `<div class="card amber"><p>${tekst(j.uwaga)}</p></div>` : ""}
    ${j.zm ? `<div class="card info"><p>${tekst("Ten przepis był zmieniany po ogłoszeniu tekstu jednolitego. Zmiany naniesione dosłownie z:")}</p><div class="links">${j.zm.map((z) => linkDok(z.isap, z.opis)).join(" ")}</div></div>` : ""}
    <div class="pager">
      ${poprz ? `<a class="btn secondary" href="#/akt/${a.id}/${poprz.id}">‹ ${esc(poprz.etykieta)}</a>` : "<span style='flex:1'></span>"}
      ${nast ? `<a class="btn secondary" href="#/akt/${a.id}/${nast.id}">${esc(nast.etykieta)} ›</a>` : "<span style='flex:1'></span>"}
    </div>
    ${kartaZrodla("Dziennik Ustaw / ISAP", "stan prawny na " + data(stan.stanNa), `<p class="url">${tekst(a.nazwa)}</p>
      <div class="links">${linkISAP(a.tekst.isap, "Oryginał w ISAP")} ${linkISAP(a.tekst.pdf, "PDF")}</div>`)}`;
  if (hit) {
    const el = document.getElementById("l" + hit);
    if (el) {
      el.scrollIntoView({ block: "center" });
    }
  }
}

// ── Ściągi ──

function wierszSciagi(s) {
  return `<a class="row" href="#/sciaga/${s.id}">${kafel(s.skrot, s.kolor)}<span class="row-main"><span class="row-title">${esc(s.tytul)}</span>
    <span class="row-sub">${s.wiersze.length} pozycji ze źródłami</span></span><span class="row-chev">›</span></a>`;
}

function widokSciagi() {
  ustawNaglowek("Ściągi");
  ustawZakladke("sciagi");
  widok.innerHTML = `
    <div class="section-header"><div class="section-title">Ściągi</div>
    <div class="section-sub">${tekst("Liczby i terminy do szybkiego sprawdzenia w terenie. Przy każdej pozycji jest paragraf i link do oryginału.")}</div></div>
    <div class="list-group" style="margin-top:12px">${stan.sciagi.map(wierszSciagi).join("")}</div>`;
}

function widokSciaga(id) {
  const s = stan.sciagi.find((x) => x.id === id);
  if (!s) {
    return widokSciagi();
  }
  ustawNaglowek(s.tytul, "#/sciagi");
  ustawZakladke("sciagi");
  widok.innerHTML = `
    <div class="section-header"><div class="section-title">${esc(s.tytul)}</div></div>
    <div class="cheat" style="margin-top:12px">${s.wiersze.map(([k, v, zr]) => `
      <div class="cheat-row"><div class="cheat-k">${tekst(k)}</div><div class="cheat-v">${tekst(v)}</div><div class="cheat-src">${chipZrodla(zr)}</div></div>`).join("")}
    </div>
    <div class="foot">${tekst("Ściąga to skrót. Wiążące jest brzmienie przepisu - dotknij paragrafu, żeby je przeczytać.")}</div>`;
}

// ── Nauka (powtórki 1/2/4/7/14/30/60/120 dni + egzamin próbny) ──

function postep() {
  return czytaj(KLUCZ.nauka, { pytania: {}, egzaminy: [] });
}

function statystykiNauki() {
  const p = postep();
  const teraz = Date.now();
  let doPowtorki = 0;
  let opanowane = 0;
  for (const q of stan.pytania) {
    const s = p.pytania[q.id];
    if (s && s.due <= teraz) {
      doPowtorki++;
    }
    if (s && s.box >= 3) {
      opanowane++;
    }
  }
  const nowe = stan.pytania.filter((q) => !p.pytania[q.id]).length;
  return { doPowtorki, opanowane, nowe, egzaminy: p.egzaminy };
}

function widokNauka() {
  ustawNaglowek("Nauka");
  ustawZakladke("nauka");
  const n = statystykiNauki();
  const ostatni = n.egzaminy[n.egzaminy.length - 1];
  widok.innerHTML = `
    <div class="section-header"><div class="section-title">Nauka</div>
    <div class="section-sub">${tekst("Pytania z przepisów ppoż. Po każdej odpowiedzi widzisz paragraf, z którego pochodzi.")}</div></div>
    <div class="tiles" style="margin-top:12px">
      <div class="tile"><div class="tile-num">${n.doPowtorki}</div><div class="tile-label">do powtórki</div></div>
      <div class="tile"><div class="tile-num">${n.nowe}</div><div class="tile-label">nowych pytań</div></div>
      <div class="tile"><div class="tile-num">${n.opanowane}</div><div class="tile-label">opanowanych</div></div>
      <div class="tile"><div class="tile-num">${ostatni ? Math.round(ostatni.wynik * 100) + "%" : "-"}</div><div class="tile-label">ostatni egzamin</div></div>
    </div>
    <div class="btn-row"><button class="btn" onclick="startLekcji()">Lekcja - ${PYTAN_W_LEKCJI} pytań</button></div>
    <div class="btn-row"><button class="btn secondary" onclick="startEgzaminu()">Egzamin próbny</button></div>
    <div class="card info"><p>${tekst(`Egzamin próbny: ${Math.min(PYTAN_W_EGZAMINIE, stan.pytania.length)} pytań w losowej kolejności, wynik na końcu, próg zaliczenia ${PROG_EGZAMINU * 100}% - jak na prawdziwym egzaminie (60 pytań, 70%).`)}</p>
    <p>${tekst(`Pytania ułożyłem sam z treści przepisów - to nie jest oficjalna pula egzaminacyjna, której nie publikuje się. Pula ma teraz ${stan.pytania.length} pytań i będzie rosła.`)}</p></div>
    ${n.egzaminy.length ? `<div class="section-label">Historia egzaminów</div><div class="list-group">${n.egzaminy.slice(-5).reverse().map((e) => `
      <div class="row"><span class="row-main"><span class="row-title">${Math.round(e.wynik * 100)}% (${e.dobre}/${e.razem})</span><span class="row-sub">${new Date(e.kiedy).toLocaleDateString("pl-PL")}</span></span>
      <span class="row-tag ${e.wynik >= PROG_EGZAMINU ? "ok" : ""}">${e.wynik >= PROG_EGZAMINU ? "zdany" : "niezdany"}</span></div>`).join("")}</div>` : ""}
    <div class="btn-row"><button class="btn secondary" onclick="resetNauki()">Zacznij naukę od nowa</button></div>`;
}

function losuj(t) {
  const a = t.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function startLekcji() {
  const p = postep();
  const teraz = Date.now();
  const doPowtorki = losuj(stan.pytania.filter((q) => p.pytania[q.id] && p.pytania[q.id].due <= teraz));
  const nowe = stan.pytania.filter((q) => !p.pytania[q.id]);
  let lista = doPowtorki.concat(nowe).slice(0, PYTAN_W_LEKCJI);
  if (!lista.length) {
    // Wszystko powtórzone - lekcja z pytań, których termin wypada najwcześniej.
    lista = stan.pytania.slice().sort((x, y) => p.pytania[x.id].due - p.pytania[y.id].due).slice(0, PYTAN_W_LEKCJI);
  }
  stan.sesja = { tryb: "lekcja", lista, i: 0, odp: [] };
  location.hash = "#/lekcja";
}

function startEgzaminu() {
  stan.sesja = { tryb: "egzamin", lista: losuj(stan.pytania).slice(0, PYTAN_W_EGZAMINIE), i: 0, odp: [] };
  location.hash = "#/egzamin";
}

function resetNauki() {
  if (confirm("Usunąć cały postęp nauki i historię egzaminów?")) {
    zapisz(KLUCZ.nauka, { pytania: {}, egzaminy: [] });
    widokNauka();
  }
}

function widokPytanie() {
  const s = stan.sesja;
  if (!s) {
    location.hash = "#/nauka";
    return;
  }
  const q = s.lista[s.i];
  ustawNaglowek(s.tryb === "egzamin" ? "Egzamin próbny" : "Lekcja", "#/nauka");
  ustawZakladke("nauka");
  // Odpowiedzi tasujemy przy każdym pokazaniu, żeby nie uczyć się pozycji ("zawsze B").
  const kolejnosc = losuj(q.odp.map((_, i) => i));
  s.kolejnosc = kolejnosc;
  widok.innerHTML = `
    <div class="progress"><div style="width:${(s.i / s.lista.length) * 100}%"></div></div>
    <div class="q-meta">Pytanie ${s.i + 1} z ${s.lista.length}</div>
    <div class="q-text">${tekst(q.q)}</div>
    <div class="answers">${kolejnosc.map((k) => `<button class="answer" data-k="${k}" onclick="odpowiedz(${k})">${tekst(q.odp[k])}</button>`).join("")}</div>
    <div id="feedback"></div>`;
}

function odpowiedz(k) {
  const s = stan.sesja;
  const q = s.lista[s.i];
  const dobrze = k === q.ok;
  s.odp.push({ id: q.id, k, dobrze });
  document.querySelectorAll(".answer").forEach((b) => {
    b.disabled = true;
    const bk = Number(b.dataset.k);
    if (s.tryb === "egzamin") {
      b.classList.toggle("picked", bk === k);
    } else if (bk === q.ok) {
      b.classList.add("good");
    } else if (bk === k) {
      b.classList.add("bad");
    }
  });
  const ostatnie = s.i + 1 >= s.lista.length;
  const dalej = `<div class="btn-row"><button class="btn" onclick="nastepne()">${ostatnie ? "Wynik" : "Dalej"}</button></div>`;
  if (s.tryb === "egzamin") {
    document.getElementById("feedback").innerHTML = dalej;
    return;
  }
  zapiszPowtorke(q.id, dobrze);
  s.dobrych = (s.dobrych || 0) + (dobrze ? 1 : 0);
  const przerwa = dobrze && s.dobrych % CIEKAWOSTKA_CO === 0 ? kartaCiekawostki(losowaPrzerwa()) : "";
  document.getElementById("feedback").innerHTML = `
    <div class="card ${dobrze ? "info" : "alert"} feedback"><h3>${dobrze ? "Dobrze" : "Poprawna odpowiedź: " + tekst(q.odp[q.ok])}</h3>
    <div class="links">${chipZrodla(q.zr)}</div></div>${przerwa}${dalej}`;
}

function zapiszPowtorke(id, dobrze) {
  const p = postep();
  const s = p.pytania[id] || { box: 0, due: 0 };
  s.box = dobrze ? Math.min(s.box + 1, INTERWALY_DNI.length - 1) : 0;
  s.due = Date.now() + (dobrze ? INTERWALY_DNI[s.box] * DZIEN_MS : 0);
  p.pytania[id] = s;
  zapisz(KLUCZ.nauka, p);
}

function nastepne() {
  const s = stan.sesja;
  s.i++;
  if (s.i >= s.lista.length) {
    location.hash = "#/wynik";
    return;
  }
  widokPytanie();
  window.scrollTo(0, 0);
}

function widokWynik() {
  const s = stan.sesja;
  if (!s) {
    location.hash = "#/nauka";
    return;
  }
  ustawNaglowek("Wynik", "#/nauka");
  ustawZakladke("nauka");
  const dobre = s.odp.filter((o) => o.dobrze).length;
  const wynik = dobre / s.lista.length;
  if (s.tryb === "egzamin" && !s.zapisany) {
    const p = postep();
    p.egzaminy.push({ kiedy: Date.now(), dobre, razem: s.lista.length, wynik });
    zapisz(KLUCZ.nauka, p);
    s.zapisany = true;
  }
  const bledy = s.odp.filter((o) => !o.dobrze).map((o) => stan.pytania.find((q) => q.id === o.id));
  const zdany = wynik >= PROG_EGZAMINU;
  widok.innerHTML = `
    <div class="result-big">${Math.round(wynik * 100)}%</div>
    <div class="result-sub ${zdany ? "pass" : "fail"}">${dobre} z ${s.lista.length} · ${s.tryb === "egzamin" ? (zdany ? "egzamin zdany" : "poniżej progu 70%") : "lekcja skończona"}</div>
    ${bledy.length ? `<div class="section-label">Do poprawy</div>${bledy.map((q) => `
      <div class="card"><p><b>${tekst(q.q)}</b></p><p>Poprawnie: ${tekst(q.odp[q.ok])}</p><div class="links">${chipZrodla(q.zr)}</div></div>`).join("")}` : ""}
    <div class="btn-row"><button class="btn" onclick="${s.tryb === "egzamin" ? "startEgzaminu()" : "startLekcji()"}">Jeszcze raz</button></div>
    <div class="btn-row"><a class="btn secondary" href="#/nauka">Wróć do nauki</a></div>`;
}

// ── Zmiany w prawie (porównanie z API Sejmu) ──

function noweZmiany() {
  const z = czytaj(KLUCZ.zmiany, null);
  return z ? z.nowe : [];
}

async function pobierzJson(url) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), LIMIT_ZAPYTANIA_MS);
  try {
    return await (await fetch(url, { signal: ctrl.signal })).json();
  } finally {
    clearTimeout(t);
  }
}

// API Sejmu bywa wolne (kilka sekund na akt), więc trwa tylko jedno sprawdzanie naraz.
function sprawdzZmiany(wymus) {
  const zapis = czytaj(KLUCZ.zmiany, null);
  if (!wymus && zapis && Date.now() - zapis.kiedy < WAZNOSC_SPRAWDZENIA_H * 3600000) {
    return Promise.resolve(zapis);
  }
  if (!stan.sprawdzanie) {
    stan.sprawdzanie = wykonajSprawdzenie().finally(() => (stan.sprawdzanie = null));
  }
  return stan.sprawdzanie;
}

async function wykonajSprawdzenie() {
  stan.sprawdzono = 0;
  const nowe = [];
  let bledy = 0;
  // Wszystkie akty sprawdzamy równolegle - 13 zapytań naraz zamiast po kolei.
  await Promise.all(stan.obserwowane.akty.map(async (o) => {
    try {
      const d = await pobierzJson(API_SEJM + o.eli);
      const zmieniajace = (d.references && d.references["Akty zmieniające"]) || [];
      for (const z of zmieniajace) {
        if (!o.znane.includes(z.id)) {
          const m = await pobierzJson(API_SEJM + z.id);
          nowe.push({ akt: o.nazwa, eli: z.id, od: z.date, tytul: m.title, isap: "https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=" + m.address });
        }
      }
      if (d.status !== o.status) {
        nowe.push({ akt: o.nazwa, eli: o.eli, od: null, tytul: `Zmiana statusu aktu: „${o.status}” → „${d.status}”`, isap: o.isap });
      }
    } catch (e) {
      bledy++;
    }
    stan.sprawdzono++;
    const el = document.getElementById("postep-zmian");
    if (el) {
      el.textContent = `Sprawdzam bazę Sejmu… ${stan.sprawdzono}/${stan.obserwowane.akty.length}`;
    }
  }));
  const wynik = { kiedy: Date.now(), nowe, bledy };
  if (bledy < stan.obserwowane.akty.length) {
    zapisz(KLUCZ.zmiany, wynik);
  }
  odswiezZnaczek();
  return wynik;
}

function odswiezZnaczek() {
  const n = noweZmiany().length;
  const b = document.getElementById("badge-nowosci");
  b.hidden = !n;
  b.textContent = n;
}

// ── Nowości: zmiany w prawie (opisane po ludzku) + aktualności z branży ──

function dniDo(iso) {
  return Math.round((new Date(iso + "T00:00:00") - new Date(dzisIso() + "T00:00:00")) / DZIEN_MS);
}

function znacznikDaty(iso) {
  const n = dniDo(iso);
  if (n > 0) {
    return `<span class="row-tag wait">za ${n} ${n === 1 ? "dzień" : "dni"} · ${data(iso)}</span>`;
  }
  return `<span class="row-tag ok">obowiązuje od ${data(iso)}</span>`;
}

function etykietaDziedziny(d) {
  return `<span class="row-tag ${d === "bhp" ? "blue" : ""}">${d === "bhp" ? "BHP" : "PPOŻ"}</span>`;
}

function linkZrodla(z) {
  const url = z.url.startsWith("#") ? z.url : adresDokumentu(z.url) || z.url;
  const zewn = !url.startsWith("#");
  return `<a class="chip ${zewn ? "" : "red"}" href="${url}"${zewn ? ' target="_blank" rel="noopener"' : ""}>${esc(z.opis)}${zewn ? " ↗" : " ›"}</a>`;
}

function kartaNowosci(n) {
  const termin = n.termin && dniDo(n.termin.data) > 0
    ? `<p class="deadline">⏳ ${tekst(`${n.termin.opis}: do ${data(n.termin.data)} (zostało ${dniDo(n.termin.data)} dni)`)}</p>` : "";
  return `<div class="card news" data-d="${n.dziedzina}">
    <div class="news-tags">${etykietaDziedziny(n.dziedzina)} ${znacznikDaty(n.od)}</div>
    <h3>${tekst(n.tytul)}</h3>${termin}
    <ul>${n.co.map((c) => `<li>${tekst(c)}</li>`).join("")}</ul>
    <div class="szansa"><b>Szansa dla Ciebie:</b> ${tekst(n.szansa)}</div>
    <div class="links">${n.zrodla.map(linkZrodla).join(" ")}</div></div>`;
}

function wierszAktualnosci(w) {
  return `<a class="row news-row" data-d="${w.d}" href="#/news/${w.id}">
    <span class="row-main"><span class="row-title small">${tekst(w.t)}</span>
    ${w.lead ? `<span class="row-sub lead2">${tekst(w.lead)}</span>` : ""}
    <span class="row-sub">${esc(w.z)} · ${kiedyWpis(w)} · ${w.d === "bhp" ? "BHP" : "PPOŻ"}</span></span><span class="row-chev">›</span></a>`;
}

// ── Czytnik w aplikacji: wiadomość = streszczenie, tekst, źródło na dole ──

async function wczytajArtykuly() {
  if (!stan.artykuly) {
    stan.artykuly = await (await fetch("data/artykuly.json")).json();
  }
  return stan.artykuly;
}

function kartaZrodla(nazwa, kiedy, linki) {
  return `<div class="section-label">Źródło</div>
    <div class="card source"><p><b>${esc(nazwa)}</b>${kiedy ? " · " + esc(kiedy) : ""}</p>${linki}</div>`;
}

async function widokNews(id) {
  const w = stan.aktualnosci.wpisy.find((x) => x.id === id);
  ustawNaglowek(w ? w.z : "Wiadomość", "back");
  ustawZakladke(w && w.d === "luz" ? "luz" : "nowosci");
  if (!w) {
    widok.innerHTML = `<div class="empty">${tekst("Tej wiadomości już nie ma w przeglądzie - przeglądamy ostatnie 2 tygodnie.")}</div>`;
    return;
  }
  widok.innerHTML = `<div class="spinner">Wczytuję…</div>`;
  const a = (await wczytajArtykuly())[id] || { skrot: [], tekst: [] };
  const punkty = a.skrot.length ? a.skrot : w.lead ? [w.lead] : [];
  const urzedowy = a.tekst.length > 0;
  const domena = new URL(w.url).hostname.replace(/^www\./, "");
  widok.innerHTML = `
    <article class="reader">
      <div class="post-meta">${esc(w.z)} · ${kiedyWpis(w)} ${w.d === "luz" ? "" : etykietaDziedziny(w.d)}</div>
      <h1 class="reader-title">${tekst(w.t)}</h1>
      <div class="post-foot" style="margin-top:0">${(w.tematy || []).map((t) => `<span class="tag">${esc(t)}</span>`).join("")}</div>
    </article>
    ${punkty.length ? `<div class="card summary"><div class="fun-label">⚡ W skrócie</div><ul>${punkty.map((p) => `<li>${tekst(p)}</li>`).join("")}</ul>
      <p class="note">${tekst("Najważniejsze zdania wybrane automatycznie z artykułu.")}</p></div>` : ""}
    ${urzedowy
      ? `<div class="reader-body">${a.tekst.map((p) => `<p>${tekst(p)}</p>`).join("")}</div>`
      : `${w.lead && !a.skrot.length ? "" : w.lead ? `<div class="reader-body"><p>${tekst(w.lead)}</p></div>` : ""}
         <div class="card info"><p>${tekst("Pełny tekst jest na stronie wydawcy. Artykuły z mediów chroni prawo autorskie, dlatego w aplikacji jest streszczenie, a całość otwierasz u źródła.")}</p></div>`}
    ${kartaZrodla(w.z, w.czas ? new Date(w.czas).toLocaleDateString("pl-PL") : "", `<p class="url">${esc(domena)}</p>
      <a class="btn" href="${esc(w.url)}" target="_blank" rel="noopener">Otwórz u źródła ↗</a>`)}`;
}

// ── Czytnik aktów prawnych: w skrócie, treść, źródło na dole ──

const DUZY_AKT_JEDNOSTEK = 12;

async function wczytajDok(plik) {
  if (!stan.dok[plik]) {
    stan.dok[plik] = await (await fetch(`data/dok/${plik}.json`)).json();
  }
  return stan.dok[plik];
}

function nazwaDok(d) {
  const o = stan.obserwowane.akty.find((x) => x.eli === d.eli);
  if (o) {
    return o.nazwa;
  }
  const [, rok, poz] = d.eli.split("/");
  return `Dz.U. ${rok} poz. ${poz}`;
}

function skrotDok(d) {
  if (d.streszczenie.length) {
    return d.streszczenie.map((x) => `<li>${tekst(x)}</li>`).join("");
  }
  const pkt = [];
  if (d.rola === "akt") {
    pkt.push(`Tekst: ${d.tekst.eli === d.eli ? "tekst ogłoszony" : "tekst jednolity " + d.tekst.eli.replace("DU/", "Dz.U. ").replace(/\/(\d+)$/, " poz. $1")}.`);
    pkt.push(`${d.jednostki.length} ${d.jednostki[0] && d.jednostki[0].etykieta.startsWith("Art") ? "artykułów" : "paragrafów"} do przeczytania w aplikacji.`);
  } else {
    pkt.push(`Ogłoszono ${data(d.ogloszono)}, ${d.wchodzi && d.wchodzi > dzisIso() ? "wejdzie w życie" : "obowiązuje od"} ${data(d.wchodzi)}.`);
  }
  if (d.status) {
    pkt.push(`Status w bazie Sejmu: ${d.status}.`);
  }
  return pkt.map((x) => `<li>${tekst(x)}</li>`).join("");
}

function tekstJednostki(j, hit) {
  return `<div class="law">${j.linie.map((l, i) => `<p id="l${i}" class="l${l.p}${String(i) === hit ? " hit" : ""}">${tekst(l.t)}</p>`).join("")}</div>${j.uwaga ? `<div class="card amber"><p>${tekst(j.uwaga)}</p></div>` : ""}`;
}

function zrodloDok(d) {
  return kartaZrodla("Dziennik Ustaw / ISAP", d.ogloszono ? "ogłoszono " + data(d.ogloszono) : "", `
    <p class="url">${tekst(d.tekst.tytul)}</p>
    <div class="links">${linkISAP(d.isap, "Akt w ISAP")} ${d.tekst.eli !== d.eli ? linkISAP(d.tekst.isap, "Tekst jednolity w ISAP") : ""} ${linkISAP(d.pdf, "PDF")}</div>`);
}

async function widokDok(plik) {
  ustawNaglowek("Przepis", "back");
  ustawZakladke("przepisy");
  widok.innerHTML = `<div class="spinner">Wczytuję tekst aktu…</div>`;
  const d = await wczytajDok(plik);
  ustawNaglowek(nazwaDok(d), "back");
  const maly = d.jednostki.length <= DUZY_AKT_JEDNOSTEK;
  const zmianyPo = d.zmiany_po.length ? `<div class="card amber"><p><b>${tekst("Zmiany ogłoszone po tym tekście - jeszcze nie są w nim uwzględnione:")}</b></p>
    <div class="links">${d.zmiany_po.map((z) => linkDok(z.isap, z.eli.replace("DU/", "Dz.U. ").replace(/\/(\d+)$/, " poz. $1") + (z.od ? " (" + data(z.od) + ")" : ""))).join(" ")}</div></div>` : "";
  const rozdzialy = [];
  for (const j of d.jednostki) {
    let r = rozdzialy[rozdzialy.length - 1];
    if (!r || r.nazwa !== j.rozdzial) {
      r = { nazwa: j.rozdzial, jedn: [] };
      rozdzialy.push(r);
    }
    r.jedn.push(j);
  }
  widok.innerHTML = `
    <div class="section-header"><div class="section-title" style="font-size:22px">${esc(nazwaDok(d))}</div>
    <div class="section-sub" style="color:var(--text)">${tekst(d.tytul)}</div></div>
    <div class="card summary"><div class="fun-label">⚡ W skrócie</div><ul>${skrotDok(d)}</ul></div>
    ${zmianyPo}
    ${maly
      ? d.jednostki.map((j) => `<div class="unit-head" style="padding-top:8px"><div class="unit-label" style="font-size:24px">${esc(j.etykieta)}</div></div>${tekstJednostki(j)}`).join("")
      : `<div class="search-wrap"><label class="search-box"><input class="search-input" id="szukaj-dok" type="search" placeholder="Szukaj w tym akcie, np. mobbing" autocomplete="off"></label></div>
         <div id="lista-dok">${rozdzialy.map((r) => `
           <div class="section-label">${esc(r.nazwa || "Przepisy")}</div>
           <div class="list-group">${r.jedn.map((j) => `
             <a class="row" data-q="${esc(bezOgonkow(j.linie.map((l) => l.t).join(" ")))}" href="#/dok/${plik}/${j.id}"><span class="row-main"><span class="row-title small">${esc(j.etykieta)}</span>
             <span class="row-sub">${tekst((j.linie[0] ? j.linie[0].t : "").slice(0, 120))}…</span></span><span class="row-chev">›</span></a>`).join("")}</div>`).join("")}</div>`}
    ${zrodloDok(d)}`;
  const pole = document.getElementById("szukaj-dok");
  if (pole) {
    pole.addEventListener("input", () => {
      const q = bezOgonkow(pole.value.trim());
      document.querySelectorAll("#lista-dok .row").forEach((r) => (r.hidden = q.length > 1 && !r.dataset.q.includes(q)));
      document.querySelectorAll("#lista-dok .list-group").forEach((g) => {
        const widoczne = [...g.children].some((r) => !r.hidden);
        g.hidden = !widoczne;
        g.previousElementSibling.hidden = !widoczne;
      });
    });
  }
}

async function widokDokJednostka(plik, id) {
  ustawZakladke("przepisy");
  const d = await wczytajDok(plik);
  const idx = d.jednostki.findIndex((j) => j.id === id);
  if (idx < 0) {
    return widokDok(plik);
  }
  const j = d.jednostki[idx];
  const hit = sessionStorage.getItem("bhp-hit");
  sessionStorage.removeItem("bhp-hit");
  ustawNaglowek(`${j.etykieta} · ${nazwaDok(d)}`, "back");
  const poprz = d.jednostki[idx - 1];
  const nast = d.jednostki[idx + 1];
  widok.innerHTML = `
    <div class="unit-head"><div class="unit-label">${esc(j.etykieta)}</div>
    <div class="unit-chapter">${esc(j.rozdzial || "")}</div><div class="unit-act">${tekst(d.tytul)}</div></div>
    ${tekstJednostki(j, hit)}
    <div class="pager">
      ${poprz ? `<a class="btn secondary" href="#/dok/${plik}/${poprz.id}">‹ ${esc(poprz.etykieta)}</a>` : "<span style='flex:1'></span>"}
      ${nast ? `<a class="btn secondary" href="#/dok/${plik}/${nast.id}">${esc(nast.etykieta)} ›</a>` : "<span style='flex:1'></span>"}
    </div>
    ${zrodloDok(d)}`;
  if (hit) {
    const el = document.getElementById("l" + hit);
    if (el) {
      el.scrollIntoView({ block: "center" });
    }
  }
}

// ── Czytnik: własny RSS - dziś, wczoraj, przedwczoraj, reszta tygodnia + najważniejsze ──

function dniTemu(w) {
  if (!w.czas) {
    return 99;
  }
  const d = new Date(w.czas);
  const lok = new Date(d.getFullYear(), d.getMonth(), d.getDate());
  const dzis = new Date(new Date().getFullYear(), new Date().getMonth(), new Date().getDate());
  return Math.round((dzis - lok) / DZIEN_MS);
}

function kiedyWpis(w) {
  if (!w.czas) {
    return "bez daty";
  }
  const n = dniTemu(w);
  const godz = new Date(w.czas).toLocaleTimeString("pl-PL", { hour: "2-digit", minute: "2-digit" });
  if (n === 0) {
    return "dziś " + godz;
  }
  if (n === 1) {
    return "wczoraj " + godz;
  }
  return `${n} dni temu`;
}

function wybraneTematy() {
  return czytaj(KLUCZ.tematy, []);
}

function pasuje(w) {
  const t = wybraneTematy();
  const d = stan.filtrCzytnika || "all";
  return w.d !== "luz" && (d === "all" || w.d === d) && (!t.length || (w.tematy || []).some((x) => t.includes(x)));
}

function najwazniejsze(ile) {
  return stan.aktualnosci.wpisy
    .filter((w) => dniTemu(w) <= 7 && pasuje(w))
    .sort((a, b) => b.pkt - a.pkt || (b.czas || "").localeCompare(a.czas || ""))
    .slice(0, ile);
}

function nowychOdWizyty() {
  const ostatnia = czytaj(KLUCZ.wizyta, 0);
  return stan.aktualnosci.wpisy.filter((w) => w.d !== "luz" && w.czas && Date.parse(w.czas) > ostatnia).length;
}

function kartaWpisu(w, ostatnia) {
  const nowy = w.czas && Date.parse(w.czas) > ostatnia;
  return `<article class="card post">
    <div class="post-meta">${nowy ? '<span class="dot"></span>' : ""}${esc(w.z)} · ${kiedyWpis(w)} ${etykietaDziedziny(w.d)}</div>
    <a class="post-link" href="#/news/${w.id}"><h3>${tekst(w.t)}</h3>
    ${w.lead ? `<p class="post-lead">${tekst(w.lead)}</p>` : ""}</a>
    <div class="post-foot">${(w.tematy || []).map((t) => `<span class="tag">${esc(t)}</span>`).join("")}
    <a class="chip red" href="#/news/${w.id}">Czytaj ›</a></div></article>`;
}

const GRUPY = [
  ["Dziś", (n) => n === 0],
  ["Wczoraj", (n) => n === 1],
  ["Przedwczoraj", (n) => n === 2],
  ["Wcześniej w tym tygodniu", (n) => n >= 3 && n <= 6],
  ["Tydzień temu i dawniej", (n) => n >= 7],
];

function widokCzytnik() {
  ustawNaglowek("Wiadomości", "#/start");
  ustawZakladke("nowosci");
  const ostatnia = stan.poprzedniaWizyta || 0;
  stan.limity = stan.limity || {};
  const wpisy = stan.aktualnosci.wpisy.filter(pasuje);
  const wszystkieTematy = [...new Set(stan.aktualnosci.wpisy.filter((w) => w.d !== "luz").flatMap((w) => w.tematy || []))];
  const wybrane = wybraneTematy();
  const top = najwazniejsze(NAJWAZNIEJSZYCH);
  widok.innerHTML = `
    <div class="section-header"><div class="section-title">Wiadomości</div>
    <div class="section-sub">${tekst(`Twój przegląd BHP i ppoż z ${stan.aktualnosci.wpisy.filter((w) => w.d !== "luz").length} artykułów z ostatnich 2 tygodni. Dotknij wiadomości, żeby przeczytać ją w aplikacji.`)}</div></div>
    <div class="seg">${[["all", "Wszystko"], ["bhp", "BHP"], ["ppoz", "PPOŻ"]].map(([k, n]) => `<button class="${(stan.filtrCzytnika || "all") === k ? "on" : ""}" onclick="stan.filtrCzytnika='${k}';widokCzytnik()">${n}</button>`).join("")}</div>
    <div class="section-label">Moje tematy ${wybrane.length ? `<button class="link-btn" onclick="zapisz(KLUCZ.tematy, []);widokCzytnik()">wyczyść</button>` : ""}</div>
    <div class="tags-pick">${wszystkieTematy.map((t) => `<button class="tag ${wybrane.includes(t) ? "on" : ""}" onclick="przelaczTemat('${esc(t)}')">${esc(t)}</button>`).join("")}</div>
    ${top.length ? `<div class="section-label">⭐ Najważniejsze z tygodnia</div>${top.map((w) => kartaWpisu(w, ostatnia)).join("")}` : ""}
    ${GRUPY.map(([nazwa, warunek]) => {
      const lista = wpisy.filter((w) => warunek(dniTemu(w)) && !top.includes(w));
      if (!lista.length) {
        return "";
      }
      const limit = stan.limity[nazwa] || NA_STRONE;
      return `<div class="section-label">${nazwa} · ${lista.length}</div>${lista.slice(0, limit).map((w) => kartaWpisu(w, ostatnia)).join("")}
        ${lista.length > limit ? `<div class="btn-row"><button class="btn secondary" onclick="stan.limity['${nazwa}']=${limit + NA_STRONE};widokCzytnik()">Pokaż więcej (${lista.length - limit})</button></div>` : ""}`;
    }).join("")}
    ${!wpisy.length ? `<div class="empty">${tekst("Brak wiadomości dla wybranych tematów. Wyczyść filtr tematów.")}</div>` : ""}
    <div class="foot">${tekst(`Pobrano ${stan.aktualnosci.pobrano}. Źródła: strazacki.pl, Przegląd Pożarniczy i Google News (gov.pl, PIP, portale prawne i lokalne). Ważność liczona automatycznie z tematów - to podpowiedź, nie ocena prawnika.`)}</div>`;
}

function przelaczTemat(t) {
  const w = wybraneTematy();
  zapisz(KLUCZ.tematy, w.includes(t) ? w.filter((x) => x !== t) : w.concat(t));
  widokCzytnik();
}

function filtrujNowosci(d) {
  stan.filtr = d;
  document.querySelectorAll(".seg button").forEach((b) => b.classList.toggle("on", b.dataset.f === d));
  document.querySelectorAll("[data-d]").forEach((el) => (el.hidden = d !== "all" && el.dataset.d !== d));
}

async function widokZmiany(wymus) {
  ustawNaglowek("Nowości");
  ustawZakladke("nowosci");
  const nowosci = stan.nowosci.slice().sort((a, b) => b.od.localeCompare(a.od));
  const branza = stan.aktualnosci.wpisy.filter((w) => w.d !== "luz");
  widok.innerHTML = `
    <div class="section-header"><div class="section-title">Nowości</div>
    <div class="section-sub">${tekst("Zmiany w przepisach opisane po ludzku, terminy i wiadomości z branży BHP i ppoż.")}</div></div>
    <div class="seg"><button data-f="all" onclick="filtrujNowosci('all')">Wszystko</button><button data-f="bhp" onclick="filtrujNowosci('bhp')">BHP</button><button data-f="ppoz" onclick="filtrujNowosci('ppoz')">PPOŻ</button></div>
    <div id="nowe"><div class="spinner" id="postep-zmian">Sprawdzam bazę Sejmu…</div></div>
    <div class="section-label">Najważniejsze zmiany w prawie</div>
    ${nowosci.map(kartaNowosci).join("")}
    <div class="section-label">Z branży - najważniejsze z tygodnia</div>
    <div class="list-group">${najwazniejsze(5).map(wierszAktualnosci).join("")}
      <a class="row" href="#/czytnik">${kafel("NEWS", "#2f5d8a")}<span class="row-main"><span class="row-title">Czytaj wszystkie wiadomości</span><span class="row-sub">${branza.length} wpisów z ostatnich 2 tygodni</span></span><span class="row-chev">›</span></a></div>
    <div class="foot">${tekst(`Wiadomości z: strazacki.pl, Przegląd Pożarniczy, Google News (gov.pl, PIP, portale prawne). Pobrano ${stan.aktualnosci.pobrano}. To linki do cudzych artykułów - przepis zawsze sprawdzaj w ISAP.`)}</div>
    <div class="section-label">Wszystkie zmiany obserwowanych aktów</div>
    ${stan.obserwowane.akty.filter((o) => o.ostatnie.length).map((o) => `
      <div class="card" data-d="${o.dziedzina}"><h3>${esc(o.nazwa)} ${etykietaDziedziny(o.dziedzina)}</h3>
      ${o.ostatnie.map((z) => `<p><b>${z.od && z.od > dzisIso() ? "wejdzie w życie " : "od "}${data(z.od)}</b> - ${adresDokumentu(z.isap) ? `<a href="${adresDokumentu(z.isap)}">${tekst(z.tytul)} ›</a>` : `<a href="${z.isap}" target="_blank" rel="noopener">${tekst(z.tytul)} ↗</a>`}</p>`).join("")}</div>`).join("")}
    <div class="btn-row"><button class="btn secondary" onclick="widokZmiany(true)">Sprawdź bazę Sejmu teraz</button></div>
    <div class="foot">Lista bazowa aktów pobrana ${data(stan.obserwowane.pobrano)}. Źródło: api.sejm.gov.pl (ELI).</div>`;
  filtrujNowosci(stan.filtr || "all");
  const wynik = await sprawdzZmiany(wymus);
  const el = document.getElementById("nowe");
  if (!el) {
    return;
  }
  const kiedy = new Date(wynik.kiedy).toLocaleString("pl-PL", { dateStyle: "short", timeStyle: "short" });
  if (wynik.nowe.length) {
    el.innerHTML = `<div class="section-label">Nowe od ${data(stan.obserwowane.pobrano)}</div>${wynik.nowe.map((z) => `
      <div class="card alert"><h3>${esc(z.akt)}</h3><p>${tekst(z.tytul)}${z.od ? ` - od ${data(z.od)}` : ""}</p><div class="links">${linkISAP(z.isap, "Zobacz w ISAP")}</div></div>`).join("")}
      <div class="foot">Sprawdzono ${kiedy}. Teksty w aplikacji jeszcze nie uwzględniają tych zmian.</div>`;
  } else if (wynik.bledy >= stan.obserwowane.akty.length) {
    el.innerHTML = `<div class="card info"><p>${tekst("Nie udało się połączyć z bazą Sejmu. Sprawdź internet i dotknij „Sprawdź teraz”.")}</p></div>`;
  } else {
    el.innerHTML = `<div class="card info"><p>✓ ${tekst(`Brak nowych zmian. Sprawdzono ${kiedy}.`)}</p></div>`;
  }
}

function dzisIso() {
  return new Date().toISOString().slice(0, 10);
}

// ── Start aplikacji ──

function ustawMotyw(m) {
  document.documentElement.dataset.theme = m;
  document.getElementById("btn-theme").textContent = m === "dark" ? "☀" : "☾";
  document.querySelector('meta[name="theme-color"]').content = m === "dark" ? "#000000" : "#ffffff";
}

async function init() {
  ustawMotyw(czytaj(KLUCZ.motyw, "light"));
  document.getElementById("btn-theme").onclick = () => {
    const m = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    zapisz(KLUCZ.motyw, m);
    ustawMotyw(m);
  };
  document.querySelectorAll(".tab-item").forEach((t) => (t.onclick = () => (location.hash = "#/" + t.dataset.tab)));

  document.getElementById("btn-refresh").onclick = odswiezWszystko;
  await wczytajDane(false);

  window.addEventListener("hashchange", trasa);
  trasa();
  const poOdswiezeniu = sessionStorage.getItem(KOMUNIKAT_PO_ODSWIEZENIU);
  if (poOdswiezeniu) {
    sessionStorage.removeItem(KOMUNIKAT_PO_ODSWIEZENIU);
    pokazKomunikat(poOdswiezeniu);
  }
  odswiezZnaczek();
  sprawdzZmiany(false).then(() => {
    if ((location.hash || "#/start") === "#/start") {
      widokStart();
    }
  });

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("sw.js").catch(() => {});
  }
}

// Wczytuje dane aplikacji; "swieze" omija pamięć telefonu i pobiera najnowszą wersję z serwera.
async function wczytajDane(swieze) {
  const dopisek = swieze ? `?t=${Date.now()}` : "";
  const opcje = swieze ? { cache: "no-store" } : {};
  const [akty, sciagi, pytania, obserwowane, nowosci, aktualnosci, ciekawostki, spis] = await Promise.all(
    ["akty", "sciagi", "pytania", "obserwowane", "nowosci", "aktualnosci", "ciekawostki", "dok/spis"].map((n) => fetch(`data/${n}.json${dopisek}`, opcje).then((r) => r.json()))
  );
  stan.nowosci = nowosci;
  stan.spis = spis;
  stan.aktualnosci = aktualnosci;
  stan.ciekawostki = ciekawostki;
  stan.akty = akty.akty;
  stan.stanNa = akty.stanNa;
  stan.sciagi = sciagi;
  stan.pytania = pytania;
  stan.obserwowane = obserwowane;
  stan.aktyMapa = {};
  stan.akty.forEach((a) => (stan.aktyMapa[a.id] = a));
}

const KOMUNIKAT_PO_ODSWIEZENIU = "bhp-komunikat";

// Przycisk ↻: sprawdza bazę Sejmu (nowe przepisy), pobiera najnowsze dane i wiadomości, a na końcu
// przeładowuje aplikację, żeby wczytać też nową wersję jej kodu (nowe funkcje), nie tylko dane.
async function odswiezWszystko() {
  const b = document.getElementById("btn-refresh");
  if (b.classList.contains("spin")) {
    return;
  }
  b.classList.add("spin");
  pokazKomunikat("Sprawdzam nowe przepisy w bazie Sejmu…");
  try {
    await wczytajDane(true);
    stan.artykuly = null;
    stan.dok = {};
    stan.indeks = null;
    stan.dokZaladowane = null;
    stan.wszystkieDok = null;
    stan.warsztat = null;
    const wynik = await sprawdzZmiany(true);
    const godz = new Date(wynik.kiedy).toLocaleTimeString("pl-PL", { hour: "2-digit", minute: "2-digit" });
    let komunikat = `✓ Przepisy aktualne. Sprawdzono ${godz}, wiadomości z ${stan.aktualnosci.pobrano.slice(11)}.`;
    if (wynik.bledy >= stan.obserwowane.akty.length) {
      komunikat = "Brak połączenia z bazą Sejmu. Spróbuj za chwilę.";
    } else if (wynik.nowe.length) {
      komunikat = `Uwaga: ${wynik.nowe.length} ${wynik.nowe.length === 1 ? "nowa zmiana" : "nowe zmiany"} w przepisach - zobacz Nowości.`;
    }
    if ("serviceWorker" in navigator) {
      await navigator.serviceWorker.getRegistration().then((r) => r && r.update()).catch(() => {});
    }
    sessionStorage.setItem(KOMUNIKAT_PO_ODSWIEZENIU, komunikat);
    location.reload();
    return;
  } catch (e) {
    pokazKomunikat("Nie udało się odświeżyć - sprawdź internet.");
  } finally {
    b.classList.remove("spin");
  }
}

function pokazKomunikat(t) {
  let el = document.getElementById("komunikat");
  if (!el) {
    el = document.createElement("div");
    el.id = "komunikat";
    document.body.appendChild(el);
  }
  el.textContent = t;
  el.className = "toast on";
  clearTimeout(stan.komunikatCzas);
  stan.komunikatCzas = setTimeout(() => (el.className = "toast"), 4500);
}

function kartaAktualnosci() {
  const z = czytaj(KLUCZ.zmiany, null);
  const kiedy = z ? new Date(z.kiedy).toLocaleString("pl-PL", { day: "numeric", month: "numeric", hour: "2-digit", minute: "2-digit" }) : "jeszcze nie sprawdzono";
  const opis = z && z.nowe.length ? `${z.nowe.length} nowych zmian - zobacz Nowości` : "brak nowych zmian";
  return `<div class="card refresh-card"><div class="refresh-row"><div><b>Aktualność przepisów</b><p>${tekst(`Sprawdzono: ${kiedy} · ${opis}`)}</p></div>
    <button class="btn small" onclick="odswiezWszystko()">↻ Sprawdź</button></div></div>`;
}

init();
