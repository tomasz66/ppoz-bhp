# Buduje app/data/warsztat.json: lista kontrolna "Obchód obiektu" i wzory dokumentów (IBP, wypadek, ORZ).
# Każdy punkt i krok ma "dowod" - dosłowny fragment przepisu. Skrypt sprawdza, że ten fragment
# naprawdę jest we wskazanym artykule/paragrafie, więc nic nie trafi do aplikacji bez pokrycia w prawie.
# Użycie: python3 skrypty/zbuduj_warsztat.py   (z folderu bhp-ppoz)
import json
import sys

from zbuduj_przypadki import KP, OGOLNE, WYP, R, U, W, tekst_jednostki


def k(id, co, zal, zr, dowod):
    return {"id": id, "co": co, "zal": zal, "zr": zr, "dowod": dowod}


def r(j, u):
    return {"a": R, "j": j, "u": u}


OBCHOD = [
    {"id": "dok", "tytul": "Dokumenty i organizacja", "ikona": "📋", "punkty": [
        k("ibp", "Jest instrukcja bezpieczeństwa pożarowego, aktualizowana co najmniej raz na 2 lata.",
          "Opracować lub zaktualizować instrukcję bezpieczeństwa pożarowego. Aktualizacja co najmniej raz na 2 lata i po zmianie sposobu użytkowania obiektu. Nie jest wymagana m.in. dla budynku lub strefy do 1000 m³ bez strefy zagrożenia wybuchem.",
          r("p6", "ust. 7"), "co najmniej raz na 2 lata"),
        k("ibp-dostep", "Instrukcja bezpieczeństwa pożarowego leży w miejscu dostępnym dla straży.",
          "Umieścić egzemplarz instrukcji w miejscu dostępnym dla ekip ratowniczych (np. przy wejściu, w portierni).",
          r("p6", "ust. 9"), "w miejscach dostępnych dla ekip ratowniczych"),
        k("instr-pozar", "W widocznym miejscu wisi instrukcja postępowania na wypadek pożaru z telefonami alarmowymi.",
          "Wywiesić w widocznych miejscach instrukcję postępowania na wypadek pożaru z wykazem telefonów alarmowych.",
          r("p4", "ust. 2 pkt 3"), "umieszczają w widocznych miejscach instrukcje postępowania na wypadek pożaru"),
        k("zapoznanie", "Pracownicy zostali zapoznani z przepisami przeciwpożarowymi.",
          "Zapoznać pracowników z przepisami przeciwpożarowymi i instrukcją, potwierdzić to podpisami.",
          {"a": U, "j": "a4", "u": "ust. 1 pkt 6"}, "zapoznać pracowników z przepisami przeciwpożarowymi"),
        k("wyznaczeni", "Wyznaczono pracowników do gaszenia pożarów, ewakuacji i pierwszej pomocy.",
          "Wyznaczyć na piśmie pracowników do udzielania pierwszej pomocy oraz do działań przy zwalczaniu pożarów i ewakuacji.",
          {"dok": KP, "j": "a2091", "u": "art. 209¹ § 1 pkt 2"}, "wykonywania działań w zakresie zwalczania pożarów i ewakuacji pracowników"),
        k("probna-ewak", "Próbna ewakuacja odbyła się w ciągu ostatnich 2 lat (obiekt dla ponad 50 stałych użytkowników).",
          "Przeprowadzić praktyczne sprawdzenie organizacji i warunków ewakuacji (co najmniej raz na 2 lata; szkoły i przedszkola - raz w roku). Powiadomić komendanta powiatowego PSP najpóźniej tydzień wcześniej.",
          r("p17", "ust. 1"), "co najmniej raz na 2 lata przeprowadzać praktyczne sprawdzenie"),
    ]},
    {"id": "gasnice", "tytul": "Gaśnice", "ikona": "🧯", "punkty": [
        k("gas-rodzaj", "Rodzaj gaśnic pasuje do tego, co może się palić (np. gaśnica klasy F w kuchni z frytownicą).",
          "Dobrać gaśnice do grup pożarów występujących w obiekcie (A, B, C, D, F).",
          r("p32", "ust. 2"), "Rodzaj gaśnic powinien być dostosowany"),
        k("gas-ilosc", "Liczba gaśnic wystarcza: 2 kg środka gaśniczego na 100 m² (ZL, magazyny ponad 500 MJ/m², wybuch) lub na 300 m² (pozostałe strefy).",
          "Uzupełnić gaśnice do wymaganej ilości: jedna jednostka 2 kg (lub 3 dm³) środka na każde 100 m² albo 300 m² strefy pożarowej.",
          r("p32", "ust. 3"), "na każde 100 m2"),
        k("gas-30m", "Z każdego miejsca do najbliższej gaśnicy jest nie więcej niż 30 m.",
          "Rozmieścić gaśnice tak, żeby odległość z każdego miejsca, w którym może przebywać człowiek, do najbliższej gaśnicy nie przekraczała 30 m.",
          r("p33", "ust. 2 pkt 1"), "nie powinna być większa niż 30 m"),
        k("gas-dostep", "Do gaśnic jest wolne przejście szerokości co najmniej 1 m.",
          "Usunąć przedmioty zastawiające gaśnice - zapewnić dostęp szerokości co najmniej 1 m.",
          r("p33", "ust. 2 pkt 2"), "dostęp o szerokości co najmniej 1 m"),
        k("gas-miejsce", "Gaśnice wiszą w miejscach widocznych, z dala od pieców i grzejników.",
          "Przenieść gaśnice w miejsca łatwo dostępne i widoczne (wejścia, klatki schodowe, korytarze), z dala od źródeł ciepła.",
          r("p33", "ust. 1"), "działanie źródeł ciepła"),
        k("gas-przeglad", "Gaśnice mają aktualny przegląd (data na etykiecie, nie starszy niż rok).",
          "Zlecić przegląd i konserwację gaśnic - w terminach producenta, nie rzadziej niż raz w roku.",
          r("p3", "ust. 3"), "nie rzadziej jednak niż raz w roku"),
        k("gas-znak", "Miejsca gaśnic są oznakowane znakiem.",
          "Oznakować miejsca gaśnic i urządzeń przeciwpożarowych znakami zgodnymi z Polskimi Normami.",
          r("p4", "ust. 2 pkt 4 lit. b"), "miejsca usytuowania urządzeń przeciwpożarowych i gaśnic"),
    ]},
    {"id": "urzadzenia", "tytul": "Hydranty, prąd, urządzenia", "ikona": "🚒", "punkty": [
        k("urz-przeglad", "Urządzenia przeciwpożarowe (hydranty, sygnalizacja pożaru, oświetlenie awaryjne, drzwi ppoż, oddymianie) mają aktualny przegląd.",
          "Zlecić przeglądy i konserwację urządzeń przeciwpożarowych - nie rzadziej niż raz w roku, wpisać do książki obiektu lub protokołu.",
          r("p3", "ust. 3"), "nie rzadziej jednak niż raz w roku"),
        k("weze", "Węże hydrantowe przeszły próbę ciśnieniową w ciągu ostatnich 5 lat.",
          "Zlecić próbę ciśnieniową węży hydrantów wewnętrznych (raz na 5 lat).",
          r("p3", "ust. 4"), "raz na 5 lat poddawane próbie ciśnieniowej"),
        k("hydr-miejsce", "Przed hydrantem jest wolne miejsce na rozwinięcie węża.",
          "Usunąć przedmioty sprzed hydrantu - zapewnić przestrzeń do rozwinięcia linii gaśniczej.",
          r("p21", "ust. 4"), "dostateczną przestrzeń do rozwinięcia linii gaśniczej"),
        k("hydr-wys", "Zawór hydrantu jest na wysokości ok. 1,35 m od podłogi.",
          "Skorygować wysokość zaworu hydrantu do 1,35 ± 0,1 m od podłogi (do wykonania przez instalatora).",
          r("p21", "ust. 1"), "1,35±0,1 m"),
        k("ppwp", "Jest przeciwpożarowy wyłącznik prądu (gdy wymagają go warunki techniczne).",
          "Sprawdzić, czy obiekt wymaga przeciwpożarowego wyłącznika prądu, i zlecić jego montaż oraz oznakowanie.",
          r("p4", "ust. 2 pkt 2"), "przeciwpożarowe wyłączniki prądu"),
        k("rozdzielnica", "Dostęp do tablic elektrycznych, wyłączników i głównego kurka gazu jest wolny.",
          "Odsłonić tablice rozdzielcze, wyłączniki prądu i kurki główne gazu.",
          r("p4", "ust. 1 pkt 18 lit. f"), "wyłączników i tablic rozdzielczych prądu elektrycznego"),
        k("instalacje", "Instalacje i urządzenia są sprawne (bez uszkodzonych kabli, przeciążonych przedłużaczy, prowizorek).",
          "Wyłączyć z użytku niesprawne urządzenia i instalacje, naprawić je i zapewnić okresowe kontrole (np. pomiary elektryczne).",
          r("p4", "ust. 1 pkt 2"), "użytkowanie instalacji, urządzeń i narzędzi niesprawnych technicznie"),
    ]},
    {"id": "ewakuacja", "tytul": "Ewakuacja", "ikona": "🚪", "punkty": [
        k("drzwi-ewak", "Drzwi ewakuacyjne otwierają się od razu, bez szukania klucza.",
          "Zmienić sposób zamykania drzwi ewakuacyjnych tak, żeby dało się je natychmiast otworzyć (np. zamek antypaniczny).",
          r("p4", "ust. 1 pkt 14"), "zamykanie drzwi ewakuacyjnych w sposób uniemożliwiający ich natychmiastowe użycie"),
        k("drogi-ewak", "Na korytarzach i drogach ewakuacyjnych nie stoją kartony, palety ani meble.",
          "Usunąć materiały palne i przedmioty z dróg ewakuacyjnych.",
          r("p4", "ust. 1 pkt 11"), "składowanie materiałów palnych na drogach komunikacji ogólnej służących ewakuacji"),
        k("drzwi-ppoz", "Drzwi przeciwpożarowe nie są podparte klinem ani przywiązane.",
          "Usunąć kliny i blokady z drzwi przeciwpożarowych - muszą same się zamknąć w razie pożaru (dopuszczalne trzymacze zwalniane przez system alarmowy).",
          r("p4", "ust. 1 pkt 15"), "blokowanie drzwi i bram przeciwpożarowych"),
        k("znaki-ewak", "Drogi i wyjścia ewakuacyjne są oznakowane.",
          "Oznakować drogi i wyjścia ewakuacyjne znakami zgodnymi z Polskimi Normami.",
          r("p4", "ust. 2 pkt 4 lit. a"), "drogi i wyjścia ewakuacyjne"),
        k("oswietlenie", "Oświetlenie awaryjne działa (tam, gdzie jest wymagane).",
          "Naprawić lub uzupełnić oświetlenie awaryjne i zlecić jego przegląd.",
          r("p15", "ust. 1 pkt 5"), "oświetlenia awaryjnego"),
        k("okna", "Wyjścia ewakuacyjne i okna dla ekip ratowniczych nie są zastawione.",
          "Odsłonić wyjścia ewakuacyjne i okna przeznaczone dla ekip ratowniczych.",
          r("p4", "ust. 1 pkt 18 lit. e"), "wyjść ewakuacyjnych albo okien dla ekip ratowniczych"),
    ]},
    {"id": "porzadek", "tytul": "Porządek i materiały palne", "ikona": "🔥", "punkty": [
        k("odl-05", "Materiały palne i dekoracje są co najmniej 0,5 m od pieców, lamp grzewczych i gorących urządzeń.",
          "Odsunąć materiały palne i palny wystrój na co najmniej 0,5 m od urządzeń nagrzewających się powyżej 100°C.",
          r("p4", "ust. 1 pkt 8"), "w odległości mniejszej niż 0,5 m od"),
        k("techniczne", "W pomieszczeniach technicznych, na strychu i w piwnicy nie składuje się rzeczy palnych.",
          "Usunąć materiały palne z pomieszczeń technicznych (kotłownia, rozdzielnia), strychów i korytarzy piwnicznych.",
          r("p4", "ust. 1 pkt 12"), "składowanie materiałów palnych w pomieszczeniach technicznych"),
        k("butle", "Butle z gazem palnym nie stoją w piwnicy ani na strychu.",
          "Przenieść butle z gazem palnym (także puste) z piwnic, strychów i nieużytkowych poddaszy.",
          r("p4", "ust. 1 pkt 13"), "butli przeznaczonych do gazów palnych na nieużytkowych poddaszach i strychach oraz w piwnicach"),
        k("grzejniki", "Grzejniki elektryczne nie stoją bezpośrednio na palnej podłodze (chyba że producent na to pozwala).",
          "Ustawić grzejniki elektryczne na podłożu niepalnym albo zgodnie z instrukcją producenta.",
          r("p4", "ust. 1 pkt 7"), "elektrycznych urządzeń ogrzewczych ustawionych bezpośrednio na podłożu palnym"),
        k("ogien", "Przy materiałach niebezpiecznych pożarowo nie pali się papierosów i nie używa ognia.",
          "Wprowadzić i oznakować zakaz palenia i używania otwartego ognia w miejscach z materiałami niebezpiecznymi pożarowo.",
          r("p4", "ust. 1 pkt 1 lit. b"), "w miejscach występowania materiałów niebezpiecznych pożarowo"),
        k("kominy", "Przewody kominowe są czyszczone (paliwo stałe co 3 miesiące, gaz i olej co 6 miesięcy, gastronomia co miesiąc, wentylacja raz w roku).",
          "Zlecić kominiarzowi czyszczenie przewodów dymowych, spalinowych i wentylacyjnych w wymaganych terminach.",
          r("p34", "ust. 1"), "co najmniej raz na 3 miesiące"),
        k("prace-poz", "Spawanie, cięcie i inne prace pożarowo niebezpieczne mają ustaloną procedurę (ocena zagrożenia, osoba odpowiedzialna, sprzęt gaśniczy, kontrola po pracy).",
          "Wprowadzić zasady zabezpieczania prac pożarowo niebezpiecznych (np. pisemne zezwolenie): ocena zagrożenia, wyznaczenie odpowiedzialnych, sprzęt gaśniczy na miejscu, kontrola miejsca po pracy.",
          r("p36", "ust. 1"), "ocenia zagrożenie pożarowe w miejscu"),
    ]},
    {"id": "teren", "tytul": "Teren wokół obiektu", "ikona": "🌳", "punkty": [
        k("droga-poz", "Droga pożarowa jest przejezdna (bez zaparkowanych aut, kontenerów, szlabanu bez klucza).",
          "Udrożnić drogę pożarową i utrzymywać ją w stanie umożliwiającym przejazd wozów strażackich.",
          r("p5", ""), "w stanie umożliwiającym wykorzystanie tych dróg"),
        k("sklad-sciana", "Rzeczy składowane pod ścianą budynku są co najmniej 5 m od drogi pożarowej.",
          "Przenieść składowane materiały tak, żeby zachować co najmniej 5 m od drogi pożarowej i dostęp do budynku.",
          r("p4", "ust. 4 pkt 4"), "minimalnej odległości 5 m od drogi pożarowej"),
        k("granica", "Gałęzie, chrust i inne materiały palne leżą co najmniej 4 m od granicy działki.",
          "Przenieść materiały palne (gałęzie, chrust, odpady roślinne) na co najmniej 4 m od granicy sąsiedniej działki.",
          r("p4", "ust. 1 pkt 6"), "w odległości mniejszej niż 4 m od granicy działki sąsiedniej"),
        k("woda", "Dostęp do hydrantów zewnętrznych i innych źródeł wody do gaszenia jest wolny.",
          "Odsłonić hydranty zewnętrzne i źródła wody do celów przeciwpożarowych.",
          r("p4", "ust. 1 pkt 18 lit. c"), "źródeł wody do celów przeciwpożarowych"),
        k("pas-2m", "Wokół placu składowego jest pas ochronny szerokości 2 m (niepalny lub oczyszczony grunt).",
          "Wykonać wokół placu składowego pas ochronny o szerokości co najmniej 2 m z nawierzchni niepalnej lub oczyszczonego gruntu.",
          r("p4", "ust. 3"), "pas ochronny o minimalnej szerokości 2 m"),
    ]},
    {"id": "bhp", "tytul": "BHP - pracodawca", "ikona": "👷", "punkty": [
        k("orz", "Ryzyko zawodowe jest ocenione i udokumentowane, a pracownicy o nim poinformowani.",
          "Ocenić i udokumentować ryzyko zawodowe na każdym stanowisku, poinformować pracowników (podpisy).",
          {"dok": KP, "j": "a226", "u": "art. 226"}, "ocenia i dokumentuje ryzyko zawodowe"),
        k("szkolenia", "Pracownicy mają szkolenie BHP wstępne i aktualne okresowe.",
          "Przeprowadzić brakujące szkolenia BHP (wstępne przed dopuszczeniem do pracy, okresowe w terminach).",
          {"dok": KP, "j": "a2373", "u": "art. 237³ § 2"}, "przed dopuszczeniem go do pracy"),
        k("apteczka", "Jest apteczka i działa system pierwszej pomocy.",
          "Zapewnić apteczki (ilość i wyposażenie ustalić z lekarzem medycyny pracy) i wyznaczyć osoby do ich obsługi.",
          {"dok": OGOLNE, "j": "para_44", "u": "§ 44"}, "środki do udzielania pierwszej pomocy"),
        k("rejestr", "Pracodawca prowadzi rejestr wypadków przy pracy.",
          "Założyć rejestr wypadków przy pracy; dokumentację powypadkową przechowywać 10 lat.",
          {"dok": KP, "j": "a234", "u": "art. 234 § 3"}, "prowadzić rejestr wypadków przy pracy"),
        k("napoje", "Pracownicy mają dostęp do wody pitnej lub innych napojów.",
          "Zapewnić wszystkim pracownikom wodę zdatną do picia lub inne napoje.",
          {"dok": OGOLNE, "j": "para_112", "u": "§ 112"}, "wodę zdatną do picia"),
        k("kontrole", "Stan BHP jest systematycznie kontrolowany, a usterki zapisywane i usuwane.",
          "Ustalić systematyczne kontrole stanu BHP oraz sposób zapisywania i usuwania nieprawidłowości.",
          {"dok": OGOLNE, "j": "para_40", "u": "§ 40"}, "systematyczne kontrole stanu bezpieczeństwa i higieny pracy"),
    ]},
]


