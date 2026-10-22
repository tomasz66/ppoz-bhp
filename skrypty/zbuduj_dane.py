# Składa app/data/akty.json z jednostek wyciągniętych parserami (zrodla/*.json).
# Na tekst jednolity nanosi zmiany ogłoszone później - dosłownie z Dz.U., z oznaczeniem źródła.
# Użycie: python3 skrypty/zbuduj_dane.py   (z folderu bhp-ppoz)
import json
import re

ISAP = "https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id="
PDF = "https://api.sejm.gov.pl/eli/acts/DU/{}/text.pdf"

ZM_2024 = {"opis": "Dz.U. 2024 poz. 1716", "isap": ISAP + "WDU20240001716", "od": "2024-12-23"}
ZM_2026_R = {"opis": "Dz.U. 2026 poz. 1276", "isap": ISAP + "WDU20260001276", "od": "2026-09-30"}
ZM_2026_U = {"opis": "Dz.U. 2026 poz. 815", "isap": ISAP + "WDU20260000815", "od": "2026-07-04"}


def wczytaj(plik):
    return json.load(open(plik, encoding="utf-8"))


def oczysc_etykiete(e):
    # "§ 17a4)Dodany przez..." -> "§ 17a"
    m = re.match(r"^(§|Art\.)\s?(\d+[a-z]*)", e)
    return f"{m.group(1)} {m.group(2)}"


def kotwica(etykieta):
    return re.sub(r"[^0-9a-z]", "", etykieta.lower().replace("§", "p").replace("art.", "a"))


def znajdz(jednostki, etykieta):
    return next(j for j in jednostki if j["etykieta"] == etykieta)


def wstaw_po(linie, poprzedzajacy_prefiks, nowe):
    # Wstawia nowe linie po ostatniej linii należącej do jednostki zaczynającej się od prefiksu.
    i = next(k for k, l in enumerate(linie) if l["t"].startswith(poprzedzajacy_prefiks))
    poz = linie[i]["p"]
    j = i + 1
    while j < len(linie) and linie[j]["p"] > poz:
        j += 1
    linie[j:j] = nowe


def nowa(p, t, zm):
    return {"p": p, "t": t, "zm": zm["opis"]}


