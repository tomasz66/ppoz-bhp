# Buduje teksty aktów prawnych do czytnika w aplikacji: app/data/dok/DU_RRRR_POZ.json.
# Obejmuje akty BHP (aktualny tekst jednolity z API Sejmu) oraz akty zmieniające
# z zakładki Nowości i listy zmian. Teksty aktów prawnych nie są chronione prawem autorskim
# (art. 4 ustawy o prawie autorskim), więc mogą być w całości w aplikacji.
# Użycie: python3 skrypty/zbuduj_teksty.py   (z folderu bhp-ppoz)
import json
import os
import re
import subprocess
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from parsuj_html import Parser  # noqa: E402
from stary_pdf_na_tekst import main as stary_pdf  # noqa: E402

API = "https://api.sejm.gov.pl/eli/acts/"
ISAP = "https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id="
ZRODLA = "zrodla/dok"
WYJSCIE = "app/data/dok"
ROK_NOWYCH_PDF = 2012

# Akty, które aplikacja ma już w pełnej, ręcznie sprawdzonej wersji (zakładka Przepisy).
W_APLIKACJI = {"DU/1991/351": "ustawa-ppoz", "DU/2010/719": "rozp-ochrona-budynkow", "DU/2009/1030": "rozp-woda-drogi"}

NAGLOWEK = re.compile(r"^(Dziennik Ustaw( Nr \d+)?|–\s*\d+\s*–|Poz\. \d+|\d+)$")
PRZYPIS = re.compile(r"^(W brzmieniu ustalonym|Dodan[yae]|Uchylon[yae]|Ze zmianą|Zmienion|Utracił|Utraciła|Przez art|Zmiany tekstu|Obecnie|Na podstawie art|Niniejsz|Minister |Prezes Rady|Zmiany wymienion|Stosuje się|Ustawa została|Rozporządzenie zostało|Część wspólna)")
ZNACZNIK = re.compile(r"^\d+[a-z]*\)$")
NUMER = r"\d+[a-z]*(?:\[\w+\])?[a-z]*"


def api(eli):
    with urllib.request.urlopen(API + eli, timeout=60) as r:
        return json.load(r)


def pobierz_plik(url, sciezka):
    if not os.path.exists(sciezka):
        with urllib.request.urlopen(url, timeout=120) as r:
            open(sciezka, "wb").write(r.read())


def isap_id(eli):
    _, rok, poz = eli.split("/")
    return f"WDU{rok}{int(poz):07d}"


def wdu_na_eli(wdu):
    # WDU20260000927 -> DU/2026/927; przed 2012 r. ISAP koduje numer Dz.U.: WDU19740240141 -> DU/1974/141
    rok, reszta = int(wdu[3:7]), wdu[7:]
    return f"DU/{rok}/{int(reszta[3:]) if rok < ROK_NOWYCH_PDF else int(reszta)}"


def plik(eli):
    return eli.replace("/", "_")


# ── Tekst z PDF ──

def oczysc(linie):
    # Usuwa nagłówki stron i bloki przypisów (seria "1)" "2)" + treść przypisu aż do nagłówka strony).
    wynik, i = [], 0
    while i < len(linie):
        s = linie[i].strip()
        if ZNACZNIK.match(s):
            j = i
            while j < len(linie) and (ZNACZNIK.match(linie[j].strip()) or not linie[j].strip()):
                j += 1
            if j < len(linie) and PRZYPIS.match(linie[j].strip()):
                while j < len(linie) and not NAGLOWEK.match(linie[j].strip()):
                    j += 1
                i = j
                continue
        if NAGLOWEK.match(s) or s == "﻿":
            i += 1
            continue
        wynik.append(linie[i])
        i += 1
    return wynik


def scal(linie):
    out, czekajacy = [], None
    for l in linie:
        s = l.strip().lstrip("﻿")
        if not s:
            continue
        if ZNACZNIK.match(s) or re.match(r"^[a-z]\)$", s):
            czekajacy = s
            continue
        if czekajacy:
            s = czekajacy + " " + s
            czekajacy = None
        out.append(s)
    return out


def poziom(s, rodzaj):
    if rodzaj == "art" and re.match(rf"^§ {NUMER}\. ", s):
        return 2
    if re.match(r"^\d+[a-z]*\. ", s):
        return 2 if rodzaj == "par" else 3
    if re.match(r"^\d+[a-z]*\)", s):
        return 3
    if re.match(r"^[a-z]\) ", s):
        return 4
    if s.startswith("– "):
        return 5
    return None


