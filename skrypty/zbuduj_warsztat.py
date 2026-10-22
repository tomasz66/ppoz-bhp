# Buduje app/data/warsztat.json: lista kontrolna "Obchód obiektu" i wzory dokumentów (IBP, wypadek, ORZ).
# Każdy punkt i krok ma "dowod" - dosłowny fragment przepisu. Skrypt sprawdza, że ten fragment
# naprawdę jest we wskazanym artykule/paragrafie, więc nic nie trafi do aplikacji bez pokrycia w prawie.
# Użycie: python3 skrypty/zbuduj_warsztat.py   (z folderu bhp-ppoz)
import json
import sys

from zbuduj_przypadki import KP, OGOLNE, WYP, R, U, tekst_jednostki


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

WZORY = [IBP, WYPADEK, ORZ]


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
