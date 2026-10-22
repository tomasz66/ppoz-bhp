# Dzieli tekst aktu z PDF Dziennika Ustaw (po pdftotext, bez -layout) na artykuły/paragrafy.
# Usuwa nagłówki stron i bloki przypisów. Wynik w tym samym formacie co parsuj_html.py.
# Użycie: python3 parsuj_pdf.py wejscie.txt wyjscie.json "znacznik startu" [art|par]
import json
import re
import sys

PRZYPIS = re.compile(r"^(W brzmieniu ustalonym|Dodan[yae]|Uchylon[yae]|Ze zmianą|Zmienion|Utracił|Utraciła|Przez art|Zmiany tekstu|Obecnie|Na podstawie art)")
NAGLOWEK = re.compile(r"^(Dziennik Ustaw|–\s*\d+\s*–|Poz\. \d+)$")
ZNACZNIK = re.compile(r"^\d+[a-z]*\)$")


def oczysc(linie):
    # Usuń bloki przypisów: seria "1)" "2)" a po niej treść przypisu - aż do nagłówka strony.
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
        if NAGLOWEK.match(s):
            i += 1
            continue
        wynik.append(linie[i])
        i += 1
    return wynik


def scal(linie):
    # Znacznik punktu w osobnej linii ("1)" + pusta + treść) łączymy z treścią.
    out, czekajacy = [], None
    for l in linie:
        s = l.strip()
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


def poziom(s):
    if re.match(r"^\d+[a-z]*\. ", s):
        return 2
    if re.match(r"^\d+[a-z]*\)", s):
        return 3
    if re.match(r"^[a-z]\) ", s):
        return 4
    if s.startswith("– "):
        return 5
    return None


def main(wej, wyj, start, rodzaj):
    tekst = open(wej, encoding="utf-8").read()
    tekst = tekst[tekst.index(start):]
    linie = scal(oczysc(tekst.split("\n")))
    wzor = re.compile(r"^(Art\.|§)\s?(\d+[a-z]*)\.(\d+\))?\s*(.*)$")
    jednostki, rozdzial, obecna, i = [], "", None, 0
    while i < len(linie):
        s = linie[i]
        if re.match(r"^Rozdział \d+[a-z]*$", s) or re.match(r"^DZIAŁ [IVX]+", s):
            tytul = linie[i + 1] if i + 1 < len(linie) else ""
            rozdzial = s + " " + tytul
            i += 2
            continue
        m = wzor.match(s)
        if m and (m.group(1) == "Art." if rodzaj == "art" else m.group(1) == "§"):
            etyk = ("Art. " if rodzaj == "art" else "§ ") + m.group(2)
            obecna = {"id": etyk.replace(" ", "").replace(".", "").lower(), "etykieta": etyk, "rozdzial": rozdzial, "linie": []}
            jednostki.append(obecna)
            reszta = m.group(4)
            if reszta:
                obecna["linie"].append({"p": poziom(reszta) or 2, "t": reszta})
            i += 1
            continue
        if obecna is not None:
            # Usuń odnośnik przypisu doklejony do znacznika, np. "2)1) działaniach" -> "2) działaniach".
            s = re.sub(r"^(\d+[a-z]*[.)])\d+\)\s*", r"\1 ", s)
            p = poziom(s)
            if p is None and obecna["linie"]:
                obecna["linie"][-1]["t"] += " " + s
            else:
                obecna["linie"].append({"p": p or 2, "t": s})
        i += 1
    json.dump(jednostki, open(wyj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(jednostki), "jednostek")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
