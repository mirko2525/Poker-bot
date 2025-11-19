import os
import re
import glob
from pathlib import Path

import cv2

ROOT_DIR = Path(__file__).parent

# cartella dove hai scompattato lo zip
INPUT_DIR = ROOT_DIR / "card_templates_raw" / "hero1"
# cartella dove salviamo i template pronti
OUTPUT_DIR = ROOT_DIR / "card_templates" / "pokerstars" / "hero_back"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SUITS_MAP_IT_SHORT = {
    "cuori": "h",
    "fiori": "c",
    "picche": "s",
    "quadri": "d",
    "cuadri": "d",  # typo difensivo
}

# dimensione target per la carta dietro (porzione visibile)
HERO_BACK_SIZE = (70, 140)  # (width, height)


def main() -> None:
    png_paths = glob.glob(str(INPUT_DIR / "*.png"))
    if not png_paths:
        print(f"Nessun PNG trovato in {INPUT_DIR}")
        return

    for path in png_paths:
        fname = os.path.basename(path)
        stem, _ = os.path.splitext(fname)  # es: "Kquadri", "Jfiori"

        m = re.match(r"([2-9TJQKA])(.+)", stem, re.IGNORECASE)
        if not m:
            print("Nome NON riconosciuto, salto:", fname)
            continue

        rank, suit_it = m.groups()
        rank = rank.upper()
        suit_it = suit_it.lower()

        if suit_it == "cuadri":
            suit_it = "quadri"

        if suit_it not in SUITS_MAP_IT_SHORT:
            print("Seme sconosciuto, salto:", fname)
            continue

        suit_short = SUITS_MAP_IT_SHORT[suit_it]  # h/c/s/d
        code = f"{rank}{suit_short}"              # es: "Kh", "Td"

        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            print("Errore nel leggere:", path)
            continue

        tmpl = cv2.resize(img, HERO_BACK_SIZE, interpolation=cv2.INTER_AREA)
        tmpl = cv2.GaussianBlur(tmpl, (3, 3), 0)

        out_path = OUTPUT_DIR / f"{code}.png"
        cv2.imwrite(str(out_path), tmpl)
        print("Salvato hero_back template:", out_path)

    print("\n✅ Template hero_back pronti in:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
