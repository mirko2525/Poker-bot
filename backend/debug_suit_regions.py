#!/usr/bin/env python3
"""
DEBUG SUIT REGIONS
Script per vedere ESATTAMENTE cosa stiamo ritagliando.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from card_recognition_ranksuit import extract_rank_region, extract_suit_region

def main():
    """Estrae e salva rank/suit regions per debug visivo."""
    
    print("=" * 70)
    print("🔍 DEBUG SUIT REGIONS - EXTRACTION")
    print("=" * 70)
    print()
    
    base_dir = Path(".")
    out_dir = base_dir / "debug_suits"
    out_dir.mkdir(exist_ok=True)
    
    # Test su carte note con suit diverse
    test_cards = [
        ("output_regions_flop_v2/board_card_1.png", "6d"),  # diamonds
        ("output_regions_flop_v2/board_card_2.png", "Ah"),  # hearts
        ("output_regions_flop_v2/board_card_3.png", "2c"),  # clubs
        ("output_regions_deck_1/board_card_4.png", "As"),   # spades
        ("output_regions_hero_1_fixed/hero_card_2.png", "8c"),  # clubs
        ("output_regions_deck_2/board_card_3.png", "Kd"),   # diamonds
    ]
    
    print(f"📂 Extracting regions from {len(test_cards)} known cards:")
    print()
    
    for i, (card_path, expected) in enumerate(test_cards, 1):
        card_file = base_dir / card_path
        
        if not card_file.exists():
            print(f"  ⏭️  Skipping {expected} (file not found)")
            continue
        
        img = Image.open(card_file)
        
        # Extract regions
        rank_region = extract_rank_region(img)
        suit_region = extract_suit_region(img)
        
        # Save with descriptive names
        rank_file = out_dir / f"card{i}_{expected}_rank.png"
        suit_file = out_dir / f"card{i}_{expected}_suit.png"
        
        rank_region.save(rank_file)
        suit_region.save(suit_file)
        
        print(f"  ✅ {expected:3s}: rank {rank_region.width}x{rank_region.height}, suit {suit_region.width}x{suit_region.height}")
        print(f"       → {rank_file.name}, {suit_file.name}")
    
    print()
    print("=" * 70)
    print(f"📁 Debug images saved to: {out_dir}/")
    print()
    print("👁️  NEXT STEP:")
    print("   1. Open the images in debug_suits/ folder")
    print("   2. Check if suit regions show the suit symbol clearly:")
    print("      - card1_6d_suit.png should show ♦ (diamond)")
    print("      - card2_Ah_suit.png should show ♥ (heart)")
    print("      - card3_2c_suit.png should show ♣ (club)")
    print("      - card4_As_suit.png should show ♠ (spade)")
    print()
    print("   3. If ALL suits look the same → coordinates are WRONG")
    print("   4. If suits are off-center → adjust SUIT_BOX in card_recognition_ranksuit.py")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
