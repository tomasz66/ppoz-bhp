# Buduje app/data/liczby.json: "Mapa liczb" - odległości (na rysunku budynku i działki) i terminy (oś czasu).
# Każda liczba ma "dowod" - dosłowny fragment przepisu, sprawdzany w tekście jednostki.
# Użycie: python3 skrypty/zbuduj_liczby.py   (z folderu bhp-ppoz)
import json
import sys

from zbuduj_przypadki import KP, SZKOL, WYP, R, W, tekst_jednostki


def l(id, wartosc, co, zr, dowod, grupa="mapa"):
    return {"id": id, "w": wartosc, "co": co, "zr": zr, "dowod": dowod, "g": grupa}


def r(j, u):
    return {"a": R, "j": j, "u": u}


def w(j, u):
    return {"a": W, "j": j, "u": u}


def d(dok, j, u):
    return {"dok": dok, "j": j, "u": u}


LICZBY = [
    # ── Na rysunku (id = miejsce na mapie w app/mapa.js) ──
    l("gas30", "30 m", "Maksymalna odległość z każdego miejsca, gdzie może być człowiek, do najbliższej gaśnicy.", r("p33", "ust. 2 pkt 1"), "nie powinna być większa niż 30 m"),
    l("gas1", "1 m", "Wolny dostęp do gaśnicy - co najmniej 1 m szerokości.", r("p33", "ust. 2 pkt 2"), "dostęp o szerokości co najmniej 1 m"),
    l("gas2kg", "2 kg / 100 m²", "Jedna jednostka 2 kg (3 dm³) środka gaśniczego na każde 100 m² strefy (ZL I, II, III, V, PM ponad 500 MJ/m², wybuch) - w pozostałych na 300 m².", r("p32", "ust. 3"), "na każde 100 m2"),
    l("piec05", "0,5 m", "Materiały palne i palny wystrój (zasłony, dekoracje) co najmniej 0,5 m od urządzeń nagrzewających się powyżej 100°C.", r("p4", "ust. 1 pkt 8"), "w odległości mniejszej niż 0,5 m od"),
    l("hydr135", "1,35 m", "Wysokość zaworu hydrantu wewnętrznego od podłogi (± 0,1 m).", r("p21", "ust. 1"), "1,35±0,1 m"),
    l("galezie4", "4 m", "Gałęzie, chrust i inne materiały palne składowane poza budynkiem - co najmniej 4 m od granicy działki sąsiedniej.", r("p4", "ust. 1 pkt 6"), "w odległości mniejszej niż 4 m od granicy działki sąsiedniej"),
    l("smola5", "5 m", "Rozgrzewanie smoły otwartym ogniem - co najmniej 5 m od budynku i składowisk materiałów palnych.", r("p4", "ust. 1 pkt 4"), "w odległości mniejszej niż 5 m od obiektu"),
    l("pas2", "2 m", "Pas ochronny wokół placu składowego (niepalny lub oczyszczony grunt).", r("p4", "ust. 3"), "pas ochronny o minimalnej szerokości 2 m"),
    l("sklad5", "5 m", "Materiały palne składowane pod ścianą budynku - co najmniej 5 m od drogi pożarowej.", r("p4", "ust. 4 pkt 4"), "minimalnej odległości 5 m od drogi pożarowej"),
    l("droga4", "4 m", "Minimalna szerokość drogi pożarowej (w miejscu ustawienia wozów i 10 m od niego); dalej 3,5 m albo 3 m.", w("p13", "§ 13 ust. 1"), "co najmniej 4 m"),
    l("droga515", "5-15 m", "Odległość bliższej krawędzi drogi pożarowej od ściany budynku ZL (dla pozostałych 5-25 m). Między drogą a ścianą bez drzew i elementów wyższych niż 3 m.", w("p12", "§ 12 ust. 2"), "o 5–15 m dla obiektów zaliczanych do kategorii zagrożenia ludzi"),
    l("plac", "20 × 20 m", "Plac manewrowy na końcu drogi pożarowej bez przejazdu (albo inne rozwiązanie do zawracania).", w("p12", "§ 12 ust. 9"), "20 m x 20 m"),
    l("dojscie", "1,5 m · 50 m", "Dojście od wyjścia z budynku do drogi pożarowej: szerokość min. 1,5 m, długość max 50 m.", w("p12", "§ 12 ust. 4"), "dojściem o szerokości minimalnej 1,5 m i długości nie większej niż 50 m"),
    # ── Terminy ppoż ──
    l("przeglad", "raz w roku", "Przeglądy i konserwacja urządzeń przeciwpożarowych i gaśnic - w terminach producenta, nie rzadziej niż raz w roku.", r("p3", "ust. 3"), "nie rzadziej jednak niż raz w roku", "ppoz"),
    l("weze", "co 5 lat", "Próba ciśnieniowa węży hydrantów wewnętrznych.", r("p3", "ust. 4"), "raz na 5 lat poddawane próbie ciśnieniowej", "ppoz"),
    l("hydr1h", "1 godzina", "Minimalny czas zasilania hydrantów wewnętrznych wodą.", r("p18", "ust. 4"), "co najmniej przez 1 godzinę", "ppoz"),
    l("ibp2", "co 2 lata", "Aktualizacja instrukcji bezpieczeństwa pożarowego (i po zmianach w obiekcie).", r("p6", "ust. 7"), "co najmniej raz na 2 lata", "ppoz"),
    l("ewak2", "co 2 lata", "Próbna ewakuacja w obiekcie dla ponad 50 stałych użytkowników.", r("p17", "ust. 1"), "co najmniej raz na 2 lata przeprowadzać praktyczne sprawdzenie", "ppoz"),
    l("ewak1", "raz w roku", "Próbna ewakuacja w szkołach, przedszkolach, internatach - najpóźniej 3 miesiące od przyjścia nowych użytkowników.", r("p17", "ust. 2"), "co najmniej raz na rok", "ppoz"),
    l("psp7", "tydzień przed", "Powiadomienie komendanta powiatowego PSP o terminie próbnej ewakuacji.", r("p17", "ust. 4"), "nie później niż na tydzień", "ppoz"),
    l("komin1", "co miesiąc", "Czyszczenie przewodów dymowych od palenisk gastronomii i zbiorowego żywienia.", r("p34", "ust. 1 pkt 1"), "co najmniej raz w miesiącu", "ppoz"),
    l("komin3", "co 3 miesiące", "Czyszczenie przewodów od palenisk na paliwo stałe (poza gastronomią).", r("p34", "ust. 1 pkt 2"), "co najmniej raz na 3 miesiące", "ppoz"),
    l("komin6", "co 6 miesięcy", "Czyszczenie przewodów od palenisk na paliwo płynne i gazowe.", r("p34", "ust. 1 pkt 3"), "co najmniej raz na 6 miesięcy", "ppoz"),
    l("wentyl", "raz w roku", "Czyszczenie przewodów wentylacyjnych w obiektach z paleniskami.", r("p34", "ust. 2"), "co najmniej raz w roku", "ppoz"),
    # ── Terminy BHP ──
    l("szk3", "co 3 lata", "Szkolenie okresowe BHP pracowników na stanowiskach robotniczych (prace szczególnie niebezpieczne - co roku).", d(SZKOL, "para_15", "§ 15 ust. 1"), "nie rzadziej niż raz na 3 lata", "bhp"),
    l("szk6", "co 6 lat", "Szkolenie okresowe BHP pracowników administracyjno-biurowych (jeśli wymagane).", d(SZKOL, "para_15", "§ 15 ust. 2"), "raz na 6 lat", "bhp"),
    l("szk5", "co 5 lat", "Szkolenie okresowe BHP pracodawców, kierowników i pracowników inżynieryjno-technicznych.", d(SZKOL, "para_15", "§ 15 ust. 2"), "nie rzadziej niż raz na 5 lat", "bhp"),
    l("wyp14", "14 dni", "Termin na protokół powypadkowy od zawiadomienia o wypadku.", d(WYP, "p9", "§ 9 ust. 1"), "nie później niż w terminie 14 dni", "bhp"),
    l("wyp5", "5 dni", "Termin na zatwierdzenie protokołu powypadkowego przez pracodawcę.", d(WYP, "p13", "§ 13 ust. 1"), "nie później niż w terminie 5 dni", "bhp"),
    l("wyp10", "10 lat", "Przechowywanie protokołu i dokumentacji powypadkowej.", d(KP, "a234", "art. 234 § 3¹"), "przez 10 lat", "bhp"),
]


def main():
    bledy = 0
    for x in LICZBY:
        try:
            jest = x["dowod"].replace(" ", "") in tekst_jednostki(x["zr"]).replace(" ", "").replace(" ", "")
        except StopIteration:
            jest = False
        if not jest:
            bledy += 1
            print("BRAK POKRYCIA:", x["id"], x["zr"], x["dowod"])
    if bledy:
        sys.exit(f"{bledy} liczb bez pokrycia w przepisach - popraw przed zapisem")
    json.dump(LICZBY, open("app/data/liczby.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("zapisano", len(LICZBY), "liczb")


if __name__ == "__main__":
    main()
