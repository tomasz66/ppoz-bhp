# Zbiera aktualności z branży BHP i ppoż do app/data/aktualnosci.json - "własny RSS" Tomka.
# Dla każdego wpisu: prawdziwy adres artykułu (linki Google News są rozkodowywane),
# zajawka z artykułu (og:description), tematy i punkty ważności do sekcji "Najważniejsze z tygodnia".
# Przeglądarka nie może sama czytać obcych RSS (CORS), więc robi to ten skrypt
# - ręcznie albo raz dziennie automatem (GitHub Actions po wystawieniu aplikacji).
# Użycie: python3 skrypty/zbuduj_aktualnosci.py   (z folderu bhp-ppoz)
import email.utils
import hashlib
import html
import json
import os
import re
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from tekst_artykulu import akapity, streszczenie

DNI_WSTECZ = 14
MAX_WPISOW = 250
WATKI = 12
LIMIT_S = 15
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/605.1.15"}
GOOGLE = "https://news.google.com/rss/search?q={}+when:{}d&hl=pl&gl=PL&ceid=PL:pl"
DNI_LUZ = 30
PAMIEC = "zrodla/pamiec_aktualnosci.json"
ARTYKULY = "app/data/artykuly.json"
# Materiały urzędowe nie są chronione prawem autorskim (art. 4 pr. aut.) - pełny tekst w aplikacji.
# Z mediów bierzemy tylko kilka zdań-streszczenia i odsyłamy do źródła.
URZEDOWE = re.compile(r"(^|\.)(gov\.pl|pip\.gov\.pl|ciop\.pl|policja\.pl|sejm\.gov\.pl)$")
POMIJANE_ZRODLA = ["vietnam", "ukrinform"]


def google(zapytanie, dni=DNI_WSTECZ):
    return GOOGLE.format(urllib.parse.quote(zapytanie), dni)


ZRODLA = [
    ("ppoz", "strazacki.pl", "https://www.strazacki.pl/feed"),
    ("ppoz", "Przegląd Pożarniczy", "https://www.ppoz.pl/rss"),
    ("ppoz", None, google('"ochrony przeciwpożarowej"')),
    ("ppoz", None, google('"inspektor ochrony przeciwpożarowej" OR "instrukcja bezpieczeństwa pożarowego" OR "próbna ewakuacja"')),
    ("ppoz", None, google('pożar hali OR pożar zakładu OR pożar magazynu')),
    ("ppoz", None, google('"czujki dymu" OR "czujka czadu" OR "punkty schronienia"')),
    ("ppoz", None, google('"Państwowa Straż Pożarna" przepisy OR kontrola')),
    ("bhp", None, google("przepisy BHP")),
    ("bhp", None, google('"Państwowa Inspekcja Pracy" OR "inspektor pracy" OR "inspekcja pracy"')),
    ("bhp", None, google('"wypadek przy pracy"')),
    ("bhp", None, google("mobbing Kodeks pracy")),
    ("bhp", None, google('"szkolenie BHP" OR "szkolenia BHP" OR "służba BHP"')),
    ("bhp", None, google('"badania lekarskie" pracowników OR "medycyna pracy"')),
    ("bhp", None, google('"Kodeks pracy" zmiany')),
    ("bhp", None, google('upał w pracy OR "temperatura w pracy"')),
]
# Zabawne historie nie mogą dotyczyć czyjejś krzywdy - takie wpisy pomijamy w kanale "luz".
SMUTNE = ["zgin", "nie zyje", "smierc", "smiertel", "ofiar", "ranny", "ranna", "rannych", "tragedi", "splon",
          "pozar", "wypad", "promil", "zwlok", "cialo", "utonal", "utonela", "reanim", "zatrzyman",
          "plon", "podpal", "przerzucil", "znecan", "lotto", "losowan"]
LUZ_MUSI = ["stra"]
LUZ_AKCJA = ["nietypow", "uratow", "utknal", "utknela", "utknely", "wpadl", "wpadla", "basen", "komin", "drzew", "zaskakuj", "niecodzien"]

