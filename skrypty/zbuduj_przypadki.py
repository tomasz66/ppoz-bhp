# Buduje app/data/ciekawostki.json: "Czy wiesz, że…" - życiowe sytuacje z podstawą prawną.
# Każdy przypadek ma "dowod" - dosłowny fragment przepisu. Skrypt sprawdza, że ten fragment
# naprawdę jest we wskazanym artykule/paragrafie, więc nic nie trafi do aplikacji bez pokrycia w prawie.
# Źródło: {"a": akt w zakładce Przepisy, "j": jednostka} albo {"dok": plik z data/dok, "j": jednostka}.
# Użycie: python3 skrypty/zbuduj_przypadki.py   (z folderu bhp-ppoz)
import json
import sys

KP, OGOLNE, SZKOL, WYP, WYPADK, MONIT = "DU_1974_141", "DU_1997_844", "DU_2004_1860", "DU_2009_870", "DU_2002_1673", "DU_1998_973"
R = "rozp-ochrona-budynkow"
U = "ustawa-ppoz"
W = "rozp-woda-drogi"


def p(d, s, t, zr, dowod, tagi):
    return {"d": d, "s": s, "t": t, "zr": zr, "dowod": dowod, "tagi": tagi}


PRZYPADKI = [
    # ── PPOŻ ──
    p("ppoz", "Właściciel podgrzewa smołę palnikiem przy remoncie dachu garażu, metr od ściany.",
      "Nie wolno rozgrzewać smoły otwartym ogniem bliżej niż 5 m od budynku, składowiska lub placu z materiałami palnymi. Wyjątek: dach niepalny w budowanym obiekcie albo specjalny podgrzewacz.",
      {"a": R, "j": "p4", "u": "ust. 1 pkt 4"}, "w odległości mniejszej niż 5 m od obiektu", ["smoła", "dach", "remont", "ogień"]),
    p("ppoz", "Sąsiad układa gałęzie i chrust pod płotem, przy granicy działki.",
      "Materiałów palnych, w tym gałęzi, chrustu i resztek roślin, nie wolno składować poza budynkami bliżej niż 4 m od granicy działki sąsiedniej.",
      {"a": R, "j": "p4", "u": "ust. 1 pkt 6"}, "w odległości mniejszej niż 4 m od granicy działki sąsiedniej", ["gałęzie", "chrust", "ogród", "działka", "ogrodzenie", "płot"]),
    p("ppoz", "Rolnik chce wiosną wypalić suchą trawę na łące.",
      "Wypalanie wierzchniej warstwy gleby i traw jest zabronione w miejscu, w którym może zapalić materiały palne lub sąsiednie obiekty. Ten sam zakaz dotyczy rozpalania ognia i wysypywania gorącego popiołu.",
      {"a": R, "j": "p4", "u": "ust. 1 pkt 5"}, "wypalanie wierzchniej warstwy gleby i traw", ["trawa", "wypalanie", "popiół", "ognisko", "łąka"]),
    p("ppoz", "W sklepie drzwi ewakuacyjne na noc i w dzień zamyka się na kłódkę „żeby nikt nie wyszedł bez płacenia”.",
      "Zakazane jest zamykanie drzwi ewakuacyjnych w sposób uniemożliwiający ich natychmiastowe użycie w razie pożaru lub innego zagrożenia.",
      {"a": R, "j": "p4", "u": "ust. 1 pkt 14"}, "zamykanie drzwi ewakuacyjnych w sposób uniemożliwiający ich natychmiastowe użycie", ["drzwi", "ewakuacja", "kłódka", "sklep", "wyjście"]),
    p("ppoz", "Drzwi przeciwpożarowe na klatce schodowej są podparte klinem, bo „ciężko się otwierają”.",
      "Nie wolno blokować drzwi i bram przeciwpożarowych tak, że nie zamkną się same w razie pożaru.",
      {"a": R, "j": "p4", "u": "ust. 1 pkt 15"}, "blokowanie drzwi i bram przeciwpożarowych", ["drzwi przeciwpożarowe", "klin", "klatka schodowa"]),
    p("ppoz", "Na korytarzu prowadzącym do wyjścia stoją kartony i palety.",
      "Materiałów palnych nie wolno składować na drogach komunikacji ogólnej służących ewakuacji ani zwężać ich przedmiotami poniżej wymaganych wymiarów.",
      {"a": R, "j": "p4", "u": "ust. 1 pkt 11"}, "składowanie materiałów palnych na drogach komunikacji ogólnej służących ewakuacji", ["korytarz", "droga ewakuacyjna", "kartony", "palety", "magazyn"]),
    p("ppoz", "Gaśnica wisi za regałem z towarem, trzeba go odsunąć, żeby ją zdjąć.",
      "Zakazane jest uniemożliwianie lub ograniczanie dostępu do gaśnic i urządzeń przeciwpożarowych, a także do wyłączników prądu i głównych kurków gazu.",
      {"a": R, "j": "p4", "u": "ust. 1 pkt 18"}, "uniemożliwianie lub ograniczanie dostępu do", ["gaśnica", "dostęp", "regał", "hydrant", "wyłącznik prądu", "kurek gazu"]),
    p("ppoz", "W piwnicy bloku lokator trzyma butlę z gazem do grilla.",
      "Butli do gazów palnych - pełnych, niepełnych i pustych - nie wolno przechowywać w piwnicach, na strychach i nieużytkowych poddaszach.",
      {"a": R, "j": "p4", "u": "ust. 1 pkt 13"}, "butli przeznaczonych do gazów palnych na nieużytkowych poddaszach i strychach oraz w piwnicach", ["butla", "gaz", "piwnica", "strych", "grill"]),
    p("ppoz", "Na strychu kamienicy mieszkańcy trzymają stare meble i gazety.",
      "Materiałów palnych nie wolno składować w pomieszczeniach technicznych, na nieużytkowych poddaszach i strychach oraz na korytarzach w piwnicach.",
      {"a": R, "j": "p4", "u": "ust. 1 pkt 12"}, "składowanie materiałów palnych w pomieszczeniach technicznych", ["strych", "poddasze", "piwnica", "meble", "kotłownia"]),
    p("ppoz", "Zasłony w restauracji wiszą tuż przy gorącym piecu.",
      "Materiałów palnych i palnego wystroju nie wolno trzymać bliżej niż 0,5 m od urządzeń, których powierzchnia może nagrzać się powyżej 100°C.",
      {"a": R, "j": "p4", "u": "ust. 1 pkt 8"}, "w odległości mniejszej niż 0,5 m od", ["zasłony", "piec", "dekoracje", "wystrój", "grzejnik"]),
    p("ppoz", "Abażur lampy z papieru dotyka żarówki.",
      "Osłony punktów świetlnych nie mogą być z materiałów palnych. Materiały trudno zapalne są dopuszczalne co najmniej 0,05 m od żarówki.",
      {"a": R, "j": "p4", "u": "ust. 1 pkt 9"}, "stosowanie na osłony punktów świetlnych materiałów palnych", ["lampa", "żarówka", "abażur", "oświetlenie"]),
    p("ppoz", "Kierowca wstawia motocykl na zimę do pomieszczenia gospodarczego, z pełnym bakiem.",
      "W pomieszczeniu, które nie jest garażem, pojazd może stać tylko z opróżnionym zbiornikiem paliwa i na stałe odłączonym akumulatorem.",
      {"a": R, "j": "p4", "u": "ust. 1 pkt 3"}, "jeżeli nie opróżniono zbiornika paliwa pojazdu", ["garaż", "samochód", "motocykl", "paliwo", "akumulator"]),
    p("ppoz", "Właściciel hurtowni pyta, czy musi wywiesić instrukcję, co robić w razie pożaru.",
      "Tak. Właściciele, zarządcy i użytkownicy budynków (poza domami jednorodzinnymi) umieszczają w widocznych miejscach instrukcje postępowania na wypadek pożaru z wykazem telefonów alarmowych.",
      {"a": R, "j": "p4", "u": "ust. 2 pkt 3"}, "umieszczają w widocznych miejscach instrukcje postępowania na wypadek pożaru", ["instrukcja", "telefony alarmowe", "tablica", "hurtownia"]),
    p("ppoz", "Szkoła planuje próbną ewakuację na jutro i nikogo nie informuje.",
      "O terminie praktycznego sprawdzenia ewakuacji trzeba powiadomić komendanta powiatowego (miejskiego) PSP najpóźniej tydzień wcześniej.",
      {"a": R, "j": "p17", "u": "ust. 4"}, "nie później niż na tydzień przed ich przeprowadzeniem", ["próbna ewakuacja", "szkoła", "komendant", "PSP"]),
    p("ppoz", "Instrukcja bezpieczeństwa pożarowego w hotelu ma 4 lata i nikt jej nie ruszał.",
      "Instrukcję bezpieczeństwa pożarowego aktualizuje się co najmniej raz na 2 lata oraz po każdej zmianie sposobu użytkowania lub procesu, która wpływa na warunki ochrony ppoż.",
      {"a": R, "j": "p6", "u": "ust. 7"}, "co najmniej raz na 2 lata", ["instrukcja bezpieczeństwa pożarowego", "IBP", "aktualizacja", "hotel"]),
    p("ppoz", "Mały warsztat (budynek 600 m³, bez strefy zagrożenia wybuchem) - czy potrzebna jest instrukcja bezpieczeństwa pożarowego?",
      "Nie jest wymagana, gdy nie ma strefy zagrożenia wybuchem, a kubatura brutto budynku nie przekracza 1000 m³.",
      {"a": R, "j": "p6", "u": "ust. 8 pkt 1"}, "nie przekracza 1000 m3", ["instrukcja bezpieczeństwa pożarowego", "IBP", "warsztat", "kubatura"]),
    p("ppoz", "Właściciel sklepu pyta, czy musi zapoznać pracowników z przepisami ppoż.",
      "Tak. Właściciel obiektu ma obowiązek zapoznać pracowników z przepisami przeciwpożarowymi i ustalić sposoby postępowania na wypadek pożaru.",
      {"a": U, "j": "a4", "u": "ust. 1 pkt 6-7"}, "zapoznać pracowników z przepisami przeciwpożarowymi", ["szkolenie ppoż", "pracownicy", "sklep"]),
    p("ppoz", "Wynajmujący lokal mówi, że za ppoż odpowiada właściciel budynku, bo „to jego budynek”.",
      "Odpowiedzialność przechodzi na zarządcę lub użytkownika, jeśli przejął ją umową. Bez umowy odpowiada ten, kto faktycznie włada obiektem.",
      {"a": U, "j": "a4", "u": "ust. 1a"}, "faktycznie władającym budynkiem", ["najem", "odpowiedzialność", "umowa", "właściciel"]),
    p("ppoz", "Przed halą zaparkowano dostawczaki na drodze pożarowej.",
      "Właściciel lub zarządca terenu musi utrzymywać drogę pożarową w stanie umożliwiającym przejazd wozów straży pożarnej.",
      {"a": R, "j": "p5", "u": ""}, "utrzymują znajdujące się na nich drogi pożarowe", ["droga pożarowa", "parking", "hala", "dojazd"]),
    p("ppoz", "W hali produkcyjnej na belkach zalega gruba warstwa pyłu drzewnego.",
      "W obiektach produkcyjnych i magazynowych, gdzie zalegają warstwy pyłów palnych, trzeba regularnie sprzątać według zasad z Polskich Norm.",
      {"a": R, "j": "p4", "u": "ust. 6"}, "pyły palne zalegające w warstwach", ["pył", "stolarnia", "hala", "sprzątanie", "wybuch"]),
    # ── BHP ──
    p("bhp", "Szef każe wejść na rusztowanie bez barierek. Pracownik się boi - może odmówić?",
      "Tak. Gdy warunki łamią przepisy BHP i stwarzają bezpośrednie zagrożenie zdrowia lub życia, pracownik może powstrzymać się od pracy, od razu zawiadamiając przełożonego. Zachowuje wynagrodzenie i nie mogą go spotkać negatywne konsekwencje.",
      {"dok": KP, "j": "a210", "u": "§ 1-3"}, "ma prawo powstrzymać się od wykonywania pracy", ["odmowa pracy", "zagrożenie", "rusztowanie", "prawa pracownika"]),
    p("bhp", "Nowy pracownik ma zacząć jutro, a badań jeszcze nie zrobił. Może wejść na halę „na próbę”?",
      "Nie. Pracodawca nie może dopuścić do pracy nikogo bez aktualnego orzeczenia lekarskiego o braku przeciwwskazań na danym stanowisku.",
      {"dok": KP, "j": "a229", "u": "§ 4"}, "nie może dopuścić do pracy pracownika bez aktualnego orzeczenia lekarskiego", ["badania lekarskie", "nowy pracownik", "orzeczenie", "medycyna pracy"]),
    p("bhp", "Pracownik wraca do tej samej firmy na to samo stanowisko po 3 tygodniach przerwy. Znowu badania wstępne?",
      "Nie, jeśli wraca w ciągu 30 dni od końca poprzedniej umowy na to samo stanowisko lub o takich samych warunkach.",
      {"dok": KP, "j": "a229", "u": "§ 1¹ pkt 1"}, "w ciągu 30 dni po rozwiązaniu lub wygaśnięciu poprzedniego stosunku pracy", ["badania wstępne", "powrót do pracy", "30 dni"]),
    p("bhp", "Pracownik był na zwolnieniu 5 tygodni. Może od razu wrócić do pracy?",
      "Po chorobie trwającej dłużej niż 30 dni pracownik musi przejść kontrolne badania lekarskie.",
      {"dok": KP, "j": "a229", "u": "§ 2"}, "trwającej dłużej niż 30 dni", ["badania kontrolne", "L4", "zwolnienie lekarskie", "choroba"]),
    p("bhp", "Kto płaci za badania okresowe i czy pracownik idzie na nie w czasie pracy?",
      "Płaci pracodawca. Badania okresowe i kontrolne przeprowadza się w miarę możliwości w godzinach pracy, a pracownik zachowuje za ten czas wynagrodzenie.",
      {"dok": KP, "j": "a229", "u": "§ 3, § 6"}, "na koszt pracodawcy", ["badania okresowe", "koszt", "wynagrodzenie"]),
    p("bhp", "Nowa osoba na magazynie ma zacząć od razu, „szkolenie się zrobi później”.",
      "Nie wolno. Pracodawca musi przeszkolić pracownika z BHP przed dopuszczeniem do pracy. Szkolenia odbywają się w czasie pracy i na koszt pracodawcy.",
      {"dok": KP, "j": "a2373", "u": "§ 2-3"}, "przed dopuszczeniem go do pracy", ["szkolenie wstępne", "instruktaż", "nowy pracownik", "magazyn"]),
    p("bhp", "Jak często szkolenie okresowe BHP ma magazynier, a jak często księgowa?",
      "Stanowiska robotnicze - nie rzadziej niż raz na 3 lata (prace szczególnie niebezpieczne - co rok). Kierownicy i pracodawcy - raz na 5 lat. Stanowiska administracyjno-biurowe - raz na 6 lat.",
      {"dok": SZKOL, "j": "para_15", "u": "ust. 1-2"}, "nie rzadziej niż raz na 3 lata", ["szkolenie okresowe", "częstotliwość", "biuro", "robotnik"]),
    p("bhp", "Firma awansowała pracownika na brygadzistę. Kiedy pierwsze szkolenie okresowe?",
      "Osoby kierujące pracownikami przechodzą pierwsze szkolenie okresowe do 6 miesięcy od objęcia stanowiska. Pozostali pracownicy - do 12 miesięcy.",
      {"dok": SZKOL, "j": "para_15", "u": "ust. 4"}, "w okresie do 6 miesięcy od rozpoczęcia pracy", ["szkolenie okresowe", "kierownik", "brygadzista", "awans"]),
    p("bhp", "Biuro rachunkowe pyta, czy księgowe w ogóle muszą mieć szkolenie okresowe.",
      "Nie muszą, jeśli przeważająca działalność firmy ma kategorię ryzyka nie wyższą niż trzecia. Obowiązek wraca, gdy ocena ryzyka pokaże taką potrzebę - wtedy szkolenie najpóźniej w ciągu 6 miesięcy.",
      {"dok": KP, "j": "a2373", "u": "§ 2²-2⁴"}, "nie jest wymagane w przypadku pracownika na stanowisku administracyjno-biurowym", ["szkolenie okresowe", "biuro rachunkowe", "administracyjno-biurowe", "kategoria ryzyka"]),
    p("bhp", "Pracownik przechodzi z biura na produkcję. Wystarczy mu szkolenie, które już ma?",
      "Nie. Przy przeniesieniu na stanowisko robotnicze albo z czynnikami szkodliwymi trzeba zrobić instruktaż stanowiskowy, zakończony sprawdzianem wiedzy i umiejętności.",
      {"dok": SZKOL, "j": "para_11", "u": "ust. 1 pkt 2, ust. 6"}, "pracownika przenoszonego na stanowisko", ["instruktaż stanowiskowy", "przeniesienie", "produkcja"]),
    p("bhp", "Pracownik raz jeździ wózkiem, a raz obsługuje prasę. Ile instruktaży?",
      "Pracownik pracujący na kilku stanowiskach powinien odbyć instruktaż stanowiskowy na każdym z nich.",
      {"dok": SZKOL, "j": "para_11", "u": "ust. 2"}, "na każdym z tych stanowisk", ["instruktaż stanowiskowy", "kilka stanowisk", "wózek"]),
    p("bhp", "Pracodawca każe pracownikom kupić sobie buty robocze.",
      "Nie może. Odzież i obuwie robocze pracodawca dostarcza nieodpłatnie, gdy własne ubranie może się zniszczyć lub mocno zabrudzić albo wymagają tego względy BHP. Za zgodą pracownika może on używać własnych - wtedy dostaje ekwiwalent.",
      {"dok": KP, "j": "a2377", "u": "§ 1, § 4"}, "dostarczyć pracownikowi nieodpłatnie odzież i obuwie robocze", ["odzież robocza", "buty", "ekwiwalent", "ubranie"]),
    p("bhp", "Operator maszyny chce pracować we własnym kombinezonie za ekwiwalent.",
      "Przy bezpośredniej obsłudze maszyn i przy pracach mocno brudzących lub skażających nie wolno pozwolić na własną odzież roboczą - zapewnia ją pracodawca.",
      {"dok": KP, "j": "a2377", "u": "§ 3"}, "bezpośrednią obsługą maszyn", ["odzież robocza", "maszyny", "ekwiwalent"]),
    p("bhp", "Firma ma 8 pracowników. Czy szef może sam „robić BHP”?",
      "Tak, jeśli ukończył odpowiednie szkolenie i zatrudnia do 10 pracowników (albo do 50 przy kategorii ryzyka nie wyższej niż trzecia). Powyżej 100 pracowników trzeba utworzyć służbę BHP.",
      {"dok": KP, "j": "a23711", "u": "§ 1"}, "zatrudnia do 10 pracowników", ["służba BHP", "mała firma", "pracodawca", "bhpowiec"]),
    p("bhp", "Firma bez BHP-owca na etacie chce zlecić BHP komuś z zewnątrz.",
      "Może. Gdy brakuje kompetentnych pracowników, pracodawca powierza zadania służby BHP specjaliście spoza zakładu pracy, który musi mieć wymagane kwalifikacje.",
      {"dok": KP, "j": "a23711", "u": "§ 2"}, "specjalistom spoza zakładu pracy", ["służba BHP", "outsourcing", "specjalista", "usługi BHP"]),
    p("bhp", "Kto w firmie ma udzielać pierwszej pomocy i ewakuować ludzi przy pożarze?",
      "Pracodawca musi wyznaczyć pracowników do pierwszej pomocy oraz do gaszenia pożarów i ewakuacji, zapewnić im środki i łączność ze służbami. Jeśli zatrudnia wyłącznie młodocianych lub niepełnosprawnych, może to robić sam.",
      {"dok": KP, "j": "a2091", "u": "§ 1, § 4"}, "wyznaczyć pracowników do", ["pierwsza pomoc", "ewakuacja", "gaszenie pożarów", "wyznaczeni pracownicy"]),
    p("bhp", "Ile apteczek ma być w zakładzie i kto je obsługuje?",
      "Liczbę, miejsce i wyposażenie apteczek ustala się z lekarzem medycyny pracy. Na każdej zmianie obsługują je przeszkoleni pracownicy, a przy apteczce wisi instrukcja pierwszej pomocy i lista tych osób.",
      {"dok": OGOLNE, "j": "para_44", "u": "ust. 2-4"}, "w porozumieniu z lekarzem", ["apteczka", "pierwsza pomoc", "lekarz medycyny pracy"]),
    p("bhp", "Pracownik spadł z drabiny. Kto ustala przyczyny wypadku?",
      "Zespół powypadkowy powołany przez pracodawcę - pracownik służby BHP i społeczny inspektor pracy.",
      {"dok": WYP, "j": "p4", "u": ""}, "pracownik służby bezpieczeństwa i higieny pracy oraz społeczny inspektor pracy", ["wypadek przy pracy", "zespół powypadkowy", "postępowanie powypadkowe"]),
    p("bhp", "Ile czasu jest na protokół powypadkowy?",
      "Zespół powypadkowy sporządza protokół najpóźniej w 14 dni od zawiadomienia o wypadku. Opóźnienie trzeba uzasadnić w protokole.",
      {"dok": WYP, "j": "p9", "u": "ust. 1-2"}, "nie później niż w terminie 14 dni", ["protokół powypadkowy", "termin", "wypadek przy pracy"]),
    p("bhp", "Na budowie zginął pracownik. Kogo pracodawca musi zawiadomić?",
      "O wypadku śmiertelnym, ciężkim lub zbiorowym pracodawca niezwłocznie zawiadamia okręgowego inspektora pracy i prokuratora.",
      {"dok": KP, "j": "a234", "u": "§ 2"}, "niezwłocznie zawiadomić właściwego okręgowego inspektora pracy i prokuratora", ["wypadek śmiertelny", "ciężki wypadek", "PIP", "prokurator"]),
    p("bhp", "Jak długo trzymać dokumentację z wypadku przy pracy?",
      "Protokół powypadkowy z pozostałą dokumentacją pracodawca przechowuje przez 10 lat. Musi też prowadzić rejestr wypadków.",
      {"dok": KP, "j": "a234", "u": "§ 3-3¹"}, "przez 10 lat", ["dokumentacja powypadkowa", "archiwum", "rejestr wypadków"]),
    p("bhp", "Pracownik po alkoholu przewrócił się na hali i złamał rękę. Czy dostanie odszkodowanie z ZUS?",
      "Świadczenia wypadkowe nie przysługują, jeśli nietrzeźwy pracownik w znacznym stopniu przyczynił się do wypadku. Nie przysługują też, gdy jedyną przyczyną było umyślne lub rażąco niedbałe złamanie przepisów BHP przez pracownika.",
      {"dok": WYPADK, "j": "a21", "u": "ust. 1-2"}, "będąc w stanie nietrzeźwości", ["alkohol", "wypadek", "ZUS", "odszkodowanie", "nietrzeźwość"]),
    p("bhp", "Księgowa pracuje przy komputerze 8 godzin bez przerwy.",
      "Pracodawca zapewnia albo przeplatanie pracy przy monitorze z inną pracą (nie dłużej niż godzina ciągiem), albo co najmniej 5 minut przerwy po każdej godzinie - wliczanej do czasu pracy.",
      {"dok": MONIT, "j": "p7", "u": ""}, "co najmniej 5-minutową przerwę", ["komputer", "monitor", "przerwa", "biuro"]),
    p("bhp", "Pracownik biurowy potrzebuje okularów do pracy przy komputerze. Kto płaci?",
      "Pracodawca zapewnia okulary lub soczewki korygujące wzrok, jeśli badanie okulistyczne w ramach medycyny pracy wykaże ich potrzebę przy pracy z monitorem.",
      {"dok": MONIT, "j": "p8", "u": "ust. 2"}, "okulary lub szkła kontaktowe korygujące wzrok", ["okulary", "monitor", "komputer", "biuro"]),
    p("bhp", "W małym pokoju biurowym siedzi 6 osób na 9 m².",
      "Na każdego pracownika w pomieszczeniu stałej pracy powinno przypadać co najmniej 13 m³ wolnej objętości i 2 m² wolnej powierzchni podłogi.",
      {"dok": OGOLNE, "j": "para_19", "u": "ust. 2"}, "13 m3 wolnej objętości", ["biuro", "metraż", "pomieszczenie pracy", "powierzchnia"]),
    p("bhp", "Od jakiej wysokości praca to już „praca na wysokości”?",
      "Od 1,0 m nad podłogą lub ziemią.",
      {"dok": OGOLNE, "j": "para_105", "u": "ust. 1"}, "co najmniej 1,0 m nad poziomem podłogi lub ziemi", ["praca na wysokości", "antresola", "podest"]),
    p("bhp", "Na antresoli magazynu nie ma barierki, bo „przecież każdy uważa”.",
      "Powierzchnie wyżej niż 1,0 m, na których przebywają pracownicy, wymagają balustrady: poręcz na wysokości co najmniej 1,1 m, krawężnik co najmniej 0,15 m i poprzeczka w połowie.",
      {"dok": OGOLNE, "j": "para_106", "u": "ust. 1"}, "co najmniej 1,1 m", ["balustrada", "barierka", "antresola", "praca na wysokości"]),
    p("bhp", "Pracownik niesie po drabinie worek cementu 25 kg.",
      "Drabiną nie wolno przenosić ciężarów powyżej 10 kg. Zakazane jest też m.in. używanie drabiny rozstawnej jako przystawnej, schodzenie plecami i noszenie drabiny dłuższej niż 4 m w pojedynkę.",
      {"dok": OGOLNE, "j": "para_50", "u": "ust. 2"}, "o masie powyżej 10 kg", ["drabina", "ciężar", "budowa", "remont"]),
    p("bhp", "Monter pracuje na drabinie na 3 m bez szelek i kasku.",
      "Przy pracach na drabinach powyżej 2 m pracodawca zapewnia sprzęt chroniący przed upadkiem (np. szelki z linką) i hełmy ochronne do prac na wysokości.",
      {"dok": OGOLNE, "j": "para_110", "u": "ust. 1"}, "hełmów ochronnych", ["drabina", "szelki", "kask", "praca na wysokości"]),
    p("bhp", "Czy pracodawca musi dawać pracownikom wodę do picia?",
      "Tak - wszystkim pracownikom wodę zdatną do picia lub inne napoje, a przy pracy w warunkach szczególnie uciążliwych dodatkowo inne napoje.",
      {"dok": OGOLNE, "j": "para_112", "u": ""}, "wodę zdatną do picia", ["woda", "napoje", "upał"]),
    p("bhp", "Lipiec 2027, w hali jest 36°C.",
      "Od 11.01.2027 w pomieszczeniach pracy temperatura nie może przekraczać 35°C (chyba że nie pozwala na to technologia). Powyżej 28°C pracodawca musi zastosować rozwiązania techniczne lub organizacyjne.",
      {"dok": "DU_2026_927", "j": "p1", "u": "§ 30a"}, "niewyższą niż 35", ["upał", "temperatura", "hala", "lato"]),
    p("bhp", "Firma zatrudnia 12 osób. Czy potrzebny jest regulamin antymobbingowy?",
      "Tak. Pracodawca zatrudniający co najmniej 10 pracowników ustala reguły i procedury przeciwdziałania mobbingowi i dyskryminacji w regulaminie (osobnym albo w regulaminie pracy).",
      {"dok": KP, "j": "a943a", "u": "§ 1"}, "co najmniej 10 pracowników", ["mobbing", "regulamin", "dyskryminacja"]),
    p("bhp", "Kierownik skarży się, że zespół go izoluje i ośmiesza. Czy to może być mobbing?",
      "Tak. Według nowych przepisów mobbing może pochodzić od pracodawcy, przełożonego, współpracownika, ale też od podwładnego - od jednej osoby albo od grupy.",
      {"dok": KP, "j": "a943_2", "u": "§ 8"}, "podwładnego", ["mobbing", "kierownik", "podwładny"]),
    p("bhp", "Inspektor pracy uznał, że zleceniobiorca pracuje jak etatowiec.",
      "Inspektor może najpierw polecić zawarcie umowy o pracę, a jeśli pracodawca tego nie zrobi - w drodze decyzji stwierdzić istnienie stosunku pracy.",
      {"dok": "DU_2026_473", "j": "a1", "u": "pkt 2"}, "stwierdzania, w drodze decyzji, istnienia stosunku pracy", ["PIP", "umowa zlecenie", "B2B", "etat"]),
    p("bhp", "Pracownik nie dostał papierowego orzeczenia z medycyny pracy. Gdzie je znajdzie?",
      "Orzeczenie w postaci elektronicznej trafia do Systemu Informacji Medycznej, a pracownik widzi je na Internetowym Koncie Pacjenta. Papierowy wydruk dostaje na żądanie.",
      {"dok": "DU_2026_456", "j": "p1", "u": "pkt 4"}, "Internetowego Konta Pacjenta", ["orzeczenie lekarskie", "IKP", "medycyna pracy", "e-orzeczenie"]),
]


