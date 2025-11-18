#!/usr/bin/env python3
"""
TABLE LAYOUT - COORDINATE CARTE
================================

ORDINE CAPO: Definizione coordinate per estrarre le 7 carte (5 board + 2 hero).

Layout specifico per skin/risoluzione PokerStars.
Coordinate relative alla finestra del tavolo (non schermo intero).

Struttura:
- hero_cards: [(x1, y1, w, h), (x2, y2, w, h)]
- board_cards: [(x1, y1, w, h), ..., (x5, y5, w, h)]
"""

from typing import List, Tuple, Dict, Optional
import cv2
import numpy as np
from card_recognition_fullcard import FullCardRecognizer


class TableLayout:
    """
    Layout coordinate per un tavolo PokerStars.
    
    ORDINE CAPO: Una classe per ogni skin/risoluzione.
    """
    
    def __init__(
        self,
        hero_cards: List[Tuple[int, int, int, int]],
        board_cards: List[Tuple[int, int, int, int]],
        name: str = "default"
    ):
        """
        Args:
            hero_cards: Lista di 2 tuple (x, y, w, h) per hero cards
            board_cards: Lista di 5 tuple (x, y, w, h) per board cards
            name: Nome del layout
        """
        self.hero_cards = hero_cards
        self.board_cards = board_cards
        self.name = name
    
    @classmethod
    def pokerstars_1920x1080(cls):
        """
        Layout per PokerStars risoluzione 1920×1080, tavolo singolo centrato.
        
        TODO CAPO: Queste coordinate sono PLACEHOLDER.
        Servono coordinate reali dal tuo setup.
        """
        # Placeholder - da calibrare
        hero_cards = [
            (860, 850, 80, 110),   # Hero card 1
            (950, 850, 80, 110),   # Hero card 2
        ]
        
        board_cards = [
            (650, 450, 80, 110),   # Board 1
            (740, 450, 80, 110),   # Board 2
            (830, 450, 80, 110),   # Board 3 (centro)
            (920, 450, 80, 110),   # Board 4
            (1010, 450, 80, 110),  # Board 5
        ]
        
        return cls(hero_cards, board_cards, "pokerstars_1920x1080")


def recognize_table_cards(
    screen_gray: np.ndarray,
    layout: TableLayout,
    recognizer: FullCardRecognizer
) -> Dict:
    """
    ORDINE CAPO: Riconosce tutte le 7 carte da uno screenshot tavolo.
    
    Args:
        screen_gray: Screenshot del tavolo in grayscale
        layout: TableLayout con coordinate
        recognizer: FullCardRecognizer inizializzato
        
    Returns:
        Dict con struttura:
        {
            "hero": [
                {"code": "Ah", "score": 0.95, "conf": "strong"},
                {"code": "Kd", "score": 0.88, "conf": "strong"}
            ],
            "board": [
                {"code": "7c", "score": 0.92, "conf": "strong"},
                {"code": None, "score": 0.0, "conf": "none"},  # slot vuoto
                ...
            ]
        }
    """
    results = {
        "hero": [],
        "board": []
    }
    
    # Riconosci hero cards
    for (x, y, w, h) in layout.hero_cards:
        crop = screen_gray[y:y+h, x:x+w]
        code, score, conf = recognizer.recognize_card(crop)
        results["hero"].append({
            "code": code,
            "score": score,
            "conf": conf,
        })
    
    # Riconosci board cards
    for (x, y, w, h) in layout.board_cards:
        crop = screen_gray[y:y+h, x:x+w]
        code, score, conf = recognizer.recognize_card(crop)
        results["board"].append({
            "code": code,
            "score": score,
            "conf": conf,
        })
    
    return results


def visualize_layout(
    screen: np.ndarray,
    layout: TableLayout,
    output_path: Optional[str] = None
) -> np.ndarray:
    """
    Visualizza le bounding box del layout su uno screenshot.
    Utile per debug/calibrazione.
    
    Args:
        screen: Screenshot (color o gray)
        layout: TableLayout da visualizzare
        output_path: Path dove salvare (opzionale)
        
    Returns:
        Immagine con overlay delle box
    """
    # Converti in color se necessario
    if len(screen.shape) == 2:
        vis = cv2.cvtColor(screen, cv2.COLOR_GRAY2BGR)
    else:
        vis = screen.copy()
    
    # Disegna hero cards (verde)
    for i, (x, y, w, h) in enumerate(layout.hero_cards):
        cv2.rectangle(vis, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(vis, f"H{i+1}", (x+5, y+20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    # Disegna board cards (giallo)
    for i, (x, y, w, h) in enumerate(layout.board_cards):
        cv2.rectangle(vis, (x, y), (x+w, y+h), (0, 255, 255), 2)
        cv2.putText(vis, f"B{i+1}", (x+5, y+20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    if output_path:
        cv2.imwrite(output_path, vis)
    
    return vis


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🎯 TABLE LAYOUT SYSTEM")
    print("="*80 + "\n")
    
    # Test layout
    layout = TableLayout.pokerstars_1920x1080()
    
    print(f"Layout: {layout.name}")
    print(f"Hero cards: {len(layout.hero_cards)}")
    print(f"Board cards: {len(layout.board_cards)}")
    
    print("\n⚠️ NOTA CAPO:")
    print("Queste coordinate sono PLACEHOLDER!")
    print("Servono coordinate reali dal tuo setup PokerStars.")
    print("\n" + "="*80 + "\n")
