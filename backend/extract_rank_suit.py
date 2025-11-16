#!/usr/bin/env python3
"""
Script per estrarre RANK e SUIT da carte complete.
Crea template riutilizzabili per Piano A (13 ranks + 4 suits).

FASE 6 FIX: Usa normalize_card_image() come single source of truth.
Template e live recognition passano dalla STESSA normalizzazione.
"""

from pathlib import Path
from PIL import Image
import sys
from card_normalization import normalize_card_image

def extract_rank_suit_from_card(card_image_path: str, card_code: str):
    """
    Estrae rank e suit da una carta completa.
    
    Args:
        card_image_path: Path alla carta completa (es: hero_card_1.png)
        card_code: Codice carta (es: '6d', 'Ah')
    
    Le carte PokerStars hanno rank+suit nell'angolo top-left.
    Tipicamente: primi ~25-30% width e ~20-25% height.
    """
    base_dir = Path(__file__).resolve().parent
    
    img_path = base_dir / card_image_path
    if not img_path.exists():
        print(f"❌ File not found: {img_path}")
        return False
    
    if len(card_code) != 2:
        print(f"❌ Invalid card code: {card_code}")
        return False
    
    rank = card_code[0].upper()
    suit = card_code[1].lower()
    
    # Load image
    img = Image.open(img_path)
    
    print(f"📸 Processing: {card_image_path}")
    print(f"   Card code: {card_code}")
    print(f"   Image size: {img.width}x{img.height}")
    print()
    
    # Extract rank region (top-left corner, upper portion)
    # Typical card size: 89x118 (from our config)
    # Rank is in top ~30% of card, left ~30%
    rank_width = int(img.width * 0.35)
    rank_height = int(img.height * 0.25)
    
    rank_region = img.crop((0, 0, rank_width, rank_height))
    
    # Extract suit region (top-left corner, includes rank overlap)
    # CALIBRATED coordinates (Fase 6 fix v4): 10%-45% (larger) for different layouts
    suit_y_start = int(img.height * 0.10)
    suit_y_end = int(img.height * 0.45)
    suit_width = int(img.width * 0.35)
    
    suit_region = img.crop((0, suit_y_start, suit_width, suit_y_end))
    
    # Save rank
    ranks_dir = base_dir / "card_templates" / "ranks"
    ranks_dir.mkdir(parents=True, exist_ok=True)
    
    rank_file = ranks_dir / f"{rank}.png"
    rank_region.save(rank_file)
    print(f"✅ Rank saved: {rank_file.name} ({rank_region.width}x{rank_region.height})")
    
    # Save suit
    suits_dir = base_dir / "card_templates" / "suits"
    suits_dir.mkdir(parents=True, exist_ok=True)
    
    # Map suit letter to name
    suit_names = {
        'c': 'clubs',
        'd': 'diamonds', 
        'h': 'hearts',
        's': 'spades'
    }
    
    suit_name = suit_names.get(suit, suit)
    suit_file = suits_dir / f"{suit_name}.png"
    suit_region.save(suit_file)
    print(f"✅ Suit saved: {suit_file.name} ({suit_region.width}x{suit_region.height})")
    
    return True


def extract_from_best_samples():
    """
    Estrae rank e suit dalle migliori carte disponibili.
    """
    base_dir = Path(__file__).resolve().parent
    
    print("=" * 70)
    print("🃏 EXTRACTING RANKS AND SUITS FROM BEST SAMPLES")
    print("=" * 70)
    print()
    
    # Best samples per ogni carta che abbiamo
    best_samples = {
        '2c': 'output_regions_flop_v2/board_card_3.png',
        '4d': 'output_regions_hero_3_fixed/hero_card_2.png',
        '4h': 'output_regions_hero_3_fixed/hero_card_1.png',
        '6d': 'output_regions_flop_v2/board_card_1.png',
        '8c': 'output_regions_hero_1_fixed/hero_card_2.png',
        'Ac': 'output_regions_river/board_card_5.png',
        'Ah': 'output_regions_flop_v2/board_card_2.png',
    }
    
    extracted_ranks = set()
    extracted_suits = set()
    
    for card_code, img_path in best_samples.items():
        print(f"Processing {card_code}...")
        if extract_rank_suit_from_card(img_path, card_code):
            extracted_ranks.add(card_code[0])
            extracted_suits.add(card_code[1])
            print()
    
    print("=" * 70)
    print("📊 EXTRACTION SUMMARY")
    print("=" * 70)
    print(f"✅ Ranks extracted: {sorted(extracted_ranks)} ({len(extracted_ranks)}/13)")
    print(f"✅ Suits extracted: {sorted(extracted_suits)} ({len(extracted_suits)}/4)")
    print()
    print("📋 MISSING:")
    
    all_ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
    all_suits = ['c', 'd', 'h', 's']
    
    missing_ranks = [r for r in all_ranks if r not in extracted_ranks]
    missing_suits = [s for s in all_suits if s not in extracted_suits]
    
    print(f"   Ranks needed: {missing_ranks}")
    print(f"   Suits needed: {missing_suits}")
    print()
    print("=" * 70)


def main():
    """Main CLI."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "extract":
            extract_from_best_samples()
        elif sys.argv[1] == "single" and len(sys.argv) == 4:
            card_path = sys.argv[2]
            card_code = sys.argv[3]
            extract_rank_suit_from_card(card_path, card_code)
        else:
            print("Usage:")
            print("  python extract_rank_suit.py extract")
            print("  python extract_rank_suit.py single <card_image_path> <card_code>")
    else:
        extract_from_best_samples()


if __name__ == "__main__":
    main()
