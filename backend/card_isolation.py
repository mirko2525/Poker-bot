#!/usr/bin/env python3
"""
CARD ISOLATION - Contour Detection
Isola la carta bianca dal tavolo verde usando OpenCV contour detection.

Capo's info: carte hanno SFONDO BIANCO, tavolo è VERDE.
"""

import cv2
import numpy as np
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def isolate_card_from_green_table(card_image: Image.Image) -> Image.Image:
    """
    Isola la carta bianca dal tavolo verde usando contour detection.
    
    Args:
        card_image: PIL Image contenente carta + sfondo verde tavolo
    
    Returns:
        PIL Image della carta isolata con sfondo bianco
    """
    try:
        # Convert PIL to OpenCV
        img_rgb = np.array(card_image.convert('RGB'))
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        
        # Define range for WHITE color (carta)
        # White in HSV: low saturation, high value
        lower_white = np.array([0, 0, 180])  # H, S, V
        upper_white = np.array([180, 50, 255])
        
        # Create mask for white pixels (carta)
        mask_white = cv2.inRange(hsv, lower_white, upper_white)
        
        # Morphological operations to clean noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask_white = cv2.morphologyEx(mask_white, cv2.MORPH_CLOSE, kernel)
        mask_white = cv2.morphologyEx(mask_white, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            logger.debug("No white card contour found, returning original")
            return card_image
        
        # Find largest contour (should be the card)
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        
        # Check if contour is large enough (at least 20% of image)
        min_area = img_bgr.shape[0] * img_bgr.shape[1] * 0.20
        
        if area < min_area:
            logger.debug(f"Contour too small: {area} < {min_area}, returning original")
            return card_image
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Extract card region
        card_region = img_bgr[y:y+h, x:x+w]
        
        # Convert back to PIL
        card_rgb = cv2.cvtColor(card_region, cv2.COLOR_BGR2RGB)
        card_pil = Image.fromarray(card_rgb)
        
        return card_pil
        
    except Exception as e:
        logger.error(f"Error isolating card: {e}")
        return card_image


def isolate_card_simple_threshold(card_image: Image.Image) -> Image.Image:
    """
    Isola carta dal tavolo verde sostituendo SOLO il verde con bianco.
    Preserva simboli neri e colorati della carta.
    
    Args:
        card_image: PIL Image contenente carta + sfondo verde
    
    Returns:
        PIL Image con sfondo verde sostituito da bianco, simboli preservati
    """
    try:
        # Convert to numpy
        img_rgb = np.array(card_image.convert('RGB'))
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2HSV)
        
        # Define range for GREEN color (tavolo)
        # Green: H=60 (35-85), high S, medium V
        lower_green = np.array([25, 40, 20])
        upper_green = np.array([95, 255, 120])
        
        # Mask green pixels (tavolo)
        mask_green = cv2.inRange(hsv, lower_green, upper_green)
        
        # Replace ONLY green pixels with white
        result = img_rgb.copy()
        result[mask_green > 0] = [255, 255, 255]
        
        # Convert back to PIL
        result_pil = Image.fromarray(result)
        
        return result_pil
        
    except Exception as e:
        logger.error(f"Error in simple threshold: {e}")
        return card_image


def main():
    """Test card isolation."""
    from pathlib import Path
    
    print("=" * 70)
    print("🔧 CARD ISOLATION TEST")
    print("=" * 70)
    print()
    
    # Test su carte estratte
    test_dir = Path('extracted_cards_all')
    if not test_dir.exists():
        print("❌ Test directory not found")
        return
    
    output_dir = Path('isolated_cards_test')
    output_dir.mkdir(exist_ok=True)
    
    test_files = sorted(test_dir.glob('*.jpg'))[:5]  # Prime 5
    
    for card_file in test_files:
        card_img = Image.open(card_file)
        
        # Method 1: Contour detection
        isolated_contour = isolate_card_from_green_table(card_img)
        isolated_contour.save(output_dir / f'{card_file.stem}_contour.jpg')
        
        # Method 2: Simple threshold
        isolated_simple = isolate_card_simple_threshold(card_img)
        isolated_simple.save(output_dir / f'{card_file.stem}_threshold.jpg')
        
        print(f"✅ {card_file.name}: isolated")
    
    print()
    print(f"📁 Isolated cards saved to {output_dir}/")
    print("   Compare contour vs threshold methods")
    print("=" * 70)


if __name__ == "__main__":
    main()
