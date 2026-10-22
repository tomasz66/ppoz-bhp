# PPOŻ BHP - stan projektu (22.10.2026)

**NA ŻYWO: https://tomasz66.github.io/ppoz-bhp/** - repo `tomasz66/ppoz-bhp` (publiczne, GitHub Pages przez Actions). Wiadomości odświeżają się same codziennie o 6:00 (cron w `.github/workflows/pages.yml`) i przy każdym wysłaniu zmian. Push tylko na prośbę Tomka.

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
- **Luz** (6. zakładka): mem dnia + losowanie, 12 autorskich memów (formaty klasyk / drake / "nikt:"), nietypowe interwencje strażaków z 30 dni (kanał "luz" w skrypcie, filtr SMUTNE - bez tragedii), żarty, ciekawostki.
- **Ciekawostki i żarty** (`data/ciekawostki.json`): 20 ciekawostek z linkiem do przepisu + 15 własnych żartów; ciekawostka dnia na Start, w lekcji co 3. dobrą odpowiedź na zmianę fakt/żart. Start ma też "Najbliższe terminy" i 3 wiadomości z branży.
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
- [ ] Więcej pytań (cel: 150+), m.in. z WT i ustawy (art. 5, 6, 7)
- [ ] Warsztat: wzory dokumentów (IBP, ORZ, protokół wypadku)