def s(id, tytul, pomoc, zr, dowod, przyklad=""):
    return {"id": id, "tytul": tytul, "pomoc": pomoc, "przyklad": przyklad, "zr": zr, "dowod": dowod}


IBP = {
    "id": "ibp", "tytul": "Instrukcja bezpieczeństwa pożarowego", "ikona": "🔥", "kolor": "#c0392b",
    "opis": "Krok po kroku według § 6 rozporządzenia o ochronie ppoż budynków. Wymagana m.in. w obiektach użyteczności publicznej, zamieszkania zbiorowego, produkcyjnych, magazynowych i inwentarskich.",
    "glowa": ["Nazwa obiektu", "Adres", "Właściciel / zarządca", "Data opracowania"],
    "uwagi": [
        {"t": "Nie jest wymagana, gdy nie ma strefy zagrożenia wybuchem, a budynek lub strefa ma do 1000 m³ (inwentarski do 1500 m³, obiekt inny niż budynek do 1000 m²).", "zr": r("p6", "ust. 8"), "dowod": "nie przekracza 1000 m3"},
        {"t": "Aktualizacja co najmniej raz na 2 lata i po zmianach wpływających na ochronę ppoż.", "zr": r("p6", "ust. 7"), "dowod": "co najmniej raz na 2 lata"},
    ],
    "kroki": [
        s("warunki", "Warunki ochrony przeciwpożarowej", "Opisz obiekt: przeznaczenie, sposób użytkowania, technologię, co i gdzie się składuje, konstrukcję, kategorię zagrożenia ludzi (ZL) lub gęstość obciążenia ogniowego, strefy pożarowe, zagrożenie wybuchem.",
          r("p6", "ust. 1 pkt 1"), "warunki ochrony przeciwpożarowej, wynikające z przeznaczenia",
          "Budynek handlowy, 1 kondygnacja, 450 m², strefa ZL III. Brak strefy zagrożenia wybuchem."),
        s("wyposazenie", "Urządzenia przeciwpożarowe i gaśnice + przeglądy", "Wypisz gaśnice (typ, liczba, miejsce), hydranty, sygnalizację, oświetlenie awaryjne, wyłącznik prądu. Dla każdego: kto i jak często robi przegląd (min. raz w roku).",
          r("p6", "ust. 1 pkt 2"), "określenie wyposażenia w wymagane urządzenia przeciwpożarowe i gaśnice",
          "6 gaśnic proszkowych GP-6 ABC (wejście, korytarz, zaplecze). Przegląd: firma serwisowa, raz w roku, wrzesień."),
        s("postepowanie", "Postępowanie na wypadek pożaru i innego zagrożenia", "Kto alarmuje, pod jaki numer (112 / 998), kto wyłącza prąd i gaz, kto prowadzi ewakuację, kto czeka na straż i przekazuje informacje.",
          r("p6", "ust. 1 pkt 3"), "sposoby postępowania na wypadek pożaru i innego zagrożenia"),
        s("prace", "Zabezpieczenie prac pożarowo niebezpiecznych", "Jeśli przewiduje się spawanie, cięcie, prace z otwartym ogniem: kto wydaje zgodę, jak przygotować miejsce, jaki sprzęt gaśniczy, kontrola po pracy.",
          r("p6", "ust. 1 pkt 4"), "sposoby zabezpieczenia prac niebezpiecznych pod względem pożarowym"),
        s("ewakuacja", "Warunki i organizacja ewakuacji, praktyczne sprawdzanie", "Drogi i wyjścia ewakuacyjne, miejsce zbiórki, kto sprawdza pomieszczenia, osoby z niepełnosprawnościami. Próbna ewakuacja: jak często i kto ją prowadzi.",
          r("p6", "ust. 1 pkt 5"), "warunki i organizację ewakuacji ludzi oraz praktyczne sposoby ich sprawdzania"),
        s("zapoznanie", "Zapoznanie użytkowników i pracowników z przepisami i instrukcją", "Jak i kiedy (przy przyjęciu do pracy, po aktualizacji), potwierdzenie podpisem.",
          r("p6", "ust. 1 pkt 6"), "sposoby zapoznania użytkowników obiektu"),
        s("obowiazki", "Zadania i obowiązki stałych użytkowników", "Obowiązki właściciela, kierownika, pracowników, osób wyznaczonych do ewakuacji i gaszenia.",
          r("p6", "ust. 1 pkt 7"), "zadania i obowiązki w zakresie ochrony przeciwpożarowej"),
        s("plany", "Plany obiektu i terenu", "Rysunki z: wymiarami i liczbą kondygnacji, odległościami od sąsiednich obiektów, strefami pożarowymi, drogami i wyjściami ewakuacyjnymi, gaśnicami i urządzeniami, kurkiem gazu, wyłącznikiem prądu, hydrantami zewnętrznymi, drogami pożarowymi i wjazdami.",
          r("p6", "ust. 1 pkt 8"), "plany obiektów, obejmujące także ich usytuowanie"),
        s("autor", "Kto opracował instrukcję", "Imię i nazwisko, uprawnienia (np. inspektor ochrony przeciwpożarowej), data.",
          r("p6", "ust. 1 pkt 9"), "wskazanie osób lub podmiotów opracowujących instrukcję"),
    ],
}

