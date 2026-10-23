// Asystent: "Ja pytam" (pytanie → objaśnienie z paragrafów) i "Przepytaj mnie" (AI pyta jak egzaminator
// albo klient, ocenia odpowiedź). Lektor (mowa iPhone'a) i mikrofon. AI dostaje wyłącznie fragmenty
// przepisów wyszukane w aplikacji i ma się na nie powoływać numerami [1], [2]…
//
//   pytanie ─► wyszukanie paragrafów (indeks z app.js) ─► Claude (klucz z telefonu) ─► tekst + źródła ─► lektor
//
// Klucz API zapisuje się tylko w tym telefonie (localStorage), nigdy w repozytorium.

const SDK_URL = "https://cdn.jsdelivr.net/npm/@anthropic-ai/sdk@0.133.0/+esm";
const KLUCZ_A = { klucz: "bhp-ai-klucz", model: "bhp-ai-model", lektor: "bhp-ai-lektor" };
const MODELE = [
  { id: "claude-opus-5-5", nazwa: "Najlepsza jakość", wej: 4, wyj: 20 },
  { id: "claude-haiku-5-5", nazwa: "Oszczędny (ok. 40× taniej)", wej: 0.1, wyj: 0.5 },
];
const MILION = 1e6;
const FRAGMENTOW = 10;
const ZNAKOW_FRAGMENTU = 6000;
const TUR_W_PAMIECI = 6;
const MAX_TOKENOW = 16000;
const FALLBACK_BETA = "server-side-fallback-2026-07-01";
const ZDANIE_LEKTORA = 220;
const PAUZA_PO_CANCEL_MS = 150;
const CISZA_DYKTOWANIA_MS = 2000;
const SPRAWDZ_LEKTORA_MS = 1500;

const SYSTEM_PYTAM = `Jesteś asystentem do nauki przepisów BHP i ochrony przeciwpożarowej dla przyszłego inspektora ochrony ppoż. Odpowiadasz po polsku.
Zasady:
- Opieraj się WYŁĄCZNIE na fragmentach przepisów z bieżącej i wcześniejszych wiadomości (oznaczonych [1], [2]…). Po każdym twierdzeniu podaj numer fragmentu w nawiasie kwadratowym, np. [2].
- Liczby, odległości i terminy podawaj dokładnie tak, jak w przepisie.
- Jeśli fragmenty nie odpowiadają na pytanie, powiedz wprost: „W przepisach, które mam w aplikacji, tego nie znalazłem” i zasugeruj, gdzie szukać (np. Polska Norma, warunki techniczne). Nie zgaduj.
- Tłumacz prosto, jak doświadczony kolega: najpierw krótka odpowiedź, potem 1-2 zdania wyjaśnienia i praktyczny przykład z życia (sklep, przedszkole, warsztat).
- Tekst będzie czytany na głos: pisz zwykłymi zdaniami, bez nagłówków, gwiazdek, tabel i list. Zwykle 60-160 słów.
Odpowiedź jest pilna - zacznij widoczną odpowiedź od razu.`;

const SYSTEM_PRZEPYTAJ = `Jesteś egzaminatorem i trenerem na kursie inspektora ochrony przeciwpożarowej i specjalisty BHP. Odpowiadasz po polsku.
Przebieg: dostajesz fragmenty przepisów [1], [2]… i tryb. Zadajesz JEDNO pytanie oparte wyłącznie na tych fragmentach - nie podawaj odpowiedzi.
- Tryb „egzamin”: pytanie jak na egzaminie, konkretne (liczba, termin, warunek, obowiązek).
- Tryb „klient”: mówisz jako właściciel małej firmy, który zadaje praktyczne pytanie potocznym językiem, opisując swoją sytuację.
Gdy kursant odpowie, oceń: zacznij od „Dobrze”, „Częściowo” albo „Źle”, potem powiedz, co było trafne, czego zabrakło, i podaj poprawną odpowiedź z numerem fragmentu, np. [1]. W trybie „klient” oceń też, czy odpowiedź byłaby zrozumiała dla właściciela firmy.
Jeśli kursant dopytuje, odpowiadaj na podstawie fragmentów. Tekst będzie czytany na głos: zwykłe zdania, bez list, nagłówków i gwiazdek, krótko.
Odpowiedź jest pilna - zacznij widoczną odpowiedź od razu.`;

stan.asystent = { tryb: "pytam", styl: "egzamin", rozmowa: [], wiadomosci: [], zrodla: [], koszt: 0, zajety: false };

