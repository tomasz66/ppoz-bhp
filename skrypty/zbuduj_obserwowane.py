# Pobiera z API Sejmu stan obserwowanych aktów: listę aktów zmieniających (znane dziś)
# oraz zmiany od OD_DATY z tytułem i datą wejścia w życie - do zakładki "Zmiany".
# Aplikacja porównuje później tę listę z API i pokazuje tylko nowe pozycje.
# Użycie: python3 skrypty/zbuduj_obserwowane.py   (z folderu bhp-ppoz)
import json
import urllib.request

API = "https://api.sejm.gov.pl/eli/acts/"
ISAP = "https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id="
OD_DATY = "2025-06-01"

OBSERWOWANE = [
    ("ppoz", "DU/1991/351", "Ustawa o ochronie przeciwpożarowej", "ustawa-ppoz"),
    ("ppoz", "DU/2010/719", "Rozporządzenie o ochronie przeciwpożarowej budynków, innych obiektów budowlanych i terenów", "rozp-ochrona-budynkow"),
    ("ppoz", "DU/2009/1030", "Rozporządzenie o przeciwpożarowym zaopatrzeniu w wodę oraz drogach pożarowych", "rozp-woda-drogi"),
    ("ppoz", "DU/2002/690", "Warunki techniczne, jakim powinny odpowiadać budynki (WT 2002)", None),
    ("bhp", "DU/1974/141", "Kodeks pracy", None),
    ("bhp", "DU/1997/844", "Ogólne przepisy bezpieczeństwa i higieny pracy", None),
    ("bhp", "DU/1997/704", "Służba bezpieczeństwa i higieny pracy", None),
    ("bhp", "DU/2004/1860", "Szkolenie w dziedzinie BHP", None),
    ("bhp", "DU/2009/870", "Ustalanie okoliczności i przyczyn wypadków przy pracy", None),
    ("bhp", "DU/2002/1673", "Ustawa wypadkowa (ubezpieczenie z tytułu wypadków przy pracy)", None),
    ("bhp", "DU/1996/332", "Badania lekarskie pracowników", None),
    ("bhp", "DU/1998/973", "BHP na stanowiskach z monitorami ekranowymi", None),
    ("bhp", "DU/2018/1286", "Najwyższe dopuszczalne stężenia i natężenia (NDS/NDN)", None),
]


def pobierz(eli):
    with urllib.request.urlopen(API + eli, timeout=30) as r:
        return json.load(r)


def isap_id(eli):
    # DU/2024/1716 -> WDU20240001716 (od 2012 r.); starsze akty mają numer Dz.U. - bierzemy z API.
    _, rok, poz = eli.split("/")
    return f"WDU{rok}{int(poz):07d}"


def main():
    wynik = []
    for dziedzina, eli, nazwa, akt in OBSERWOWANE:
        d = pobierz(eli)
        zmieniajace = d.get("references", {}).get("Akty zmieniające", [])
        ostatnie = []
        for z in zmieniajace:
            if (z.get("date") or "") < OD_DATY:
                continue
            m = pobierz(z["id"])
            ostatnie.append({"eli": z["id"], "od": z.get("date"), "tytul": m["title"], "isap": ISAP + isap_id(z["id"])})
        ostatnie.sort(key=lambda x: x["od"] or "", reverse=True)
        wynik.append({
            "dziedzina": dziedzina, "eli": eli, "nazwa": nazwa, "akt": akt,
            "tytul": d["title"], "status": d.get("status"),
            "isap": ISAP + d.get("address", ""),
            "znane": [z["id"] for z in zmieniajace],
            "ostatnie": ostatnie,
        })
        print(eli, d.get("status"), len(zmieniajace), "zmian,", len(ostatnie), "od", OD_DATY)
    json.dump({"pobrano": "2026-10-22", "akty": wynik}, open("app/data/obserwowane.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