WYPADEK = {
    "id": "wypadek", "tytul": "Wypadek przy pracy - postępowanie", "ikona": "🩹", "kolor": "#2f5d8a",
    "opis": "Notatki zespołu powypadkowego krok po kroku, według rozporządzenia o ustalaniu okoliczności i przyczyn wypadków przy pracy. Sam protokół sporządza się na urzędowym wzorze - te notatki pomagają go wypełnić.",
    "glowa": ["Pracodawca", "Poszkodowany (imię, nazwisko, stanowisko)", "Data i godzina wypadku", "Miejsce wypadku"],
    "uwagi": [
        {"t": "Protokół powypadkowy - najpóźniej 14 dni od zawiadomienia o wypadku, na wzorze ustalonym przez ministra.", "zr": {"dok": WYP, "j": "p9", "u": "§ 9"}, "dowod": "nie później niż w terminie 14 dni"},
        {"t": "Wypadek śmiertelny, ciężki lub zbiorowy - pracodawca niezwłocznie zawiadamia inspektora pracy i prokuratora.", "zr": {"dok": KP, "j": "a234", "u": "art. 234 § 2"}, "dowod": "zawiadomić właściwego okręgowego inspektora pracy i prokuratora"},
        {"t": "Protokół i dokumentację powypadkową przechowuje się 10 lat.", "zr": {"dok": KP, "j": "a234", "u": "art. 234 § 3¹"}, "dowod": "przez 10 lat"},
    ],
    "kroki": [
        s("zabezpieczenie", "Zabezpieczenie miejsca wypadku", "Kto zabezpieczył miejsce i jak: brak osób postronnych, maszyny zatrzymane, nic nie przestawiano. Zmiany tylko za zgodą pracodawcy (przy ciężkim - po uzgodnieniu z inspektorem pracy i prokuratorem) albo dla ratowania ludzi.",
          {"dok": WYP, "j": "p3", "u": "§ 3"}, "zabezpieczyć miejsce wypadku"),
        s("zespol", "Skład zespołu powypadkowego", "Pracownik służby BHP + społeczny inspektor pracy (w mniejszych firmach: pracodawca lub pracownik z przeszkoleniem BHP, specjalista spoza zakładu, przedstawiciel pracowników).",
          {"dok": WYP, "j": "p4", "u": "§ 4"}, "pracownik służby bezpieczeństwa i higieny pracy oraz społeczny inspektor pracy"),
        s("ogledziny", "Oględziny miejsca i warunków pracy", "Stan maszyn i urządzeń ochronnych, warunki pracy, organizacja, środki ochrony indywidualnej, pora, oświetlenie, nawierzchnia.",
          {"dok": WYP, "j": "p7", "u": "§ 7 ust. 1 pkt 1"}, "dokonać oględzin miejsca wypadku"),
        s("szkic", "Szkic lub zdjęcia miejsca wypadku", "Co sfotografowano, opis szkicu, wymiary, położenie przedmiotów.",
          {"dok": WYP, "j": "p7", "u": "§ 7 ust. 1 pkt 2"}, "sporządzić szkic lub wykonać fotografię miejsca wypadku"),
        s("poszkodowany", "Wyjaśnienia poszkodowanego", "Jeśli stan zdrowia pozwala: co robił, jak doszło do zdarzenia, czy był przeszkolony, jakie miał środki ochrony.",
          {"dok": WYP, "j": "p7", "u": "§ 7 ust. 1 pkt 3"}, "wysłuchać wyjaśnień poszkodowanego"),
        s("swiadkowie", "Informacje od świadków", "Imiona, nazwiska, co widzieli.",
          {"dok": WYP, "j": "p7", "u": "§ 7 ust. 1 pkt 4"}, "zebrać informacje dotyczące wypadku od świadków wypadku"),
        s("lekarz", "Opinia lekarza (i innych specjalistów)", "Rodzaj urazu, skutki, czy wypadek ciężki. Inne dowody: dokumentacja szkoleń, badań lekarskich, ocena ryzyka.",
          {"dok": WYP, "j": "p7", "u": "§ 7 ust. 1 pkt 5"}, "zasięgnąć opinii lekarza"),
        s("przyczyny", "Okoliczności i przyczyny", "Przebieg zdarzenia w kolejności. Przyczyny techniczne, organizacyjne i ludzkie (zwykle jest ich kilka).",
          {"dok": WYP, "j": "p7", "u": "§ 7 ust. 1"}, "ustalenia okoliczności i przyczyn wypadku"),
        s("kwalifikacja", "Kwalifikacja prawna", "Czy to wypadek przy pracy według art. 3 ustawy wypadkowej: nagłe zdarzenie, przyczyna zewnętrzna, uraz lub śmierć, związek z pracą. Jeśli nie - uzasadnienie.",
          {"dok": WYP, "j": "p7", "u": "§ 7 ust. 1 pkt 7"}, "dokonać prawnej kwalifikacji wypadku"),
        s("profilaktyka", "Środki profilaktyczne i wnioski", "Co zmienić, żeby wypadek się nie powtórzył - także w ocenie ryzyka zawodowego na tym stanowisku. Termin i osoba odpowiedzialna.",
          {"dok": WYP, "j": "p7", "u": "§ 7 ust. 1 pkt 8"}, "określić środki profilaktyczne oraz wnioski"),
        s("zapoznanie", "Zapoznanie poszkodowanego z protokołem", "Data zapoznania, uwagi i zastrzeżenia poszkodowanego. Poszkodowany może przeglądać akta i robić kopie.",
          {"dok": WYP, "j": "p11", "u": "§ 11"}, "zapoznać poszkodowanego z treścią protokołu powypadkowego"),
        s("zatwierdzenie", "Zatwierdzenie przez pracodawcę", "Pracodawca zatwierdza protokół najpóźniej 5 dni od sporządzenia i niezwłocznie doręcza go poszkodowanemu.",
          {"dok": WYP, "j": "p13", "u": "§ 13 ust. 1"}, "nie później niż w terminie 5 dni"),
    ],
}