def tekst_jednostki(zr):
    if "a" in zr:
        akty = json.load(open("app/data/akty.json", encoding="utf-8"))["akty"]
        j = next(j for a in akty if a["id"] == zr["a"] for j in a["jednostki"] if j["id"] == zr["j"])
    else:
        d = json.load(open(f"app/data/dok/{zr['dok']}.json", encoding="utf-8"))
        j = next(j for j in d["jednostki"] if j["id"] == zr["j"])
    return " ".join(l["t"] for l in j["linie"]) + " " + j.get("uwaga", "")


def main():
    stare = json.load(open("app/data/ciekawostki.json", encoding="utf-8"))
    bledy = 0
    for c in PRZYPADKI:
        try:
            jest = c["dowod"].replace(" ", "") in tekst_jednostki(c["zr"]).replace(" ", "").replace(" ", "")
        except StopIteration:
            jest = False
        if not jest:
            bledy += 1
            print("BRAK POKRYCIA:", c["s"][:60], c["zr"], c["dowod"])
    # Dotychczasowe ciekawostki (zweryfikowane wcześniej) zostają - jako fakty bez opisu sytuacji.
    for c in stare["ciekawostki"]:
        c.setdefault("d", "ppoz" if c["zr"].get("a") in ("rozp-ochrona-budynkow", "ustawa-ppoz", "rozp-woda-drogi") else "bhp")
    if bledy:
        sys.exit(f"{bledy} przypadków bez pokrycia w przepisach - popraw przed zapisem")
    wynik = {"przypadki": PRZYPADKI, "ciekawostki": stare["ciekawostki"]}
    json.dump(wynik, open("app/data/ciekawostki.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("zapisano", len(PRZYPADKI), "przypadków +", len(stare["ciekawostki"]), "ciekawostek; memy i żarty usunięte")


if __name__ == "__main__":
    main()