def rozporzadzenie_2010():
    jedn = [j for j in wczytaj("zrodla/r2010.json") if j["id"].startswith("chpt")]
    for j in jedn:
        j["etykieta"] = oczysc_etykiete(j["etykieta"])
        j["rozdzial"] = j["rozdzial"].replace(
            "Stosowanie stałych urządzeń gaśniczych, systemów sygnalizacji pożarowej, dźwiękowych systemów ostrzegawczych i gaśnic",
            "Stosowanie stałych urządzeń gaśniczych, systemów sygnalizacji pożarowej, autonomicznych czujek dymu, autonomicznych czujek tlenku węgla, dźwiękowych systemów ostrzegawczych i gaśnic")

    # Zmiany z Dz.U. 2024 poz. 1716 (od 23.12.2024) - treść przepisana dosłownie z ogłoszonego aktu.
    p3 = znajdz(jedn, "§ 3")
    wstaw_po(p3["linie"], "3. ", [nowa(2, "3a. Wymagań, o których mowa w ust. 1–3, nie stosuje się do autonomicznych czujek dymu i autonomicznych czujek tlenku węgla. Urządzenia te należy zamontować, konserwować i eksploatować w sposób określony w instrukcjach obsługi, opracowanych przez ich producentów.", ZM_2024)])
    p3["zm"] = [ZM_2024]

    p4 = znajdz(jedn, "§ 4")
    wstaw_po(p4["linie"], "5) umieszczają, przy wjazdach", [
        nowa(3, "6) oznakowują w budynkach handlowych, produkcyjnych oraz magazynowych, w których ściana oddzielenia przeciwpożarowego oddziela strefy pożarowe o powierzchni co najmniej 2000 m2 każda i zachodzi co najmniej jeden z następujących warunków:", ZM_2024),
        nowa(4, "a) ściany zewnętrzne lub dach co najmniej jednej strefy pożarowej nie są wykonane z materiałów niepalnych lub", ZM_2024),
        nowa(4, "b) w co najmniej jednej strefie pożarowej gęstość obciążenia ogniowego przekracza 1000 MJ/m2", ZM_2024),
        nowa(5, "– miejsce połączenia ściany oddzielenia przeciwpożarowego ze ścianą zewnętrzną oraz z dachem w sposób określony w załączniku nr 1 albo inny uzgodniony z właściwym miejscowo komendantem powiatowym (miejskim) Państwowej Straży Pożarnej, umożliwiający jednoznaczną identyfikację tego miejsca z zewnątrz budynku;", ZM_2024),
        nowa(3, "7) oznakowują punkty schronienia, o których mowa w art. 84a ustawy z dnia 5 grudnia 2024 r. o ochronie ludności i obronie cywilnej (Dz. U. poz. 1907, z 2025 r. poz. 1705 oraz z 2026 r. poz. 646 i 815), w sposób określony w załączniku nr 1a do rozporządzenia.", ZM_2026_R),
    ])
    p4["zm"] = [ZM_2024, ZM_2026_R]

    p28 = znajdz(jedn, "§ 28")
    p28a = {"id": "chpt_6-para_28a", "etykieta": "§ 28a", "rozdzial": p28["rozdzial"], "zm": [ZM_2024], "linie": [
        nowa(2, "1. Pomieszczenie mieszkalne lub jednostkę mieszkalną, o której mowa w przepisach wydanych na podstawie art. 45 ustawy z dnia 29 sierpnia 1997 r. o usługach hotelarskich oraz usługach pilotów wycieczek i przewodników turystycznych (Dz. U. z 2023 r. poz. 1944), w których są świadczone usługi hotelarskie, a także lokal mieszkalny należy wyposażyć w co najmniej jedną autonomiczną czujkę dymu, spełniającą wymagania Polskiej Normy dotyczącej autonomicznych czujek dymu.", ZM_2024),
        nowa(2, "2. Przepisu ust. 1 nie stosuje się w przypadku ochrony pomieszczenia mieszkalnego, jednostki mieszkalnej lub lokalu mieszkalnego, o których mowa w ust. 1, przez system sygnalizacji pożarowej lub stałe samoczynne urządzenie gaśnicze.", ZM_2024),
        nowa(2, "3. Pomieszczenie, w którym odbywa się proces spalania paliwa stałego, ciekłego lub gazowego, wchodzące w skład lokalu mieszkalnego lub lokalu użytkowego przeznaczonego na pobyt ludzi, znajdującego się w strefie pożarowej zakwalifikowanej do kategorii zagrożenia ludzi ZL, należy wyposażyć w co najmniej jedną autonomiczną czujkę tlenku węgla, spełniającą wymagania Polskiej Normy dotyczącej urządzeń elektrycznych do wykrywania tlenku węgla w pomieszczeniach domowych.", ZM_2024),
        nowa(2, "4. Przepisu ust. 3 nie stosuje się w przypadku, gdy proces spalania odbywa się w urządzeniu z zamkniętą komorą spalania, a także gdy spalanie ma miejsce w zasilanym paliwem gazowym urządzeniu przeznaczonym do przygotowania posiłków.", ZM_2024),
    ], "uwaga": "Terminy przejściowe (§ 2 Dz.U. 2024 poz. 1716): lokale mieszkalne i pomieszczenia ze spalaniem w lokalach mieszkalnych użytkowane w dniu wejścia w życie zmiany - od 1 stycznia 2030 r.; pomieszczenia i jednostki z usługami hotelarskimi oraz pomieszczenia ze spalaniem w lokalach użytkowych - od 30 czerwca 2026 r."}
    jedn.insert(jedn.index(p28) + 1, p28a)

    p37 = znajdz(jedn, "§ 37")
    for l in p37["linie"]:
        if l["t"].startswith("8. "):
            l["t"] = l["t"].replace("załącznik ", "załącznik nr 2 ", 1)
            l["zm"] = ZM_2024["opis"]
    p37["zm"] = [ZM_2024]
    return jedn


def ustawa():
    jedn = wczytaj("zrodla/ustawa.json")
    a = znajdz(jedn, "Art. 14fa")
    for l in a["linie"]:
        if l["t"].startswith("3. "):
            l["t"] = "3. Plany ratownicze w zakresie zdarzeń z dużą liczbą poszkodowanych oraz działań ratowniczych i działań pomocowych podczas katastrof, klęsk żywiołowych i zdarzeń nadzwyczajnych są skorelowane z planami reagowania kryzysowego, o których mowa w art. 6j ustawy z dnia 26 kwietnia 2007 r. o zarządzaniu kryzysowym, oraz z planami postępowania awaryjnego, o których mowa w art. 84 ust. 1 ustawy z dnia 29 listopada 2000 r. – Prawo atomowe (Dz. U. z 2026 r. poz. 1)."
            l["zm"] = ZM_2026_U["opis"]
    a["zm"] = [ZM_2026_U]
    return jedn


