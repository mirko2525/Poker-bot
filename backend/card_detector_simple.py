#!/usr/bin/env python3
"""
CARD DETECTOR SIMPLE - Slot-Based Approach
Invece di contour detection, usa slot fissi + presenza check.

Strategia:
- Board zone divisa in 5 slot orizzontali
- Hero zone divisa in 2 slot orizzontali
- Per ogni slot: check se c'è carta bianca (white pixels > threshold)
"""

from PIL import Image
import numpy as np
from typing import List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_cards_from_slots(screenshot: Image.Image,
                             zone_box: Tuple[int, int, int, int],
                             num_slots: int,
                             white_threshold: float = 0.15) -> List[Image.Image]:
    """
    Estrae carte da zona usando slot fissi.
    
    Args:
        screenshot: PIL Image dello screenshot
        zone_box: (x, y, width, height) della zona
        num_slots: Numero di slot (5 per board, 2 per hero)
        white_threshold: Soglia white pixels per considerare slot con carta
    
    Returns:
        Lista di PIL Images delle carte (include None per slot vuoti)
    """
    x, y, w, h = zone_box
    
    slot_width = w // num_slots
    cards = []
    
    for i in range(num_slots):
        # Coordinate slot
        slot_x = x + (i * slot_width)
        slot_y = y
        
        # Crop slot con margini (80% centrale per evitare bordi)
        margin_x = int(slot_width * 0.1)
        margin_y = int(h * 0.1)
        
        slot_img = screenshot.crop((
            slot_x + margin_x,
            slot_y + margin_y,
            slot_x + slot_width - margin_x,
            slot_y + h - margin_y
        ))
        
        # Check se c'è carta (white pixels)
        arr = np.array(slot_img.convert('L'), dtype=np.float32)
        white_pixels = np.sum(arr > 200)
        total_pixels = arr.size
        white_ratio = white_pixels / total_pixels
        
        if white_ratio > white_threshold:
            cards.append(slot_img)
            logger.debug(f"Slot {i+1}: CARTA trovata (white={white_ratio:.2f})")
        else:
            cards.append(None)
            logger.debug(f"Slot {i+1}: EMPTY (white={white_ratio:.2f})")
    
    # Filtra None
    cards_filtered = [c for c in cards if c is not None]
    
    logger.info(f"Found {len(cards_filtered)}/{num_slots} cards in zone")
    
    return cards_filtered


def cut_board_cards_slot_based(screenshot: Image.Image, room_config: dict) -> List[Image.Image]:
    """
    Estrae board cards usando slot-based approach.
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
    
    num_slots = params.get('max_board_cards', 5)
    white_threshold = params.get('card_white_threshold', 0.15)
    
    return extract_cards_from_slots(screenshot, zone_box, num_slots, white_threshold)


def cut_hero_cards_slot_based(screenshot: Image.Image, room_config: dict) -> List[Image.Image]:
    """
    Estrae hero cards usando slot-based approach.
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
    
    num_slots = params.get('max_hero_cards', 2)
    white_threshold = params.get('card_white_threshold', 0.15)
    
    return extract_cards_from_slots(screenshot, zone_box, num_slots, white_threshold)


def main():
    """Test slot-based detection."""
    import json
    from pathlib import Path
    
    print("=" * 70)
    print("🔧 SLOT-BASED CARD DETECTION TEST")
    print("=" * 70)
    print()
    
    # Load config
    with open('rooms/pokerstars_6max_zones.json', 'r') as f:
        config = json.load(f)
    
    # Add white threshold param
    config['detection_params']['card_white_threshold'] = 0.15
    
    # Test screenshot
    screenshot = Image.open('screenshots_test/screenshot_clean.png')
    
    print("📸 Testing screenshot_clean.png")
    print()
    
    # Extract cards
    board_cards = cut_board_cards_slot_based(screenshot, config)
    hero_cards = cut_hero_cards_slot_based(screenshot, config)
    
    print(f"🎴 Board cards found: {len(board_cards)}")
    print(f"🃏 Hero cards found: {len(hero_cards)}")
    print()
    
    # Save debug images
    debug_dir = Path('debug_slot_cards')
    debug_dir.mkdir(exist_ok=True)
    
    for i, card in enumerate(board_cards, 1):
        card.save(debug_dir / f'board_{i}.png')
    
    for i, card in enumerate(hero_cards, 1):
        card.save(debug_dir / f'hero_{i}.png')
    
    print(f"📁 Cards saved to {debug_dir}/")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