ORZ = {
    "id": "orz", "tytul": "Ocena ryzyka zawodowego", "ikona": "⚠️", "kolor": "#b25000",
    "opis": "Karta oceny ryzyka dla jednego stanowiska. Ocena ryzyka jest obowiązkowa (art. 226 KP), metoda jest dowolna - tu skala trzystopniowa jak w normie PN-N-18002 (norma, nie przepis).",
    "glowa": ["Firma", "Stanowisko", "Opis pracy, maszyny i narzędzia", "Liczba pracowników na stanowisku", "Data oceny i oceniający"],
    "uwagi": [
        {"t": "Kolejność środków: najpierw usunąć zagrożenie, potem rozwiązania techniczne i organizacyjne (ochrona zbiorowa), na końcu środki ochrony indywidualnej.", "zr": {"dok": OGOLNE, "j": "para_39", "u": "§ 39"}, "dowod": "środki ochrony indywidualnej"},
        {"t": "Pracowników trzeba poinformować o ryzyku i zasadach ochrony przed zagrożeniami (najlepiej z podpisem).", "zr": {"dok": KP, "j": "a226", "u": "art. 226 pkt 2"}, "dowod": "informuje pracowników o ryzyku zawodowym"},
    ],
    "zagrozenia": [
        "Upadek na tym samym poziomie (poślizgnięcie, potknięcie)", "Upadek z wysokości", "Uderzenie o nieruchome przedmioty",
        "Spadające przedmioty", "Ruchome części maszyn", "Ostre krawędzie, narzędzia tnące", "Porażenie prądem elektrycznym",
        "Pożar", "Wybuch", "Gorące powierzchnie, oparzenia", "Substancje chemiczne", "Pyły", "Hałas", "Drgania (wibracje)",
        "Niewłaściwe oświetlenie", "Praca przy monitorze ekranowym", "Ręczne przenoszenie ciężarów", "Wymuszona pozycja ciała",
        "Mikroklimat gorący lub zimny", "Ruch pojazdów, wózki widłowe", "Stres, praca zmianowa", "Czynniki biologiczne",
    ],
    "zr": {"dok": KP, "j": "a226", "u": "art. 226 pkt 1"}, "dowod": "ocenia i dokumentuje ryzyko zawodowe",
}


