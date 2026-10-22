# Wyciąga z HTML artykułu akapity treści i układa streszczenie z najważniejszych zdań.
# Streszczenie jest wyciągowe (zdania z artykułu, bez dopisywania), więc nie zmyśla faktów.
import html
import re
from html.parser import HTMLParser

BLOKI = {"p", "li", "h2", "h3", "h4", "blockquote", "div", "td"}
POMIJANE = {"script", "style", "nav", "footer", "aside", "form", "figure", "header", "noscript", "button", "svg"}
SMIECI = re.compile(r"(cookie|newsletter|zaloguj|subskryb|reklama|udostępnij|polub nas|czytaj też|czytaj także|zobacz też|zobacz także|przeczytaj również|komentarz|©|wszelkie prawa|regulamin|polityka prywatności|zgod[ęa] na)", re.I)
SLOWA_BRANZY = ["przepis", "rozporządz", "ustaw", "obowiąz", "pracodaw", "pracowni", "kontrol", "inspekc", "kar", "termin",
                "bezpiecz", "pożar", "ewakuac", "straż", "wypad", "szkoleni", "mobbing", "badan", "czujk", "zmian", "od "]
MIN_ZDANIE, MAX_ZDANIE = 50, 280
PUNKTOW = 4


class Bloki(HTMLParser):
    # Zbiera tekst bloków (akapitów). Tekst bloku zagnieżdżonego zamyka blok nadrzędny,
    # dzięki temu działa i dla <p>, i dla stron budowanych z samych <div> (np. gov.pl).
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pomin = 0
        self.w_tresci = 0
        self.bloki = []
        self.bufor = ""
        self.stos = []

    def zamknij(self):
        t = re.sub(r"\s+", " ", self.bufor).strip()
        if t:
            self.bloki.append({"t": t, "tresc": self.w_tresci > 0})
        self.bufor = ""

    def handle_starttag(self, tag, attrs):
        if tag in POMIJANE:
            self.pomin += 1
        klasy = dict(attrs).get("class") or ""
        if tag in ("article", "main") or "editor-content" in klasy or "article-body" in klasy or "entry-content" in klasy:
            self.w_tresci += 1
            self.stos.append(tag)
        elif tag in BLOKI:
            self.zamknij()
        if tag == "br":
            self.bufor += " "

    def handle_endtag(self, tag):
        if tag in POMIJANE and self.pomin:
            self.pomin -= 1
        if tag in BLOKI:
            self.zamknij()
        if self.stos and tag == self.stos[-1]:
            self.zamknij()
            self.stos.pop()
            self.w_tresci -= 1

    def handle_data(self, data):
        if not self.pomin:
            self.bufor += data


def akapity(strona):
    p = Bloki()
    try:
        p.feed(strona)
    except Exception:
        return []
    bloki = [b for b in p.bloki if b["tresc"]] or p.bloki
    wynik, widziane = [], set()
    for b in bloki:
        t = html.unescape(b["t"])
        if len(t) < 60 or SMIECI.search(t) or t in widziane:
            continue
        widziane.add(t)
        wynik.append(t)
    return wynik[:40]


def zdania(tekst):
    return [z.strip() for z in re.split(r"(?<=[.!?])\s+(?=[A-ZĄĆĘŁŃÓŚŹŻ0-9„\"])", tekst) if z.strip()]


def streszczenie(tytul, lead, paragrafy):
    # Punkty za: słowa z tytułu, słowa branżowe, liczby/daty i miejsce w tekście (początek ważniejszy).
    rdzenie = {w[:5] for w in re.findall(r"\w{5,}", tytul.lower())}
    kandydaci = []
    for nr, z in enumerate(z for p in paragrafy for z in zdania(p)):
        if not MIN_ZDANIE <= len(z) <= MAX_ZDANIE or (lead and z[:60] in lead) or z.lower().startswith(tytul.lower()[:40]):
            continue
        male = z.lower()
        pkt = 2 * len(rdzenie & {w[:5] for w in re.findall(r"\w{5,}", male)})
        pkt += sum(1 for s in SLOWA_BRANZY if s in male)
        pkt += 1.5 if re.search(r"\d", z) else 0
        pkt += max(0, 3 - nr * 0.4)
        kandydaci.append((pkt, nr, z))
    najlepsze = sorted(kandydaci, reverse=True)[:PUNKTOW]
    return [z for _, _, z in sorted(najlepsze, key=lambda x: x[1])]
