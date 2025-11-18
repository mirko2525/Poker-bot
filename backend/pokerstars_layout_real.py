#!/usr/bin/env python3
"""
POKERSTARS LAYOUT - COORDINATE REALI
=====================================

ORDINE CAPO: Coordinate estratte da screenshot PokerStars reali.

Risoluzione: 2048×1279 (screenshot browser PokerStars)
Origine: top-left (0,0)

Formato: (x, y, w, h) in pixel
"""

import cv2
from typing import Dict, List, Tuple
from card_recognition_fullcard import FullCardRecognizer


class PokerStarsLayout2048x1279:
    """
    Layout REALE per PokerStars screenshot 2048×1279.
    
    ORDINE CAPO: Coordinate misurate da screenshot live.
    """
    
    def __init__(self):
        # Hero cards (2 carte in basso)
        # Ordine: sinistra → destra
        self.hero_cards = [
            (772, 838, 132, 188),   # hero[0] - carta sinistra
            (815, 850, 133, 189),   # hero[1] - carta destra
        ]
        
        # Board cards (5 carte al centro)
        # Ordine: sinistra → destra
        self.board_cards = [
            (715, 571, 115, 164),   # board[0] - 1a carta
            (841, 571, 115, 164),   # board[1] - 2a carta
            (966, 571, 116, 164),   # board[2] - 3a carta (centro)
            (1092, 571, 115, 164),  # board[3] - 4a carta
            (1218, 571, 115, 164),  # board[4] - 5a carta
        ]


def recognize_table_cards(
    screen_bgr,
    layout: PokerStarsLayout2048x1279,
    recognizer: FullCardRecognizer
) -> Dict:
    """
    ORDINE CAPO: Riconosce tutte le 7 carte da screenshot tavolo.
    
    Args:
        screen_bgr: Screenshot BGR del tavolo
        layout: Layout con coordinate
        recognizer: FullCardRecognizer inizializzato
        
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
    
    def crop_and_recognize(x, y, w, h):
        """Helper: crop + recognize"""
        crop = gray[y:y+h, x:x+w]
        return recognizer.recognize_card(crop)
    
    results = {
        "hero": [],
        "board": []
    }
    
    # Recognize hero cards
    for (x, y, w, h) in layout.hero_cards:
        code, score, conf = crop_and_recognize(x, y, w, h)
        results["hero"].append({
            "code": code,
            "score": score,
            "conf": conf,
            "bbox": (x, y, w, h),
        })
    
    # Recognize board cards
    for (x, y, w, h) in layout.board_cards:
        code, score, conf = crop_and_recognize(x, y, w, h)
        results["board"].append({
            "code": code,
            "score": score,
            "conf": conf,
            "bbox": (x, y, w, h),
        })
    
    return results


def visualize_recognition(
    screen_bgr,
    results: Dict,
    output_path: str = None
):
    """
    Visualizza risultati riconoscimento su screenshot.
    
    Args:
        screen_bgr: Screenshot originale
        results: Output di recognize_table_cards()
        output_path: Dove salvare (opzionale)
    """
    vis = screen_bgr.copy()
    
    # Hero cards (verde)
    for i, card in enumerate(results["hero"]):
        x, y, w, h = card["bbox"]
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
        
        cv2.rectangle(vis, (x, y), (x+w, y+h), color, 3)
        
        # Label
        label = f"H{i+1}: {code} ({score:.2f})"
        cv2.putText(vis, label, (x, y-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    # Board cards (cyan)
    for i, card in enumerate(results["board"]):
        x, y, w, h = card["bbox"]
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
        
        cv2.rectangle(vis, (x, y), (x+w, y+h), color, 3)
        
        # Label
        label = f"B{i+1}: {code} ({score:.2f})"
        cv2.putText(vis, label, (x, y-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    if output_path:
        cv2.imwrite(output_path, vis)
    
    return vis


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🎯 POKERSTARS LAYOUT - COORDINATE REALI")
    print("="*80 + "\n")
    
    layout = PokerStarsLayout2048x1279()
    
    print(f"Hero cards: {len(layout.hero_cards)}")
    for i, (x, y, w, h) in enumerate(layout.hero_cards):
        print(f"  H{i+1}: x={x:4d} y={y:4d} w={w:3d} h={h:3d}")
    
    print(f"\nBoard cards: {len(layout.board_cards)}")
    for i, (x, y, w, h) in enumerate(layout.board_cards):
        print(f"  B{i+1}: x={x:4d} y={y:4d} w={w:3d} h={h:3d}")
    
    print("\n" + "="*80)
    print("✅ Layout pronto per tavolo vero!")
    print("="*80 + "\n")
