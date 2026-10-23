# PPOŻ BHP - stan projektu (22.10.2026)

**NA ŻYWO: https://tomasz66.github.io/ppoz-bhp/** - repo `tomasz66/ppoz-bhp` (publiczne, GitHub Pages przez Actions). Wiadomości odświeżają się same codziennie o 6:00 (cron w `.github/workflows/pages.yml`) i przy każdym wysłaniu zmian. Push tylko na prośbę Tomka.

**Baza wiedzy (kierunek, kurs, ceny, źródła do nauki, raporty, dziennik decyzji): `BAZA WIEDZY.md`** - tylko lokalnie, poza repo.

Aplikacja Tomka: kompendium przepisów BHP i ppoż + nauka do egzaminu inspektora ochrony przeciwpożarowej. Styl jak Pomocnik Strażaka (jasny, karty z kolorowymi kafelkami, ciemny motyw ☾).

Zasada nadrzędna: **każdy przepis, ściąga i pytanie ma klikalne źródło** (ISAP / API Sejmu). W tekstach przepisów tylko treść z Dz.U. - nic dopisanego od siebie.

## Co jest w środku (`app/`)

- **Przepisy** - pełny tekst 3 aktów ppoż, podzielony na artykuły/paragrafy, z wyszukiwarką:
  - ustawa o ochronie ppoż (tekst jednolity Dz.U. 2025 poz. 188 + zmiana art. 14fa z Dz.U. 2026 poz. 815),
  - rozp. MSWiA 7.06.2010 o ochronie ppoż budynków (TJ Dz.U. 2023 poz. 822 + zmiany Dz.U. 2024 poz. 1716 i 2026 poz. 1276 naniesione dosłownie, z żółtym paskiem),
  - rozp. MSWiA 24.07.2009 woda i drogi pożarowe (bez zmian).
  - Załączniki (rysunki, tabele) tylko w PDF - link przy akcie.
  - BHP: 9 aktów jako linki do ISAP (tekst w aplikacji - etap 2).
