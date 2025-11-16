#!/usr/bin/env python3
"""
Card Templates Module - Fase 4

Questo modulo gestisce la creazione e il caricamento dei template delle carte poker.
Template matching per riconoscimento delle 52 carte del mazzo.

Ordini del Capo - Fase 4: Template-based card recognition (no neural networks).
"""

import os
import json
from pathlib import Path
from PIL import Image, ImageOps
import numpy as np
from typing import Dict, Optional, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Standard card template dimensions
CARD_TEMPLATE_WIDTH = 64
CARD_TEMPLATE_HEIGHT = 96

# Card code mapping (52 cards)
CARD_RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
CARD_SUITS = ['h', 'd', 'c', 's']  # hearts, diamonds, clubs, spades

def get_all_card_codes() -> List[str]:
    """
    Generate list of all 52 card codes (Ah, Ad, Ac, As, 2h, 2d, ..., Ks).
    
    Returns:
        List of all possible card codes
    """
    return [rank + suit for rank in CARD_RANKS for suit in CARD_SUITS]


def normalize_card_image(image: Image.Image, 
                        target_width: int = CARD_TEMPLATE_WIDTH,
                        target_height: int = CARD_TEMPLATE_HEIGHT) -> Image.Image:
    """
    Normalize a card image to standard template format.
    
    Args:
        image: PIL Image of a card
        target_width: Target width for template
        target_height: Target height for template
        
    Returns:
        Normalized PIL Image (grayscale, resized)
    """
    try:
        # Convert to grayscale
        if image.mode != 'L':
            image = ImageOps.grayscale(image)
        
        # Resize to standard dimensions
        normalized = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Optional: enhance contrast
        # normalized = ImageOps.autocontrast(normalized)
        
        return normalized
        
    except Exception as e:
        logger.error(f"Error normalizing card image: {e}")
        # Return a blank template as fallback
        return Image.new('L', (target_width, target_height), color=128)


def create_card_templates_from_raw_samples(raw_samples_dir: str, 
                                         normalized_dir: str) -> Dict[str, str]:
    """
    Process raw sample card images into normalized templates.
    
    Args:
        raw_samples_dir: Directory containing raw card sample images
        normalized_dir: Directory to save normalized templates
        
    Returns:
        Dictionary mapping card codes to normalized template file paths
    """
    raw_path = Path(raw_samples_dir)
    normalized_path = Path(normalized_dir)
    
    # Create normalized directory if it doesn't exist
    normalized_path.mkdir(parents=True, exist_ok=True)
    
    if not raw_path.exists():
        logger.warning(f"Raw samples directory not found: {raw_path}")
        return {}
    
    processed_templates = {}
    
    # Process all PNG files in raw_samples
    for raw_file in raw_path.glob("*.png"):
        try:
            # Extract card code from filename
            # Expected format: Ah_1.png, Kd_sample.png, etc.
            filename = raw_file.stem  # Remove .png extension
            
            # Try to extract card code (first 2 characters)
            if len(filename) >= 2:
                potential_card_code = filename[:2]
                
                # Validate card code
                if (potential_card_code[0] in CARD_RANKS and 
                    potential_card_code[1] in CARD_SUITS):
                    
                    card_code = potential_card_code
                    
                    # Load and normalize the image
                    raw_image = Image.open(raw_file)
                    normalized_image = normalize_card_image(raw_image)
                    
                    # Save normalized template
                    normalized_file = normalized_path / f"{card_code}.png"
                    normalized_image.save(normalized_file)
                    
                    processed_templates[card_code] = str(normalized_file)
                    logger.info(f"Created template: {card_code} from {raw_file.name}")
                else:
                    logger.warning(f"Invalid card code in filename: {filename}")
            else:
                logger.warning(f"Filename too short to extract card code: {filename}")
                
        except Exception as e:
            logger.error(f"Error processing {raw_file}: {e}")
    
    logger.info(f"Created {len(processed_templates)} card templates")
    return processed_templates