# ── Praca projektowa na kurs inspektora ppoż (wytyczne CS PSP Częstochowa, 2026) ──
# Każdy punkt: co wpisać, przykład i podstawa prawna w pełnym brzmieniu (do tabeli w pracy).
# zr = jednostka do sprawdzenia cytatu (None = dane z dokumentacji budowlanej, bez paragrafu).
WT = "DU_2002_690"
ATEX = "DU_2010_931"
UZG = "DU_2023_1563"
WT_PELNA = "rozporządzenie Ministra Infrastruktury z dnia 12 kwietnia 2002 r. w sprawie warunków technicznych, jakim powinny odpowiadać budynki i ich usytuowanie (Dz.U. z 2022 r. poz. 1225)"
R_PELNA = "rozporządzenie Ministra Spraw Wewnętrznych i Administracji z dnia 7 czerwca 2010 r. w sprawie ochrony przeciwpożarowej budynków, innych obiektów budowlanych i terenów (Dz.U. z 2023 r. poz. 822 ze zm.)"
W_PELNA = "rozporządzenie Ministra Spraw Wewnętrznych i Administracji z dnia 24 lipca 2009 r. w sprawie przeciwpożarowego zaopatrzenia w wodę oraz dróg pożarowych (Dz.U. Nr 124, poz. 1030)"
U_PELNA = "ustawa z dnia 24 sierpnia 1991 r. o ochronie przeciwpożarowej (Dz.U. z 2025 r. poz. 188 ze zm.)"
ATEX_PELNA = "rozporządzenie Ministra Gospodarki z dnia 8 lipca 2010 r. w sprawie minimalnych wymagań, dotyczących bezpieczeństwa i higieny pracy, związanych z możliwością wystąpienia w miejscu pracy atmosfery wybuchowej (Dz.U. Nr 138, poz. 931)"
UZG_PELNA = "rozporządzenie Ministra Spraw Wewnętrznych i Administracji z dnia 5 sierpnia 2023 r. w sprawie uzgadniania projektu zagospodarowania działki lub terenu, projektu architektoniczno-budowlanego, projektu technicznego oraz projektu urządzenia przeciwpożarowego pod względem zgodności z wymaganiami ochrony przeciwpożarowej (Dz.U. z 2023 r. poz. 1563)"
DOK_BUD = "dokumentacja budowlana obiektu"


def pp(nr, tytul, pomoc, podstawa, zr=None, dowod="", przyklad=""):
    return {"id": f"p{nr}", "nr": nr, "tytul": tytul, "pomoc": pomoc, "przyklad": przyklad, "podstawa": podstawa, "zr": zr, "dowod": dowod}