- **Ściągi** - 9 kart (gaśnice, przeglądy, IBP, ewakuacja, czujki, kominy, drogi pożarowe, uprawnienia inspektora, obowiązki właściciela), każda pozycja z paragrafem.
- **Nauka** - 50 pytań (własne, z treści przepisów, nie oficjalna pula), lekcja 10 pytań z powtórkami 1/2/4/7/14/30/60/120 dni, egzamin próbny (do 60 pytań, próg 70%). Postęp w localStorage telefonu.
- **Nowości** (22.10 wieczór, zamiast "Zmiany"): filtr Wszystko/BHP/PPOŻ; 8 najważniejszych zmian po ludzku z odliczaniem terminów i "Szansa dla Ciebie" (`data/nowosci.json` - pisane ręcznie z przeczytanych aktów: mobbing 5.11.2026, upały 11.01.2027, PIP decyzje, e-potwierdzenia szkoleń, czujki, punkty schronienia, WT, ołów); aktualności z branży (`data/aktualnosci.json`, skrypt `skrypty/zbuduj_aktualnosci.py`: strazacki.pl, ppoz.pl, Google News - przeglądarka nie może czytać RSS sama, CORS; po wystawieniu odświeżać automatycznie GitHub Actions raz dziennie).
- **Czytnik wiadomości** (`#/czytnik`, z Start "Więcej wiadomości" i z Nowości): ~250 artykułów z 14 dni, grupy Dziś/Wczoraj/Przedwczoraj/Wcześniej w tym tygodniu/Starsze, "⭐ Najważniejsze z tygodnia" (punkty z tematów i źródła), "Moje tematy" (filtr zapamiętany w telefonie), kropka = nowe od ostatniej wizyty, zajawka rozwijana dotknięciem, "Pokaż więcej" po 15. Skrypt rozkodowuje linki Google News do adresu wydawcy i pobiera og:description (pamięć w `zrodla/pamiec_aktualnosci.json`).
- **Czytnik w aplikacji (22.10 wieczór, prośba Tomka: "nie wychodzić do stron")**: każda wiadomość otwiera się w `#/news/<id>` - ⚡ W skrócie (4 zdania wybrane automatycznie z artykułu, `skrypty/tekst_artykulu.py`), treść, źródło na dole. Pełny tekst tylko z materiałów urzędowych (gov.pl, PIP - art. 4 pr. aut.); z mediów tylko streszczenie + "Otwórz u źródła" (prawo autorskie). Treść w `data/artykuly.json` (ładowana przy otwarciu).
- **Akty prawne w aplikacji** `#/dok/DU_RRRR_POZ`: 9 aktów BHP + WT (tekst jednolity z API Sejmu) + 19 aktów zmieniających (`skrypty/zbuduj_teksty.py` -> `data/dok/*.json`, spis w `data/dok/spis.json`). Każdy link ISAP w aplikacji, dla którego mamy tekst, otwiera czytnik; ISAP/PDF jako źródło na dole. Duże akty: lista z wyszukiwarką, małe: cały tekst. Karta "zmiany ogłoszone po tekście jednolitym".
- **Czy wiesz** (6. zakładka, zamiast Luzu - memy i żarty USUNIĘTE 22.10 na prośbę Tomka: "daremne"): 55 przypadków z życia (sytuacja → co mówi prawo → źródło) + 20 ciekawostek, filtr BHP/PPOŻ. Budowane skryptem `skrypty/zbuduj_przypadki.py` - każdy przypadek ma `dowod` (dosłowny fragment przepisu), skrypt przerywa, jeśli go nie ma w tekście. Tomek chce tego WIĘCEJ (przyda się przy obsłudze małych firm).
- **Odświeżanie ↻** (22.10, prośba Tomka): przycisk w nagłówku na każdym ekranie + karta "Aktualność przepisów" na Start. Sprawdza API Sejmu (nowe zmiany w 13 aktach), pobiera świeże dane (`?t=` + no-store), czyści pamięć czytników, aktualizuje service worker, pokazuje komunikat.
- **Warsztat** (22.10 noc, prośba Tomka): `#/warsztat`, wejście ze Start. **Obchód obiektu** - 44 punkty w 7 działach (dokumenty, gaśnice, hydranty/prąd, ewakuacja, porządek, teren, BHP), każdy OK / Uwaga / Nie dotyczy + notatka → raport z zaleceniami, paragrafem i linkiem ISAP (Kopiuj / Udostępnij / Drukuj-PDF). **Wzory**: IBP (9 kroków z § 6), wypadek przy pracy (notatki zespołu powypadkowego, terminy), ocena ryzyka (zagrożenia + macierz PN-N-18002). Zapis tylko w telefonie (localStorage `bhp-obchody`, `bhp-dokumenty`). Dane: `skrypty/zbuduj_warsztat.py` -> `data/warsztat.json` (sprawdza cytat `dowod` w przepisie), kod `app/warsztat.js`.
- **Asystent AI** (23.10, `#/asystent`, wejście ze Start): tryb „Ja pytam” (pytanie → objaśnienie z paragrafów, przypisy [n] klikalne) i „Przepytaj mnie” (egzamin / pyta klient, ocena odpowiedzi). Lektor = mowa iPhone'a (speechSynthesis, zdanie po zdaniu), mikrofon = webkitSpeechRecognition (gdy brak - dyktowanie z klawiatury), przycisk „✋ Przerwij i zapytaj”. Claude przez SDK z jsDelivr (`@anthropic-ai/sdk@0.133.0`, `dangerouslyAllowBrowser`), klucz API wklejany w aplikacji, tylko w localStorage telefonu (`bhp-ai-klucz`). Model do wyboru: Opus 5.5 (domyślny, z `fallbacks: "default"`) albo Haiku 5.5 (oszczędny); effort low. Wyszukiwanie fragmentów: BM25 po jednostkach, premia ×1,5 dla 3 aktów ppoż, przypadki/ściągi + ich pełny paragraf; „Służba BHP” (1997/704, tekst ze skanu z błędami) wyłączona z kontekstu AI. Historii nie przycinamy (preserved thinking) - po 6 turach nowa rozmowa. Kod `app/asystent.js`.
- **Wyszukiwarka "wszystko naraz"** na Start (`#/szukaj`): przypadki, ściągi, przepisy ppoż, akty BHP (doczytywane w tle), nowości, akty zmieniające, pytania, wiadomości. Bez polskich znaków i odmiany (rdzeń = słowo minus 3 litery, min. 4) + mapa synonimów `SYNONIMY` w app.js (płot→granica działki, czad→tlenek węgla...). Gdy coś nie znajduje - dopisać synonim.
- Ciekawostka/przypadek dnia na Start, w lekcji co 3. dobrą odpowiedź (bez żartów). Start ma też "Najbliższe terminy" i 3 wiadomości z branży.
- Wykrywanie nowych zmian - aplikacja sama pyta API Sejmu o 13 aktów (ppoż + BHP) i pokazuje nowe akty zmieniające (alert na Start + cyfra na zakładce). Lista bazowa z 22.10.2026. Karta o WT 2002 (uchylone, okres przejściowy art. 102a-102c Prawa budowlanego, Dz.U. 2026 poz. 1161).