# Tematy: słowa (bez polskich znaków, małe litery) -> etykieta. Punkty decydują o "Najważniejsze z tygodnia".
TEMATY = [
    ("Przepisy", 3, ["przepis", "ustaw", "rozporzadz", "kodeks", "nowelizac", "projekt", "obowiaz", "wchodz", "nowe zasady", "zmiany"]),
    ("Kontrole PIP", 2, ["pip", "inspekcj", "inspektor pracy", "kontrol", "mandat", "kara"]),
    ("Mobbing", 2, ["mobbing", "dyskrymin", "nekan"]),
    ("Ppoż w obiektach", 2, ["przeciwpozar", "ppoz", "ewakuac", "czujk", "gasnic", "hydrant", "schronien", "instrukcj"]),
    ("Szkolenia", 1, ["szkoleni", "kurs", "egzamin"]),
    ("Zdrowie w pracy", 1, ["lekar", "badani", "upal", "temperatur", "stres", "medycyn"]),
    ("Wypadki", 1, ["wypad", "zginal", "zginela", "smierc", "ranny", "obrazen", "stracil", "stracila"]),
    ("Pożary", 1, ["pozar", "plonie", "splon", "ogien", "zadymien"]),
    ("Straż", 0, ["straz", "osp", "psp", "strazak", "jednost"]),
]
WAZNE_ZRODLA = {"Gov.pl": 2, "Państwowa Inspekcja Pracy": 2, "Przegląd Pożarniczy": 1, "INFOR.PL": 1, "Prawo.pl": 1, "Rzeczpospolita": 1, "Dziennik Gazeta Prawna": 1, "Bankier.pl": 1}


def pobierz(url, dane=None, naglowki=None):
    req = urllib.request.Request(url, data=dane, headers={**UA, **(naglowki or {})})
    with urllib.request.urlopen(req, timeout=LIMIT_S) as r:
        return r.read().decode("utf-8", "replace"), r.geturl()


def czysc(s):
    s = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", s or "", flags=re.S)
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def pole(item, nazwa):
    m = re.search(rf"<{nazwa}[^>]*>(.*?)</{nazwa}>", item, re.S)
    return czysc(m.group(1)) if m else ""


def bez_ogonkow(s):
    return s.lower().translate(str.maketrans("ąćęłńóśźż", "acelnoszz"))


def rozkoduj_google(link):
    # Link news.google.com/rss/articles/<id> -> adres artykułu u wydawcy (to samo robi przeglądarka).
    aid = link.split("/articles/")[1].split("?")[0]
    strona, _ = pobierz(f"https://news.google.com/rss/articles/{aid}")
    sg = re.search(r'data-n-a-sg="([^"]+)"', strona).group(1)
    ts = re.search(r'data-n-a-ts="([^"]+)"', strona).group(1)
    wew = f'["garturlreq",[["X","X",["X","X"],null,null,1,1,"US:en",null,1,null,null,null,null,null,0,1],"X","X",1,[1,1,1],1,1,null,0,0,null,0],"{aid}",{ts},"{sg}"]'
    cialo = "f.req=" + urllib.parse.quote(json.dumps([[["Fbv4je", wew, None, "generic"]]]))
    odp, _ = pobierz("https://news.google.com/_/DotsSplashUi/data/batchexecute", cialo.encode(),
                     {"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"})
    return json.loads(json.loads(odp.split("\n\n")[1])[0][2])[1]


