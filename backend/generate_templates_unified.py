#!/usr/bin/env python3
"""
TEMPLATE GENERATION - UNIFIED PIPELINE
Genera template rank e suit usando normalize_card_image() come single source of truth.

Ordini del Capo Fase 6: Complete reset con screenshot canonici.
"""

from pathlib import Path
from PIL import Image
import sys
from card_normalization import normalize_card_image

def generate_templates_from_raw_samples():
    """
    Genera template rank e suit da card_templates/raw_samples/.
    
    File naming convention: [rank][suit]_name.png
    Esempi: 6d_flop_1.png, Ah_flop_1.png, 2c_turn_2.png
    """
    
    print("=" * 70)
    print("🔧 GENERATING TEMPLATES - UNIFIED PIPELINE")
    print("=" * 70)
    print()
    
    base_dir = Path(__file__).resolve().parent
    raw_samples_dir = base_dir / "card_templates" / "raw_samples"
    ranks_dir = base_dir / "card_templates" / "ranks"
    suits_dir = base_dir / "card_templates" / "suits"
    
    # Create output directories
    ranks_dir.mkdir(parents=True, exist_ok=True)
    suits_dir.mkdir(parents=True, exist_ok=True)
    
    if not raw_samples_dir.exists():
        print(f"❌ Raw samples directory not found: {raw_samples_dir}")
        return
    
    # Suit mapping
    suit_map = {
        'c': 'clubs',
        'd': 'diamonds',
        'h': 'hearts',
        's': 'spades'
    }
    
    extracted_ranks = set()
    extracted_suits = set()
    
    # Process all PNG files
    sample_files = sorted(raw_samples_dir.glob("*.png"))
    
    if not sample_files:
        print(f"❌ No samples found in {raw_samples_dir}")
        return
    
    print(f"Processing {len(sample_files)} card samples...")
    print()
    
    for sample_file in sample_files:
        # Extract card code from filename (first 2 chars)
        filename = sample_file.stem
        
        if len(filename) < 2:
            print(f"⏭️  Skipping {sample_file.name}: filename too short")
            continue
        
        card_code = filename[:2]
        rank = card_code[0].upper()
        suit = card_code[1].lower()
        
        # Validate
        valid_ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
        valid_suits = ['c', 'd', 'h', 's']
        
        if rank not in valid_ranks or suit not in valid_suits:
            print(f"⏭️  Skipping {sample_file.name}: invalid card code '{card_code}'")
            continue
        
        print(f"Processing {card_code} from {sample_file.name}...")
        
        # Load RAW card
        try:
            card_raw = Image.open(sample_file)
            
            # NORMALIZE with single source of truth
            card_normalized = normalize_card_image(card_raw)
            
            # Extract rank region (0-25% height, 0-35% width)
            rank_width = int(card_normalized.width * 0.35)
            rank_height = int(card_normalized.height * 0.25)
            rank_region = card_normalized.crop((0, 0, rank_width, rank_height))
            
            # Extract suit region (10-45% height, 0-35% width)
            suit_y_start = int(card_normalized.height * 0.10)
            suit_y_end = int(card_normalized.height * 0.45)
            suit_width = int(card_normalized.width * 0.35)
            suit_region = card_normalized.crop((0, suit_y_start, suit_width, suit_y_end))
            
            # Save rank template
            rank_file = ranks_dir / f"{rank}.png"
            rank_region.save(rank_file)
            extracted_ranks.add(rank)
            print(f"   ✅ Rank {rank} saved: {rank_file.name} ({rank_region.width}x{rank_region.height})")
            
            # Save suit template
            suit_name = suit_map[suit]
            suit_file = suits_dir / f"{suit_name}.png"
            suit_region.save(suit_file)
            extracted_suits.add(suit)
            print(f"   ✅ Suit {suit} ({suit_name}) saved: {suit_file.name} ({suit_region.width}x{suit_region.height})")
            print()
            
        except Exception as e:
            print(f"   ❌ Error processing {sample_file.name}: {e}")
            print()
            continue
    
    print("=" * 70)
    print("📊 GENERATION SUMMARY")
    print("=" * 70)
    print(f"✅ Extracted {len(extracted_ranks)} ranks: {sorted(extracted_ranks)}")
    print(f"✅ Extracted {len(extracted_suits)} suits: {sorted(extracted_suits)}")
    print()
    print(f"📁 Templates saved to:")
    print(f"   - {ranks_dir}/")
    print(f"   - {suits_dir}/")
    print()
    print("✅ All templates generated with normalize_card_image()")
    print("   Same pipeline for template and live recognition!")
    print("=" * 70)


if __name__ == "__main__":
    generate_templates_from_raw_samples()