## Jak przebudować dane

Z folderu `bhp-ppoz/`:
1. `python3 skrypty/parsuj_html.py zrodla/2023_822.html zrodla/r2010.json` (HTML z API Sejmu, pomija przypisy)
2. `python3 skrypty/parsuj_pdf.py zrodla/u.txt zrodla/ustawa.json "<znacznik startu>" art` (PDF po `pdftotext`)
3. `python3 skrypty/stary_pdf_na_tekst.py zrodla/2009_1030.pdf zrodla/w2.txt` + `parsuj_pdf.py ... par` (stare PDF-y z dwiema kolumnami i dziwnym kodowaniem)
4. `python3 skrypty/zbuduj_dane.py` -> `app/data/akty.json` (tu nanoszone są zmiany po tekście jednolitym)
5. `python3 skrypty/zbuduj_obserwowane.py` -> `app/data/obserwowane.json` (lista bazowa do wykrywania zmian)

Po nowej zmianie w prawie: pobrać akt zmieniający, dopisać w `zbuduj_dane.py` (jak ZM_2024), przebudować, odświeżyć obserwowane.

## Podgląd lokalny

`cd bhp-ppoz/app && python3 -m http.server 8791` -> http://localhost:8791 (port 8765 zajmuje Pomocnik Strażaka).

## Do zrobienia / decyzje Tomka

- [x] Nazwa: "PPOŻ BHP" (Tomek 22.10.2026)
- [x] Wystawione na GitHub Pages 22.10.2026
- [x] Pełny tekst aktów BHP w czytniku (22.10) - [ ] do zrobienia: ściągi i pytania z BHP, wyszukiwarka główna obejmująca akty BHP
- [ ] WT - dział VI (bezpieczeństwo pożarowe) gdy wyjaśni się sytuacja z nowymi WT
- [ ] Tekst „Służba BHP” (DU/1997/704) jest ze skanu z błędami - poprawić źródło (PDF/ręcznie)
- [ ] Plan nauki 23.10: 2) karty pojęć z pojęciami powiązanymi i dopytaniami, 3) mapa liczb (rysunek), 4) „Znajdź błąd” ze zdjęć
- [ ] Więcej pytań (cel: 150+), m.in. z WT i ustawy (art. 5, 6, 7)
- [x] Warsztat: obchód obiektu + wzory IBP, wypadek, ORZ (22.10.2026)