def zajawka_ze_strony(strona):
    for wzor in (r'<meta[^>]+(?:property|name)=["\']og:description["\'][^>]+content=["\']([^"\']*)',
                 r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+(?:property|name)=["\']og:description',
                 r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)'):
        m = re.search(wzor, strona, re.I)
        if m and len(m.group(1)) > 40:
            return czysc(m.group(1))
    return ""


def uzupelnij(w, pamiec):
    # Adres, zajawkę, streszczenie i (dla urzędów) pełny tekst zapamiętujemy,
    # żeby kolejne uruchomienia nie pobierały ich drugi raz.
    zapis = pamiec.get(w["link"])
    if zapis and "skrot" in zapis:
        w.update(zapis)
        return w
    tresc = []
    try:
        if "news.google.com" in w["link"]:
            w["url"] = rozkoduj_google(w["link"])
        strona, _ = pobierz(w["url"])
        if not w.get("lead"):
            w["lead"] = zajawka_ze_strony(strona)
        tresc = akapity(strona)
    except Exception:
        pass
    w["skrot"] = streszczenie(w["t"], w.get("lead", ""), tresc)
    domena = urllib.parse.urlparse(w["url"]).netloc.lower().removeprefix("www.")
    w["tekst"] = tresc if URZEDOWE.search(domena) else []
    pamiec[w["link"]] = {"url": w["url"], "lead": w.get("lead", ""), "skrot": w["skrot"], "tekst": w["tekst"]}
    return w


def ocen(w):
    tekst = bez_ogonkow(w["t"] + " " + w.get("lead", ""))
    tematy, punkty = [], WAZNE_ZRODLA.get(w["z"], 0)
    for nazwa, pkt, slowa in TEMATY:
        # Słowo musi zaczynać wyraz: "pozar" pasuje do "pożar hali", ale nie do "przeciwpożarowy".
        if any(re.search(r"\b" + re.escape(s), tekst) for s in slowa):
            tematy.append(nazwa)
            punkty += pkt
    if "policj" in bez_ogonkow(w["z"]):
        punkty -= 3
    w["tematy"] = tematy[:3]
    w["pkt"] = punkty


def main():
    granica = datetime.now(timezone.utc) - timedelta(days=DNI_WSTECZ)
    granica_luz = datetime.now(timezone.utc) - timedelta(days=DNI_LUZ)
    wpisy, widziane = [], set()
    for dziedzina, nazwa, url in ZRODLA:
        try:
            xml, _ = pobierz(url)
        except Exception as e:
            print("BŁĄD", url[:80], e)
            continue
        przed = len(wpisy)
        for item in re.findall(r"<item>(.*?)</item>", xml, re.S):
            tytul = pole(item, "title")
            zrodlo = nazwa or pole(item, "source")
            if not nazwa and zrodlo and tytul.endswith(" - " + zrodlo):
                tytul = tytul[: -len(zrodlo) - 3]
            data = pole(item, "pubDate")
            kiedy = email.utils.parsedate_to_datetime(data) if data else None
            if kiedy and kiedy < (granica_luz if dziedzina == "luz" else granica):
                continue
            klucz = re.sub(r"\W+", "", bez_ogonkow(tytul))[:60]
            if not tytul or klucz in widziane or any(p in bez_ogonkow(zrodlo) for p in POMIJANE_ZRODLA):
                continue
            bt = bez_ogonkow(tytul)
            if dziedzina == "luz" and (any(x in bt for x in SMUTNE) or not any(x in bt for x in LUZ_MUSI)
                                       or not any(x in bt for x in LUZ_AKCJA)):
                continue
            widziane.add(klucz)
            link = pole(item, "link")
            lead = pole(item, "description") if nazwa else ""
            wpisy.append({
                "d": dziedzina, "t": tytul, "z": zrodlo, "link": link, "url": link,
                "lead": lead[:400],
                "czas": kiedy.astimezone(timezone.utc).isoformat() if kiedy else None,
            })
        print(f"{dziedzina:5} {(nazwa or url.split('q=')[1][:60]):60} +{len(wpisy) - przed}")

    wpisy.sort(key=lambda w: w["czas"] or "", reverse=True)
    wpisy = [w for w in wpisy if w["d"] != "luz"][:MAX_WPISOW] + [w for w in wpisy if w["d"] == "luz"]
    pamiec = json.load(open(PAMIEC, encoding="utf-8")) if os.path.exists(PAMIEC) else {}
    with ThreadPoolExecutor(WATKI) as pula:
        wpisy = list(pula.map(lambda w: uzupelnij(w, pamiec), wpisy))
    json.dump(pamiec, open(PAMIEC, "w", encoding="utf-8"), ensure_ascii=False)

    artykuly = {}
    for w in wpisy:
        ocen(w)
        w.pop("link", None)
        # Treść do czytnika w osobnym pliku - lista wiadomości ładuje się szybko, treść dopiero po otwarciu.
        w["id"] = hashlib.sha1(w["url"].encode()).hexdigest()[:10]
        artykuly[w["id"]] = {"skrot": w.pop("skrot", []), "tekst": w.pop("tekst", [])}
    json.dump(artykuly, open(ARTYKULY, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    z_zajawka = sum(1 for w in wpisy if w.get("lead"))
    json.dump({"pobrano": datetime.now(ZoneInfo("Europe/Warsaw")).strftime("%Y-%m-%d %H:%M"), "wpisy": wpisy},
              open("app/data/aktualnosci.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("zapisano", len(wpisy), "wpisów, z zajawką:", z_zajawka)


if __name__ == "__main__":
    main()
