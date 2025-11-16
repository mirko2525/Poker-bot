#!/usr/bin/env python3
"""
PROCESS RAW TEMPLATES - ORDINE CAPO
====================================

I template forniti dal Capo sono RAW (carte complete).
Devo processarli con la PIPELINE UNICA:
1. Normalize con normalize_card_for_template()
2. Estrarre rank region (0-35% width, 0-25% height)
3. Estrarre suit region (0-35% width, 10-45% height)
4. Salvare regions normalizzate
"""

from PIL import Image
from pathlib import Path
from card_normalization import normalize_card_for_template

ranks_dir = Path("card_templates/ranks")
suits_dir = Path("card_templates/suits")

print("🔧 PROCESSING RAW TEMPLATES CON PIPELINE UNICA\n")

# Process ranks
print("=== RANKS ===")
for rank_file in sorted(ranks_dir.glob("*.png")):
    # Load raw template
    raw = Image.open(rank_file)
    print(f"{rank_file.name}: {raw.size} mode={raw.mode}")
    
    # Normalize con pipeline unica
    normalized = normalize_card_for_template(raw)
    
    # Extract rank region (top-left 35% x 25%)
    w, h = normalized.size
    rank_w = int(w * 0.35)
    rank_h = int(h * 0.25)
    rank_region = normalized.crop((0, 0, rank_w, rank_h))
    
    # Sovrascrivi con region normalizzata
    rank_region.save(rank_file)
    print(f"  ✅ Processed → {rank_region.size} mode={rank_region.mode}")

print("\n=== SUITS ===")
for suit_file in sorted(suits_dir.glob("*.png")):
    # Load raw template
    raw = Image.open(suit_file)
    print(f"{suit_file.name}: {raw.size} mode={raw.mode}")
    
    # Normalize con pipeline unica
    normalized = normalize_card_for_template(raw)
    
    # Extract suit region (0-35% width, 10-45% height)
    w, h = normalized.size
    suit_w = int(w * 0.35)
    suit_y_start = int(h * 0.10)
    suit_y_end = int(h * 0.45)
    suit_region = normalized.crop((0, suit_y_start, suit_w, suit_y_end))
    
    # Sovrascrivi con region normalizzata
    suit_region.save(suit_file)
    print(f"  ✅ Processed → {suit_region.size} mode={suit_region.mode}")

print("\n✅ TEMPLATE PROCESSING COMPLETE")
print("Tutti i template ora usano la PIPELINE UNICA")