def load_card_templates(template_dir: str) -> Dict[str, np.ndarray]:
    """
    Load card templates from normalized directory.
    
    Args:
        template_dir: Directory containing normalized card template images
        
    Returns:
        Dictionary mapping card codes to numpy arrays (grayscale)
    """
    template_path = Path(template_dir)
    
    if not template_path.exists():
        logger.error(f"Template directory not found: {template_path}")
        return {}
    
    templates = {}
    
    # Load all card templates
    for template_file in template_path.glob("*.png"):
        try:
            card_code = template_file.stem  # e.g., "Ah" from "Ah.png"
            
            # Validate card code
            if (len(card_code) == 2 and 
                card_code[0] in CARD_RANKS and 
                card_code[1] in CARD_SUITS):
                
                # Load image and convert to numpy array
                template_image = Image.open(template_file)
                
                # Ensure grayscale
                if template_image.mode != 'L':
                    template_image = ImageOps.grayscale(template_image)
                
                # Convert to numpy array
                template_array = np.array(template_image, dtype=np.float32)
                
                # Normalize to 0-1 range
                template_array = template_array / 255.0
                
                templates[card_code] = template_array
                logger.debug(f"Loaded template: {card_code} ({template_array.shape})")
                
            else:
                logger.warning(f"Invalid template filename: {template_file.name}")
                
        except Exception as e:
            logger.error(f"Error loading template {template_file}: {e}")
    
    logger.info(f"Loaded {len(templates)} card templates")
    return templates


def save_card_template_config(templates_info: Dict[str, str], 
                            config_path: str) -> None:
    """
    Save card template configuration to JSON file.
    
    Args:
        templates_info: Dictionary with card template information
        config_path: Path to save the configuration JSON
    """
    try:
        config = {
            "card_template_config": {
                "template_dimensions": {
                    "width": CARD_TEMPLATE_WIDTH,
                    "height": CARD_TEMPLATE_HEIGHT
                },
                "total_cards": len(templates_info),
                "available_templates": list(templates_info.keys()),
                "missing_cards": [card for card in get_all_card_codes() 
                                if card not in templates_info]
            }
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        logger.info(f"Saved template config: {config_path}")
        
    except Exception as e:
        logger.error(f"Error saving template config: {e}")


def get_template_stats(template_dir: str) -> Dict:
    """
    Get statistics about available card templates.
    
    Args:
        template_dir: Directory containing card templates
        
    Returns:
        Dictionary with template statistics
    """
    templates = load_card_templates(template_dir)
    all_cards = get_all_card_codes()
    
    available = list(templates.keys())
    missing = [card for card in all_cards if card not in available]
    
    # Group by suits and ranks
    suits_coverage = {}
    ranks_coverage = {}
    
    for card in available:
        rank, suit = card[0], card[1]
        
        if suit not in suits_coverage:
            suits_coverage[suit] = []
        suits_coverage[suit].append(rank)
        
        if rank not in ranks_coverage:
            ranks_coverage[rank] = []
        ranks_coverage[rank].append(suit)
    
    return {
        "total_possible": len(all_cards),
        "available": len(available),
        "missing": len(missing),
        "coverage_percentage": len(available) / len(all_cards) * 100,
        "available_cards": sorted(available),
        "missing_cards": sorted(missing),
        "suits_coverage": {suit: len(cards) for suit, cards in suits_coverage.items()},
        "ranks_coverage": {rank: len(suits) for rank, suits in ranks_coverage.items()}
    }


def main():
    """Main function for testing card template operations."""
    
    print("🃏 CARD TEMPLATES MODULE - FASE 4")
    print("=" * 50)
    
    # Directories
    raw_dir = "card_templates/raw_samples"
    normalized_dir = "card_templates/normalized"
    config_file = "card_templates/config.json"
    
    print(f"Raw samples directory: {raw_dir}")
    print(f"Normalized templates directory: {normalized_dir}")
    print()
    
    # Check if we have raw samples to process
    raw_path = Path(raw_dir)
    if raw_path.exists() and list(raw_path.glob("*.png")):
        print("📁 Processing raw samples into normalized templates...")
        templates_info = create_card_templates_from_raw_samples(raw_dir, normalized_dir)
        
        if templates_info:
            print(f"✅ Created {len(templates_info)} templates")
            save_card_template_config(templates_info, config_file)
        else:
            print("❌ No valid card samples found")
    else:
        print("ℹ️  No raw samples found - skipping template creation")
    
    print()
    
    # Load and display template statistics
    print("📊 Template Statistics:")
    stats = get_template_stats(normalized_dir)
    
    print(f"   Available: {stats['available']}/{stats['total_possible']} ({stats['coverage_percentage']:.1f}%)")
    
    if stats['available'] > 0:
        print(f"   Cards available: {', '.join(stats['available_cards'])}")
    
    if stats['missing'] > 0:
        print(f"   Cards missing: {', '.join(stats['missing_cards'])}")
    
    print()
    print("🔧 Next steps:")
    print("1. Add card samples to card_templates/raw_samples/ (format: Ah_1.png)")
    print("2. Run this script to create normalized templates")
    print("3. Use load_card_templates() in card recognition")


if __name__ == "__main__":
    main()