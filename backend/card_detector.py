#!/usr/bin/env python3
"""
CARD DETECTOR - Zone Based Detection
Trova carte dentro zone usando computer vision invece di coordinate fisse.

Strategia Capo:
- JSON ha ZONE grandi (board_row, hero_row)
- Dentro ogni zona: HSV + contour detection per trovare carte bianche
- Filtra per area e aspect ratio
- Ordina per X da sinistra a destra
"""

import cv2
import numpy as np
from PIL import Image
from typing import List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_cards_in_zone(zone_image: Image.Image,
                       min_area: int = 5000,
                       max_area: int = 20000,
                       min_aspect: float = 1.0,
                       max_aspect: float = 1.6) -> List[Tuple[int, int, int, int]]:
    """
    Trova carte dentro una zona usando contour detection.
    
    Args:
        zone_image: PIL Image della zona (es. board_row o hero_row)
        min_area: Area minima contorno (pixel²)
        max_area: Area massima contorno
        min_aspect: Aspect ratio minimo (height/width)
        max_aspect: Aspect ratio massimo
    
    Returns:
        Lista di bounding boxes (x, y, w, h) ordinati per X (sinistra→destra)
    """
    try:
        # Convert PIL to OpenCV
        img_rgb = np.array(zone_image.convert('RGB'))
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        
        # Detect WHITE (carta) and remove GREEN (tavolo)
        # White in HSV: low saturation, high value
        lower_white = np.array([0, 0, 180])
        upper_white = np.array([180, 50, 255])
        mask_white = cv2.inRange(hsv, lower_white, upper_white)
        
        # Morphological operations per pulizia
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask_white = cv2.morphologyEx(mask_white, cv2.MORPH_CLOSE, kernel)
        mask_white = cv2.morphologyEx(mask_white, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        boxes = []
        
        for cnt in contours:
            # Bounding rectangle
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h
            aspect = h / w if w > 0 else 0
            
            # Filtri: area e aspect ratio devono essere da carta
            if min_area < area < max_area and min_aspect < aspect < max_aspect:
                boxes.append((x, y, w, h))
                logger.debug(f"Found card candidate: x={x}, y={y}, w={w}, h={h}, area={area}, aspect={aspect:.2f}")
        
        # Ordina per X (da sinistra a destra)
        boxes.sort(key=lambda b: b[0])
        
        logger.info(f"Found {len(boxes)} cards in zone")
        return boxes
        
    except Exception as e:
        logger.error(f"Error finding cards in zone: {e}")
        return []


def extract_cards_from_zone(screenshot: Image.Image,
                            zone_box: Tuple[int, int, int, int],
                            max_cards: int = 5,
                            **detection_params) -> List[Image.Image]:
    """
    Estrae carte da una zona dello screenshot.
    
    Args:
        screenshot: PIL Image dello screenshot completo
        zone_box: (x, y, width, height) della zona
        max_cards: Numero massimo carte da estrarre
        **detection_params: min_area, max_area, min_aspect, max_aspect
    
    Returns:
        Lista di PIL Images delle carte trovate (ordinate sinistra→destra)
    """
    try:
        x, y, w, h = zone_box
        
        # Crop zona
        zone_image = screenshot.crop((x, y, x + w, y + h))
        
        # Find cards
        boxes = find_cards_in_zone(zone_image, **detection_params)
        
        # Extract card images
        cards = []
        for card_x, card_y, card_w, card_h in boxes[:max_cards]:
            # Coordinate relative alla zona → assolute
            abs_x = x + card_x
            abs_y = y + card_y
            
            # Crop carta dallo screenshot originale
            card_img = screenshot.crop((abs_x, abs_y, abs_x + card_w, abs_y + card_h))
            cards.append(card_img)
        
        return cards
        
    except Exception as e:
        logger.error(f"Error extracting cards from zone: {e}")
        return []


def cut_board_cards_zone_based(screenshot: Image.Image, room_config: dict) -> List[Image.Image]:
    """
    Estrae board cards usando zone-based detection.
    
    Args:
        screenshot: PIL Image screenshot
        room_config: Dict con 'zones' e 'detection_params'
    
    Returns:
        Lista di PIL Images (board cards)
    """
    zones = room_config.get('zones', {})
    params = room_config.get('detection_params', {})
    
    board_zone = zones.get('board_row', {})
    zone_box = (
        board_zone.get('x', 0),
        board_zone.get('y', 0),
        board_zone.get('width', 0),
        board_zone.get('height', 0)
    )
    
    detection_params = {
        'min_area': params.get('card_min_area', 5000),
        'max_area': params.get('card_max_area', 20000),
        'min_aspect': params.get('card_min_aspect_ratio', 1.0),
        'max_aspect': params.get('card_max_aspect_ratio', 1.6)
    }
    
    max_cards = params.get('max_board_cards', 5)
    
    return extract_cards_from_zone(screenshot, zone_box, max_cards, **detection_params)


def cut_hero_cards_zone_based(screenshot: Image.Image, room_config: dict) -> List[Image.Image]:
    """
    Estrae hero cards usando zone-based detection.
    
    Args:
        screenshot: PIL Image screenshot
        room_config: Dict con 'zones' e 'detection_params'
    
    Returns:
        Lista di PIL Images (hero cards)
    """
    zones = room_config.get('zones', {})
    params = room_config.get('detection_params', {})
    
    hero_zone = zones.get('hero_row', {})
    zone_box = (
        hero_zone.get('x', 0),
        hero_zone.get('y', 0),
        hero_zone.get('width', 0),
        hero_zone.get('height', 0)
    )
    
    detection_params = {
        'min_area': params.get('card_min_area', 5000),
        'max_area': params.get('card_max_area', 20000),
        'min_aspect': params.get('card_min_aspect_ratio', 1.0),
        'max_aspect': params.get('card_max_aspect_ratio', 1.6)
    }
    
    max_cards = params.get('max_hero_cards', 2)
    
    return extract_cards_from_zone(screenshot, zone_box, max_cards, **detection_params)


def main():
    """Test zone-based detection."""
    import json
    from pathlib import Path
    
    print("=" * 70)
    print("🔧 ZONE-BASED CARD DETECTION TEST")
    print("=" * 70)
    print()
    
    # Load config
    with open('rooms/pokerstars_6max_zones.json', 'r') as f:
        config = json.load(f)
    
    # Test screenshot
    screenshot = Image.open('screenshots_test/screenshot1.png')
    
    print("📸 Testing screenshot1.png")
    print()
    
    # Extract board cards
    board_cards = cut_board_cards_zone_based(screenshot, config)
    print(f"🎴 Board cards found: {len(board_cards)}")
    
    # Extract hero cards
    hero_cards = cut_hero_cards_zone_based(screenshot, config)
    print(f"🃏 Hero cards found: {len(hero_cards)}")
    print()
    
    # Save debug images
    debug_dir = Path('debug_zone_cards')
    debug_dir.mkdir(exist_ok=True)
    
    for i, card in enumerate(board_cards, 1):
        card.save(debug_dir / f'board_card_{i}.png')
    
    for i, card in enumerate(hero_cards, 1):
        card.save(debug_dir / f'hero_card_{i}.png')
    
    print(f"📁 Debug images saved to {debug_dir}/")
    print("   👁️  Check these to verify cards are properly detected!")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
