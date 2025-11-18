#!/usr/bin/env python3
"""
POKERSTARS LAYOUT - COORDINATE REALI
=====================================

ORDINE CAPO: Coordinate estratte da screenshot PokerStars reali.

Risoluzione base: 2048×1279 (screenshot browser PokerStars)
Origine: top-left (0,0)

Formato: (x, y, w, h) in pixel

NOTA: Se lo screenshot reale ha una risoluzione diversa ma stesso aspect ratio,
le coordinate vengono scalate automaticamente rispetto alla risoluzione base.
"""

import cv2
from typing import Dict, List, Tuple
from card_recognition_fullcard import FullCardRecognizer
from card_recognition_ranksuit import (
    load_rank_templates,
    load_suit_templates,
    recognize_card_ranksuit,
)
from PIL import Image

# Risoluzione base per cui sono state misurate le coordinate
BASE_WIDTH = 2048
BASE_HEIGHT = 1279


class PokerStarsLayout2048x1279:
    """Layout REALE per PokerStars screenshot 2048×1279.

    ORDINE CAPO: Coordinate misurate da screenshot live.
    """

    def __init__(self) -> None:
        # Hero cards (2 carte in basso)
        # Ordine: sinistra → destra
        self.hero_cards = [
            (772, 838, 132, 188),   # hero[0] - carta sinistra (full card)
            (815, 850, 133, 189),   # hero[1] - carta destra (full card)
        ]

        # ROI angolino hero1 (rank+suit) misurato su screenshot 1920×1080.
        # Normalizzato in frazioni [0-1] rispetto a (width, height) immagine.
        # Dallo screen con rettangolo blu:
        #   top-left  (384, 709)
        #   bottom-right (475, 776)
        #   w=91, h=67 su 1920×1080 → frazioni:
        #   fx = 384/1920 = 0.20
        #   fy = 709/1080 ≈ 0.6565
        #   fw = 91/1920 ≈ 0.0474
        #   fh = 67/1080 ≈ 0.0620
        self.hero1_corner_frac = (0.20, 0.6565, 0.0474, 0.0620)

        # Board cards (5 carte al centro)
        # Ordine: sinistra → destra
        self.board_cards = [
            (715, 571, 115, 164),   # board[0] - 1a carta
            (841, 571, 115, 164),   # board[1] - 2a carta
            (966, 571, 116, 164),   # board[2] - 3a carta (centro)
            (1092, 571, 115, 164),  # board[3] - 4a carta
            (1218, 571, 115, 164),  # board[4] - 5a carta
        ]


def _scale_bbox(
    bbox: Tuple[int, int, int, int],
    scale_x: float,
    scale_y: float,
    max_w: int,
    max_h: int,
) -> Tuple[int, int, int, int]:
    """Scala una bbox dalla risoluzione base a quella reale dello screenshot.

    Mantiene la bbox entro i limiti dell'immagine.
    """
    x, y, w, h = bbox

    x = int(round(x * scale_x))
    y = int(round(y * scale_y))
    w = int(round(w * scale_x))
    h = int(round(h * scale_y))

    # Clamping sui limiti immagine
    x = max(0, min(x, max_w - 1))
    y = max(0, min(y, max_h - 1))
    w = max(1, min(w, max_w - x))
    h = max(1, min(h, max_h - y))

    return x, y, w, h


# Carichiamo i template rank+suit una sola volta a livello modulo
_RANK_TEMPLATES = load_rank_templates()
_SUIT_TEMPLATES = load_suit_templates()


def recognize_table_cards(
    screen_bgr,
    layout: PokerStarsLayout2048x1279,
    recognizer: FullCardRecognizer,
) -> Dict:
    """ORDINE CAPO: Riconosce tutte le 7 carte da screenshot tavolo.

    Args:
        screen_bgr: Screenshot BGR del tavolo (qualsiasi risoluzione)
        layout: Layout con coordinate misurate su 2048×1279
        recognizer: FullCardRecognizer inizializzato

    La funzione adatta automaticamente le coordinate se lo screenshot
    non è esattamente 2048×1279 ma mantiene lo stesso aspect ratio.

    Returns:
        {
            "hero": [
                {"code": "Kd", "score": 0.95, "conf": "strong", "bbox": (x,y,w,h)},
                ...
            ],
            "board": [
                {"code": "2h", "score": 0.92, "conf": "strong", "bbox": (x,y,w,h)},
                ...
            ]
        }
    """
    # Convert to grayscale
    gray = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape[:2]

    # Fattori di scala rispetto alla risoluzione base
    scale_x = w / BASE_WIDTH
    scale_y = h / BASE_HEIGHT

    def crop_and_recognize(x: int, y: int, w_box: int, h_box: int):
        """Helper: crop + recognize"""
        crop = gray[y:y + h_box, x:x + w_box]
        return recognizer.recognize_card(crop)

    results: Dict[str, List[Dict]] = {
        "hero": [],
        "board": [],
    }

    # Recognize hero cards
    if layout.hero_cards:
        # HERO1 (carta dietro): usiamo bbox full-card ma riconoscimento rank+suit
        x1, y1, w1, h1 = layout.hero_cards[0]
        sx1, sy1, sw1, sh1 = _scale_bbox((x1, y1, w1, h1), scale_x, scale_y, w, h)
        hero1_code = None
        hero1_score = 0.0
        hero1_conf = "none"

        hero1_bgr = screen_bgr[sy1:sy1 + sh1, sx1:sx1 + sw1]
        if hero1_bgr.size > 0 and _RANK_TEMPLATES and _SUIT_TEMPLATES:
            hero1_pil = Image.fromarray(cv2.cvtColor(hero1_bgr, cv2.COLOR_BGR2RGB))
            code, conf = recognize_card_ranksuit(hero1_pil, _RANK_TEMPLATES, _SUIT_TEMPLATES)
            if code is not None:
                hero1_code = code
                hero1_score = conf
                hero1_conf = "strong" if conf >= 0.75 else "weak"

        results["hero"].append(
            {
                "code": hero1_code,
                "score": hero1_score,
                "conf": hero1_conf,
                "bbox": (sx1, sy1, sw1, sh1),
            }
        )

        # HERO2 (carta davanti) con full-card recognizer
        if len(layout.hero_cards) > 1:
            x2, y2, w2, h2 = layout.hero_cards[1]
            sx2, sy2, sw2, sh2 = _scale_bbox((x2, y2, w2, h2), scale_x, scale_y, w, h)
            code2, score2, conf2 = crop_and_recognize(sx2, sy2, sw2, sh2)
        else:
            sx2 = sy2 = sw2 = sh2 = 0
            code2 = None
            score2 = 0.0
            conf2 = "none"

        results["hero"].append(
            {
                "code": code2,
                "score": score2,
                "conf": conf2,
                "bbox": (sx2, sy2, sw2, sh2),
            }
        )

    # Recognize board cards (blu nel debug overlay)
    for (x, y, w_box, h_box) in layout.board_cards:
        sx, sy, sw, sh = _scale_bbox((x, y, w_box, h_box), scale_x, scale_y, w, h)
        code, score, conf = crop_and_recognize(sx, sy, sw, sh)
        results["board"].append(
            {
                "code": code,
                "score": score,
                "conf": conf,
                "bbox": (sx, sy, sw, sh),
            }
        )

    return results


