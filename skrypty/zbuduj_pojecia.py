# Buduje app/data/pojecia.json: karty pojęć ppoż i BHP do nauki i do tłumaczenia klientom.
# Karta: definicja, przykład z życia, typowy błąd, "jak powiedzieć klientowi", pojęcia powiązane
# i pytania, o które ktoś może dopytać. Definicja i każda odpowiedź mają "dowod" - dosłowny fragment
# przepisu, sprawdzany w tekście jednostki (jak w zbuduj_przypadki.py).
# Użycie: python3 skrypty/zbuduj_pojecia.py   (z folderu bhp-ppoz)
import json
import sys

from zbuduj_przypadki import KP, OGOLNE, SZKOL, WYP, WYPADK, R, U, W, tekst_jednostki

WT = "DU_2002_690"
NDS = "DU_2018_1286"


def r(j, u):
    return {"a": R, "j": j, "u": u}


def u(j, uu):
    return {"a": U, "j": j, "u": uu}


def w(j, uu):
    return {"a": W, "j": j, "u": uu}


def d(dok, j, uu):
    return {"dok": dok, "j": j, "u": uu}


def q(pyt, odp, zr, dowod):
    return {"q": pyt, "a": odp, "zr": zr, "dowod": dowod}


def karta(id, nazwa, dz, defi, zr, dowod, przyklad, blad, klient, powiazane, dopytania):
    return {"id": id, "nazwa": nazwa, "d": dz, "def": defi, "zr": zr, "dowod": dowod, "przyklad": przyklad,
            "blad": blad, "klient": klient, "powiazane": powiazane, "dopytania": dopytania}


