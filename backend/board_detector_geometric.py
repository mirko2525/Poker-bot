#!/usr/bin/env python3
"""
BOARD CARD DETECTOR - GEOMETRIC APPROACH
=========================================

Usa misure geometriche precise invece di template matching.
Basato su analisi screenshot PokerStars 2048×1279:

- 3ª carta = CENTRO ORIZZONTALE dello schermo (reference point)
- Distanza centro-centro: 6.128% della larghezza
- Larghezza carta: 5.645% della larghezza
- Altezza carta: 12.823% dell'altezza
- Centro verticale board: 51.056% dell'altezza

SLOTS:
  0     1     2     3     4
  |-----|-----|-----|-----|
         flop  REF  flop
              turn turn turn
  river river river river river

Fase FLOP:    carte 1, 2, 3
Fase TURN:    carte 1, 2, 3, 4
Fase RIVER:   carte 0, 1, 2, 3, 4
"""

from PIL import Image
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# GEOMETRIC CONSTANTS (da misure reali screenshot 2048×1279)
# ============================================================================

CARD_WIDTH_RATIO = 0.05645        # 5.645% della larghezza schermo
CARD_HEIGHT_RATIO = 0.12823       # 12.823% dell'altezza schermo
CENTER_SPACING_RATIO = 0.06128    # Distanza centro-centro tra carte
BOARD_CENTER_Y_RATIO = 0.51056    # Posizione verticale del centro board

# Slots attivi per fase
SLOTS_BY_PHASE = {
    "PREFLOP": [],
    "FLOP": [1, 2, 3],
    "TURN": [1, 2, 3, 4],
    "RIVER": [0, 1, 2, 3, 4],
}

# ============================================================================
# GEOMETRIC BOARD DETECTION
# ============================================================================

def calculate_board_slot_bbox(
    slot_index: int,
    screen_width: int,
    screen_height: int
) -> Tuple[int, int, int, int]:
    """
    Calcola bounding box di uno slot board usando geometria.
    
    Args:
        slot_index: 0-4, dove 2 = 3ª carta (centro schermo)
        screen_width: Larghezza screenshot
        screen_height: Altezza screenshot
        
    Returns:
        (x1, y1, x2, y2) - bounding box della carta
    """
    # Dimensioni carta in pixel
    card_width = int(screen_width * CARD_WIDTH_RATIO)
    card_height = int(screen_height * CARD_HEIGHT_RATIO)
    
    # Centro schermo = 3ª carta (slot_index=2)
    center_x_screen = screen_width // 2
    center_y_board = int(screen_height * BOARD_CENTER_Y_RATIO)
    
    # Distanza tra centri carte
    center_spacing = int(screen_width * CENTER_SPACING_RATIO)
    
    # Offset relativo alla 3ª carta (slot 2 = reference)
    offset = slot_index - 2  # -2, -1, 0, +1, +2
    
    # Centro di questa carta
    center_x = center_x_screen + (offset * center_spacing)
    center_y = center_y_board
    
    # Bounding box
    x1 = int(center_x - card_width / 2)
    y1 = int(center_y - card_height / 2)
    x2 = x1 + card_width
    y2 = y1 + card_height
    
    return (x1, y1, x2, y2)


def detect_board_cards_geometric(
    screenshot: Image.Image,
    phase: str = "RIVER"
) -> List[Image.Image]:
    """
    Estrae carte board usando detection geometrica.
    
    Args:
        screenshot: Screenshot completo
        phase: "PREFLOP" | "FLOP" | "TURN" | "RIVER"
        
    Returns:
        Lista di immagini carte estratte
    """
    width, height = screenshot.size
    
    # Determina quali slot estrarre
    active_slots = SLOTS_BY_PHASE.get(phase.upper(), [])
    
    if not active_slots:
        logger.debug(f"Phase {phase}: no cards on board")
        return []
    
    logger.info(f"\n{'='*80}")
    logger.info(f"🎴 GEOMETRIC BOARD DETECTION")
    logger.info(f"{'='*80}")
    logger.info(f"Screenshot: {width}x{height}px")
    logger.info(f"Phase: {phase.upper()}")
    logger.info(f"Active slots: {active_slots}")
    
    # Estrai carte
    cards = []
    for slot_idx in active_slots:
        x1, y1, x2, y2 = calculate_board_slot_bbox(slot_idx, width, height)
        
        logger.info(f"\nSlot {slot_idx}:")
        logger.info(f"  Position: ({x1}, {y1}) → ({x2}, {y2})")
        logger.info(f"  Size: {x2-x1}x{y2-y1}px")
        
        # Crop carta
        card_img = screenshot.crop((x1, y1, x2, y2))
        cards.append(card_img)
        
        logger.info(f"  ✅ Card extracted")
    
    logger.info(f"\n{'='*80}")
    logger.info(f"✅ Total cards extracted: {len(cards)}")
    logger.info(f"{'='*80}\n")
    
    return cards