TRASY.push([/^#\/asystent$/, () => widokAsystenta()]);

// ── Wyszukiwanie fragmentów do pytania (luźniejsze niż wyszukiwarka: wystarczy część słów) ──

// Słowa pytające i "wypełniacze" - nic nie mówią o temacie, więc nie biorą udziału w szukaniu.
const STOP_PYTANIA = new Set(["ile", "jak", "jaki", "jaka", "jakie", "jakich", "gdzie", "kiedy", "musi", "musze", "trzeba", "moze", "moge", "mozna",
  "powinien", "powinna", "powinno", "ktore", "ktory", "ktora", "mam", "przez", "tak", "ten", "tym", "tego", "byc", "albo", "lub", "mnie",
  "powiedz", "dokladnie", "wiecej", "prosze", "czym", "jakim", "jest", "mają", "maja", "moj", "moja", "moje", "nas", "nam"]);
// Akty z tekstem odczytanym ze skanu (z błędami) - nie podajemy ich AI jako podstawy.
const NIEPEWNE_TEKSTY = new Set(["DU/1997/704"]);
const LIMIT_TYPU = { case: 2, sciaga: 2 };
// Trzy akty ppoż z zakładki Przepisy to rdzeń nauki - ich paragrafy dostają pierwszeństwo przed warunkami technicznymi.
const PREMIA_PPOZ = 1.5;
// BM25 - standardowa ocena trafności: rzadkie słowa ważą więcej, a długi paragraf nie wygrywa samą długością.
const BM25_K1 = 1.2;
const BM25_B = 0.75;

// Jednostki do szukania: cały artykuł/paragraf (linie sklejone), przypadek albo wiersz ściągi.
function jednostkiAI() {
  stan.indeks = stan.indeks || indeks();
  if (stan.jednostkiAI && stan.jednostkiAI.zrodlo === stan.indeks) {
    return stan.jednostkiAI;
  }
  const mapa = new Map();
  for (const e of stan.indeks) {
    if (!["ppoz", "bhp", "case", "sciaga"].includes(e.g) || (e.d && NIEPEWNE_TEKSTY.has(e.d.eli))) {
      continue;
    }
    const klucz = e.a ? `a:${e.a.id}:${e.j.id}` : e.d ? `d:${e.d.eli}:${e.j.id}` : e.c ? `c:${e.c.t.slice(0, 40)}` : `s:${e.s.id}:${e.w[0]}`;
    const j = mapa.get(klucz) || { e, norm: "" };
    j.norm += " " + e.norm;
    mapa.set(klucz, j);
  }
  const lista = [...mapa.values()];
  const srednia = lista.reduce((s, j) => s + j.norm.length, 0) / lista.length;
  stan.jednostkiAI = { zrodlo: stan.indeks, lista, srednia };
  return stan.jednostkiAI;
}

function ileRazy(tekst, w) {
  return tekst.split(w).length - 1;
}

async function fragmentyDla(pytanie) {
  if (!stan.dokZaladowane) {
    stan.dokZaladowane = await wczytajWszystkieDok();
    stan.indeks = null;
  }
  const { lista, srednia } = jednostkiAI();
  const slowa = bezOgonkow(pytanie).split(/[\s,.;:?!()„”"]+/).filter((s) => s.length > 2 && !STOP.has(s) && !STOP_PYTANIA.has(s));
  const grupy = [...new Map(slowa.map(warianty).map((w) => [w.join("|"), w])).values()];
  const idf = grupy.map((war) => {
    const df = lista.reduce((s, j) => s + (war.some((w) => j.norm.includes(w)) ? 1 : 0), 0);
    return Math.log(1 + (lista.length - df + 0.5) / (df + 0.5));
  });
  const ocenione = [];
  for (const j of lista) {
    let pkt = 0;
    grupy.forEach((war, k) => {
      const tf = war.reduce((s, w) => s + ileRazy(j.norm, w), 0);
      if (tf) {
        pkt += idf[k] * (tf * (BM25_K1 + 1)) / (tf + BM25_K1 * (1 - BM25_B + BM25_B * j.norm.length / srednia));
      }
    });
    if (pkt) {
      ocenione.push({ e: j.e, pkt: j.e.g === "ppoz" ? pkt * PREMIA_PPOZ : pkt });
    }
  }
  ocenione.sort((x, y) => y.pkt - x.pkt);

  const ileTypu = {};
  const wynik = [];
  for (const x of ocenione) {
    const limit = LIMIT_TYPU[x.e.g];
    if (limit && (ileTypu[x.e.g] || 0) >= limit) {
      continue;
    }
    const f = opisFragmentu(x.e);
    if (wynik.some((y) => y.adres === f.adres && y.tekst === f.tekst)) {
      continue;
    }
    ileTypu[x.e.g] = (ileTypu[x.e.g] || 0) + 1;
    wynik.push(f);
    // Przypadek i ściąga to skrót - dokładamy pełny paragraf, na który się powołują (np. smoła → § 4).
    const pelny = paragrafZrodla(x.e.c ? x.e.c.zr : x.e.w ? x.e.w[2] : null);
    if (pelny && !wynik.some((f) => f.adres === pelny.adres && f.tekst === pelny.tekst)) {
      wynik.push(pelny);
    }
    if (wynik.length >= FRAGMENTOW) {
      break;
    }
  }
  return wynik;
}

function paragrafZrodla(zr) {
  if (!zr || !zr.j) {
    return null;
  }
  const tekstJ = (j) => j.linie.map((l) => l.t).join("\n").slice(0, ZNAKOW_FRAGMENTU);
  if (zr.a) {
    const akt = stan.aktyMapa[zr.a];
    const j = akt && akt.jednostki.find((x) => x.id === zr.j);
    return j ? { etykieta: `${j.etykieta} · ${akt.skrot}`, tekst: tekstJ(j), adres: `#/akt/${zr.a}/${zr.j}` } : null;
  }
  const d = zr.dok && (stan.dokZaladowane || []).find((x) => x && x.eli.replaceAll("/", "_") === zr.dok);
  const j = d && d.jednostki.find((x) => x.id === zr.j);
  return j ? { etykieta: `${j.etykieta} · ${nazwaDok(d)}`, tekst: tekstJ(j), adres: `#/dok/${zr.dok}/${zr.j}` } : null;
}

// Fragment = etykieta, pełny tekst i adres w aplikacji (do klikalnego źródła).
function opisFragmentu(e) {
  const tekstJ = (j) => j.linie.map((l) => l.t).join("\n").slice(0, ZNAKOW_FRAGMENTU);
  if (e.a) {
    return { etykieta: `${e.j.etykieta} · ${e.a.skrot}`, tekst: tekstJ(e.j), adres: `#/akt/${e.a.id}/${e.j.id}` };
  }
  if (e.d) {
    return { etykieta: `${e.j.etykieta} · ${nazwaDok(e.d)}`, tekst: tekstJ(e.j), adres: `#/dok/${e.d.eli.replaceAll("/", "_")}/${e.j.id}` };
  }
  if (e.c) {
    return { etykieta: "Przypadek z życia", tekst: `${e.c.s ? "Sytuacja: " + e.c.s + "\n" : ""}Prawo: ${e.c.t}`, adres: adresZrodla(e.c.zr) };
  }
  return { etykieta: `Ściąga: ${e.s.tytul}`, tekst: `${e.w[0]}: ${e.w[1]}`, adres: adresZrodla(e.w[2]) };
}

function adresZrodla(zr) {
  if (!zr) {
    return "";
  }
  return zr.dok ? `#/dok/${zr.dok}/${zr.j}` : zr.a ? `#/akt/${zr.a}/${zr.j}` : "";
}

// Dokłada nowe fragmenty do listy źródeł rozmowy; numeracja [n] jest wspólna dla całej rozmowy.
function dopiszZrodla(fragmenty) {
  const a = stan.asystent;
  return fragmenty.map((f) => {
    let i = a.zrodla.findIndex((z) => z.etykieta === f.etykieta && z.tekst === f.tekst);
    if (i < 0) {
      a.zrodla.push(f);
      i = a.zrodla.length - 1;
    }
    return `[${i + 1}] ${f.etykieta}\n${f.tekst}`;
  }).join("\n\n");
}

// ── Rozmowa z Claude ──

async function klientAI() {
  if (!stan.anthropic) {
    const { default: Anthropic } = await import(SDK_URL);
    stan.Anthropic = Anthropic;
    stan.anthropic = new Anthropic({ apiKey: czytaj(KLUCZ_A.klucz, ""), dangerouslyAllowBrowser: true });
  }
  return stan.anthropic;
}

function wybranyModel() {
  return MODELE.find((m) => m.id === czytaj(KLUCZ_A.model, MODELE[0].id)) || MODELE[0];
}

async function zapytajAI(system, tresc, naTekst) {
  const a = stan.asystent;
  const client = await klientAI();
  const model = wybranyModel();
  // Historii nie przycinamy (zmiana wcześniejszych tur unieważnia zapis rozumowania modelu) - długą rozmowę zaczynamy od nowa.
  if (a.rozmowa.length >= TUR_W_PAMIECI * 2) {
    a.rozmowa = [];
  }
  a.rozmowa.push({ role: "user", content: tresc });
  const zapytanie = {
    model: model.id,
    max_tokens: MAX_TOKENOW,
    system,
    output_config: { effort: "low" },
    messages: a.rozmowa,
  };
  // Opus: przy odmowie z powodów bezpieczeństwa serwer sam ponawia na innym modelu.
  const strumien = model.id.startsWith("claude-opus")
    ? client.beta.messages.stream({ ...zapytanie, betas: [FALLBACK_BETA], fallbacks: "default" })
    : client.messages.stream(zapytanie);
  let tekst = "";
  strumien.on("text", (t) => {
    tekst += t;
    naTekst(tekst);
  });
  const odp = await strumien.finalMessage();
  if (odp.stop_reason === "refusal") {
    a.rozmowa.pop();
    throw new Error("odmowa");
  }
  a.rozmowa.push({ role: "assistant", content: odp.content });
  a.koszt += (odp.usage.input_tokens * model.wej + odp.usage.output_tokens * model.wyj) / MILION;
  return odp.content.filter((b) => b.type === "text").map((b) => b.text).join("");
}

// Jedno pytanie bez historii rozmowy (np. zdjęcie do oceny) - zwraca sam tekst odpowiedzi.
async function zapytajJednorazowo(tresc) {
  const client = await klientAI();
  const model = wybranyModel();
  const zapytanie = { model: model.id, max_tokens: MAX_TOKENOW, output_config: { effort: "low" }, messages: [{ role: "user", content: tresc }] };
  const strumien = model.id.startsWith("claude-opus")
    ? client.beta.messages.stream({ ...zapytanie, betas: [FALLBACK_BETA], fallbacks: "default" })
    : client.messages.stream(zapytanie);
  const odp = await strumien.finalMessage();
  if (odp.stop_reason === "refusal") {
    throw new Error("odmowa");
  }
  stan.asystent.koszt += (odp.usage.input_tokens * model.wej + odp.usage.output_tokens * model.wyj) / MILION;
  return odp.content.filter((b) => b.type === "text").map((b) => b.text).join("");
}

function opisBledu(e) {
  const A = stan.Anthropic;
  if (e.message === "odmowa") {
    return "AI odmówiło odpowiedzi na to pytanie. Spróbuj sformułować je inaczej.";
  }
  if (A && e instanceof A.AuthenticationError) {
    return "Klucz AI jest nieprawidłowy. Wklej go ponownie w Ustawieniach poniżej.";
  }
  if (A && e instanceof A.RateLimitError) {
    return "Za dużo pytań naraz - odczekaj chwilę.";
  }
  if (A && e instanceof A.APIConnectionError) {
    return "Brak połączenia z AI - sprawdź internet.";
  }
  if (A && e instanceof A.APIError && /credit|billing|balance/i.test(e.message)) {
    return "Skończyły się środki na koncie AI - doładuj w console.anthropic.com (Billing).";
  }
  return "Coś poszło nie tak: " + (e.message || e);
}

// ── Lektor (mowa iPhone'a) ──

function glosPolski() {
  const glosy = speechSynthesis.getVoices().filter((v) => v.lang && v.lang.toLowerCase().startsWith("pl"));
  return glosy.find((v) => /premium|enhanced|zosia|ewa/i.test(v.name)) || glosy[0] || null;
}

// iOS pozwala stronie mówić dopiero po dotknięciu ekranu. Cicha, krótka wypowiedź przy dotknięciu
// "odblokowuje" lektora, żeby mógł potem sam przeczytać odpowiedź, która przychodzi kilka sekund później.
// (Pusta wypowiedź nie wystarcza - iOS ją pomija.)
function odblokujLektora() {
  if (!("speechSynthesis" in window) || speechSynthesis.speaking) {
    return;
  }
  const u = new SpeechSynthesisUtterance(".");
  u.volume = 0;
  u.lang = "pl-PL";
  speechSynthesis.speak(u);
}

function czytajNaGlos(t) {
  if (!("speechSynthesis" in window)) {
    pokazKomunikat("Ten telefon nie ma lektora w przeglądarce.");
    return;
  }
  // Błąd iOS: wypowiedź dodana tuż po cancel() bywa gubiona - dlatego krótka pauza.
  const bylo = speechSynthesis.speaking || speechSynthesis.pending;
  if (bylo) {
    speechSynthesis.cancel();
  }
  setTimeout(() => mow(t), bylo ? PAUZA_PO_CANCEL_MS : 0);
}

function mow(t) {
  const czysty = t.replace(/\[\d+\]/g, "").replace(/[*#_]/g, "");
  // Długie teksty iOS potrafi uciąć - czytamy zdanie po zdaniu.
  const zdania = czysty.match(new RegExp(`[^.!?]{1,${ZDANIE_LEKTORA}}[.!?]?`, "g")) || [czysty];
  const glos = glosPolski();
  // Trzymamy wypowiedzi w pamięci - inaczej Safari potrafi je usunąć w trakcie czytania.
  stan.wypowiedzi = zdania.map((z) => {
    const u = new SpeechSynthesisUtterance(z.trim());
    u.lang = "pl-PL";
    if (glos) {
      u.voice = glos;
    }
    speechSynthesis.speak(u);
    return u;
  });
  pokazPrzerwij(true);
  const sprawdz = setInterval(() => {
    if (!speechSynthesis.speaking) {
      clearInterval(sprawdz);
      pokazPrzerwij(false);
    }
  }, 300);
}

function zatrzymajLektora() {
  if ("speechSynthesis" in window) {
    speechSynthesis.cancel();
  }
  pokazPrzerwij(false);
}

function pokazPrzerwij(widoczny) {
  const b = document.getElementById("btn-przerwij");
  if (b) {
    b.hidden = !widoczny;
  }
}

// ── Mikrofon ──

function rozpoznawanieMowy() {
  return window.SpeechRecognition || window.webkitSpeechRecognition || null;
}

function sluchaj() {
  const SR = rozpoznawanieMowy();
  zatrzymajLektora();
  odblokujLektora();
  const pole = document.getElementById("pole-asystenta");
  if (!SR) {
    // iPhone nie daje aplikacjom z ekranu początkowego rozpoznawania mowy - zostaje dyktowanie z klawiatury.
    // Pytanie wysyła się samo, gdy przez 2 sekundy nic się nie zmienia.
    stan.dyktowanie = true;
    pole.focus();
    pokazKomunikat("Dotknij 🎤 na klawiaturze i mów. Gdy skończysz, pytanie wyśle się samo.");
    return;
  }
  const r = new SR();
  r.lang = "pl-PL";
  r.interimResults = true;
  r.continuous = false;
  const mic = document.getElementById("btn-mic");
  mic.classList.add("on");
  r.onresult = (ev) => {
    pole.value = [...ev.results].map((x) => x[0].transcript).join(" ");
  };
  r.onend = () => {
    mic.classList.remove("on");
    if (pole.value.trim()) {
      wyslijDoAsystenta();
    }
  };
  r.onerror = () => {
    mic.classList.remove("on");
    pokazKomunikat("Mikrofon nie zadziałał - użyj 🎤 na klawiaturze iPhone'a.");
  };
  r.start();
}

// ── Widok ──

function dymek(w, i) {
  if (w.kto === "ja") {
    return `<div class="dymek ja">${tekst(w.t)}</div>`;
  }
  const html = esc(w.t).replace(/\n+/g, "<br>").replace(/\[(\d+)\]/g, (m, n) => {
    const z = stan.asystent.zrodla[n - 1];
    return z && z.adres ? `<a class="przypis" href="${z.adres}">${n}</a>` : m;
  });
  const numery = [...new Set([...w.t.matchAll(/\[(\d+)\]/g)].map((m) => Number(m[1])))].filter((n) => stan.asystent.zrodla[n - 1]);
  return `<div class="dymek ai${w.blad ? " blad" : ""}" id="dymek-${i}">${nbsp(html)}
    ${numery.length ? `<div class="links">${numery.map((n) => {
      const z = stan.asystent.zrodla[n - 1];
      return z.adres ? `<a class="chip" href="${z.adres}">[${n}] ${esc(z.etykieta)} ›</a>` : `<span class="chip">[${n}] ${esc(z.etykieta)}</span>`;
    }).join("")}</div>` : ""}
    ${w.blad || !w.t ? "" : `<button class="chip red" onclick="czytajNaGlos(stan.asystent.wiadomosci[${i}].t)">▶ Czytaj</button>`}
  </div>`;
}

function rysujRozmowe() {
  const el = document.getElementById("rozmowa");
  if (el) {
    el.innerHTML = stan.asystent.wiadomosci.map(dymek).join("");
    const koszt = document.getElementById("koszt-ai");
    if (koszt) {
      koszt.textContent = stan.asystent.koszt ? `Koszt tej rozmowy: ok. $${stan.asystent.koszt.toFixed(3)}` : "";
    }
  }
}

function kartaUstawien(otwarta) {
  const jest = !!czytaj(KLUCZ_A.klucz, "");
  return `<details class="card ustawienia" ${otwarta ? "open" : ""}><summary><b>⚙️ Ustawienia AI</b> ${jest ? '<span class="row-tag ok">klucz zapisany</span>' : '<span class="row-tag">brak klucza</span>'}</summary>
    <p class="pomoc">${tekst("Klucz z console.anthropic.com → API Keys. Zapisuje się tylko w tym telefonie.")}</p>
    <label class="pole"><span>Klucz API</span><input id="klucz-ai" type="password" autocomplete="off" placeholder="${jest ? "•••••• (zapisany)" : "sk-ant-…"}"></label>
    <div class="btn-row" style="margin:10px 0 0"><button class="btn small" onclick="zapiszKlucz()">Zapisz klucz</button>${jest ? `<button class="btn small secondary" onclick="usunKlucz()">Usuń</button>` : ""}</div>
    <div class="pole" style="margin-top:14px"><span>Model</span><div class="seg mini">${MODELE.map((m) => `<button class="${wybranyModel().id === m.id ? "on" : ""}" onclick="zapisz(KLUCZ_A.model,'${m.id}');widokAsystenta(true)">${esc(m.nazwa)}</button>`).join("")}</div></div>
    <label class="przelacznik"><input type="checkbox" ${czytaj(KLUCZ_A.lektor, true) ? "checked" : ""} onchange="zapisz(KLUCZ_A.lektor,this.checked)"> Lektor czyta odpowiedzi automatycznie</label>
    <div class="btn-row" style="margin:12px 0 0"><button class="btn small secondary" onclick="czytajNaGlos('Test lektora. Jeśli mnie słyszysz, czytanie odpowiedzi działa.')">🔊 Test lektora</button></div>
    <p class="pomoc">${tekst(`Mikrofon w aplikacji: ${rozpoznawanieMowy() ? "dostępny" : "niedostępny na tym telefonie - użyj 🎤 na klawiaturze"}. Polskie głosy lektora: ${"speechSynthesis" in window ? speechSynthesis.getVoices().filter((v) => (v.lang || "").toLowerCase().startsWith("pl")).length : 0}. Jeśli nic nie słychać, sprawdź przełącznik wyciszenia i głośność.`)}</p>
  </details>`;
}

function zapiszKlucz() {
  const v = document.getElementById("klucz-ai").value.trim();
  if (!v) {
    return;
  }
  zapisz(KLUCZ_A.klucz, v);
  stan.anthropic = null;
  pokazKomunikat("✓ Klucz zapisany w tym telefonie.");
  widokAsystenta(false);
}

function usunKlucz() {
  zapisz(KLUCZ_A.klucz, "");
  stan.anthropic = null;
  widokAsystenta(true);
}

function zmienTryb(tryb) {
  zatrzymajLektora();
  Object.assign(stan.asystent, { tryb, rozmowa: [], wiadomosci: [], zrodla: [] });
  widokAsystenta(false);
}

function widokAsystenta(ustawieniaOtwarte) {
  // Wejście z karty pojęcia ("Przepytaj mnie") - od razu pytanie o to pojęcie.
  if (stan.przepytajPojecie) {
    const id = stan.przepytajPojecie;
    stan.przepytajPojecie = null;
    stan.asystent.tryb = "przepytaj";
    if (czytaj(KLUCZ_A.klucz, "")) {
      przepytajZPojecia(id);
      return;
    }
  }
  ustawNaglowek("Asystent", "#/start");
  ustawZakladke("start");
  const a = stan.asystent;
  const jestKlucz = !!czytaj(KLUCZ_A.klucz, "");
  const pytam = a.tryb === "pytam";
  widok.innerHTML = `
    <div class="seg">${[["pytam", "🗣 Ja pytam"], ["przepytaj", "🎓 Przepytaj mnie"]].map(([k, n]) => `<button class="${a.tryb === k ? "on" : ""}" onclick="zmienTryb('${k}')">${n}</button>`).join("")}</div>
    ${pytam ? `<p class="opis-trybu">${tekst("Zapytaj o cokolwiek z przepisów - np. „jak mocować gaśnice i co ile przegląd”. Odpowiedź tylko na podstawie paragrafów z aplikacji, z odnośnikami.")}</p>`
      : `<div class="seg">${[["egzamin", "Egzamin"], ["klient", "Pyta klient"]].map(([k, n]) => `<button class="${a.styl === k ? "on" : ""}" onclick="stan.asystent.styl='${k}';widokAsystenta()">${n}</button>`).join("")}</div>
      <p class="opis-trybu">${tekst("AI zadaje pytanie, Ty odpowiadasz głosem albo pisząc. Dostajesz ocenę i poprawną odpowiedź z paragrafem. Możesz dopytywać.")}</p>
      <div class="btn-row"><button class="btn" onclick="noweZadanie()" ${jestKlucz ? "" : "disabled"}>🎲 Zadaj mi pytanie</button></div>`}
    <div id="rozmowa"></div>
    <div class="pasek-asystenta">
      <button class="btn przerwij" id="btn-przerwij" hidden onclick="sluchaj()">✋ Przerwij i zapytaj</button>
      <div class="wpis">
        <textarea id="pole-asystenta" rows="1" placeholder="${pytam ? "Zadaj pytanie…" : "Twoja odpowiedź…"}" ${jestKlucz ? "" : "disabled"}></textarea>
        <button class="okragly" id="btn-mic" onclick="sluchaj()" aria-label="Mów" ${jestKlucz ? "" : "disabled"}>🎤</button>
        <button class="okragly wyslij" onclick="wyslijDoAsystenta()" aria-label="Wyślij" ${jestKlucz ? "" : "disabled"}>↑</button>
      </div>
      <div class="koszt" id="koszt-ai"></div>
    </div>
    ${pytam && a.wiadomosci.length ? `<div class="btn-row"><button class="btn secondary" onclick="zmienTryb('pytam')">Nowa rozmowa</button></div>` : ""}
    ${kartaUstawien(ustawieniaOtwarte || !jestKlucz)}
    <div class="foot">${tekst("AI może się pomylić - zawsze sprawdź paragraf, na który się powołuje. Na egzamin ucz się z przepisu, nie z samego objaśnienia.")}</div>`;
  rysujRozmowe();
  const pole = document.getElementById("pole-asystenta");
  pole.addEventListener("input", () => {
    clearTimeout(stan.ciszaDyktowania);
    if (stan.dyktowanie && pole.value.trim()) {
      stan.ciszaDyktowania = setTimeout(() => {
        stan.dyktowanie = false;
        pole.blur();
        wyslijDoAsystenta();
      }, CISZA_DYKTOWANIA_MS);
    }
  });
  pole.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter" && !ev.shiftKey) {
      ev.preventDefault();
      wyslijDoAsystenta();
    }
  });
}

// Jedna wymiana: dymek użytkownika (opcjonalnie), pusty dymek AI wypełniany na żywo, potem lektor.
async function wymiana(system, tresc, dymekJa) {
  const a = stan.asystent;
  if (a.zajety) {
    return;
  }
  a.zajety = true;
  odblokujLektora();
  if (dymekJa) {
    a.wiadomosci.push({ kto: "ja", t: dymekJa });
  }
  const w = { kto: "ai", t: "" };
  a.wiadomosci.push(w);
  rysujRozmowe();
  const i = a.wiadomosci.length - 1;
  try {
    w.t = await zapytajAI(system, tresc, (t) => {
      w.t = t;
      const el = document.getElementById(`dymek-${i}`);
      if (el) {
        el.innerHTML = nbsp(esc(t)).replace(/\n+/g, "<br>");
      }
    });
    rysujRozmowe();
    if (czytaj(KLUCZ_A.lektor, true)) {
      czytajNaGlos(w.t);
      // Jeśli iPhone zablokował czytanie bez dotknięcia - podpowiedź, żeby dotknąć ▶.
      setTimeout(() => {
        if ("speechSynthesis" in window && !speechSynthesis.speaking && !speechSynthesis.pending) {
          pokazKomunikat("Dotknij ▶ Czytaj pod odpowiedzią, żeby ją odsłuchać.");
        }
      }, SPRAWDZ_LEKTORA_MS);
    }
  } catch (e) {
    w.t = opisBledu(e);
    w.blad = true;
    rysujRozmowe();
  } finally {
    a.zajety = false;
    document.getElementById(`dymek-${i}`)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

async function wyslijDoAsystenta() {
  const pole = document.getElementById("pole-asystenta");
  const q = pole.value.trim();
  const a = stan.asystent;
  if (!q || a.zajety) {
    return;
  }
  pole.value = "";
  zatrzymajLektora();
  if (a.tryb === "przepytaj" && !a.rozmowa.length) {
    pole.value = q;
    pokazKomunikat("Najpierw dotknij „Zadaj mi pytanie”.");
    return;
  }
  // Do wyszukiwania dokładamy poprzednie pytanie, żeby dopytania („a ile metrów?”) trafiały w temat.
  const poprzednie = [...a.wiadomosci].reverse().find((w) => w.kto === "ja");
  const fragmenty = await fragmentyDla(q + " " + (poprzednie ? poprzednie.t : ""));
  const kontekst = fragmenty.length ? `Fragmenty przepisów:\n\n${dopiszZrodla(fragmenty)}\n\n` : "";
  const system = a.tryb === "pytam" ? SYSTEM_PYTAM : SYSTEM_PRZEPYTAJ;
  const tresc = a.tryb === "pytam" ? `${kontekst}Pytanie: ${q}` : `${kontekst}Kursant: ${q}`;
  wymiana(system, tresc, q);
}

// Losuje temat z przypadków i ściąg (mają paragrafy), dokłada pełny tekst paragrafu i prosi o pytanie.
async function noweZadanie() {
  const a = stan.asystent;
  zatrzymajLektora();
  Object.assign(a, { rozmowa: [], wiadomosci: [], zrodla: [] });
  widokAsystenta(false);
  const pula = wszystkieCiekawostki().map((c) => ({ temat: (c.s || "") + " " + c.t, zr: c.zr }))
    .concat(stan.sciagi.flatMap((s) => s.wiersze.map((w) => ({ temat: `${s.tytul}: ${w[0]} - ${w[1]}`, zr: w[2] }))));
  const los = pula[Math.floor(Math.random() * pula.length)];
  const fragmenty = await fragmentyDla(los.temat);
  const paragraf = paragrafZrodla(los.zr);
  const temat = { etykieta: paragraf ? paragraf.etykieta : "Temat", tekst: los.temat, adres: adresZrodla(los.zr) };
  const kontekst = dopiszZrodla([temat, ...(paragraf ? [paragraf] : []), ...fragmenty.slice(0, 3)]);
  wymiana(SYSTEM_PRZEPYTAJ, `Fragmenty przepisów:\n\n${kontekst}\n\nTryb: ${a.styl}. Zadaj jedno pytanie.`, "");
}

// Pytanie o konkretne pojęcie: karta (definicja + dopytania) i pełne paragrafy, na które się powołuje.
async function przepytajZPojecia(id) {
  const a = stan.asystent;
  const k = stan.pojecia.find((x) => x.id === id);
  zatrzymajLektora();
  Object.assign(a, { tryb: "przepytaj", rozmowa: [], wiadomosci: [], zrodla: [] });
  widokAsystenta(false);
  if (!stan.dokZaladowane) {
    stan.dokZaladowane = await wczytajWszystkieDok();
    stan.indeks = null;
  }
  const karta = { etykieta: `Pojęcie: ${k.nazwa}`, tekst: `${k.def}\n${k.dopytania.map((p) => `${p.q} ${p.a}`).join("\n")}`, adres: `#/pojecie/${k.id}` };
  const paragrafy = [k.zr, ...k.dopytania.map((p) => p.zr)].map(paragrafZrodla).filter(Boolean)
    .filter((f, i, lista) => lista.findIndex((y) => y.adres === f.adres) === i);
  const powiazane = k.powiazane.map((p) => (stan.pojecia.find((x) => x.id === p) || {}).nazwa).filter(Boolean).join(", ");
  const kontekst = dopiszZrodla([karta, ...paragrafy]);
  wymiana(SYSTEM_PRZEPYTAJ, `Fragmenty przepisów:\n\n${kontekst}\n\nTryb: ${a.styl}. Zadaj jedno pytanie o pojęcie „${k.nazwa}”${powiazane ? ` (możesz też zahaczyć o pojęcia powiązane: ${powiazane})` : ""}.`, "");
}