POJECIA = [
    # ── PPOŻ: budynek i jego podział ──
    karta("strefa-pozarowa", "Strefa pożarowa", "ppoz",
          "Budynek albo jego część oddzielona od reszty ścianami i stropami oddzielenia przeciwpożarowego albo pasem wolnego terenu - tak, żeby pożar nie przeszedł dalej.",
          d(WT, "para_226", "§ 226 ust. 1 WT"), "Strefę pożarową stanowi budynek albo jego część",
          "Hala magazynowa z biurem oddzielonym ścianą ogniową i drzwiami przeciwpożarowymi - to dwie strefy: magazynowa (PM) i biurowa (ZL III).",
          "Przebicie ściany oddzielenia pod nową instalację bez uszczelnienia przejścia albo wymiana drzwi przeciwpożarowych na zwykłe - strefa przestaje być strefą.",
          "To część budynku, w której pożar ma zostać zamknięty na tyle długo, żeby ludzie zdążyli wyjść, a strażacy dojechać.",
          ["zl", "pm", "goo", "gasnica"],
          [q("Jak liczy się powierzchnię strefy pożarowej?", "Jako powierzchnię wewnętrzną budynku lub jego części, łącznie z antresolami.",
             d(WT, "para_226", "§ 226 ust. 3 WT"), "wlicza się do niej także powierzchnię antresoli"),
           q("Czy jedno piętro może być osobną strefą?", "Tak - kondygnacja może być częścią budynku tworzącą strefę, jeśli klatki schodowe i szyby dźwigowe spełniają wymagania dla klatek.",
             d(WT, "para_226", "§ 226 ust. 2 WT"), "jest także jego kondygnacja"),
           q("Po co mi wiedzieć, ile ma strefa?", "Od powierzchni strefy zależy m.in. liczba gaśnic: 2 kg środka gaśniczego na każde 100 m² albo 300 m² strefy.",
             r("p32", "ust. 3"), "na każde 100 m2")]),
    karta("zl", "Kategorie zagrożenia ludzi (ZL I-V)", "ppoz",
          "Podział budynków i stref, w których przebywają ludzie (mieszkalne, zamieszkania zbiorowego, użyteczności publicznej), według tego, kto w nich przebywa i jak łatwo się ewakuuje.",
          d(WT, "para_209", "§ 209 ust. 2 WT"), "zalicza się do jednej lub do więcej niż jedna spośród następujących kategorii zagrożenia ludzi",
          "ZL I - kino, sala weselna (ponad 50 osób z zewnątrz). ZL II - przedszkole, szpital, DPS. ZL III - urząd, biuro, sklep. ZL IV - mieszkania. ZL V - hotel, internat.",
          "Przyjęcie, że mały sklep to zawsze ZL III - jeśli jest w nim pomieszczenie dla ponad 50 klientów naraz, wchodzi ZL I z ostrzejszymi wymaganiami.",
          "Kategoria mówi, jak trudna będzie ewakuacja. Im trudniejsza (np. dzieci, chorzy, tłum obcych ludzi), tym ostrzejsze przepisy.",
          ["strefa-pozarowa", "pm", "ewakuacja", "hydrant"],
          [q("Do jakiej kategorii należy przedszkole?", "ZL II - budynki przeznaczone przede wszystkim dla ludzi o ograniczonej zdolności poruszania się, np. szpitale, żłobki, przedszkola, domy dla osób starszych.",
             d(WT, "para_209", "§ 209 ust. 2 pkt 2 WT"), "żłobki, przedszkola"),
           q("Kiedy budynek wpada do ZL I?", "Gdy ma pomieszczenia do jednoczesnego przebywania ponad 50 osób, które nie są jego stałymi użytkownikami (i nie jest przeznaczony głównie dla osób o ograniczonej zdolności poruszania się).",
             d(WT, "para_209", "§ 209 ust. 2 pkt 1 WT"), "ponad 50 osób niebędących ich stałymi użytkownikami"),
           q("A blok mieszkalny?", "ZL IV - budynki mieszkalne.", d(WT, "para_209", "§ 209 ust. 2 pkt 4 WT"), "ZL IV - mieszkalne")]),
    karta("pm", "Strefa PM (produkcyjna i magazynowa)", "ppoz",
          "Budynki i strefy produkcyjne i magazynowe. Do PM zalicza się też garaże, kotłownie, hydrofornie, rozdzielnie elektryczne i podobne pomieszczenia.",
          d(WT, "para_209", "§ 209 ust. 1 i 3 WT"), "garaży, hydroforni, kotłowni",
          "Warsztat samochodowy, stolarnia, magazyn hurtowni, kotłownia w szkole.",
          "Traktowanie kotłowni czy garażu w budynku biurowym jak zwykłego pomieszczenia biurowego.",
          "W strefach PM o zagrożeniu decyduje nie liczba ludzi, tylko to, ile i czego się tam pali - stąd pytania o ilość i rodzaj składowanych materiałów.",
          ["goo", "strefa-pozarowa", "zl"],
          [q("Od czego zależą wymagania w strefie PM?", "Głównie od gęstości obciążenia ogniowego - np. przy ponad 500 MJ/m² jedna gaśnica (2 kg środka) przypada na każde 100 m², a nie 300 m².",
             r("p32", "ust. 3 pkt 1 lit. b"), "produkcyjnej i magazynowej o gęstości obciążenia ogniowego ponad 500 MJ/m2")]),
    karta("goo", "Gęstość obciążenia ogniowego", "ppoz",
          "Ile energii (ciepła) wydzieliłoby się przy spaleniu wszystkiego, co palne w pomieszczeniu lub strefie, w przeliczeniu na 1 m² - w MJ/m². Zasady jej ustalania podaje Polska Norma, do której odsyłają warunki techniczne.",
          d(WT, "para_208", "§ 208 WT"), "gęstości obciążenia ogniowego pomieszczeń i stref pożarowych",
          "Magazyn kartonów i palet ma dużą gęstość (często ponad 500 MJ/m²), magazyn stalowych profili - małą.",
          "Zmiana tego, co się składuje (np. z metalu na tworzywa), bez sprawdzenia, czy nie przekroczono progów 500, 1000 albo 4000 MJ/m².",
          "To miara, „ile paliwa” leży w hali. Więcej paliwa - większy pożar - więcej gaśnic i ostrzejsze wymagania.",
          ["pm", "strefa-pozarowa", "gasnica"],
          [q("Jaki próg najczęściej zmienia wymagania?", "500 MJ/m² - np. dla liczby gaśnic w strefach produkcyjnych i magazynowych.",
             r("p32", "ust. 3 pkt 1 lit. b"), "ponad 500 MJ/m2")]),
    karta("materialy-niebezpieczne", "Materiały niebezpieczne pożarowo", "ppoz",
          "M.in. gazy palne, ciecze palne o temperaturze zapłonu poniżej 55°C, materiały samozapalne, wybuchowe i pirotechniczne oraz inne, jeśli sposób ich składowania lub użycia może spowodować pożar.",
          r("p2", "ust. 1 pkt 1"), "ciecze palne o temperaturze zapłonu poniżej 328,15 K (55ºC)",
          "Benzyna, rozpuszczalniki i farby w warsztacie, butle z propanem, fajerwerki w sklepie.",
          "Kanister benzyny w kotłowni albo rozpuszczalniki przy grzejniku.",
          "To rzeczy, które zapalą się łatwo albo gwałtownie - trzymamy je osobno, oznaczone i z dala od ognia.",
          ["strefa-wybuchu", "prace-pozarowe"],
          [q("Czy takie miejsca trzeba oznakować?", "Tak - pomieszczenia i tereny z materiałami niebezpiecznymi pożarowo oznakowuje się znakami zgodnymi z Polskimi Normami.",
             r("p4", "ust. 2 pkt 4 lit. e"), "pomieszczenia i tereny z materiałami niebezpiecznymi pożarowo"),
           q("Czy można tam palić?", "Nie - w miejscach występowania materiałów niebezpiecznych pożarowo zakazany jest otwarty ogień i palenie tytoniu.",
             r("p4", "ust. 1 pkt 1 lit. b"), "w miejscach występowania materiałów niebezpiecznych pożarowo")]),
    karta("strefa-wybuchu", "Strefa zagrożenia wybuchem", "ppoz",
          "Przestrzeń, w której może powstać mieszanina wybuchowa substancji palnych z powietrzem (stężenie między dolną a górną granicą wybuchowości).",
          r("p2", "ust. 1 pkt 6"), "mieszanina wybuchowa substancji palnych z powietrzem",
          "Lakiernia, magazyn gazów, silos z pyłem drzewnym lub mąką.",
          "Spawanie w pomieszczeniu, gdzie wcześniej malowano, bez sprawdzenia stężenia par.",
          "Tu wystarczy iskra, żeby doszło do wybuchu - dlatego żadnego ognia, iskrzących narzędzi i zwykłych urządzeń elektrycznych.",
          ["materialy-niebezpieczne", "prace-pozarowe", "ibp"],
          [q("Czy przy strefie wybuchu zawsze trzeba mieć IBP?", "Zwolnienie z instrukcji (małe obiekty do 1000 m³) działa tylko, gdy nie ma strefy zagrożenia wybuchem.",
             r("p6", "ust. 8"), "jeżeli nie występuje w nich strefa zagrożenia wybuchem"),
           q("Kiedy wolno tam spawać?", "Tylko gdy stężenie par lub gazów w miejscu pracy nie przekracza 10% dolnej granicy wybuchowości.",
             r("p36", "ust. 2 pkt 2"), "nie przekracza 10% ich dolnej granicy wybuchowości")]),
    # ── PPOŻ: urządzenia i sprzęt ──
    karta("urzadzenia-ppoz", "Urządzenia przeciwpożarowe", "ppoz",
          "Urządzenia do zapobiegania, wykrywania i zwalczania pożaru albo ograniczania jego skutków: m.in. instalacje gaśnicze, sygnalizacja pożarowa, oświetlenie ewakuacyjne, hydranty, oddymianie, drzwi przeciwpożarowe sterowane systemem, przeciwpożarowe wyłączniki prądu.",
          r("p2", "ust. 1 pkt 9"), "hydranty wewnętrzne i zawory hydrantowe",
          "W biurowcu: czujki i centrala sygnalizacji pożaru, hydranty na korytarzach, oprawy oświetlenia awaryjnego nad wyjściami.",
          "Brak przeglądu, bo „przecież nic się nie paliło”, albo zastawione elementy sterujące (przyciski oddymiania, ROP).",
          "To sprzęt, który ma zadziałać w najgorszym momencie - jeśli nie jest sprawdzany, nie wiadomo, czy zadziała.",
          ["gasnica", "hydrant", "ppwp"],
          [q("Jak często przegląd?", "W terminach producenta, ale nie rzadziej niż raz w roku.", r("p3", "ust. 3"), "nie rzadziej jednak niż raz w roku"),
           q("A autonomiczne czujki dymu w mieszkaniu?", "Do nich nie stosuje się tych zasad przeglądów - montuje się je, konserwuje i eksploatuje według instrukcji producenta.",
             r("p3", "ust. 3a"), "autonomicznych czujek dymu")]),
    karta("gasnica", "Gaśnica - dobór i rozmieszczenie", "ppoz",
          "Gaśnica musi pasować do grup pożarów, które mogą wystąpić: A - ciała stałe, B - ciecze, C - gazy, D - metale, F - tłuszcze w urządzeniach kuchennych.",
          r("p32", "ust. 2"), "F - tłuszczów i olejów w urządzeniach kuchennych",
          "Kuchnia restauracji z frytownicą - gaśnica do grupy F. Biuro - zwykle proszkowa ABC lub pianowa.",
          "Gaśnica proszkowa przy frytownicy zamiast gaśnicy do tłuszczów, albo gaśnica schowana za regałem.",
          "Gaśnica ma wisieć tam, gdzie każdy ją zobaczy i dobiegnie w kilka sekund, i ma pasować do tego, co się może zapalić.",
          ["urzadzenia-ppoz", "strefa-pozarowa", "goo"],
          [q("Ile gaśnic?", "Jedna jednostka 2 kg (lub 3 dm³) środka gaśniczego na każde 100 m² strefy (ZL I, II, III, V, PM ponad 500 MJ/m², wybuch) albo na 300 m² w pozostałych.",
             r("p32", "ust. 3"), "na każde 100 m2"),
           q("Jak daleko do gaśnicy?", "Z każdego miejsca, gdzie może być człowiek, nie więcej niż 30 m.", r("p33", "ust. 2 pkt 1"), "nie powinna być większa niż 30 m"),
           q("Ile miejsca przed gaśnicą?", "Dostęp o szerokości co najmniej 1 m.", r("p33", "ust. 2 pkt 2"), "dostęp o szerokości co najmniej 1 m"),
           q("Gdzie wieszać?", "W miejscach łatwo dostępnych i widocznych: przy wejściach, na klatkach schodowych, korytarzach, przy wyjściach na zewnątrz - z dala od pieców i grzejników.",
             r("p33", "ust. 1"), "przy wyjściach z pomieszczeń na zewnątrz")]),
    karta("hydrant", "Hydrant wewnętrzny (25, 33, 52)", "ppoz",
          "Punkt poboru wody w budynku: hydrant 25 i 33 (wąż półsztywny), hydrant 52 (wąż płasko składany) albo sam zawór 52 dla straży.",
          r("p18", "ust. 1"), "hydrantem 52",
          "Szafka hydrantowa 25 na korytarzu biurowca z wężem półsztywnym na zwijadle.",
          "Szafka zastawiona szafą lub kartonami, wąż bez próby ciśnieniowej od lat.",
          "To „kran strażacki” - może z niego skorzystać pracownik (hydrant 25) albo straż. Musi być do niego wolny dostęp.",
          ["urzadzenia-ppoz", "zl", "gasnica"],
          [q("Na jakiej wysokości zawór?", "1,35 ± 0,1 m od podłogi.", r("p21", "ust. 1"), "1,35±0,1 m"),
           q("Co ile próba węży?", "Raz na 5 lat próba ciśnieniowa na maksymalne ciśnienie robocze.", r("p3", "ust. 4"), "raz na 5 lat poddawane próbie ciśnieniowej"),
           q("Jak długo musi być woda?", "Zasilanie hydrantów wewnętrznych - co najmniej przez 1 godzinę.", r("p18", "ust. 4"), "co najmniej przez 1 godzinę")]),
    karta("ppwp", "Przeciwpożarowy wyłącznik prądu", "ppoz",
          "Urządzenie do odcięcia prądu w budynku na potrzeby akcji gaśniczej. Obiekty wyposaża się w nie zgodnie z warunkami technicznymi.",
          r("p4", "ust. 2 pkt 2"), "przeciwpożarowe wyłączniki prądu",
          "Czerwony przycisk w skrzynce przy wejściu do hali, opisany „Przeciwpożarowy wyłącznik prądu”.",
          "Wyłącznik zastawiony, bez oznakowania, albo nikt nie wie, co wyłącza.",
          "Dzięki niemu strażak może bezpiecznie lać wodę, bo instalacja nie jest pod napięciem.",
          ["urzadzenia-ppoz"],
          [q("Czy dostęp do niego musi być wolny?", "Tak - zakazane jest ograniczanie dostępu do wyłączników i tablic rozdzielczych prądu.",
             r("p4", "ust. 1 pkt 18 lit. f"), "wyłączników i tablic rozdzielczych prądu elektrycznego")]),
    # ── PPOŻ: ewakuacja i dojazd ──
    karta("ewakuacja", "Przejście i droga ewakuacyjna", "ppoz",
          "Przejście ewakuacyjne to droga w pomieszczeniu do wyjścia z niego. Jego długość jest ograniczona, np. w strefach ZL do 40 m.",
          d(WT, "para_237", "§ 237 ust. 1 WT"), "przejściem ewakuacyjnym",
          "W hali magazynowej z regałami: od najdalszego regału do drzwi wyjściowych.",
          "Palety na korytarzu, drzwi ewakuacyjne zamknięte na klucz „żeby nikt nie wychodził”.",
          "To droga, którą ludzie wyjdą w dymie i panice - musi być krótka, wolna i oznakowana.",
          ["zl", "probna-ewakuacja", "ibp"],
          [q("Czy drzwi ewakuacyjne można zamykać na klucz?", "Nie w sposób, który uniemożliwia ich natychmiastowe użycie w razie pożaru.",
             r("p4", "ust. 1 pkt 14"), "zamykanie drzwi ewakuacyjnych w sposób uniemożliwiający ich natychmiastowe użycie"),
           q("Czy muszą być oznakowane?", "Tak - drogi i wyjścia ewakuacyjne oznakowuje się znakami zgodnymi z Polskimi Normami (poza budynkami mieszkalnymi).",
             r("p4", "ust. 2 pkt 4 lit. a"), "drogi i wyjścia ewakuacyjne"),
           q("A oświetlenie awaryjne?", "Tak, w pomieszczeniach i na drogach ewakuacyjnych wymienionych w przepisach techniczno-budowlanych.",
             r("p15", "ust. 1 pkt 5"), "oświetlenia awaryjnego")]),
    karta("droga-pozarowa", "Droga pożarowa", "ppoz",
          "Utwardzona droga, którą wozy straży dojadą do budynku o każdej porze roku. Wymagana m.in. dla budynków ZL I i ZL II, wysokich oraz dużych stref PM.",
          w("p12", "§ 12 ust. 1"), "Drogę pożarową o utwardzonej nawierzchni",
          "Pas wzdłuż dłuższego boku przedszkola, z którego drabina sięgnie okien.",
          "Parking, kontener na śmieci albo szlaban bez klucza na drodze pożarowej.",
          "To droga dla wozu strażackiego i drabiny - jeśli jest zastawiona, pomoc stoi kilkadziesiąt metrów dalej.",
          ["zl", "ewakuacja"],
          [q("Jaka szerokość?", "Co najmniej 4 m (w miejscach ustawienia wozów i 10 m od nich), na pozostałych odcinkach 3,5 m albo 3 m.",
             w("p13", "§ 13 ust. 1"), "co najmniej 4 m"),
           q("Jak daleko od ściany?", "Bliższa krawędź drogi 5-15 m od ściany budynku ZL i 5-25 m dla pozostałych.", w("p12", "§ 12 ust. 2"), "o 5–15 m dla obiektów zaliczanych do kategorii zagrożenia ludzi"),
           q("A jeśli droga jest ślepa?", "Musi być przejazd bez cofania albo plac manewrowy 20 m × 20 m (lub inne rozwiązanie do zawracania).",
             w("p12", "§ 12 ust. 9"), "20 m x 20 m")]),
    # ── PPOŻ: dokumenty i organizacja ──
    karta("ibp", "Instrukcja bezpieczeństwa pożarowego (IBP)", "ppoz",
          "Dokument z warunkami ochrony ppoż obiektu, wyposażeniem i przeglądami, postępowaniem w razie pożaru, ewakuacją, obowiązkami ludzi i planami. Wymagany w obiektach użyteczności publicznej, zamieszkania zbiorowego, produkcyjnych, magazynowych i inwentarskich.",
          r("p6", "ust. 1"), "zapewniają i wdrażają instrukcję bezpieczeństwa pożarowego",
          "Sklep 450 m² z zapleczem - IBP z planem, rozmieszczeniem 6 gaśnic i opisem ewakuacji.",
          "Instrukcja „z szuflady” sprzed 6 lat, nieaktualna po przebudowie, której nikt z pracowników nie zna.",
          "To instrukcja obsługi budynku na wypadek pożaru - kto co robi, gdzie jest sprzęt, którędy wychodzimy.",
          ["ewakuacja", "probna-ewakuacja", "strefa-wybuchu", "wlasciciel"],
          [q("Kiedy nie jest wymagana?", "Gdy nie ma strefy zagrożenia wybuchem, a budynek lub strefa ma do 1000 m³ (inwentarski do 1500 m³, obiekt inny niż budynek do 1000 m²).",
             r("p6", "ust. 8"), "nie przekracza 1000 m3"),
           q("Co ile aktualizacja?", "Co najmniej raz na 2 lata i po zmianach wpływających na ochronę ppoż.", r("p6", "ust. 7"), "co najmniej raz na 2 lata"),
           q("Gdzie ją trzymać?", "W miejscach dostępnych dla ekip ratowniczych.", r("p6", "ust. 9"), "w miejscach dostępnych dla ekip ratowniczych")]),
    karta("probna-ewakuacja", "Praktyczne sprawdzenie ewakuacji (próbna ewakuacja)", "ppoz",
          "Ćwiczenie organizacji i warunków ewakuacji z całego obiektu - co najmniej raz na 2 lata w obiekcie dla ponad 50 stałych użytkowników (poza ZL IV).",
          r("p17", "ust. 1"), "co najmniej raz na 2 lata przeprowadzać praktyczne sprawdzenie",
          "Biurowiec z 80 pracownikami - alarm, wyjście wszystkich na miejsce zbiórki, sprawdzenie czasu i problemów.",
          "Ćwiczenie „na papierze” bez wyjścia ludzi albo bez powiadomienia straży.",
          "Raz na jakiś czas sprawdzamy w praktyce, czy wszyscy wiedzą, którędy i dokąd wyjść - lepiej odkryć problem na ćwiczeniu niż w dymie.",
          ["ewakuacja", "ibp", "zl"],
          [q("A w szkole i przedszkolu?", "Co najmniej raz w roku, najpóźniej 3 miesiące od przyjścia nowych użytkowników.", r("p17", "ust. 2"), "co najmniej raz na rok"),
           q("Czy trzeba zgłosić straży?", "Tak - komendanta powiatowego PSP powiadamia się najpóźniej tydzień wcześniej.", r("p17", "ust. 4"), "nie później niż na tydzień")]),
    karta("prace-pozarowe", "Prace niebezpieczne pod względem pożarowym", "ppoz",
          "Prace remontowo-budowlane z otwartym ogniem, cięciem z iskrami i spawaniem - w obiektach, na dachach, terenach przyległych i placach składowych - oraz prace w strefach zagrożonych wybuchem.",
          r("p2", "ust. 1 pkt 4"), "prace remontowo-budowlane związane z użyciem otwartego ognia",
          "Spawanie konstrukcji w hali, cięcie szlifierką na dachu, zgrzewanie papy palnikiem.",
          "Spawacz z zewnętrznej firmy zaczyna bez sprawdzenia miejsca i bez gaśnicy, a po pracy wszyscy wychodzą - żar tli się w izolacji.",
          "Większość pożarów przy remontach zaczyna się od iskry, którą ktoś przegapił. Dlatego przed pracą oceniamy miejsce, a po pracy je kontrolujemy.",
          ["strefa-wybuchu", "materialy-niebezpieczne", "ibp"],
          [q("Co musi zrobić właściciel przed pracą?", "M.in. ocenić zagrożenie pożarowe w miejscu pracy, ustalić zabezpieczenia, wskazać odpowiedzialnych i dopuścić tylko osoby z kwalifikacjami.",
             r("p36", "ust. 1"), "ocenia zagrożenie pożarowe w miejscu"),
           q("A po pracy?", "Skontrolować miejsce pracy i rejony przyległe.", r("p36", "ust. 2 pkt 4"), "poddać kontroli miejsce")]),
    karta("wlasciciel", "Obowiązki właściciela obiektu (art. 4 ustawy)", "ppoz",
          "Właściciel m.in. przestrzega wymagań ppoż, wyposaża obiekt w urządzenia i gaśnice, zapewnia ich przeglądy, zapewnia ewakuację, przygotowuje obiekt do akcji, zapoznaje pracowników z przepisami i ustala postępowanie na wypadek pożaru.",
          u("a4", "ust. 1"), "wyposażyć budynek, obiekt budowlany lub teren w wymagane urządzenia przeciwpożarowe i gaśnice",
          "Właściciel hurtowni: gaśnice z przeglądem, IBP, przeszkoleni pracownicy, droga pożarowa wolna.",
          "Właściciel wynajmuje halę i uważa, że „to sprawa najemcy”, choć umowa nic o tym nie mówi.",
          "Za bezpieczeństwo pożarowe odpowiada właściciel - chyba że umowa przekazuje to zarządcy lub najemcy.",
          ["ibp", "urzadzenia-ppoz", "inspektor"],
          [q("A jeśli budynek jest wynajęty?", "Odpowiedzialność przejmuje (w całości lub części) zarządca lub użytkownik na podstawie umowy; bez umowy - ten, kto faktycznie włada obiektem.",
             u("a4", "ust. 1a"), "faktycznie władającym budynkiem")]),
    karta("inspektor", "Inspektor ochrony przeciwpożarowej", "ppoz",
          "Uprawnienia nabywa się na 5 lat po szkoleniu inspektorów albo szkoleniu aktualizującym w szkołach i ośrodkach PSP.",
          u("a4a", "ust. 1"), "nabywa na okres 5 lat",
          "Inspektor przygotowuje IBP, sprawdza obiekt, szkoli pracowników z ppoż.",
          "Spóźnienie z aktualizacją - uprawnienia wygasają i trzeba robić pełny kurs od nowa.",
          "Osoba z uprawnieniami, która może wykonywać za właściciela czynności z zakresu ochrony przeciwpożarowej.",
          ["wlasciciel", "ibp"],
          [q("Kiedy zrobić szkolenie aktualizujące?", "W okresie ważności uprawnień.", u("a4a", "ust. 4"), "w okresie ważności nabytych uprawnień"),
           q("Jakie wykształcenie jest potrzebne?", "Co najmniej średnie lub średnie branżowe i uprawnienia inspektora (albo kwalifikacje technika pożarnictwa) - do czynności z art. 4 ust. 1.",
             u("a4", "ust. 2b"), "co najmniej wykształcenie średnie lub średnie branżowe")]),
    # ── BHP ──
    karta("ryzyko-zawodowe", "Ryzyko zawodowe", "bhp",
          "Prawdopodobieństwo niepożądanych zdarzeń związanych z pracą, powodujących straty - zwłaszcza niekorzystnych skutków zdrowotnych u pracowników.",
          d(OGOLNE, "para_2", "§ 2 ust. 1 pkt 7 ogólnych przepisów BHP"), "prawdopodobieństwo wystąpienia niepożądanych zdarzeń",
          "Magazynier: upadek z drabiny, potrącenie wózkiem, dźwiganie. Każde zagrożenie ma swoje ryzyko.",
          "Ocena ryzyka skopiowana z internetu, niepasująca do stanowiska, bez podpisów pracowników.",
          "Ocena ryzyka to lista: co tu może komuś zrobić krzywdę, jak bardzo i co z tym robimy.",
          ["wypadek", "szkolenie-bhp", "nds"],
          [q("Czy to obowiązek?", "Tak - pracodawca ocenia i dokumentuje ryzyko zawodowe i informuje o nim pracowników.",
             d(KP, "a226", "art. 226 KP"), "ocenia i dokumentuje ryzyko zawodowe"),
           q("Jaka kolejność środków?", "Najpierw usunąć zagrożenie, potem rozwiązania organizacyjne i techniczne, ochrona zbiorowa, a dopiero na końcu środki ochrony indywidualnej.",
             d(OGOLNE, "para_39", "§ 39 ogólnych przepisów BHP"), "środki ochrony indywidualnej")]),
    karta("wypadek", "Wypadek przy pracy", "bhp",
          "Nagłe zdarzenie wywołane przyczyną zewnętrzną, powodujące uraz lub śmierć, które nastąpiło w związku z pracą.",
          d(WYPADK, "a3", "art. 3 ust. 1 ustawy wypadkowej"), "nagłe zdarzenie wywołane przyczyną zewnętrzną",
          "Pracownik poślizgnął się na mokrej posadzce w magazynie i złamał rękę.",
          "Uznanie, że to nie wypadek, „bo sam był nieuważny” - nieuwaga nie wyklucza wypadku przy pracy.",
          "Cztery warunki: nagle, z zewnątrz, uraz, w związku z pracą. Jeśli są wszystkie - to wypadek przy pracy.",
          ["ryzyko-zawodowe", "zespol-powypadkowy"],
          [q("Ile czasu na protokół?", "Zespół powypadkowy sporządza protokół najpóźniej 14 dni od zawiadomienia o wypadku.",
             d(WYP, "p9", "§ 9 rozp. o wypadkach"), "nie później niż w terminie 14 dni"),
           q("Kogo zawiadomić przy ciężkim wypadku?", "Niezwłocznie okręgowego inspektora pracy i prokuratora (wypadek śmiertelny, ciężki, zbiorowy).",
             d(KP, "a234", "art. 234 § 2 KP"), "zawiadomić właściwego okręgowego inspektora pracy i prokuratora")]),
    karta("zespol-powypadkowy", "Zespół powypadkowy", "bhp",
          "Zespół powołany przez pracodawcę do ustalenia okoliczności i przyczyn wypadku: pracownik służby BHP i społeczny inspektor pracy.",
          d(WYP, "p4", "§ 4 rozp. o wypadkach"), "pracownik służby bezpieczeństwa i higieny pracy oraz społeczny inspektor pracy",
          "W firmie 30-osobowej bez społecznego inspektora: pracodawca powołuje BHP-owca z zewnątrz i przedstawiciela pracowników.",
          "Ustalanie przyczyn przez szefa „na szybko”, bez oględzin, zdjęć i rozmowy ze świadkami.",
          "Zespół ma ustalić, co się stało i dlaczego - rzetelnie, bo od protokołu zależą pieniądze poszkodowanego z ZUS.",
          ["wypadek", "sluzba-bhp"],
          [q("Co zespół robi najpierw?", "Niezwłocznie: oględziny miejsca, szkic lub zdjęcia, wyjaśnienia poszkodowanego, świadkowie, opinia lekarza, kwalifikacja prawna, wnioski.",
             d(WYP, "p7", "§ 7 rozp. o wypadkach"), "dokonać oględzin miejsca wypadku"),
           q("Ile ma pracodawca na zatwierdzenie protokołu?", "Najpóźniej 5 dni od sporządzenia.", d(WYP, "p13", "§ 13 rozp. o wypadkach"), "nie później niż w terminie 5 dni")]),
    karta("sluzba-bhp", "Służba BHP", "bhp",
          "Komórka lub osoba pełniąca funkcje doradcze i kontrolne w BHP. Pracodawca z ponad 100 pracownikami tworzy służbę BHP, do 100 - powierza zadania pracownikowi zatrudnionemu przy innej pracy.",
          d(KP, "a23711", "art. 237¹¹ § 1 KP"), "Pracodawca zatrudniający więcej niż 100 pracowników tworzy służbę",
          "Firma 40-osobowa (handel) - szef po szkoleniu może sam pełnić zadania służby BHP albo zlecić je specjaliście z zewnątrz.",
          "Przekonanie, że mała firma „nie musi mieć nic z BHP” - zadania służby trzeba komuś powierzyć.",
          "Ktoś w firmie musi pilnować BHP - albo pracownik, albo szef po szkoleniu, albo firma z zewnątrz.",
          ["szkolenie-bhp", "zespol-powypadkowy"],
          [q("Kiedy szef może sam pełnić zadania służby BHP?", "Po odpowiednim szkoleniu, jeśli zatrudnia do 10 pracowników albo do 50 przy kategorii ryzyka nie wyższej niż trzecia.",
             d(KP, "a23711", "art. 237¹¹ § 1 KP"), "zatrudnia do 10 pracowników"),
           q("Czy można zlecić to firmie z zewnątrz?", "Tak - w braku kompetentnych pracowników pracodawca może powierzyć zadania specjalistom spoza zakładu.",
             d(KP, "a23711", "art. 237¹¹ § 2 KP"), "specjalistom spoza zakładu pracy")]),
    karta("szkolenie-bhp", "Szkolenie BHP - wstępne i okresowe", "bhp",
          "Szkolenie BHP prowadzi się jako wstępne (instruktaż ogólny i stanowiskowy przed dopuszczeniem do pracy) i okresowe (aktualizacja wiedzy).",
          d(SZKOL, "para_6", "§ 6 rozp. o szkoleniach"), "szkolenie wstępne i szkolenie okresowe",
          "Nowy magazynier: instruktaż ogólny w pierwszym dniu, stanowiskowy u kierownika, potem okresowe co 3 lata.",
          "Pracownik zaczyna pracę „od jutra”, a instruktaż stanowiskowy „kiedyś się zrobi”.",
          "Zanim ktoś zacznie pracę, musi wiedzieć, jak jej nie przypłacić zdrowiem. Potem co kilka lata odświeżamy.",
          ["ryzyko-zawodowe", "sluzba-bhp"],
          [q("Co ile okresowe dla robotników?", "Nie rzadziej niż raz na 3 lata, a przy pracach szczególnie niebezpiecznych - raz w roku.",
             d(SZKOL, "para_15", "§ 15 ust. 1 rozp. o szkoleniach"), "nie rzadziej niż raz na 3 lata"),
           q("A dla biurowych?", "Nie rzadziej niż raz na 6 lat (o ile w ogóle są wymagane - przy niskiej kategorii ryzyka mogą być zwolnieni).",
             d(SZKOL, "para_15", "§ 15 ust. 2 rozp. o szkoleniach"), "raz na 6 lat"),
           q("Czy można dopuścić do pracy bez szkolenia?", "Nie - pracodawca zapewnia szkolenie BHP przed dopuszczeniem do pracy.",
             d(KP, "a2373", "art. 237³ § 2 KP"), "przed dopuszczeniem go do pracy")]),
    karta("nds", "NDS i NDSCh", "bhp",
          "NDS - najwyższe dopuszczalne stężenie: średnia ważona stężenia z 8-godzinnej zmiany, która przez całe życie zawodowe nie powinna zaszkodzić pracownikowi ani jego przyszłym pokoleniom. NDSCh - stężenie chwilowe (do 15 minut).",
          d(NDS, "para_2", "§ 2 rozp. NDS/NDN"), "wartość średnia ważona stężenia",
          "Lakiernia: pomiary par rozpuszczalników, stolarnia: pył drewna twardego.",
          "Brak pomiarów, bo „wentylacja jest”, albo pomiary z czasów, gdy była inna technologia.",
          "To granica, poniżej której wdychanie pyłów czy oparów przez lata pracy nie powinno szkodzić.",
          ["ryzyko-zawodowe"],
          [q("Czym różni się NDSCh?", "To średnia stężenia, które nie powinno zaszkodzić, jeśli występuje krótko w ciągu zmiany.",
             d(NDS, "para_2", "§ 2 rozp. NDS/NDN"), "najwyższe dopuszczalne stężenie chwilowe (NDSCh)")]),
]


def sprawdz(opis, zr, dowod):
    try:
        jest = dowod.replace(" ", "") in tekst_jednostki(zr).replace(" ", "").replace(" ", "")
    except StopIteration:
        jest = False
    if not jest:
        print("BRAK POKRYCIA:", opis[:60], zr, dowod)
    return jest


def main():
    ids = {k["id"] for k in POJECIA}
    bledy = 0
    for k in POJECIA:
        bledy += not sprawdz(k["nazwa"], k["zr"], k["dowod"])
        for p in k["dopytania"]:
            bledy += not sprawdz(p["q"], p["zr"], p["dowod"])
        for p in k["powiazane"]:
            if p not in ids:
                bledy += 1
                print("NIEZNANE POWIĄZANIE:", k["id"], "->", p)
    if bledy:
        sys.exit(f"{bledy} błędów - popraw przed zapisem")
    json.dump(POJECIA, open("app/data/pojecia.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("zapisano", len(POJECIA), "kart pojęć,", sum(len(k["dopytania"]) for k in POJECIA), "dopytań")


if __name__ == "__main__":
    main()
