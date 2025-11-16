#!/usr/bin/env python3
"""
Card Recognition Module - Fase 4

Riconoscimento di singole carte usando template matching.
Strategia: MSE (Mean Squared Error) per confrontare immagini normalizzate.

Ordini del Capo - Fase 4: Template matching semplice senza OpenCV/reti neurali.
"""

import numpy as np
from PIL import Image, ImageOps
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path

from card_templates import (
    load_card_templates, normalize_card_image, 
    CARD_TEMPLATE_WIDTH, CARD_TEMPLATE_HEIGHT
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Recognition parameters
MSE_THRESHOLD = 0.05  # Maximum MSE to accept a card match (strict but reasonable)
MIN_CONFIDENCE_SCORE = 0.95  # Minimum confidence score to accept recognition


def calculate_mse(image1: np.ndarray, image2: np.ndarray) -> float:
    """
    Calculate Mean Squared Error between two images.
    
    Args:
        image1: First image array (normalized 0-1)
        image2: Second image array (normalized 0-1)
        
    Returns:
        MSE value (lower is better match)
    """
    try:
        # Ensure same shape
        if image1.shape != image2.shape:
            logger.warning(f"Shape mismatch: {image1.shape} vs {image2.shape}")
            return float('inf')
        
        # Calculate MSE
        mse = np.mean((image1 - image2) ** 2)
        return float(mse)
        
    except Exception as e:
        logger.error(f"Error calculating MSE: {e}")
        return float('inf')


def normalize_card_for_recognition(card_image: Image.Image) -> np.ndarray:
    """
    Normalize a card image for recognition (convert to same format as templates).
    
    Args:
        card_image: PIL Image of card to recognize
        
    Returns:
        Normalized numpy array (0-1 range)
    """
    try:
        # Use the same normalization as templates
        normalized_image = normalize_card_image(
            card_image, 
            CARD_TEMPLATE_WIDTH, 
            CARD_TEMPLATE_HEIGHT
        )
        
        # Convert to numpy array and normalize to 0-1
        card_array = np.array(normalized_image, dtype=np.float32) / 255.0
        
        return card_array
        
    except Exception as e:
        logger.error(f"Error normalizing card for recognition: {e}")
        # Return blank array as fallback
        return np.zeros((CARD_TEMPLATE_HEIGHT, CARD_TEMPLATE_WIDTH), dtype=np.float32)


def recognize_card(card_image: Image.Image, 
                  templates: Dict[str, np.ndarray],
                  mse_threshold: float = MSE_THRESHOLD) -> Tuple[Optional[str], float]:
    """
    Recognize a single card using template matching.
    
    Args:
        card_image: PIL Image of card to recognize
        templates: Dictionary of card templates (code -> numpy array)
        mse_threshold: Maximum MSE to accept a match
        
    Returns:
        Tuple of (card_code or None, confidence_score)
    """
    if not templates:
        logger.warning("No templates provided for card recognition")
        return None, 0.0
    
    try:
        # Check if card position is empty (mostly uniform)
        card_array_check = np.array(card_image.convert('L'), dtype=np.float32)
        mean_brightness = card_array_check.mean()
        brightness_std = card_array_check.std()
        
        # If very dark with low variance, it's likely an empty position
        if mean_brightness < 55 and brightness_std < 15:
            logger.debug(f"Empty card position detected (dark): brightness={mean_brightness:.1f}, std={brightness_std:.1f}")
            return None, 0.0
        
        # Normalize the input card
        card_array = normalize_card_for_recognition(card_image)
        
        best_card = None
        best_mse = float('inf')
        
        # Compare with all templates
        for card_code, template in templates.items():
            mse = calculate_mse(card_array, template)
            
            if mse < best_mse:
                best_mse = mse
                best_card = card_code
        
        # Calculate confidence score (1 - normalized MSE)
        # Normalize MSE to 0-1 range (assuming max MSE is around 1.0 for completely different images)
        max_possible_mse = 1.0
        normalized_mse = min(best_mse / max_possible_mse, 1.0)
        confidence = 1.0 - normalized_mse
        
        # Check if match is good enough
        if best_mse <= mse_threshold and confidence >= MIN_CONFIDENCE_SCORE:
            logger.debug(f"Recognized card: {best_card} (MSE: {best_mse:.4f}, Confidence: {confidence:.3f})")
            return best_card, confidence
        else:
            logger.debug(f"No confident match found (Best: {best_card}, MSE: {best_mse:.4f}, Confidence: {confidence:.3f})")
            return None, confidence
            
    except Exception as e:
        logger.error(f"Error recognizing card: {e}")
        return None, 0.0


def recognize_cards(card_images: List[Image.Image], 
                   templates: Dict[str, np.ndarray]) -> List[Tuple[Optional[str], float]]:
    """
    Recognize multiple cards from a list of images.
    
    Args:
        card_images: List of PIL Images to recognize
        templates: Dictionary of card templates
        
    Returns:
        List of tuples (card_code or None, confidence_score)
    """
    results = []
    
    for i, card_image in enumerate(card_images):
        try:
            card_code, confidence = recognize_card(card_image, templates)
            results.append((card_code, confidence))
            
            if card_code:
                logger.debug(f"Card {i+1}: {card_code} (confidence: {confidence:.3f})")
            else:
                logger.debug(f"Card {i+1}: unrecognized (confidence: {confidence:.3f})")
                
        except Exception as e:
            logger.error(f"Error recognizing card {i+1}: {e}")
            results.append((None, 0.0))
    
    return results


def filter_recognized_cards(recognition_results: List[Tuple[Optional[str], float]]) -> List[str]:
    """
    Filter and return only successfully recognized cards.
    Removes duplicates with lower confidence (keeps first occurrence).
    
    Args:
        recognition_results: List of (card_code, confidence) tuples
        
    Returns:
        List of card codes (excludes None/unrecognized cards and suspicious duplicates)
    """
    recognized = []
    seen_cards = {}
    
    for idx, (card_code, confidence) in enumerate(recognition_results):
        if card_code is not None:
            # If we've seen this card before, keep the one with higher confidence
            if card_code in seen_cards:
                prev_idx, prev_conf = seen_cards[card_code]
                if confidence > prev_conf:
                    # Replace previous occurrence with this one
                    recognized[recognized.index(card_code)] = None  # Mark for removal
                    recognized.append(card_code)
                    seen_cards[card_code] = (idx, confidence)
                    logger.warning(f"Duplicate card {card_code} detected - keeping higher confidence match")
                # else: ignore this duplicate, keep the previous one
            else:
                recognized.append(card_code)
                seen_cards[card_code] = (idx, confidence)
    
    # Remove None markers
    return [card for card in recognized if card is not None]


def get_recognition_stats(recognition_results: List[Tuple[Optional[str], float]]) -> Dict:
    """
    Get statistics about card recognition results.
    
    Args:
        recognition_results: List of recognition results
        
    Returns:
        Dictionary with recognition statistics
    """
    total_cards = len(recognition_results)
    recognized_cards = sum(1 for card_code, conf in recognition_results if card_code is not None)
    unrecognized_cards = total_cards - recognized_cards
    
    if recognized_cards > 0:
        confidences = [conf for card_code, conf in recognition_results if card_code is not None]
        avg_confidence = sum(confidences) / len(confidences)
        min_confidence = min(confidences)
        max_confidence = max(confidences)
    else:
        avg_confidence = min_confidence = max_confidence = 0.0
    
    return {
        "total_cards": total_cards,
        "recognized": recognized_cards,
        "unrecognized": unrecognized_cards,
        "recognition_rate": recognized_cards / total_cards if total_cards > 0 else 0.0,
        "average_confidence": avg_confidence,
        "min_confidence": min_confidence,
        "max_confidence": max_confidence
    }


def test_card_recognition_on_regions(output_regions_dir: str, 
                                   templates: Dict[str, np.ndarray]) -> None:
    """
    Test card recognition on extracted regions from Phase 3.
    
    Args:
        output_regions_dir: Directory containing extracted card regions
        templates: Card templates dictionary
    """
    regions_path = Path(output_regions_dir)
    
    if not regions_path.exists():
        print(f"❌ Regions directory not found: {regions_path}")
        return
    
    print(f"🧪 Testing card recognition on: {output_regions_dir}")
    
    # Find all card images
    hero_cards = list(regions_path.glob("hero_card_*.png"))
    board_cards = list(regions_path.glob("board_card_*.png"))
    
    all_cards = sorted(hero_cards) + sorted(board_cards)
    
    if not all_cards:
        print("❌ No card images found")
        return
    
    print(f"📁 Found {len(all_cards)} card images")
    
    # Load and recognize all cards
    card_images = []
    for card_file in all_cards:
        try:
            card_img = Image.open(card_file)
            card_images.append(card_img)
        except Exception as e:
            logger.error(f"Error loading {card_file}: {e}")
    
    # Perform recognition
    results = recognize_cards(card_images, templates)
    
    # Display results
    print("\n🎯 Recognition Results:")
    for i, (card_file, (card_code, confidence)) in enumerate(zip(all_cards, results)):
        status = "✅" if card_code else "❌"
        card_display = card_code if card_code else "unrecognized"
        print(f"   {status} {card_file.name}: {card_display} (confidence: {confidence:.3f})")
    
    # Statistics
    stats = get_recognition_stats(results)
    print("\n📊 Statistics:")
    print(f"   Recognition rate: {stats['recognition_rate']:.1%}")
    print(f"   Average confidence: {stats['average_confidence']:.3f}")
    
    recognized_cards = filter_recognized_cards(results)
    if recognized_cards:
        print(f"   Recognized cards: {', '.join(recognized_cards)}")


def main():
    """Main function for testing card recognition."""
    
    print("🎯 CARD RECOGNITION MODULE - FASE 4")
    print("=" * 50)
    
    # Load templates
    templates_dir = "card_templates/normalized"
    print(f"Loading templates from: {templates_dir}")
    
    templates = load_card_templates(templates_dir)
    
    if not templates:
        print("❌ No card templates found!")
        print("💡 Run card_templates.py first to create templates")
        return
    
    print(f"✅ Loaded {len(templates)} card templates")
    print()
    
    # Test on available region outputs
    test_directories = [
        "output_regions_flop",
        "output_regions_turn", 
        "output_regions_river",
        "output_regions_preflop"
    ]
    
    for test_dir in test_directories:
        if Path(test_dir).exists():
            test_card_recognition_on_regions(test_dir, templates)
            print()
        else:
            print(f"⏩ Skipping {test_dir} (not found)")
    
    print("🔧 Next steps:")
    print("1. Add more card samples to improve template coverage")
    print("2. Tune MSE_THRESHOLD and MIN_CONFIDENCE_SCORE for better accuracy")
    print("3. Test with different poker scenarios")


if __name__ == "__main__":
    main()