# Starsze PDF-y Dz.U. (do ok. 2011) mają dwie kolumny i własne kodowanie polskich liter (à=ą, ˝=ż...).
# Skrypt czyta bloki kolumnami, naprawia litery i łączy wyrazy przeniesione z myślnikiem.
# Użycie: python3 stary_pdf_na_tekst.py wejscie.pdf wyjscie.txt
import re
import sys

import fitz

LITERY = str.maketrans({"˝": "ż", "à": "ą", "Ê": "ś", "´": "ę", "∏": "ł", "ç": "ć", "ƒ": "ń", "ê": "ź",
                        "Ñ": "Ą", "¢": "Ę", "¯": "Ż", "Œ": "Ś", "£": "Ł", "Æ": "Ć", "Ò": "Ń", "è": "Ź"})
NAGLOWEK = re.compile(r"^(Dziennik Ustaw Nr \d+|— \d+ —|Poz\. \d+)\s*$")


def main(wej, wyj):
    doc = fitz.open(wej)
    linie = []
    for strona in doc:
        srodek = strona.rect.width / 2
        bloki = [b for b in strona.get_text("blocks") if b[6] == 0]
        # Bloki pełnej szerokości (tytuł) zostają na swoim miejscu; reszta: lewa kolumna, potem prawa.
        bloki.sort(key=lambda b: (0 if b[2] - b[0] > srodek * 1.3 else (1 if b[0] < srodek else 2), b[1]))
        for b in bloki:
            # Pomiń przypisy (blok zaczyna się kreską), podpis elektroniczny i stopkę RCL.
            if b[4].lstrip().startswith("———") or "Elektronicznie" in b[4] or "www.rcl.gov.pl" in b[4]:
                continue
            for l in b[4].split("\n"):
                if not NAGLOWEK.match(l.strip()):
                    linie.append(l.translate(LITERY))
            linie.append("")
    tekst = "\n".join(linie)
    tekst = re.sub(r"(\w)-\n(\w)", r"\1\2", tekst).replace("—", "–")
    open(wyj, "w", encoding="utf-8").write(tekst)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
