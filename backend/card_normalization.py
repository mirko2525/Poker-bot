#!/usr/bin/env python3
"""
CARD NORMALIZATION - Single Source of Truth
Funzione unica per normalizzare carte, usata sia per template che per live recognition.

Ordini del Capo Fase 6: NO green removal, solo grayscale + resize.
Template e live devono passare dalla STESSA trasformazione.
"""

from PIL import Image, ImageOps
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Standard card dimensions (from config)
CARD_TEMPLATE_WIDTH = 89
CARD_TEMPLATE_HEIGHT = 118

# ============================================================================
# SINGLE SOURCE OF TRUTH - Template & Recognition Normalization
# ============================================================================

def normalize_card_for_template(img: Image.Image) -> Image.Image:
    """
    🎯 PIPELINE UNICA per template generation E live recognition.
    
    ORDINE DEL CAPO FASE 6.2:
    - Questa funzione DEVE essere usata:
      1. Quando crei i template rank/suit
      2. Quando riconosci le carte live
    
    Pipeline:
    - Grayscale
    - Resize a dimensioni standard (89x118)
    - Autocontrast=True (leggero)
    - NO isolate_card (carte già estratte pulite da geometric)
    
    Args:
        img: PIL Image della carta estratta da board_detector_geometric
        
    Returns:
        PIL Image normalizzata (L mode, 89x118px)
    """
    return normalize_card_image(
        img,
        target_width=CARD_TEMPLATE_WIDTH,
        target_height=CARD_TEMPLATE_HEIGHT,
        use_autocontrast=True,
        isolate_card=False  # Carte già pulite da geometric detection
    )


def normalize_card_image(card_image: Image.Image,
                        target_width: int = CARD_TEMPLATE_WIDTH,
                        target_height: int = CARD_TEMPLATE_HEIGHT,
                        use_autocontrast: bool = True,
                        isolate_card: bool = False) -> Image.Image:
    """
    Normalizza una carta per template generation o recognition.
    
    QUESTA È LA SINGLE SOURCE OF TRUTH per normalizzazione carte.
    Template e live recognition DEVONO usare questa funzione.
    
    Pipeline:
    1. Isolate card from green table (optional, default ON)
    2. Convert to grayscale
    3. Resize to standard dimensions (LANCZOS)
    4. Optional: light autocontrast (same for template and live)
    
    Args:
        card_image: PIL Image della carta (raw, con sfondo verde o altro)
        target_width: Larghezza target (default 89px)
        target_height: Altezza target (default 118px)
        use_autocontrast: Applica autocontrast leggero (default True)
        isolate_card: Isola carta bianca da sfondo verde (default True)
    
    Returns:
        PIL Image normalizzata (grayscale, resized)
    """
    try:
        # Step 0: Isolate white card from green table
        if isolate_card:
            from card_isolation import isolate_card_simple_threshold
            card_image = isolate_card_simple_threshold(card_image)
        
        # Step 1: Convert to grayscale
        if card_image.mode != 'L':
            grayscale = ImageOps.grayscale(card_image)
        else:
            grayscale = card_image
        
        # Step 2: Resize to standard dimensions
        normalized = grayscale.resize(
            (target_width, target_height), 
            Image.Resampling.LANCZOS
        )
        
        # Step 3: Optional autocontrast (light, same for all)
        if use_autocontrast:
            normalized = ImageOps.autocontrast(normalized, cutoff=1)
        
        return normalized
        
    except Exception as e:
        logger.error(f"Error normalizing card image: {e}")
        # Return a blank template as fallback
        return Image.new('L', (target_width, target_height), color=128)


def main():
    """Test della normalizzazione su carte raw."""
    from pathlib import Path
    import numpy as np
    
    print("=" * 70)
    print("🔧 CARD NORMALIZATION TEST")
    print("=" * 70)
    print()
    
    # Test su carte raw estratte dallo screenshot (con verde)
    test_dir = Path('test_live_extraction_flop_v2')
    if not test_dir.exists():
        print("❌ Test directory not found")
        return
    
    card_files = sorted(test_dir.glob('*.png'))[:3]  # Prime 3 carte
    
    print(f"Testing normalization on {len(card_files)} raw cards...")
    print()
    
    for card_file in card_files:
        # Raw card
        raw_card = Image.open(card_file)
        raw_arr = np.array(ImageOps.grayscale(raw_card))
        
        # Normalized card
        normalized = normalize_card_image(raw_card)
        norm_arr = np.array(normalized)
        
        print(f"{card_file.name}:")
        print(f"  Raw: {raw_card.width}x{raw_card.height}, "
              f"mode={raw_card.mode}, brightness={raw_arr.mean():.1f}")
        print(f"  Normalized: {normalized.width}x{normalized.height}, "
              f"mode={normalized.mode}, brightness={norm_arr.mean():.1f}")
        print()
    
    print("✅ Normalization uses: grayscale + resize (LANCZOS)")
    print("   NO green removal, NO color tricks")
    print("   Same transformation for template generation and live recognition")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
