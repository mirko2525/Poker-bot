#!/usr/bin/env python3
"""
CARD PREPROCESSING MODULE
Normalizza le carte estratte dallo screenshot rimuovendo lo sfondo verde del tavolo.
"""

from PIL import Image, ImageOps
import numpy as np
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def remove_green_background(card_image: Image.Image, 
                            green_threshold: int = 50) -> Image.Image:
    """
    Rimuove lo sfondo verde del tavolo da poker, rendendolo bianco.
    CONSERVA i simboli scuri della carta.
    
    Args:
        card_image: PIL Image della carta (RGB o RGBA)
        green_threshold: Soglia per identificare il verde (default 50)
    
    Returns:
        PIL Image con sfondo bianco e simboli preservati
    """
    # Convert to RGB if needed
    if card_image.mode == 'RGBA':
        rgb_image = card_image.convert('RGB')
    elif card_image.mode == 'RGB':
        rgb_image = card_image
    else:
        # Already grayscale or other - return as is
        return card_image
    
    # Convert to numpy
    arr = np.array(rgb_image, dtype=np.uint8)
    
    r = arr[:, :, 0].astype(np.float32)
    g = arr[:, :, 1].astype(np.float32)
    b = arr[:, :, 2].astype(np.float32)
    
    # Strategy: KEEP dark pixels (card symbols) and bright pixels (white card)
    # REPLACE mid-range green pixels (table felt)
    
    # 1. Dark pixels (likely symbols) - KEEP
    is_symbol = (r < 80) & (g < 80) & (b < 80)
    
    # 2. Bright pixels (likely white card) - KEEP  
    # But need to whiten them more
    is_bright = (r > 150) | (g > 150) | (b > 150)
    
    # 3. Green/dark background (table felt) - REPLACE
    # Dark pixels where green is dominant
    is_felt = (g > r + 20) & (g > b + 10) & (~is_symbol) & (~is_bright)
    
    # Also very dark pixels that aren't symbols
    is_very_dark = (r < 30) & (g < 80) & (b < 30) & (~is_symbol)
    
    # Combine background masks
    background_mask = is_felt | is_very_dark
    
    # Replace background with white
    arr[background_mask] = [255, 255, 255]
    
    # Brighten the "bright" pixels to make them pure white
    arr[is_bright] = [255, 255, 255]
    
    # Convert back to PIL Image
    cleaned_image = Image.fromarray(arr)
    
    return cleaned_image


def normalize_card_brightness(card_image: Image.Image, 
                               target_mean: float = 200.0) -> Image.Image:
    """
    Normalizza la luminosità della carta.
    
    Args:
        card_image: PIL Image della carta
        target_mean: Luminosità media target (default 200 per sfondo bianco)
    
    Returns:
        PIL Image normalizzata
    """
    # Convert to grayscale for analysis
    gray = ImageOps.grayscale(card_image)
    arr = np.array(gray, dtype=np.float32)
    
    current_mean = arr.mean()
    
    # Avoid division by zero
    if current_mean < 1.0:
        return card_image
    
    # Calculate scaling factor
    scale = target_mean / current_mean
    
    # Don't scale if already bright enough
    if scale < 1.2:
        return card_image
    
    # Apply scaling with clipping
    if card_image.mode == 'RGB' or card_image.mode == 'RGBA':
        arr_color = np.array(card_image, dtype=np.float32)
        
        # Scale each channel
        arr_color = np.clip(arr_color * scale, 0, 255).astype(np.uint8)
        
        return Image.fromarray(arr_color, mode=card_image.mode)
    else:
        # Grayscale
        arr = np.clip(arr * scale, 0, 255).astype(np.uint8)
        return Image.fromarray(arr, mode='L')


def preprocess_card_for_recognition(card_image: Image.Image) -> Image.Image:
    """
    Pipeline completo di preprocessing per una carta.
    
    Args:
        card_image: PIL Image della carta raw dallo screenshot
    
    Returns:
        PIL Image preprocessata pronta per il riconoscimento
    """
    # Step 1: Remove green background
    cleaned = remove_green_background(card_image)
    
    # Step 2: Normalize brightness (optional, often already good after step 1)
    # normalized = normalize_card_brightness(cleaned)
    
    return cleaned


def preprocess_cards(card_images: List[Image.Image]) -> List[Image.Image]:
    """
    Preprocessa una lista di carte.
    
    Args:
        card_images: Lista di PIL Images
    
    Returns:
        Lista di PIL Images preprocessate
    """
    processed = []
    
    for card_image in card_images:
        processed_card = preprocess_card_for_recognition(card_image)
        processed.append(processed_card)
    
    return processed


def main():
    """Test del preprocessing."""
    from pathlib import Path
    
    print("=" * 70)
    print("🔧 CARD PREPROCESSING TEST")
    print("=" * 70)
    print()
    
    # Test su carta estratta LIVE
    test_dir = Path('test_live_extraction_flop_v2')
    if not test_dir.exists():
        print("❌ Test directory not found")
        return
    
    output_dir = Path('test_live_extraction_flop_v2_preprocessed')
    output_dir.mkdir(exist_ok=True)
    
    card_files = sorted(test_dir.glob('*.png'))
    
    print(f"Processing {len(card_files)} cards...")
    print()
    
    for card_file in card_files:
        card = Image.open(card_file)
        
        # Before preprocessing
        arr_before = np.array(ImageOps.grayscale(card))
        brightness_before = arr_before.mean()
        std_before = arr_before.std()
        
        # Preprocess
        processed = preprocess_card_for_recognition(card)
        
        # After preprocessing
        arr_after = np.array(ImageOps.grayscale(processed))
        brightness_after = arr_after.mean()
        std_after = arr_after.std()
        
        # Save
        output_file = output_dir / card_file.name
        processed.save(output_file)
        
        improvement = "✅" if brightness_after > brightness_before * 2 else "⚠️ "
        
        print(f"{improvement} {card_file.name}:")
        print(f"   Before: brightness={brightness_before:.1f}, std={std_before:.1f}")
        print(f"   After:  brightness={brightness_after:.1f}, std={std_after:.1f}")
    
    print()
    print(f"📁 Processed cards saved to {output_dir}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