def wt(j, u):
    return {"dok": WT, "j": j, "u": f"{u} WT"}


def w(j, u):
    return {"a": W, "j": j, "u": u}


PRACA = {
    "id": "praca", "tytul": "Praca projektowa - analiza bezpieczeństwa pożarowego", "ikona": "🎓", "kolor": "#5e35b1", "word": True,
    "opis": "Kreator pracy zaliczeniowej na kurs inspektora ppoż (CS PSP): 34 punkty z wytycznych, przy każdym podpowiedź i podstawa prawna. Na końcu gotowy dokument do pobrania jako plik Word.",
    "glowa": ["Imię i nazwisko (jak na stronie tytułowej)", "Rodzaj budynku (do tytułu, np. szkoły podstawowej)", "Nazwa i adres obiektu", "Termin szkolenia"],
    "uwagi": [
        {"t": "Budynek musi spełniać kryteria opracowania instrukcji bezpieczeństwa pożarowego - IBP nie jest wymagana m.in. dla budynku do 1000 m³ bez strefy zagrożenia wybuchem. Wybierz większy obiekt.", "zr": r("p6", "ust. 8"), "dowod": "nie przekracza 1000 m3"},
        {"t": "Termin: praca do 9.11.2026 na wlodarczyka@cspsp.pl. Plik: nazwisko_imię_data rozpoczęcia (np. musialik_tomasz_26.10.26), Times New Roman 10 pkt, interlinia 1,0, .doc/.docx/.pdf. Obowiązkowe 3 załączniki graficzne (bez nich praca nie jest oceniana) - spakuj wszystko w jeden .zip.", "zr": r("p6", "ust. 1 pkt 8"), "dowod": "plany obiektów, obejmujące także ich usytuowanie"},
        {"t": "Uwaga: wytyczne wymieniają rozporządzenie o uzgadnianiu projektów z 2021 r. (Dz.U. 2021 poz. 1722) - zostało zastąpione rozporządzeniem z 5.08.2023 (Dz.U. 2023 poz. 1563). W pracy podaj aktualne. WT 2002 są od 20.09.2026 uznane za uchylone i stosowane w okresie przejściowym - wytyczne każą się na nie powoływać.", "zr": {"dok": UZG, "j": "para_1", "u": "§ 1"}, "dowod": "rodzaje obiektów budowlanych istotnych"},
    ],
    "kroki": [
        pp(1, "Ogólna charakterystyka budynku", "Przeznaczenie i krótki opis prowadzonej działalności: co to za obiekt, kto go używa, w jakich godzinach, ile osób.", "-", przyklad="Szkoła podstawowa, 3 kondygnacje nadziemne, ok. 420 uczniów i 45 pracowników, zajęcia 7:30-16:00."),
        pp(2, "Kwalifikacja budynku ze względu na sposób użytkowania (ZL, PM, IN)", "Wpisz, czy budynek (lub jego strefy) to ZL, PM czy IN.", f"§ 209 ust. 1 {WT_PELNA}", wt("para_209", "§ 209 ust. 1"), "produkcyjne i magazynowe, określane dalej jako PM"),
        pp(3, "Kategoria zagrożenia ludzi i dane stref", "Dla każdej strefy: kategoria ZL (I-V) lub PM/IN. Do tego: powierzchnia zabudowy, powierzchnia użytkowa, wysokość, kubatura, liczba kondygnacji, grupa wysokości (N do 12 m, SW 12-25 m, W 25-55 m, WW ponad 55 m).", f"§ 209 ust. 2 i § 8 {WT_PELNA} + dane z dokumentacji budowlanej", wt("para_8", "§ 8"), "niskie (N) - do 12 m włącznie", "Strefa 1: ZL II (przedszkole), pow. zabudowy 640 m², użytkowa 1150 m², wys. 8,4 m, kubatura 5200 m³, 2 kondygnacje, budynek niski (N)."),
        pp(4, "Gęstość obciążenia ogniowego (tylko PM)", "Jeśli są strefy PM - podaj obliczenia gęstości obciążenia ogniowego (MJ/m²) według Polskiej Normy. Dla budynku tylko ZL wpisz „nie dotyczy”.", "PN-B-02852:2001 (zasady ustalania - § 208 WT)", wt("para_208", "§ 208"), "gęstości obciążenia ogniowego pomieszczeń i stref pożarowych"),
        pp(5, "Materiały niebezpieczne pożarowo", "Czy występują? Jakie i gdzie (np. butle gazowe, farby, rozpuszczalniki, paliwo)?", f"§ 2 ust. 1 pkt 1 {R_PELNA}", r("p2", "ust. 1 pkt 1"), "materiałach niebezpiecznych pożarowo"),
        pp(6, "Strefy zagrożenia wybuchem", "TAK/NIE. Jeśli tak - gdzie i jakie strefy (0, 1, 2 dla gazów i par, 20, 21, 22 dla pyłów).", f"§ 5 {ATEX_PELNA} + dokumentacja techniczna", {"dok": ATEX, "j": "p5", "u": "§ 5"}, "Pracodawca dzieli przestrzenie zagrożone wybuchem na strefy"),
        pp(7, "Pomieszczenia zagrożone wybuchem", "TAK/NIE. Jeśli tak - gdzie, jakie strefy i na jakiej podstawie to ustalono (ocena zagrożenia wybuchem).", f"§ 37 {R_PELNA}", r("p37", "ust. 1-2"), "dokonuje się oceny zagrożenia wybuchem"),
        pp(8, "Wymagana klasa odporności pożarowej", "Podaj klasę (A-E) dla tego obiektu lub stref. Nie kopiuj tabeli z rozporządzenia.", f"§ 212 {WT_PELNA}", wt("para_212", "§ 212"), "pięć klas odporności pożarowej"),
        pp(9, "Z jakich materiałów są elementy budynku", "Opisz: a) główna konstrukcja nośna, b) konstrukcja dachu, c) strop, d) ściana zewnętrzna, e) ściana wewnętrzna, f) przekrycie dachu.", DOK_BUD, przyklad="a) żelbet monolityczny, b) drewniana więźba, c) strop Teriva, d) ceramika + styropian, e) cegła pełna, f) blachodachówka."),
        pp(10, "Odporność ogniowa elementów - istniejąca i wymagana", "Dla elementów a-f z pkt 9: klasa istniejąca (z dokumentacji) i wymagana (z tabeli dla Twojej klasy odporności pożarowej), np. R 60, REI 60, E 30.", f"§ 216 ust. 1 {WT_PELNA}", wt("para_216", "§ 216 ust. 1"), "nośność ogniowa"),
        pp(11, "Liczba stref pożarowych i sposób ich wydzielenia", "Na ile stref podzielono budynek i czym (ściany, stropy oddzielenia przeciwpożarowego).", f"§ 226 {WT_PELNA}", wt("para_226", "§ 226 ust. 1"), "Strefę pożarową stanowi budynek albo jego część"),
        pp(12, "Klasa odporności ogniowej elementów oddzielenia stref", "Tylko gdy jest więcej niż jedna strefa: wymagana klasa ścian i stropów oddzielenia oraz drzwi w nich.", f"§ 232 {WT_PELNA}", wt("para_232", "§ 232"), "Ściany i stropy stanowiące elementy oddzielenia przeciwpożarowego"),
        pp(13, "Powierzchnia stref - istniejąca i dopuszczalna", "Powierzchnia każdej strefy (wewnętrzna, z antresolami) i dopuszczalna wg tabeli (ZL - § 227, PM - § 228, IN - § 231), z ewentualnym powiększeniem za tryskacze i oddymianie.", f"§ 227 / § 228 / § 231 {WT_PELNA}", wt("para_227", "§ 227"), "Dopuszczalne powierzchnie stref pożarowych ZL"),
        pp(14, "Przestrzenie wydzielone pożarowo", "Czy są np. kotłownia, pompownia, serwerownia, magazyn? Jeśli tak - jakie.", "przepisy szczegółowe WT dla danego pomieszczenia (np. kotłownie) + dokumentacja budowlana"),
        pp(15, "Klasa odporności ogniowej elementów wydzielenia", "Dla pomieszczeń z pkt 14 - wymagana klasa ścian, stropów i drzwi wydzielających.", "przepisy szczegółowe WT dla danego pomieszczenia"),
        pp(16, "Liczba osób - w budynku i na kondygnacjach", "a) ile osób może przebywać w budynku, b) ile na każdej kondygnacji. Gdy nie wynika to z przeznaczenia - przyjmij wg powierzchni (§ 236 ust. 6).", f"§ 236 ust. 6 {WT_PELNA}", wt("para_236", "§ 236 ust. 6"), "liczbę tę należy przyjmować w odniesieniu do powierzchni"),
        pp(17, "Wyjścia, klatki schodowe, obudowa i oddymianie", "a) liczba wyjść z obiektu, b) liczba klatek schodowych, c) czy klatki są obudowane i oddymiane.", f"{DOK_BUD} + § 245 {WT_PELNA}", wt("para_245", "§ 245"), "obudowane i zamykane drzwiami dymoszczelnymi"),
        pp(18, "Długość przejść ewakuacyjnych", "Rzeczywista (zmierz na planie od najdalszego miejsca do wyjścia z pomieszczenia) i dopuszczalna (ZL - 40 m, PM - 75/100 m, z możliwym powiększeniem).", f"§ 237 ust. 1 {WT_PELNA}", wt("para_237", "§ 237 ust. 1"), "przejściem ewakuacyjnym"),
        pp(19, "Długość dojść ewakuacyjnych", "Rzeczywista (od wyjścia z pomieszczenia do wyjścia na zewnątrz lub do innej strefy, wzdłuż osi drogi) i dopuszczalna.", f"§ 256 {WT_PELNA}", wt("para_256", "§ 256"), "dojściem ewakuacyjnym"),
        pp(20, "Parametry klatki schodowej", "Rzeczywiste i wymagane: a) szerokość biegu, b) szerokość spocznika, c) wysokość stopnia, d) szerokość stopnia (z warunku 2h + s).", f"§ 68 {WT_PELNA}", wt("para_68", "§ 68"), "Graniczne wymiary schodów stałych"),
        pp(21, "Szerokości przejść i dojść ewakuacyjnych", "Rzeczywiste i wymagane. Drogi poziome: min. 0,6 m na 100 osób, nie mniej niż 1,4 m (do 20 osób - 1,2 m).", f"§ 242 {WT_PELNA}", wt("para_242", "§ 242 ust. 1"), "nie mniej niż 1,4 m"),
        pp(22, "Szerokości drzwi ewakuacyjnych", "a) drzwi z pomieszczeń, b) na drogach ewakuacyjnych, c) wyjściowe z budynku - rzeczywiste i wymagane (min. 0,6 m na 100 osób, najmniej 0,9 m, do 3 osób 0,8 m).", f"§ 239 {WT_PELNA}", wt("para_239", "§ 239 ust. 1"), "najmniejsza szerokość drzwi w świetle ościeżnicy powinna wynosić 0,9 m"),
        pp(23, "Stan sprawności osób w obiekcie", "TAK/NIE - czy uwzględniono osoby z ograniczoną sprawnością (dzieci, chorzy, niepełnosprawni). Jeśli tak - jakie rozwiązania (np. pochylnie, strefy oczekiwania, ewakuacja pozioma).", "-"),
        pp("24a", "Urządzenia ppoż: system sygnalizacji pożarowej", "Wymagany? TAK + krótki opis (np. firma, zasięg, rodzaj czujek, ROP) albo NIE.", f"§ 28 {R_PELNA}", r("p28", "ust. 1"), "Stosowanie systemu sygnalizacji pożarowej"),
        pp("24b", "Urządzenia ppoż: dźwiękowy system ostrzegawczy", "Wymagany? TAK/NIE + opis.", f"§ 29 {R_PELNA}", r("p29", "ust. 1"), "dźwiękowego systemu ostrzegawczego"),
        pp("24c", "Urządzenia ppoż: oddymianie, kurtyny dymowe", "Wymagane? TAK/NIE + opis (np. klapy dymowe w klatkach).", f"§ 245 i § 270 {WT_PELNA}", wt("para_270", "§ 270"), "Instalacja wentylacji oddymiającej powinna"),
        pp("24d", "Urządzenia ppoż: przeciwpożarowe klapy odcinające", "Wymagane? Przy przejściu przewodów wentylacyjnych przez oddzielenia przeciwpożarowe.", f"§ 268 ust. 4 {WT_PELNA}", wt("para_268", "§ 268 ust. 4"), "przeciwpożarowe klapy odcinające"),
        pp("24e", "Urządzenia ppoż: stałe urządzenia gaśnicze", "Wymagane? (tryskacze, gazowe itp.) TAK/NIE + opis.", f"§ 27 {R_PELNA}", r("p27", "ust. 1"), "stałych urządzeń gaśniczych"),
        pp("24f", "Urządzenia ppoż: hydranty wewnętrzne i zawory", "Wymagane? Jakie (25, 33, 52) i gdzie.", f"§ 19 {R_PELNA}", r("p19", "ust. 1"), "Hydranty 25 muszą być stosowane"),
        pp("24g", "Urządzenia ppoż: hydranty zewnętrzne (woda do gaszenia)", "Wymagane? TAK/NIE.", f"§ 3 {W_PELNA}", w("p3", "§ 3"), "zewnętrznego gaszenia pożaru jest wymagane"),
        pp("24h", "Urządzenia ppoż: oświetlenie ewakuacyjne", "Wymagane? TAK/NIE + opis.", f"§ 181 {WT_PELNA}", wt("para_181", "§ 181"), "samoczynnie załączające się oświetlenie awaryjne"),
        pp("24i", "Urządzenia ppoż: przeciwpożarowy wyłącznik prądu", "Wymagany? Gdzie jest i co wyłącza.", f"§ 4 ust. 2 pkt 2 {R_PELNA} (wymóg wg przepisów techniczno-budowlanych)", r("p4", "ust. 2 pkt 2"), "przeciwpożarowe wyłączniki prądu"),
        pp("24j", "Urządzenia ppoż: drzwi i bramy przeciwpożarowe", "Wymagane? Gdzie, jaka klasa (np. EI 30).", f"§ 232 ust. 1 {WT_PELNA}", wt("para_232", "§ 232 ust. 1"), "drzwi przeciwpożarowych"),
        pp("24k", "Urządzenia ppoż: dźwigi dla ekip ratowniczych", "Wymagane? (budynki ZL z kondygnacją powyżej 25 m).", f"§ 253 {WT_PELNA}", wt("para_253", "§ 253 ust. 1"), "przystosowany do potrzeb ekip ratowniczych"),
        pp(25, "Ilość środka gaśniczego w gaśnicach", "Rzeczywista i wymagana: 2 kg (3 dm³) środka na każde 100 m² (ZL I, II, III, V; PM ponad 500 MJ/m²) albo 300 m² (pozostałe).", f"§ 32 ust. 3 {R_PELNA}", r("p32", "ust. 3"), "na każde 100 m2"),
        pp(26, "Typy, rodzaje i liczba gaśnic, inny sprzęt", "Np. 8 × GP-6x ABC, 2 × GS-5x (CO₂) przy rozdzielni, koc gaśniczy w kuchni. Dobór do grup pożarów A, B, C, D, F.", f"§ 32 ust. 2 {R_PELNA}", r("p32", "ust. 2"), "Rodzaj gaśnic powinien być dostosowany"),
        pp(27, "Odległości od budynków sąsiednich (i lasu)", "Rzeczywiste odległości i minimalne wg przepisów.", f"§ 271 {WT_PELNA}", wt("para_271", "§ 271 ust. 1"), "Odległość między zewnętrznymi ścianami budynków"),
        pp(28, "Czy budynek wymaga drogi pożarowej", "TAK/NIE + uzasadnienie (który punkt § 12 ust. 1) i parametry, jeśli jest.", f"§ 12 {W_PELNA}", w("p12", "§ 12 ust. 1"), "Drogę pożarową o utwardzonej nawierzchni"),
        pp(29, "Woda do zewnętrznego gaszenia - czy wymagana i ile", "TAK/NIE; jeśli tak - ilość w dm³/s z tabel w załączniku (wg kubatury, strefy, kategorii).", f"§ 3-6 {W_PELNA}", w("p3", "§ 3"), "zewnętrznego gaszenia pożaru jest wymagane dla"),
        pp(30, "Źródła wody, hydranty zewnętrzne, stanowiska czerpania", "Opisz, gdzie są hydranty (DN 80/100), zbiorniki i dojazdy dla wozów.", f"§ 10 {W_PELNA}", w("p10", "§ 10"), "hydranty zewnętrzne nadziemne o średnicy nominalnej DN 80"),
        pp(31, "Odległości źródeł wody", "Rzeczywiste i minimalne: najbliższy hydrant od obiektu do 75 m, kolejne do 150 m, od ściany co najmniej 5 m, od krawędzi jezdni do 15 m.", f"§ 10 ust. 6 {W_PELNA}", w("p10", "§ 10 ust. 6"), "najbliższego hydrantu od chronionego obiektu budowlanego"),
        pp(32, "Zabezpieczenie instalacji użytkowych", "Wentylacyjna, grzewcza, gazowa, elektryczna, teletechniczna, odgromowa - jak zabezpieczone i czy spełniają przepisy (przeglądy, pomiary).", f"§ 4 ust. 1 pkt 2 {R_PELNA} + przepisy techniczno-budowlane i normy", r("p4", "ust. 1 pkt 2"), "niepoddawanych okresowym kontrolom"),
        pp(33, "Informacja o warunkach i strategii ewakuacji", "Czy w budynku są procedury ewakuacji, instrukcja postępowania na wypadek pożaru, plany ewakuacji, wyznaczone osoby.", f"§ 6 ust. 1 pkt 5 {R_PELNA}", r("p6", "ust. 1 pkt 5"), "warunki i organizację ewakuacji ludzi"),
        pp(34, "Czy projekt wymaga uzgodnienia z rzeczoznawcą ds. zabezpieczeń ppoż", "TAK/NIE + uzasadnienie: sprawdź, czy obiekt jest na liście obiektów istotnych w § 3 rozporządzenia z 2023 r. (np. wg kategorii ZL, kubatury, wysokości).", f"art. 6b {U_PELNA}; {UZG_PELNA}", {"a": U, "j": "a6b", "u": "art. 6b"}, "wymagają uzgodnienia z rzeczoznawcą"),
    ],
    "zalaczniki": [
        "Załącznik 1 - karta charakterystyki substancji niebezpiecznej występującej w zakładzie w największej ilości (tylko budynki PM).",
        "Załącznik 2 - plan usytuowania budynku: wymiary, odległości od sąsiednich obiektów, strefy pożarowe, ściany oddzielenia, hydranty zewnętrzne (lub inne źródła wody), miejsce zbiórki, drogi dojazdowe i pożarowe, przeciwpożarowy wyłącznik prądu.",
        "Załącznik 3 - plan ewakuacji z budynku i każdej kondygnacji: kierunki ewakuacji, znaki ewakuacyjne, gaśnice, urządzenia ppoż, przeciwpożarowy wyłącznik prądu, ściany oddzielenia, przestrzenie wydzielone.",
    ],
    "podstawy": [WT_PELNA, UZG_PELNA, R_PELNA, W_PELNA],
}