def visualize_recognition(
    screen_bgr,
    results: Dict,
    output_path: str | None = None,
):
    """Visualizza risultati riconoscimento su screenshot.

    Args:
        screen_bgr: Screenshot originale
        results: Output di recognize_table_cards()
        output_path: Dove salvare (opzionale)
    """
    vis = screen_bgr.copy()

    # Hero cards (verde)
    for i, card in enumerate(results["hero"]):
        x, y, w_box, h_box = card["bbox"]
        code = card["code"] or "???"
        conf = card["conf"]
        score = card["score"]

        # Colore box basato su confidenza
        if conf == "strong":
            color = (0, 255, 0)  # Verde
        elif conf == "weak":
            color = (0, 255, 255)  # Giallo
        else:
            color = (0, 0, 255)  # Rosso

        cv2.rectangle(vis, (x, y), (x + w_box, y + h_box), color, 3)

        # Label
        label = f"H{i+1}: {code} ({score:.2f})"
        cv2.putText(
            vis,
            label,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2,
        )

    # Board cards (cyan)
    for i, card in enumerate(results["board"]):
        x, y, w_box, h_box = card["bbox"]
        code = card["code"] or "???"
        conf = card["conf"]
        score = card["score"]

        # Colore box basato su confidenza
        if conf == "strong":
            color = (255, 255, 0)  # Cyan
        elif conf == "weak":
            color = (0, 255, 255)  # Giallo
        else:
            color = (0, 0, 255)  # Rosso

        cv2.rectangle(vis, (x, y), (x + w_box, y + h_box), color, 3)

        # Label
        label = f"B{i+1}: {code} ({score:.2f})"
        cv2.putText(
            vis,
            label,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2,
        )

    if output_path:
        cv2.imwrite(output_path, vis)

    return vis


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    import sys
    from pathlib import Path

    print("\n" + "=" * 80)
    print("🎯 POKERSTARS LAYOUT - COORDINATE REALI (SCALING TEST)")
    print("=" * 80 + "\n")

    layout = PokerStarsLayout2048x1279()

    print(f"Hero cards: {len(layout.hero_cards)}")
    for i, (x, y, w_box, h_box) in enumerate(layout.hero_cards):
        print(f"  H{i+1}: x={x:4d} y={y:4d} w={w_box:3d} h={h_box:3d}")

    print(f"\nBoard cards: {len(layout.board_cards)}")
    for i, (x, y, w_box, h_box) in enumerate(layout.board_cards):
        print(f"  B{i+1}: x={x:4d} y={y:4d} w={w_box:3d} h={h_box:3d}")

    # Test rapido opzionale con uno screenshot se passato da CLI
    if len(sys.argv) > 1:
        img_path = Path(sys.argv[1])
        print(f"\nLoading screenshot: {img_path}")
        img = cv2.imread(str(img_path))
        if img is None:
            print("❌ Cannot read image")
            sys.exit(1)

        rec = FullCardRecognizer()
        if not rec.templates:
            print("❌ No templates loaded")
            sys.exit(1)

        res = recognize_table_cards(img, layout, rec)
        print("\nHERO:")
        for c in res["hero"]:
            print(c)
        print("\nBOARD:")
        for c in res["board"]:
            print(c)

        out = visualize_recognition(img, res, "debug_pokerstars_layout.png")
        print("\n✅ Saved debug overlay: debug_pokerstars_layout.png")

    print("\n" + "=" * 80)
    print("✅ Layout pronto per tavolo vero (con scaling)!" )
    print("=" * 80 + "\n")
