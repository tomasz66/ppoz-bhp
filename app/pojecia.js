// Karty pojęć: definicja z paragrafem, przykład z życia, typowy błąd, "jak powiedzieć klientowi",
// pytania do odsłaniania (o co ktoś może dopytać) i pojęcia powiązane. Dane: data/pojecia.json
// (skrypty/zbuduj_pojecia.py - każda definicja i odpowiedź sprawdzona z brzmieniem przepisu).

TRASY.push(
  [/^#\/pojecia$/, () => widokPojec()],
  [/^#\/pojecie\/([\w-]+)$/, (m) => widokPojecia(m[1])],
);

function wierszPojecia(k) {
  return `<a class="row" href="#/pojecie/${k.id}">${kafel(k.d === "bhp" ? "BHP" : "PPOŻ", k.d === "bhp" ? "#2f5d8a" : "#c0392b")}<span class="row-main">
    <span class="row-title">${esc(k.nazwa)}</span><span class="row-sub">${tekst(k.def.length > 110 ? k.def.slice(0, 110) + "…" : k.def)}</span></span><span class="row-chev">›</span></a>`;
}

function widokPojec() {
  ustawNaglowek("Karty pojęć", "back");
  ustawZakladke("nauka");
  const f = stan.filtrPojec || "all";
  const lista = stan.pojecia.filter((k) => f === "all" || k.d === f);
  widok.innerHTML = `
    <div class="section-header"><div class="section-title">Karty pojęć</div>
    <div class="section-sub">${tekst("Każde pojęcie: definicja z paragrafu, przykład z życia, typowy błąd, jak to powiedzieć klientowi i pytania, o które ktoś może dopytać.")}</div></div>
    <div class="seg">${[["all", "Wszystko"], ["ppoz", "PPOŻ"], ["bhp", "BHP"]].map(([k, n]) => `<button class="${f === k ? "on" : ""}" onclick="stan.filtrPojec='${k}';widokPojec()">${n}</button>`).join("")}</div>
    <div class="section-label">${lista.length} pojęć</div>
    <div class="list-group">${lista.map(wierszPojecia).join("")}</div>
    <div class="foot">${tekst("Pojęcia z warunków technicznych (WT 2002): akt uznany za uchylony, stosowany w okresie przejściowym - szczegóły w zakładce Nowości.")}</div>`;
}

function tekstPojecia(k) {
  return `${k.nazwa}. ${k.def} Przykład: ${k.przyklad} Typowy błąd: ${k.blad} Jak powiedzieć klientowi: ${k.klient}`;
}

function widokPojecia(id) {
  const k = stan.pojecia.find((x) => x.id === id);
  if (!k) {
    location.replace("#/pojecia");
    return;
  }
  ustawNaglowek(k.nazwa, "back");
  ustawZakladke("nauka");
  const powiazane = k.powiazane.map((p) => stan.pojecia.find((x) => x.id === p)).filter(Boolean);
  const kogo = stan.pojecia.filter((x) => x.powiazane.includes(k.id) && !k.powiazane.includes(x.id));
  widok.innerHTML = `
    <div class="unit-head"><div class="unit-label" style="font-size:26px">${tekst(k.nazwa)}</div><div class="unit-act">${k.d === "bhp" ? "BHP" : "Ochrona przeciwpożarowa"}</div></div>
    <div class="btn-row"><button class="btn secondary" onclick="czytajNaGlos(tekstPojecia(stan.pojecia.find((x)=>x.id==='${k.id}')))">▶ Czytaj na głos</button>
      <a class="btn" href="#/asystent" onclick="stan.przepytajPojecie='${k.id}'">🎓 Przepytaj mnie</a></div>
    <div class="card"><div class="fun-label">📖 Definicja</div><p>${tekst(k.def)}</p><div class="links">${zrodloCiekawostki(k.zr)}</div></div>
    <div class="card"><div class="fun-label">🏢 Przykład z życia</div><p>${tekst(k.przyklad)}</p></div>
    <div class="card amber"><div class="fun-label">⚠️ Typowy błąd w terenie</div><p>${tekst(k.blad)}</p></div>
    <div class="card"><div class="fun-label">💬 Jak powiedzieć klientowi</div><p><i>„${tekst(k.klient)}”</i></p></div>
    <div class="section-label">O co ktoś może dopytać · ${k.dopytania.length}</div>
    ${k.dopytania.map((p) => `<details class="card dopytanie"><summary>${tekst(p.q)}<span class="odslon">pokaż</span></summary>
      <p>${tekst(p.a)}</p><div class="links">${zrodloCiekawostki(p.zr)}</div></details>`).join("")}
    <p class="opis-trybu">${tekst("Najpierw odpowiedz sam - na głos albo w myślach - dopiero potem dotknij pytania.")}</p>
    ${powiazane.length || kogo.length ? `<div class="section-label">Pojęcia powiązane</div>
      <div class="links" style="margin:0 16px">${powiazane.concat(kogo).map((x) => `<a class="chip red" href="#/pojecie/${x.id}">${esc(x.nazwa)} ›</a>`).join("")}</div>` : ""}
    <div class="foot">${tekst("Definicje i odpowiedzi są sprawdzone z brzmieniem przepisu. Dotknij paragrafu, żeby przeczytać całość.")}</div>`;
}