def ladna_etykieta(e):
    # "Art. 94[3]" -> "Art. 94³" (indeks górny jak w Dzienniku Ustaw)
    gorne = str.maketrans("0123456789abcdefghijklmnoprstuwxyz", "⁰¹²³⁴⁵⁶⁷⁸⁹ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘʷˣʸᶻ")
    return re.sub(r"\[(\w+)\]", lambda m: m.group(1).translate(gorne), e)


def jednostki_z_tekstu(tekst):
    # Akt jednolity: tekst zaczyna się po "Załącznik do obwieszczenia".
    i = tekst.find("Załącznik do obwieszczenia")
    if i > 0:
        tekst = tekst[i:]
    rodzaj = "art" if re.search(r"^Art\. 1\.", tekst, re.M) else "par"
    m = re.search(r"^Art\. 1\." if rodzaj == "art" else r"^§ 1\.", tekst, re.M)
    if m:
        poczatek = tekst.rfind("\nRozdział", 0, m.start())
        poczatek = poczatek if poczatek > 0 and m.start() - poczatek < 400 else m.start()
        tekst = tekst[poczatek:]
    linie = scal(oczysc(tekst.split("\n")))
    wzor = re.compile(rf"^(Art\.|§)\s?({NUMER})\s?\.(\d+\))?\s*(.*)$")
    jednostki, rozdzial, obecna, i, uzyte = [], "", None, 0, {}
    while i < len(linie):
        s = linie[i]
        if re.match(r"^(Rozdział|DZIAŁ|Dział) [\dIVXLa-z]+$", s):
            rozdzial = s + (" " + linie[i + 1] if i + 1 < len(linie) else "")
            i += 2
            continue
        m = wzor.match(s)
        jest_jednostka = m and ((m.group(1) == "Art.") if rodzaj == "art" else (m.group(1) == "§"))
        if jest_jednostka:
            etyk = ("Art. " if rodzaj == "art" else "§ ") + m.group(2)
            baza = re.sub(r"[^0-9a-z]", "", etyk.lower().replace("§", "p").replace("art.", "a").replace("[", "_"))
            uzyte[baza] = uzyte.get(baza, 0) + 1
            ident = baza if uzyte[baza] == 1 else f"{baza}_{uzyte[baza]}"
            obecna = {"id": ident, "etykieta": ladna_etykieta(etyk), "rozdzial": rozdzial, "linie": []}
            if uzyte[baza] > 1:
                obecna["uwaga"] = "Druga wersja tego przepisu w tekście jednolitym - zwykle nowe brzmienie, które wchodzi w życie później. Sprawdź przypis w PDF."
            jednostki.append(obecna)
            if m.group(4):
                obecna["linie"].append({"p": poziom(m.group(4), rodzaj) or 2, "t": m.group(4)})
            i += 1
            continue
        if obecna is not None:
            s = re.sub(r"^(\d+[a-z]*[.)])\d+\)\s*", r"\1 ", s)
            p = poziom(s, rodzaj)
            if p is None and obecna["linie"]:
                obecna["linie"][-1]["t"] += " " + s
            else:
                obecna["linie"].append({"p": p or 2, "t": s})
        i += 1
    for j in jednostki:
        for l in j["linie"]:
            l["t"] = re.split(r"\s(?:Minister [^:]{0,90}:|Prezydent Rzeczypospolitej Polskiej:|Prezes Rady Ministrów:|Marszałek Sejmu:)", l["t"])[0]
            l["t"] = re.sub(r"(?<=[a-ząćęłńóśźż.,;])\d{1,3}\)(?=[\s.,;§]|$)", "", l["t"])
            l["t"] = re.sub(r"\[(\w+)\]", lambda mm: ladna_etykieta(f"[{mm.group(1)}]"), l["t"])
    return jednostki


