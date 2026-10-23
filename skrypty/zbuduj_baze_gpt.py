# Eksportuje teksty z aplikacji do plików Markdown dla projektu w ChatGPT (albo Claude) - "baza",
# z której asystent głosowy odpowiada w ramach abonamentu, bez klucza API.
# Wynik: baza-chatgpt/ (poza repo). Użycie: python3 skrypty/zbuduj_baze_gpt.py   (z folderu bhp-ppoz)
import json
import os
import shutil

DANE = "app/data"
WYJSCIE = "baza-chatgpt"
# Tekst ze skanu z błędami - nie dajemy go jako podstawy.
POMIN = {"DU/1997/704"}
# Najważniejsze akty zmieniające z lat 2025-2026 (mobbing, upały, e-szkolenia, e-orzeczenia, ołów, punkty schronienia, WT).
# Czytelne nazwy plików zamiast numerów Dziennika Ustaw.
NAZWY_PLIKOW = {"DU/1974/141": "kodeks-pracy", "DU/1996/332": "badania-lekarskie", "DU/1997/844": "ogolne-przepisy-bhp",
                "DU/1998/973": "monitory-ekranowe", "DU/2002/1673": "ustawa-wypadkowa", "DU/2002/690": "warunki-techniczne-WT",
                "DU/2004/1860": "szkolenia-bhp", "DU/2009/870": "wypadki-przy-pracy", "DU/2018/1286": "NDS-NDN"}
ZMIANY = ["DU/2026/1046", "DU/2026/927", "DU/2025/1640", "DU/2026/456", "DU/2026/726", "DU/2026/1276", "DU/2026/1161"]

INSTRUKCJA = """Jesteś moim asystentem do nauki przepisów ochrony przeciwpożarowej i BHP. Uczę się do egzaminu na inspektora ochrony przeciwpożarowej i chcę umieć tłumaczyć przepisy klientom (małe firmy).

Zasady:
1. Odpowiadaj WYŁĄCZNIE na podstawie plików w tym projekcie. Zawsze podaj podstawę: paragraf lub artykuł i nazwę aktu (np. „§ 33 ust. 2 rozporządzenia o ochronie ppoż budynków”).
2. Liczby, odległości i terminy podawaj dokładnie jak w przepisie.
3. Jeśli w plikach nie ma odpowiedzi, powiedz wprost: „Nie mam tego w bazie” - nie zgaduj.
4. Mów prosto, jak doświadczony kolega: najpierw krótka odpowiedź, potem 1-2 zdania wyjaśnienia i przykład z życia (sklep, przedszkole, warsztat).
5. W rozmowie głosowej odpowiadaj krótko (do 30 sekund mówienia). Jeśli przerwę i dopytam, odpowiedz na dopytanie.
6. Gdy powiem „przepytaj mnie” (opcjonalnie: „jak egzaminator” albo „jak klient”), zadaj JEDNO pytanie z plików, poczekaj na moją odpowiedź, oceń ją (dobrze / częściowo / źle), podaj poprawną odpowiedź z paragrafem i zadaj następne.
7. Pliki 20-25 to moje materiały do nauki (karty pojęć, liczby, lista kontrolna, przypadki, pytania) - są zgodne z przepisami z plików 01-14.

Warunki techniczne (WT 2002) zostały uznane za uchylone i są stosowane w okresie przejściowym (art. 102a-102c Prawa budowlanego) - wspominaj o tym, gdy się na nie powołujesz.
"""


def linie_jednostki(j):
    return "\n".join(l["t"] for l in j["linie"])


def zapisz(nazwa, naglowek, cialo):
    with open(os.path.join(WYJSCIE, nazwa), "w", encoding="utf-8") as f:
        f.write(naglowek + "\n\n" + cialo.strip() + "\n")


def akt_md(tytul, zrodlo, jednostki):
    cialo = "\n\n".join(f"## {j['etykieta']}\n{linie_jednostki(j)}" for j in jednostki)
    return f"# {tytul}\n\nŹródło: {zrodlo}", cialo


