# Dzieli tekst aktu z HTML API Sejmu (klasy unit_chpt/para/pass/pint/lett) na jednostki.
# Wynik: lista paragrafów/artykułów z rozdziałem i liniami tekstu (wcięcie = poziom).
# Użycie: python3 parsuj_html.py wejscie.html wyjscie.json
import json
import re
import sys
from html.parser import HTMLParser

POZIOMY = {"unit_bran": 0, "unit_part": 0, "unit_chpt": 0, "unit_para": 1, "unit_arti": 1, "unit_pass": 2, "unit_pint": 3, "unit_lett": 4, "unit_tiret": 5}


class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stos = []          # (tag, rodzaj jednostki lub None)
        self.jednostki = []
        self.rozdzial = ""
        self.obecna = None
        self.tryb = None        # "h3" | "tekst" | "tytul"
        self.bufor = ""
        self.poziom = 0
        self.etykieta = ""
        self.przypis = 0        # >0 = jesteśmy w <a class="gloss-link"> (treść przypisu, pomijamy)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        klasy = (a.get("class") or "").split()
        rodzaj = next((k for k in klasy if k in POZIOMY), None)
        if tag == "a" and (self.przypis or "gloss-link" in klasy):
            self.przypis += 1
            return
        if tag == "div":
            self.stos.append(rodzaj)
            if rodzaj:
                self.poziom = POZIOMY[rodzaj]
                self.etykieta = ""
                if rodzaj in ("unit_para", "unit_arti"):
                    self.obecna = {"id": a.get("id"), "rozdzial": self.rozdzial, "linie": []}
                    self.jednostki.append(self.obecna)
            if a.get("data-template") == "xText":
                self.tryb, self.bufor = "tekst", ""
        elif tag == "h3":
            self.tryb, self.bufor = "h3", ""

    def handle_endtag(self, tag):
        if tag == "a" and self.przypis:
            self.przypis -= 1
            return
        if tag == "h3" and self.tryb == "h3":
            t = " ".join(self.bufor.split())
            if self.poziom == 0:
                self.rozdzial = t
            elif self.poziom == 1 and self.obecna is not None:
                self.obecna["etykieta"] = t.rstrip(".")
            else:
                self.etykieta = t
            self.tryb = None
        elif tag == "div" and self.stos:
            if self.tryb == "tekst" and self.stos[-1] is None:
                t = " ".join(self.bufor.split())
                if t and self.obecna is not None:
                    pref = self.etykieta + " " if self.etykieta else ""
                    self.obecna["linie"].append({"p": self.poziom, "t": pref + t})
                    self.etykieta = ""
                self.tryb = None
            self.stos.pop()

    def handle_data(self, data):
        if self.tryb and not self.przypis:
            self.bufor += data


def main(wej, wyj):
    p = Parser()
    p.feed(open(wej, encoding="utf-8").read())
    for j in p.jednostki:
        j["rozdzial"] = re.sub(r"\s+", " ", j["rozdzial"]).strip()
    json.dump(p.jednostki, open(wyj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(p.jednostki), "jednostek")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