def woda():
    # Tabela nr 1 z załącznika wpada w PDF między akapity § 13 i § 14 - wycinamy ją z tekstu.
    jedn = wczytaj("zrodla/woda.json")
    for j in jedn:
        for l in j["linie"]:
            l["t"] = re.sub(r" Lp\. Liczba mieszkańców.*?ponad 100 000 60 600", "", l["t"])
            l["t"] = re.sub(r" Tabela nr 1 Wymagana ilość wody.*$", "", l["t"])
            l["t"] = re.sub(r"Polskie Normy\. wodociągowych$", "Polskie Normy.", l["t"])
    return jedn


def przygotuj(jedn):
    for j in jedn:
        j["id"] = kotwica(j["etykieta"])
        j["rozdzial"] = re.sub(r"\s+", " ", j["rozdzial"]).strip()

    # Ostatnia jednostka w PDF ciągnie za sobą podpis i załączniki - ucinamy od podpisu.
    for l in jedn[-1]["linie"]:
        l["t"] = re.split(r"\s(?:Minister [^:]{0,90}:|Prezydent Rzeczypospolitej Polskiej:|Prezes Rady Ministrów:|Załącznik do )", l["t"])[0]

    # Odnośniki przypisów doklejone do wyrazu ("ogłoszenia12)") i treść przypisów wklejona w tekst.
    for j in jedn:
        for l in j["linie"]:
            l["t"] = re.sub(r"\d{1,2}\)(Zmiany tekstu|Zmiany wymienionego|Rozporządzenie zostało)[^)]*?r\.\.?", "", l["t"])
            l["t"] = re.sub(r"(?<=[a-ząćęłńóśźż])\d{1,2}\)(?=[\s.,;]|$)", "", l["t"])
        j["linie"] = [l for l in j["linie"] if not re.match(r"^\d+\) (Ustawa została ogłoszona|patrz)", l["t"]) and l["t"] != "patrz oryginał"]
    return jedn


AKTY = [
    {
        "id": "ustawa-ppoz", "dziedzina": "ppoz", "kafel": "USTAWA", "kolor": "#e0352b", "skrot": "Ustawa o ochronie ppoż.",
        "nazwa": "Ustawa z dnia 24 sierpnia 1991 r. o ochronie przeciwpożarowej",
        "eli": "DU/1991/351", "isap": ISAP + "WDU19910810351",
        "tekst": {"opis": "tekst jednolity Dz.U. 2025 poz. 188", "isap": ISAP + "WDU20250000188", "pdf": PDF.format("2025/188")},
        "zmiany": [ZM_2026_U], "znane": ["DU/2026/815", "DU/2024/1907", "DU/2024/1692", "DU/2024/1222"],
        "zrodlo": ustawa,
    },
    {
        "id": "rozp-ochrona-budynkow", "dziedzina": "ppoz", "kafel": "BUD", "kolor": "#c0392b", "skrot": "Ochrona ppoż. budynków",
        "nazwa": "Rozporządzenie MSWiA z dnia 7 czerwca 2010 r. w sprawie ochrony przeciwpożarowej budynków, innych obiektów budowlanych i terenów",
        "eli": "DU/2010/719", "isap": ISAP + "WDU20101090719",
        "tekst": {"opis": "tekst jednolity Dz.U. 2023 poz. 822", "isap": ISAP + "WDU20230000822", "pdf": PDF.format("2023/822")},
        "zmiany": [ZM_2024, ZM_2026_R], "znane": ["DU/2026/1276", "DU/2024/1716"],
        "zrodlo": rozporzadzenie_2010,
        "pominiete": "Załączniki (wzory oznakowania ściany oddzielenia przeciwpożarowego, punktu schronienia i tabele) - tylko w PDF.",
    },
    {
        "id": "rozp-woda-drogi", "dziedzina": "ppoz", "kafel": "WODA", "kolor": "#1e6fb8", "skrot": "Woda i drogi pożarowe",
        "nazwa": "Rozporządzenie MSWiA z dnia 24 lipca 2009 r. w sprawie przeciwpożarowego zaopatrzenia w wodę oraz dróg pożarowych",
        "eli": "DU/2009/1030", "isap": ISAP + "WDU20091241030",
        "tekst": {"opis": "tekst ogłoszony Dz.U. 2009 nr 124 poz. 1030 (bez zmian)", "isap": ISAP + "WDU20091241030", "pdf": PDF.format("2009/1030")},
        "zmiany": [], "znane": [],
        "zrodlo": lambda: woda(),
        "pominiete": "Załącznik z tabelami wymaganej ilości wody - tylko w PDF.",
    },
]


def main():
    wynik = []
    for a in AKTY:
        jedn = przygotuj(a.pop("zrodlo")())
        a["jednostki"] = jedn
        wynik.append(a)
        print(a["id"], len(jedn))
    stan = {"stanNa": "2026-10-22", "akty": wynik}
    json.dump(stan, open("app/data/akty.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