def main():
    if os.path.isdir(WYJSCIE):
        shutil.rmtree(WYJSCIE)
    os.makedirs(WYJSCIE)
    with open(os.path.join(WYJSCIE, "00-INSTRUKCJA-wklej-do-projektu.txt"), "w", encoding="utf-8") as f:
        f.write(INSTRUKCJA)

    # 01-03: akty ppoż (z naniesionymi zmianami, jak w zakładce Przepisy)
    akty = json.load(open(f"{DANE}/akty.json", encoding="utf-8"))["akty"]
    for nr, a in enumerate(akty, 1):
        nag, cialo = akt_md(a["nazwa"], f"{a['tekst']['opis']} - {a['tekst']['isap']}", a["jednostki"])
        zapisz(f"{nr:02d}-{a['id']}.md", nag, cialo)

    # 04-13: akty BHP i WT, 14: najważniejsze zmiany
    spis = json.load(open(f"{DANE}/dok/spis.json", encoding="utf-8"))
    obserwowane = {o["eli"]: o["nazwa"] for o in json.load(open(f"{DANE}/obserwowane.json", encoding="utf-8"))["akty"]}
    nr = len(akty) + 1
    zmiany = []
    for eli in spis:
        d = json.load(open(f"{DANE}/dok/{eli.replace('/', '_')}.json", encoding="utf-8"))
        if eli in POMIN:
            continue
        if d["rola"] == "akt":
            nazwa = obserwowane.get(eli, d["tytul"])
            nag, cialo = akt_md(nazwa, f"{d['tytul']} - {d['tekst']} - {d['isap']}", d["jednostki"])
            zapisz(f"{nr:02d}-{NAZWY_PLIKOW.get(eli, eli.replace('/', '_'))}.md", nag, cialo)
            nr += 1
        elif eli in ZMIANY:
            zmiany.append(f"# {d['tytul']}\n\nŹródło: {d['isap']}\n\n" + "\n\n".join(f"## {j['etykieta']}\n{linie_jednostki(j)}" for j in d["jednostki"]))
    zapisz(f"{nr:02d}-zmiany-2025-2026.md", "# Najważniejsze zmiany w przepisach 2025-2026 (akty zmieniające)", "\n\n---\n\n".join(zmiany))

    # 20-25: materiały do nauki z aplikacji
    pojecia = json.load(open(f"{DANE}/pojecia.json", encoding="utf-8"))
    zapisz("20-karty-pojec.md", "# Karty pojęć ppoż i BHP", "\n\n".join(
        f"## {k['nazwa']}\nDefinicja: {k['def']} (podstawa: {k['zr'].get('u', '')})\nPrzykład: {k['przyklad']}\nTypowy błąd: {k['blad']}\nJak powiedzieć klientowi: {k['klient']}\n"
        + "\n".join(f"- Pytanie: {p['q']} Odpowiedź: {p['a']} (podstawa: {p['zr'].get('u', '')})" for p in k["dopytania"]) for k in pojecia))
    liczby = json.load(open(f"{DANE}/liczby.json", encoding="utf-8"))
    zapisz("21-liczby-i-terminy.md", "# Liczby i terminy z przepisów", "\n".join(f"- {x['w']}: {x['co']} (podstawa: {x['zr'].get('u', '')} {x['zr'].get('j', '')})" for x in liczby))
    warsztat = json.load(open(f"{DANE}/warsztat.json", encoding="utf-8"))
    zapisz("22-lista-kontrolna-obchodu.md", "# Lista kontrolna obchodu obiektu (ppoż i BHP)", "\n\n".join(
        f"## {s['tytul']}\n" + "\n".join(f"- {p['co']} Zalecenie: {p['zal']} (podstawa: {p['zr'].get('u', '')})" for p in s["punkty"]) for s in warsztat["obchod"]))
    cw = json.load(open(f"{DANE}/ciekawostki.json", encoding="utf-8"))
    zapisz("23-przypadki-z-zycia.md", "# Przypadki z życia (sytuacja -> co mówi prawo)", "\n".join(
        f"- {('Sytuacja: ' + c['s'] + ' ') if c.get('s') else ''}Prawo: {c['t']}" for c in cw["przypadki"] + cw["ciekawostki"]))
    sciagi = json.load(open(f"{DANE}/sciagi.json", encoding="utf-8"))
    zapisz("24-sciagi.md", "# Ściągi", "\n\n".join(f"## {s['tytul']}\n" + "\n".join(f"- {w[0]}: {w[1]}" for w in s["wiersze"]) for s in sciagi))
    pytania = json.load(open(f"{DANE}/pytania.json", encoding="utf-8"))
    zapisz("25-pytania-testowe.md", "# Pytania testowe (do przepytywania)", "\n".join(
        f"- {q['q']} Odpowiedzi: {' / '.join(q['odp'])}. Poprawna: {q['odp'][q['ok']]}" for q in pytania))

    for f in sorted(os.listdir(WYJSCIE)):
        print(f"{os.path.getsize(os.path.join(WYJSCIE, f)) // 1024:5d} KB  {f}")


if __name__ == "__main__":
    main()