def visualize_board_detection(
    screenshot: Image.Image,
    phase: str = "RIVER",
    output_path: str = None
) -> Image.Image:
    """
    Visualizza i bounding box delle carte board.
    
    Args:
        screenshot: Screenshot completo
        phase: Fase del gioco
        output_path: Path dove salvare (opzionale)
        
    Returns:
        Immagine con overlay dei box
    """
    from PIL import ImageDraw, ImageFont
    
    width, height = screenshot.size
    active_slots = SLOTS_BY_PHASE.get(phase.upper(), [])
    
    # Copia per disegnare
    vis_img = screenshot.copy()
    draw = ImageDraw.Draw(vis_img)
    
    # Disegna tutti gli slot (grigi per inattivi, verdi per attivi)
    for slot_idx in range(5):
        x1, y1, x2, y2 = calculate_board_slot_bbox(slot_idx, width, height)
        
        if slot_idx in active_slots:
            color = "lime"
            width_line = 4
            label = f"Slot {slot_idx} ✓"
        else:
            color = "gray"
            width_line = 2
            label = f"Slot {slot_idx}"
        
        draw.rectangle([x1, y1, x2, y2], outline=color, width=width_line)
        draw.text((x1 + 5, y1 + 5), label, fill=color)
    
    # Marca il centro schermo (3ª carta)
    center_x = width // 2
    center_y = int(height * BOARD_CENTER_Y_RATIO)
    draw.ellipse([center_x-10, center_y-10, center_x+10, center_y+10],
                 outline="red", width=3)
    draw.text((center_x + 15, center_y - 10), "CENTER", fill="red")
    
    if output_path:
        vis_img.save(output_path)
        logger.info(f"✅ Visualization saved: {output_path}")
    
    return vis_img


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_board_zone_bbox(
    screen_width: int,
    screen_height: int,
    phase: str = "RIVER"
) -> Tuple[int, int, int, int]:
    """
    Calcola bounding box dell'intera zona board (utile per debug).
    
    Returns:
        (x, y, width, height) dell'area che contiene tutte le carte attive
    """
    active_slots = SLOTS_BY_PHASE.get(phase.upper(), [])
    
    if not active_slots:
        return (0, 0, 0, 0)
    
    # Calcola bbox di tutti gli slot attivi
    min_x = float('inf')
    min_y = float('inf')
    max_x = 0
    max_y = 0
    
    for slot_idx in active_slots:
        x1, y1, x2, y2 = calculate_board_slot_bbox(slot_idx, screen_width, screen_height)
        min_x = min(min_x, x1)
        min_y = min(min_y, y1)
        max_x = max(max_x, x2)
        max_y = max(max_y, y2)
    
    return (int(min_x), int(min_y), int(max_x - min_x), int(max_y - min_y))


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    # Test con screenshot ufficiale
    screenshot_path = Path(__file__).parent / "screenshots" / "pokerstars_river.png"
    
    if not screenshot_path.exists():
        logger.error(f"❌ Screenshot not found: {screenshot_path}")
        sys.exit(1)
    
    logger.info(f"📸 Loading screenshot: {screenshot_path}")
    screenshot = Image.open(screenshot_path)
    
    # Test detection per ogni fase
    for phase in ["FLOP", "TURN", "RIVER"]:
        logger.info(f"\n{'#'*80}")
        logger.info(f"# TEST: {phase}")
        logger.info(f"{'#'*80}")
        
        cards = detect_board_cards_geometric(screenshot, phase)
        
        # Salva visualizzazione
        vis_path = f"/tmp/board_detection_{phase.lower()}.png"
        visualize_board_detection(screenshot, phase, vis_path)
        
        # Salva carte estratte
        for i, card in enumerate(cards):
            card_path = f"/tmp/card_{phase.lower()}_{i+1}.png"
            card.save(card_path)
            logger.info(f"  💾 Card saved: {card_path}")
    
    logger.info(f"\n✅ All tests completed!")