WZORY = [PRACA, IBP, WYPADEK, ORZ]


def sprawdz(opis, zr, dowod):
    try:
        jest = dowod.replace(" ", "") in tekst_jednostki(zr).replace(" ", "").replace(" ", "")
    except StopIteration:
        jest = False
    if not jest:
        print("BRAK POKRYCIA:", opis[:60], zr, dowod)
    return jest


def main():
    bledy = 0
    for sekcja in OBCHOD:
        for p in sekcja["punkty"]:
            bledy += not sprawdz(p["co"], p["zr"], p["dowod"])
    for w in WZORY:
        for x in w["kroki"] if "kroki" in w else []:
            if x["zr"]:
                bledy += not sprawdz(x["tytul"], x["zr"], x["dowod"])
        for x in w["uwagi"]:
            bledy += not sprawdz(x["t"], x["zr"], x["dowod"])
        if "zr" in w:
            bledy += not sprawdz(w["tytul"], w["zr"], w["dowod"])
    if bledy:
        sys.exit(f"{bledy} pozycji bez pokrycia w przepisach - popraw przed zapisem")
    wynik = {"obchod": OBCHOD, "wzory": WZORY}
    json.dump(wynik, open("app/data/warsztat.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("zapisano", sum(len(s["punkty"]) for s in OBCHOD), "punktów obchodu i", len(WZORY), "wzory")


if __name__ == "__main__":
    main()