def tekst_aktu(eli, meta):
    rok = int(eli.split("/")[1])
    if meta.get("textHTML"):
        sciezka = f"{ZRODLA}/{plik(eli)}.html"
        pobierz_plik(API + eli + "/text.html", sciezka)
        p = Parser()
        p.feed(open(sciezka, encoding="utf-8").read())
        jedn = [j for j in p.jednostki if j.get("etykieta")]
        # W obwieszczeniu jednostki aktu zaczynają się od pierwszego rozdziału / § 1 załącznika.
        startowe = [k for k, j in enumerate(jedn) if j["id"].startswith(("chpt", "part", "sect")) or re.match(r"^(Art\. 1|§ 1)$", j["etykieta"].split("D")[0].strip())]
        if startowe and any(j["id"].startswith(("chpt", "part", "sect")) for j in jedn):
            jedn = [j for j in jedn if j["id"].startswith(("chpt", "part", "sect"))]
        for j in jedn:
            e = re.match(rf"^(§|Art\.)\s?({NUMER})", j["etykieta"])
            j["etykieta"] = ladna_etykieta(f"{e.group(1)} {e.group(2)}") if e else j["etykieta"]
            j["id"] = re.sub(r"[^0-9a-z_]", "", j["id"].split("-")[-1])
        widziane = {}
        for j in jedn:
            widziane[j["id"]] = widziane.get(j["id"], 0) + 1
            if widziane[j["id"]] > 1:
                j["id"] += f"_{widziane[j['id']]}"
        if jedn:
            return jedn
    pdf = f"{ZRODLA}/{plik(eli)}.pdf"
    txt = f"{ZRODLA}/{plik(eli)}.txt"
    pobierz_plik(API + eli + "/text.pdf", pdf)
    if rok < ROK_NOWYCH_PDF:
        stary_pdf(pdf, txt)
    else:
        subprocess.run(["pdftotext", pdf, txt], check=True)
    return jednostki_z_tekstu(open(txt, encoding="utf-8").read())


def zbuduj(eli, rola, zrodlo_eli=None, zmiany_po=None, streszczenie=None):
    meta = api(zrodlo_eli or eli)
    jedn = tekst_aktu(zrodlo_eli or eli, meta)
    glowny = api(eli) if zrodlo_eli else meta
    dok = {
        "eli": eli, "rola": rola, "tytul": glowny["title"], "status": glowny.get("status"),
        "isap": ISAP + glowny.get("address", isap_id(eli)),
        "pdf": API + (zrodlo_eli or eli) + "/text.pdf",
        "tekst": {"eli": zrodlo_eli or eli, "tytul": meta["title"], "isap": ISAP + meta.get("address", isap_id(zrodlo_eli or eli))},
        "ogloszono": glowny.get("announcementDate") or glowny.get("promulgation"),
        "wchodzi": glowny.get("entryIntoForce"),
        "zmiany_po": zmiany_po or [],
        "streszczenie": streszczenie or [],
        "jednostki": jedn,
    }
    json.dump(dok, open(f"{WYJSCIE}/{plik(eli)}.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    znakow = sum(len(l["t"]) for j in jedn for l in j["linie"])
    print(f"{eli:14} {rola:8} {len(jedn):4} jedn. {znakow:7} znaków  {glowny['title'][:60]}")
    return eli


def main():
    os.makedirs(ZRODLA, exist_ok=True)
    os.makedirs(WYJSCIE, exist_ok=True)
    obs = json.load(open("app/data/obserwowane.json", encoding="utf-8"))
    nowosci = json.load(open("app/data/nowosci.json", encoding="utf-8"))
    streszczenia = {}
    for n in nowosci:
        for z in n["zrodla"]:
            m = re.search(r"WDU\d{11}", z["url"])
            if m:
                streszczenia[wdu_na_eli(m.group(0))] = n["co"]
    gotowe = []

    # 1. Akty obserwowane (BHP i WT) - aktualny tekst jednolity + lista późniejszych zmian.
    for o in obs["akty"]:
        if o["eli"] in W_APLIKACJI:
            continue
        d = api(o["eli"])
        tj = d["references"].get("Inf. o tekście jednolitym", [])
        zrodlo = tj[0]["id"] if tj else o["eli"]
        # Zmiana jest poza tekstem jednolitym, jeśli ją OGŁOSZONO później niż ten tekst
        # (data wejścia w życie może być późniejsza, a tekst jednolity i tak ją zawiera).
        prom = api(zrodlo).get("promulgation") or ""
        po = []
        for z in d["references"].get("Akty zmieniające", []):
            if (z.get("date") or "") <= prom:
                continue
            ogl = api(z["id"]).get("promulgation") or ""
            if ogl > prom:
                po.append({"eli": z["id"], "od": z.get("date"), "isap": ISAP + isap_id(z["id"])})
        gotowe.append(zbuduj(o["eli"], "akt", zrodlo, po))

    # 2. Akty zmieniające - z listy zmian i ze źródeł w Nowościach.
    zmieniajace = {z["eli"] for o in obs["akty"] for z in o["ostatnie"]} | set(streszczenia) | {"DU/2026/1161"}
    for eli in sorted(zmieniajace):
        if eli in gotowe:
            continue
        try:
            gotowe.append(zbuduj(eli, "zmiana", streszczenie=streszczenia.get(eli)))
        except Exception as e:
            print("BŁĄD", eli, e)

    json.dump(sorted(gotowe), open(f"{WYJSCIE}/spis.json", "w", encoding="utf-8"))
    print("razem", len(gotowe))


if __name__ == "__main__":
    main()
