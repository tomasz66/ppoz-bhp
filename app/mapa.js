// Mapa liczb: rysunek działki z budynkiem, na którym każda odległość z przepisów stoi w swoim miejscu,
// plus lista terminów. Tryb "Sprawdź się" chowa liczby - dotykasz i sprawdzasz, czy pamiętałeś.
// Dane i cytaty: data/liczby.json (skrypty/zbuduj_liczby.py).

TRASY.push([/^#\/mapa$/, () => widokMapy()]);

stan.mapa = { quiz: false, odkryte: new Set(), wybrana: null };

// Miejsca liczb na rysunku (viewBox 360 × 400) - id jak w data/liczby.json.
const MIEJSCA = {
  gas30: [150, 127], gas1: [70, 156], gas2kg: [110, 183], piec05: [172, 82], hydr135: [196, 156],
  galezie4: [318, 50], smola5: [270, 104], pas2: [300, 133], sklad5: [300, 252], droga4: [30, 312],
  droga515: [62, 245], dojscie: [150, 252], plac: [322, 362],
};
const SZEROKOSC_ZNAKU = 6.4;
const MARGINES_ZNACZKA = 12;

async function wczytajLiczby() {
  if (!stan.liczby) {
    stan.liczby = await fetch("data/liczby.json").then((r) => r.json());
  }
  return stan.liczby;
}

function znaczek(x) {
  const [cx, cy] = MIEJSCA[x.id];
  const m = stan.mapa;
  const napis = m.quiz && !m.odkryte.has(x.id) ? "?" : x.w;
  const szer = napis.length * SZEROKOSC_ZNAKU + MARGINES_ZNACZKA;
  return `<g class="m-znaczek${m.wybrana === x.id ? " wybrany" : ""}" onclick="wybierzLiczbe('${x.id}')">
    <rect x="${cx - szer / 2}" y="${cy - 10}" width="${szer}" height="20" rx="10"></rect>
    <text x="${cx}" y="${cy + 4}" text-anchor="middle">${esc(napis)}</text></g>`;
}

// Rysunek: działka, budynek z korytarzem, gaśnicą, piecem i hydrantem, skład, smoła, gałęzie, droga pożarowa.
function rysunekMapy(liczby) {
  const naMapie = liczby.filter((x) => MIEJSCA[x.id]);
  return `<svg class="mapa" viewBox="0 0 360 400" role="img" aria-label="Rysunek działki z odległościami z przepisów ppoż">
    <defs><marker id="grot" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="m-grot"/></marker></defs>
    <rect class="m-dzialka" x="8" y="8" width="344" height="382" rx="6"/>
    <text class="m-opis" x="16" y="22">granica działki</text>
    <line class="m-plot" x1="352" y1="8" x2="352" y2="390"/>
    <text class="m-opis" x="346" y="120" transform="rotate(90 346 120)">płot · działka sąsiada</text>

    <rect class="m-budynek" x="30" y="50" width="210" height="150"/>
    <text class="m-tytul" x="38" y="66">BUDYNEK · strefa ZL III</text>
    <rect class="m-korytarz" x="30" y="115" width="210" height="24"/>
    <text x="40" y="132" class="m-ikona">🧯</text>
    <line class="m-wymiar" x1="62" y1="127" x2="232" y2="127" marker-start="url(#grot)" marker-end="url(#grot)"/>
    <text x="196" y="88" class="m-ikona">🔥</text>
    <path class="m-zaslona" d="M222 66 q4 4 0 8 q-4 4 0 8 q4 4 0 8 q-4 4 0 8"/>
    <rect class="m-hydrant" x="224" y="148" width="12" height="14"/><text class="m-h" x="230" y="159" text-anchor="middle">H</text>
    <line class="m-wyjscie" x1="120" y1="200" x2="142" y2="200"/>
    <text class="m-opis" x="137" y="214">wyjście</text>

    <text x="276" y="92" class="m-ikona">🛢</text>
    <line class="m-wymiar" x1="242" y1="88" x2="272" y2="88" marker-start="url(#grot)" marker-end="url(#grot)"/>
    <text x="300" y="38" class="m-ikona">🌿</text>
    <line class="m-wymiar" x1="322" y1="34" x2="350" y2="34" marker-start="url(#grot)" marker-end="url(#grot)"/>

    <rect class="m-pas" x="254" y="142" width="82" height="66"/>
    <rect class="m-sklad" x="264" y="152" width="62" height="46"/>
    <text class="m-opis" x="295" y="180" text-anchor="middle">skład</text>
    <line class="m-wymiar" x1="300" y1="210" x2="300" y2="288" marker-start="url(#grot)" marker-end="url(#grot)"/>

    <line class="m-wymiar" x1="62" y1="202" x2="62" y2="288" marker-start="url(#grot)" marker-end="url(#grot)"/>
    <path class="m-dojscie" d="M131 202 V288"/>

    <rect class="m-droga" x="8" y="290" width="344" height="44"/>
    <text class="m-tytul jasny" x="180" y="316" text-anchor="middle">DROGA POŻAROWA</text>
    <rect class="m-plac" x="292" y="334" width="60" height="56"/>
    <text class="m-opis" x="322" y="384" text-anchor="middle">plac</text>
    ${naMapie.map(znaczek).join("")}
  </svg>`;
}

function kartaLiczby(x) {
  return `<div class="card liczba-info"><div class="liczba-w">${esc(x.w)}</div><p>${tekst(x.co)}</p><div class="links">${zrodloCiekawostki(x.zr)}</div></div>`;
}

function wierszTerminu(x) {
  const ukryte = stan.mapa.quiz && !stan.mapa.odkryte.has(x.id);
  return `<button class="termin" onclick="wybierzLiczbe('${x.id}')"><span class="termin-w${ukryte ? " ukryte" : ""}">${ukryte ? "?" : esc(x.w)}</span><span class="termin-co">${tekst(x.co)}</span></button>
    ${stan.mapa.wybrana === x.id && !ukryte ? `<div class="links termin-zr">${zrodloCiekawostki(x.zr)}</div>` : ""}`;
}

async function widokMapy() {
  ustawNaglowek("Mapa liczb", "back");
  ustawZakladke("nauka");
  const liczby = await wczytajLiczby();
  const m = stan.mapa;
  const wybrana = liczby.find((x) => x.id === m.wybrana && MIEJSCA[x.id]);
  const przewiniecie = window.scrollY;
  widok.innerHTML = `
    <div class="section-header"><div class="section-title">Mapa liczb</div>
    <div class="section-sub">${tekst("Odległości z przepisów ppoż w miejscach, których dotyczą. Dotknij liczby, żeby zobaczyć, skąd się wzięła.")}</div></div>
    <div class="seg">${[[false, "📖 Ucz się"], [true, "🎯 Sprawdź się"]].map(([k, n]) => `<button class="${m.quiz === k ? "on" : ""}" onclick="trybMapy(${k})">${n}</button>`).join("")}</div>
    ${m.quiz ? `<p class="opis-trybu">${tekst(`Liczby są ukryte. Powiedz na głos, ile wynosi, i dotknij, żeby sprawdzić. Odkryte: ${m.odkryte.size}/${liczby.length}.`)}</p>` : ""}
    <div class="mapa-ramka">${rysunekMapy(liczby)}</div>
    <div id="mapa-info">${wybrana && (!m.quiz || m.odkryte.has(wybrana.id)) ? kartaLiczby(wybrana) : ""}</div>
    <div class="section-label">Terminy ppoż</div>
    <div class="card terminy">${liczby.filter((x) => x.g === "ppoz").map(wierszTerminu).join("")}</div>
    <div class="section-label">Terminy BHP</div>
    <div class="card terminy">${liczby.filter((x) => x.g === "bhp").map(wierszTerminu).join("")}</div>
    <div class="foot">${tekst("Rysunek jest poglądowy - nie w skali. Każda liczba jest sprawdzona z brzmieniem przepisu.")}</div>`;
  window.scrollTo(0, przewiniecie);
}

function trybMapy(quiz) {
  Object.assign(stan.mapa, { quiz, odkryte: new Set(), wybrana: null });
  widokMapy();
}

function wybierzLiczbe(id) {
  const m = stan.mapa;
  if (m.quiz) {
    m.odkryte.add(id);
  }
  m.wybrana = id;
  widokMapy().then(() => {
    const info = document.getElementById("mapa-info");
    if (MIEJSCA[id] && info.firstChild) {
      info.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  });
}
