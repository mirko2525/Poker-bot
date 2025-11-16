#!/usr/bin/env python3
"""
CALIBRAZIONE SUIT ROI
Script per trovare le coordinate ottimali per suit region.
"""

from PIL import Image
import numpy as np
from pathlib import Path

def test_suit_coordinates(card_path: str, card_code: str, y_start_pct: float, y_end_pct: float):
    """
    Testa coordinate specifiche e ritorna statistiche.
    """
    img = Image.open(card_path).convert('L')
    arr = np.array(img)
    
    CARD_HEIGHT = img.height
    CARD_WIDTH = img.width
    
    suit_width = int(CARD_WIDTH * 0.35)
    y_start = int(CARD_HEIGHT * y_start_pct)
    y_end = int(CARD_HEIGHT * y_end_pct)
    
    # Estrai regione
    region = arr[y_start:y_end, 0:suit_width]
    
    brightness = region.mean()
    dark_pixels = np.sum(region < 128)
    total_pixels = region.size
    dark_pct = dark_pixels / total_pixels * 100
    
    return {
        'brightness': brightness,
        'dark_pct': dark_pct,
        'has_content': dark_pct > 5.0  # Threshold: considera "contenuto" se >5% dark
    }

def find_optimal_coordinates():
    """
    Trova le coordinate ottimali testando diverse combinazioni.
    """
    
    print("=" * 70)
    print("🔧 CALIBRAZIONE AUTOMATICA SUIT ROI")
    print("=" * 70)
    print()
    
    # Carte test con suit diverse
    test_cards = [
        ('output_regions_flop_v2/board_card_1.png', '6d'),  # diamonds
        ('output_regions_flop_v2/board_card_2.png', 'Ah'),  # hearts
        ('output_regions_flop_v2/board_card_3.png', '2c'),  # clubs
    ]
    
    # Test diverse configurazioni
    configs = [
        # (y_start_pct, y_end_pct, description)
        (0.10, 0.35, "Compatto (10-35%)"),
        (0.12, 0.37, "Compatto+ (12-37%)"),
        (0.15, 0.40, "Medio (15-40%)"),
        (0.18, 0.43, "Medio+ (18-43%)"),
        (0.20, 0.45, "Attuale (20-45%)"),
        (0.22, 0.47, "Basso (22-47%)"),
        (0.25, 0.50, "Basso+ (25-50%)"),
    ]
    
    best_config = None
    best_score = 0
    
    print("📊 Testing coordinate configurations:")
    print()
    
    for y_start, y_end, desc in configs:
        results = []
        
        for card_path, card_code in test_cards:
            if not Path(card_path).exists():
                continue
            
            stats = test_suit_coordinates(card_path, card_code, y_start, y_end)
            results.append(stats)
        
        if not results:
            continue
        
        # Score: quante carte hanno contenuto
        cards_with_content = sum(1 for r in results if r['has_content'])
        avg_dark_pct = np.mean([r['dark_pct'] for r in results if r['has_content']])
        
        score = cards_with_content * avg_dark_pct
        
        marker = "  "
        if cards_with_content == len(results):
            marker = "✅"
        elif cards_with_content > 0:
            marker = "⚠️ "
        else:
            marker = "❌"
        
        print(f"{marker} {desc:20s}: {cards_with_content}/{len(results)} cards OK, avg_dark={avg_dark_pct:4.1f}%, score={score:6.1f}")
        
        if score > best_score:
            best_score = score
            best_config = (y_start, y_end, desc)
    
    print()
    print("=" * 70)
    
    if best_config:
        y_start, y_end, desc = best_config
        print(f"🏆 BEST CONFIGURATION: {desc}")
        print(f"   Y_START: {y_start:.2f} ({int(y_start * 100)}%)")
        print(f"   Y_END: {y_end:.2f} ({int(y_end * 100)}%)")
        print(f"   Score: {best_score:.1f}")
        print()
        
        print("📋 Code to update in card_recognition_ranksuit.py:")
        print()
        print(f"SUIT_Y = int(CARD_HEIGHT * {y_start:.2f})  # {int(y_start * 100)}%")
        print(f"SUIT_Y_END = int(CARD_HEIGHT * {y_end:.2f})  # {int(y_end * 100)}%")
        print()
        
        # Test dettagliato con best config
        print("🔍 Detailed test with best configuration:")
        print()
        for card_path, card_code in test_cards:
            if not Path(card_path).exists():
                continue
            
            stats = test_suit_coordinates(card_path, card_code, y_start, y_end)
            marker = "✅" if stats['has_content'] else "❌"
            print(f"{marker} {card_code}: brightness={stats['brightness']:5.1f}, dark={stats['dark_pct']:4.1f}%")
    else:
        print("❌ No valid configuration found")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    find_optimal_coordinates()
