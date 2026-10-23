// Warsztat: "Obchód obiektu" (lista kontrolna z podstawą prawną → zalecenia) i wzory dokumentów
// (IBP, wypadek przy pracy, ocena ryzyka). Wszystko zapisuje się tylko w tym telefonie (localStorage).
// Dane i cytaty z przepisów: data/warsztat.json, budowane i sprawdzane skryptem skrypty/zbuduj_warsztat.py.

const KLUCZ_W = { obchody: "bhp-obchody", dokumenty: "bhp-dokumenty" };
const STATUSY = [["ok", "✓ OK"], ["uw", "! Uwaga"], ["nd", "Nie dotyczy"]];
const CIEZKOSC = ["mała", "średnia", "duża"];
const PRAWDOPODOBIENSTWO = ["mało prawdopodobne", "prawdopodobne", "wysoce prawdopodobne"];
// Skala trzystopniowa PN-N-18002: [ciężkość][prawdopodobieństwo] → 0 małe, 1 średnie, 2 duże.
const MACIERZ_RYZYKA = [[0, 0, 1], [0, 1, 2], [1, 2, 2]];
const RYZYKO = ["małe", "średnie", "duże"];
const KLASA_RYZYKA = ["ok", "wait", ""];

stan.warsztat = null;

TRASY.push(
  [/^#\/warsztat$/, () => widokWarsztat()],
  [/^#\/obchod\/nowy$/, () => nowyObchod()],
  [/^#\/obchod\/(\w+)$/, (m) => widokObchod(m[1])],
  [/^#\/obchod\/(\w+)\/raport$/, (m) => widokRaportu(m[1])],
  [/^#\/wzor\/(\w+)\/nowy$/, (m) => nowyDokument(m[1])],
  [/^#\/wzor\/(\w+)\/(\w+)$/, (m) => widokWzoru(m[1], m[2])],
  [/^#\/wzor\/(\w+)\/(\w+)\/gotowe$/, (m) => widokGotowego(m[1], m[2])],
);

async function wczytajWarsztat() {
  if (!stan.warsztat) {
    stan.warsztat = await fetch("data/warsztat.json").then((r) => r.json());
  }
  return stan.warsztat;
}

function noweId() {
  return Date.now().toString(36);
}

function pole(etykieta, wartosc, atrybuty) {
  return `<label class="pole"><span>${esc(etykieta)}</span><input ${atrybuty} value="${esc(wartosc || "")}"></label>`;
}

// Podstawa prawna jako tekst do raportu: "§ 4 ust. 1 pkt 14 - Ochrona ppoż. budynków (ISAP: …)".
function podstawa(zr) {
  if (zr.a) {
    const akt = stan.aktyMapa[zr.a];
    const j = akt.jednostki.find((x) => x.id === zr.j);
    return { etykieta: `${j.etykieta}${zr.u ? " " + zr.u : ""} - ${akt.nazwa}`, isap: akt.tekst.isap };
  }
  const o = stan.obserwowane.akty.find((x) => x.eli === zr.dok.replace(/^DU_(\d+)_(\d+)$/, "DU/$1/$2"));
  return { etykieta: `${zr.u} - ${o ? o.nazwa : zr.dok}`, isap: o ? o.isap : "" };
}

function przyciskiEksportu(funkcja) {
  return `<div class="btn-row no-print"><button class="btn" onclick="${funkcja}('kopiuj')">Kopiuj tekst</button><button class="btn secondary" onclick="${funkcja}('udostepnij')">Udostępnij</button></div>
    <div class="btn-row no-print"><button class="btn secondary" onclick="window.print()">Drukuj / zapisz PDF</button></div>`;
}

async function eksportuj(tytul, tresc, jak) {
  if (jak === "udostepnij" && navigator.share) {
    try {
      await navigator.share({ title: tytul, text: tresc });
      return;
    } catch (e) {
      // Anulowane udostępnianie - nic nie robimy.
      return;
    }
  }
  try {
    await navigator.clipboard.writeText(tresc);
    pokazKomunikat("✓ Skopiowano - wklej do maila, SMS-a lub notatki.");
  } catch (e) {
    pokazKomunikat("Nie udało się skopiować - użyj Drukuj / zapisz PDF.");
  }
}

// ── Lista warsztatu ──

async function widokWarsztat() {
  ustawNaglowek("Warsztat", "back");
  ustawZakladke("start");
  const w = await wczytajWarsztat();
  const obchody = czytaj(KLUCZ_W.obchody, []);
  const dokumenty = czytaj(KLUCZ_W.dokumenty, []);
  const punktow = w.obchod.reduce((s, x) => s + x.punkty.length, 0);
  widok.innerHTML = `
    <div class="section-header"><div class="section-title">Warsztat</div>
    <div class="section-sub">${tekst("Obchód obiektu z listą kontrolną i wzory dokumentów. Każdy punkt ma podstawę prawną. Zapisuje się tylko w tym telefonie.")}</div></div>
    <div class="section-label">Obchód obiektu</div>
    <div class="list-group">
      <a class="row" href="#/obchod/nowy">${kafel("🔍", "#c0392b")}<span class="row-main"><span class="row-title">Nowy obchód</span><span class="row-sub">${tekst(`${punktow} punktów w ${w.obchod.length} działach → gotowe zalecenia z paragrafami`)}</span></span><span class="row-chev">›</span></a>
      ${obchody.map((o) => {
        const uw = Object.values(o.odp).filter((x) => x.s === "uw").length;
        return `<a class="row" href="#/obchod/${o.id}">${kafel("📍", "#3a3a3c")}<span class="row-main"><span class="row-title">${esc(o.nazwa || "Obiekt bez nazwy")}</span><span class="row-sub">${esc(data(o.data))} · ${Object.keys(o.odp).length}/${punktow} sprawdzonych${uw ? ` · ${uw} uwag` : ""}</span></span><span class="row-chev">›</span></a>`;
      }).join("")}
    </div>
    <div class="section-label">Wzory dokumentów</div>
    <div class="list-group">
      ${w.wzory.map((x) => `<a class="row" href="#/wzor/${x.id}/nowy">${kafel(x.ikona, x.kolor)}<span class="row-main"><span class="row-title">${esc(x.tytul)}</span><span class="row-sub">${tekst(x.opis)}</span></span><span class="row-chev">›</span></a>`).join("")}
    </div>
    ${dokumenty.length ? `<div class="section-label">Moje dokumenty</div><div class="list-group">${dokumenty.map((d) => {
      const x = w.wzory.find((y) => y.id === d.wzor);
      return `<a class="row" href="#/wzor/${d.wzor}/${d.id}">${kafel(x.ikona, x.kolor)}<span class="row-main"><span class="row-title">${esc(d.glowa[x.glowa[0]] || d.glowa[x.glowa[1]] || "Bez nazwy")}</span><span class="row-sub">${esc(x.tytul)} · ${esc(data(d.utworzono))}</span></span><span class="row-chev">›</span></a>`;
    }).join("")}</div>` : ""}
    <div class="foot">${tekst("To narzędzie pomocnicze - nie zastępuje przepisów techniczno-budowlanych ani projektu. W razie wątpliwości otwórz paragraf w aplikacji lub w ISAP.")}</div>`;
}

// ── Obchód ──

function nowyObchod() {
  const lista = czytaj(KLUCZ_W.obchody, []);
  const o = { id: noweId(), nazwa: "", adres: "", data: dzisIso(), obecni: "", odp: {} };
  lista.unshift(o);
  zapisz(KLUCZ_W.obchody, lista);
  location.replace(`#/obchod/${o.id}`);
}

function znajdzObchod(id) {
  const lista = czytaj(KLUCZ_W.obchody, []);
  return { lista, o: lista.find((x) => x.id === id) };
}

function kartaPunktu(p, odp) {
  const s = odp ? odp.s : "";
  return `<div class="card punkt ${s}" id="pkt-${p.id}">
    <p>${tekst(p.co)}</p>
    <div class="links">${zrodloCiekawostki(p.zr)}</div>
    <div class="seg stan-seg">${STATUSY.map(([k, n]) => `<button class="${s === k ? "on " + k : ""}" onclick="ustawPunkt('${p.id}','${k}')">${n}</button>`).join("")}</div>
    ${s === "uw" ? `<textarea class="notatka" placeholder="Co dokładnie stwierdzono? np. gaśnica przy kasie zastawiona kartonami" oninput="notatkaPunktu('${p.id}', this.value)">${esc(odp.n || "")}</textarea>
      <p class="zal"><b>Zalecenie:</b> ${tekst(p.zal)}</p>` : ""}
  </div>`;
}

async function widokObchod(id) {
  ustawNaglowek("Obchód obiektu", "#/warsztat");
  ustawZakladke("start");
  const w = await wczytajWarsztat();
  const { o } = znajdzObchod(id);
  if (!o) {
    location.replace("#/warsztat");
    return;
  }
  stan.obchodId = id;
  widok.innerHTML = `
    <div class="card">
      ${pole("Obiekt", o.nazwa, `placeholder="np. Sklep spożywczy Kowalski" oninput="daneObchodu('nazwa', this.value)"`)}
      ${pole("Adres", o.adres, `placeholder="ulica, miejscowość" oninput="daneObchodu('adres', this.value)"`)}
      ${pole("Data", o.data, `type="date" oninput="daneObchodu('data', this.value)"`)}
      ${pole("Obecni przy obchodzie", o.obecni, `placeholder="np. właściciel Jan Kowalski" oninput="daneObchodu('obecni', this.value)"`)}
    </div>
    <div class="card info" id="postep-obchodu"></div>
    ${w.obchod.map((sek) => `<div class="section-label">${sek.ikona} ${esc(sek.tytul)}</div>${sek.punkty.map((p) => kartaPunktu(p, o.odp[p.id])).join("")}`).join("")}
    <div class="btn-row"><a class="btn" href="#/obchod/${id}/raport">Zalecenia i raport ›</a></div>
    <div class="btn-row"><button class="btn secondary" onclick="usunObchod('${id}')">Usuń ten obchód</button></div>
    <div class="foot">${tekst("Zaznacz „Nie dotyczy”, gdy wymaganie nie obejmuje tego obiektu (np. brak hydrantów). Dotknij paragrafu, żeby przeczytać przepis.")}</div>`;
  odswiezPostep();
}

function odswiezPostep() {
  const { o } = znajdzObchod(stan.obchodId);
  const wszystkich = stan.warsztat.obchod.reduce((s, x) => s + x.punkty.length, 0);
  const odp = Object.values(o.odp);
  const uw = odp.filter((x) => x.s === "uw").length;
  document.getElementById("postep-obchodu").innerHTML = `<p><b>${odp.length}/${wszystkich}</b> sprawdzonych · <b>${uw}</b> ${uw === 1 ? "uwaga" : "uwag"}</p>
    <div class="pasek"><span style="width:${Math.round((odp.length / wszystkich) * 100)}%"></span></div>`;
}

function daneObchodu(pole, wartosc) {
  const { lista, o } = znajdzObchod(stan.obchodId);
  o[pole] = wartosc;
  zapisz(KLUCZ_W.obchody, lista);
}

function ustawPunkt(pid, s) {
  const { lista, o } = znajdzObchod(stan.obchodId);
  const stary = o.odp[pid];
  if (stary && stary.s === s) {
    delete o.odp[pid];
  } else {
    o.odp[pid] = { s, n: stary ? stary.n : "" };
  }
  zapisz(KLUCZ_W.obchody, lista);
  const p = stan.warsztat.obchod.flatMap((x) => x.punkty).find((x) => x.id === pid);
  document.getElementById(`pkt-${pid}`).outerHTML = kartaPunktu(p, o.odp[pid]);
  odswiezPostep();
}

function notatkaPunktu(pid, tresc) {
  const { lista, o } = znajdzObchod(stan.obchodId);
  o.odp[pid].n = tresc;
  zapisz(KLUCZ_W.obchody, lista);
}

function usunObchod(id) {
  if (!confirm("Usunąć ten obchód z telefonu? Tego nie da się cofnąć.")) {
    return;
  }
  zapisz(KLUCZ_W.obchody, czytaj(KLUCZ_W.obchody, []).filter((x) => x.id !== id));
  location.replace("#/warsztat");
}

// Raport: najpierw uwagi z zaleceniami i podstawą prawną, potem lista tego, co jest w porządku.
function blokiRaportu(o) {
  const bloki = [["h1", "Protokół z obchodu - zalecenia ppoż i BHP"]];
  bloki.push(["p", `Obiekt: ${o.nazwa || "-"}`], ["p", `Adres: ${o.adres || "-"}`], ["p", `Data obchodu: ${data(o.data)}`]);
  if (o.obecni) {
    bloki.push(["p", `Obecni: ${o.obecni}`]);
  }
  const punkty = stan.warsztat.obchod.flatMap((sek) => sek.punkty.map((p) => ({ ...p, sek: sek.tytul })));
  const uwagi = punkty.filter((p) => o.odp[p.id] && o.odp[p.id].s === "uw");
  const dobre = punkty.filter((p) => o.odp[p.id] && o.odp[p.id].s === "ok");
  bloki.push(["h2", uwagi.length ? `Stwierdzone nieprawidłowości i zalecenia (${uwagi.length})` : "Nie stwierdzono nieprawidłowości"]);
  uwagi.forEach((p, i) => {
    const pod = podstawa(p.zr);
    bloki.push(["h3", `${i + 1}. ${p.sek}`]);
    if (o.odp[p.id].n) {
      bloki.push(["p", `Stwierdzono: ${o.odp[p.id].n}`]);
    }
    bloki.push(["p", `Zalecenie: ${p.zal}`], ["zr", `Podstawa: ${pod.etykieta}`, pod.isap]);
  });
  if (dobre.length) {
    bloki.push(["h2", `W porządku (${dobre.length})`]);
    dobre.forEach((p) => bloki.push(["li", p.co]));
  }
  bloki.push(["p", "Przyjąłem do wiadomości (data, podpis właściciela lub zarządcy): ……………………………"]);
  return bloki;
}

function blokiNaHtml(bloki) {
  return bloki.map(([typ, t, url]) => {
    if (typ === "zr") {
      return `<p class="zr">${tekst(t)}${url ? ` <a href="${url}" target="_blank" rel="noopener">ISAP ↗</a>` : ""}</p>`;
    }
    return typ === "li" ? `<p class="li">• ${tekst(t)}</p>` : `<${typ}>${tekst(t)}</${typ}>`;
  }).join("");
}

function blokiNaTekst(bloki) {
  return bloki.map(([typ, t, url]) => {
    if (typ === "h1" || typ === "h2") {
      return `\n${t.toUpperCase()}`;
    }
    if (typ === "zr") {
      return url ? `${t}\n${url}` : t;
    }
    return typ === "li" ? `- ${t}` : t;
  }).join("\n").trim();
}

async function widokRaportu(id) {
  ustawNaglowek("Zalecenia", `#/obchod/${id}`);
  ustawZakladke("start");
  await wczytajWarsztat();
  const { o } = znajdzObchod(id);
  if (!o) {
    location.replace("#/warsztat");
    return;
  }
  stan.raport = blokiRaportu(o);
  widok.innerHTML = `${przyciskiEksportu("eksportRaportu")}
    <div class="card dokument">${blokiNaHtml(stan.raport)}</div>
    <div class="foot no-print">${tekst("Zalecenia są oparte na przepisach z aplikacji. Przed wysłaniem klientowi przeczytaj je i popraw, jeśli trzeba.")}</div>`;
}

function eksportRaportu(jak) {
  eksportuj("Zalecenia z obchodu", blokiNaTekst(stan.raport), jak);
}

// ── Wzory dokumentów ──

function nowyDokument(wzor) {
  const lista = czytaj(KLUCZ_W.dokumenty, []);
  const d = { id: noweId(), wzor, utworzono: dzisIso(), glowa: {}, pola: {}, wiersze: [] };
  lista.unshift(d);
  zapisz(KLUCZ_W.dokumenty, lista);
  location.replace(`#/wzor/${wzor}/${d.id}`);
}

function znajdzDokument(id) {
  const lista = czytaj(KLUCZ_W.dokumenty, []);
  return { lista, d: lista.find((x) => x.id === id) };
}

// Każda zmiana zapisuje się od razu - dane są małe, a opóźniony zapis nadpisywałby późniejsze zmiany.
function zmienDokument(zmiana) {
  const { lista, d } = znajdzDokument(stan.dokumentId);
  zmiana(d);
  zapisz(KLUCZ_W.dokumenty, lista);
}

function ryzyko(wiersz) {
  if (wiersz.c === undefined || wiersz.p === undefined) {
    return null;
  }
  return MACIERZ_RYZYKA[wiersz.c][wiersz.p];
}

function kartaZagrozenia(wiersz, i) {
  const r = ryzyko(wiersz);
  const wybor = (pole, opcje) => `<div class="seg mini">${opcje.map((n, k) => `<button class="${wiersz[pole] === k ? "on" : ""}" onclick="ustawWiersz(${i},'${pole}',${k})">${n}</button>`).join("")}</div>`;
  const tekstowe = (pole, etykieta, ph) => `<label class="pole"><span>${etykieta}</span><textarea placeholder="${ph}" oninput="zmienDokument((d)=>d.wiersze[${i}].${pole}=this.value)">${esc(wiersz[pole] || "")}</textarea></label>`;
  return `<div class="card" id="zag-${i}">
    <div class="zag-head"><b>${i + 1}. ${esc(wiersz.z)}</b>${r === null ? "" : `<span class="row-tag ${KLASA_RYZYKA[r]}">ryzyko ${RYZYKO[r]}</span>`}</div>
    ${tekstowe("zrodlo", "Źródło zagrożenia", "np. mokra podłoga na zapleczu")}
    ${tekstowe("skutki", "Możliwe skutki", "np. złamanie, stłuczenie")}
    <div class="pole"><span>Ciężkość skutków</span>${wybor("c", CIEZKOSC)}</div>
    <div class="pole"><span>Prawdopodobieństwo</span>${wybor("p", PRAWDOPODOBIENSTWO)}</div>
    ${tekstowe("srodki", "Środki, które już są", "np. obuwie antypoślizgowe, oznakowanie")}
    ${tekstowe("dodatkowe", "Środki do wdrożenia (termin, kto)", "np. mata antypoślizgowa - do 30.11, kierownik")}
    <button class="chip" onclick="usunWiersz(${i})">Usuń zagrożenie</button>
  </div>`;
}

function ustawWiersz(i, pole, k) {
  zmienDokument((d) => (d.wiersze[i][pole] = k));
  const { d } = znajdzDokument(stan.dokumentId);
  document.getElementById(`zag-${i}`).outerHTML = kartaZagrozenia(d.wiersze[i], i);
}

function dodajZagrozenie(nazwa) {
  const z = nazwa || prompt("Nazwa zagrożenia");
  if (!z) {
    return;
  }
  zmienDokument((d) => d.wiersze.push({ z }));
  widokWzoru("orz", stan.dokumentId);
}

function usunWiersz(i) {
  zmienDokument((d) => d.wiersze.splice(i, 1));
  widokWzoru("orz", stan.dokumentId);
}

async function widokWzoru(wzorId, id, zostanNaMiejscu) {
  const w = await wczytajWarsztat();
  const x = w.wzory.find((y) => y.id === wzorId);
  const { d } = znajdzDokument(id);
  if (!x || !d) {
    location.replace("#/warsztat");
    return;
  }
  ustawNaglowek(x.tytul, "#/warsztat");
  ustawZakladke("start");
  stan.dokumentId = id;
  const przewiniecie = window.scrollY;
  const kroki = (x.kroki || []).map((k, i) => `<div class="card">
      <h3>${k.nr ? `Pkt ${k.nr}` : i + 1}. ${tekst(k.tytul)}</h3>
      <p class="pomoc">${tekst(k.pomoc)}</p>
      ${k.przyklad ? `<p class="pomoc"><i>Przykład: ${tekst(k.przyklad)}</i></p>` : ""}
      ${k.podstawa ? `<p class="pomoc"><b>Podstawa prawna:</b> ${tekst(k.podstawa)}</p>` : ""}
      ${k.zr ? `<div class="links">${zrodloCiekawostki(k.zr)}</div>` : ""}
      <textarea class="notatka" oninput="zmienDokument((d)=>d.pola['${k.id}']=this.value)">${esc(d.pola[k.id] || "")}</textarea>
    </div>`).join("");
  const zagrozenia = x.zagrozenia ? `
    <div class="section-label">Zagrożenia (${d.wiersze.length})</div>
    ${d.wiersze.map(kartaZagrozenia).join("")}
    <div class="card"><h3>Dodaj zagrożenie</h3><p class="pomoc">${tekst("Dotknij typowego zagrożenia albo wpisz własne.")}</p>
      <div class="links">${x.zagrozenia.map((z) => `<button class="chip" onclick="dodajZagrozenie(this.textContent)">${esc(z)}</button>`).join("")}<button class="chip red" onclick="dodajZagrozenie()">+ Własne</button></div></div>` : "";
  widok.innerHTML = `
    <div class="section-header"><div class="section-title">${tekst(x.tytul)}</div><div class="section-sub">${tekst(x.opis)}</div></div>
    <div class="card amber">${x.uwagi.map((u) => `<div class="uwaga-wzoru"><p>${tekst(u.t)}</p><div class="links">${zrodloCiekawostki(u.zr)}</div></div>`).join("")}</div>
    <div class="card">${x.glowa.map((g) => pole(g, d.glowa[g], `oninput="zmienDokument((d)=>d.glowa[${JSON.stringify(g).replace(/"/g, "&quot;")}]=this.value)"`)).join("")}</div>
    ${kroki}${zagrozenia}
    <div class="btn-row"><a class="btn" href="#/wzor/${wzorId}/${id}/gotowe">Gotowy dokument ›</a></div>
    <div class="btn-row"><button class="btn secondary" onclick="usunDokument('${id}')">Usuń dokument</button></div>`;
  if (zostanNaMiejscu) {
    window.scrollTo(0, przewiniecie);
  }
}

function usunDokument(id) {
  if (!confirm("Usunąć ten dokument z telefonu? Tego nie da się cofnąć.")) {
    return;
  }
  zapisz(KLUCZ_W.dokumenty, czytaj(KLUCZ_W.dokumenty, []).filter((x) => x.id !== id));
  location.replace("#/warsztat");
}

function blokiDokumentu(x, d) {
  const bloki = [["h1", x.tytul]];
  x.glowa.forEach((g) => bloki.push(["p", `${g}: ${d.glowa[g] || "-"}`]));
  (x.kroki || []).forEach((k, i) => {
    // Praca projektowa ma gotowe brzmienie podstawy (pełny tytuł aktu i Dz.U.), pozostałe wzory - z paragrafu.
    if (k.podstawa) {
      bloki.push(["h2", `${k.nr}. ${k.tytul}`], ["p", d.pola[k.id] || "(do uzupełnienia)"], ["zr", `Podstawa prawna: ${k.podstawa}`]);
      return;
    }
    const pod = podstawa(k.zr);
    bloki.push(["h2", `${i + 1}. ${k.tytul}`], ["p", d.pola[k.id] || "(do uzupełnienia)"], ["zr", `Podstawa: ${pod.etykieta}`, pod.isap]);
  });
  if (x.zalaczniki) {
    bloki.push(["h2", "Załączniki graficzne (obowiązkowe)"]);
    x.zalaczniki.forEach((z) => bloki.push(["li", z]));
  }
  if (x.podstawy) {
    bloki.push(["h2", "Podstawy prawne"]);
    x.podstawy.forEach((pp, i) => bloki.push(["p", `${i + 1}. ${pp}`]));
  }
  if (x.zagrozenia) {
    bloki.push(["h2", "Zidentyfikowane zagrożenia"]);
    d.wiersze.forEach((r, i) => {
      const poziom = ryzyko(r);
      bloki.push(["h3", `${i + 1}. ${r.z}`]);
      bloki.push(["p", `Źródło: ${r.zrodlo || "-"}`], ["p", `Możliwe skutki: ${r.skutki || "-"}`]);
      bloki.push(["p", `Ciężkość: ${r.c === undefined ? "-" : CIEZKOSC[r.c]} · Prawdopodobieństwo: ${r.p === undefined ? "-" : PRAWDOPODOBIENSTWO[r.p]} · Ryzyko: ${poziom === null ? "-" : RYZYKO[poziom].toUpperCase()}`]);
      bloki.push(["p", `Środki istniejące: ${r.srodki || "-"}`], ["p", `Środki do wdrożenia: ${r.dodatkowe || "-"}`]);
    });
    const pod = podstawa(x.zr);
    bloki.push(["zr", `Podstawa: ${pod.etykieta}. Metoda: skala trzystopniowa wg PN-N-18002.`, pod.isap]);
    bloki.push(["p", "Zapoznałem się z oceną ryzyka zawodowego (data, imię i nazwisko, podpis pracownika): ……………………………"]);
  }
  return bloki;
}

async function widokGotowego(wzorId, id) {
  const w = await wczytajWarsztat();
  const x = w.wzory.find((y) => y.id === wzorId);
  const { d } = znajdzDokument(id);
  if (!x || !d) {
    location.replace("#/warsztat");
    return;
  }
  ustawNaglowek("Gotowy dokument", `#/wzor/${wzorId}/${id}`);
  ustawZakladke("start");
  stan.gotowy = { tytul: x.tytul, bloki: blokiDokumentu(x, d), x, d };
  widok.innerHTML = `${x.word ? `<div class="btn-row no-print"><button class="btn" onclick="pobierzWord()">📄 Pobierz plik Word (.doc)</button></div>` : ""}
    ${przyciskiEksportu("eksportDokumentu")}
    <div class="card dokument">${blokiNaHtml(stan.gotowy.bloki)}</div>
    <div class="foot no-print">${tekst("Szkic do dopracowania - przeczytaj całość przed podpisaniem lub wysłaniem.")}</div>`;
}

function eksportDokumentu(jak) {
  eksportuj(stan.gotowy.tytul, blokiNaTekst(stan.gotowy.bloki), jak);
}

// ── Praca projektowa jako plik Word ──
// Word otwiera HTML zapisany jako .doc - tak powstaje plik w formacie z wytycznych:
// strona tytułowa, tabela (Pkt | Wymagania | Analiza | Podstawa prawna), Times New Roman 10 pkt, interlinia 1,0.
const SPRAWDZAJACY = "kpt. Ariel Włodarczyk";

function nazwaPlikuPracy(d, x) {
  const [imie = "imie", ...reszta] = (d.glowa[x.glowa[0]] || "").trim().split(/\s+/).filter(Boolean);
  const nazwisko = reszta.length ? reszta[reszta.length - 1] : "nazwisko";
  const termin = (d.glowa[x.glowa[3]] || "").match(/(\d{1,2})\.(\d{1,2})(?:\.\d{2}(\d{2}))?/);
  const data = termin ? `${termin[1].padStart(2, "0")}.${termin[2].padStart(2, "0")}.${termin[3] || String(new Date().getFullYear()).slice(2)}` : "";
  return `${bezOgonkow(nazwisko)}_${bezOgonkow(imie)}${data ? "_" + data : ""}.doc`;
}

function pobierzWord() {
  const { x, d } = stan.gotowy;
  const g = (i) => esc(d.glowa[x.glowa[i]] || "…");
  const wiersze = x.kroki.map((k) => `<tr><td>${esc(k.nr)}</td><td>${esc(k.tytul)}</td><td>${esc(d.pola[k.id] || "").replace(/\n/g, "<br>")}</td><td>${esc(k.podstawa)}</td></tr>`).join("");
  const html = `<html><head><meta charset="utf-8"><style>
    body { font-family: "Times New Roman", serif; font-size: 10pt; line-height: 1.0; }
    td, th { font-family: "Times New Roman", serif; font-size: 10pt; border: 1px solid #000; padding: 3pt; vertical-align: top; }
    table { border-collapse: collapse; width: 100%; } th { background: #d9d9d9; }
    .tytul { text-align: center; } h1 { font-size: 16pt; } h2 { font-size: 12pt; }
  </style></head><body>
    <div class="tytul"><p style="font-size:14pt">Centralna Szkoła Państwowej Straży Pożarnej<br>Szkolenie inspektorów ochrony przeciwpożarowej</p>
    <p>Termin szkolenia: ${g(3)}</p><br><br><p style="font-size:12pt"><b>${g(0)}</b></p><br><br>
    <h1>ANALIZA BEZPIECZEŃSTWA POŻAROWEGO BUDYNKU ${g(1).toUpperCase()}</h1><p>${g(2)}</p><br><br>
    <p style="text-align:right">Sprawdzający:<br><b>${SPRAWDZAJACY}</b></p><br><br><p>Częstochowa ${new Date().getFullYear()} r.</p></div>
    <br style="page-break-before:always">
    <h2 style="text-align:center">ANALIZA ZAGROŻENIA POŻAROWEGO</h2>
    <table><tr><th>Pkt</th><th>Wymagania</th><th>Analiza, opis, parametr, komentarz</th><th>Podstawa prawna</th></tr>${wiersze}</table>
    <h2>Załączniki</h2>${x.zalaczniki.map((z) => `<p>• ${esc(z)}</p>`).join("")}
    <h2>Podstawy prawne</h2>${x.podstawy.map((p, i) => `<p>${i + 1}. ${esc(p)}</p>`).join("")}
  </body></html>`;
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob(["﻿" + html], { type: "application/msword" }));
  a.download = nazwaPlikuPracy(d, x);
  document.body.appendChild(a);
  a.click();
  a.remove();
  pokazKomunikat(`Zapisano ${a.download}. Otwórz w Wordzie lub Pages i dopracuj.`);
}
