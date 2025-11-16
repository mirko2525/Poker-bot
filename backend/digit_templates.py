#!/usr/bin/env python3
"""
Digit Templates Module - Fase 4

Gestione dei template per cifre e simboli per OCR di pot e stack.
Template per 0-9, punto decimale, virgola, simbolo euro.

Ordini del Capo - Fase 4: Template-based digit recognition per numeri poker.
"""

from pathlib import Path
from PIL import Image, ImageOps
import numpy as np
from typing import Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Standard digit template dimensions
DIGIT_TEMPLATE_WIDTH = 16
DIGIT_TEMPLATE_HEIGHT = 24

# Supported digits and symbols
DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
SYMBOLS = ['.', ',', '€', '$']  # Decimal point, comma, euro, dollar
ALL_CHARACTERS = DIGITS + SYMBOLS

def normalize_digit_image(image: Image.Image, 
                         target_width: int = DIGIT_TEMPLATE_WIDTH,
                         target_height: int = DIGIT_TEMPLATE_HEIGHT) -> Image.Image:
    """
    Normalize a digit image to standard template format.
    
    Args:
        image: PIL Image of a digit/symbol
        target_width: Target width for template
        target_height: Target height for template
        
    Returns:
        Normalized PIL Image (grayscale, resized, enhanced)
    """
    try:
        # Convert to grayscale
        if image.mode != 'L':
            image = ImageOps.grayscale(image)
        
        # Resize to standard dimensions
        normalized = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Enhance contrast and clarity
        normalized = ImageOps.autocontrast(normalized)
        
        # Optional: Apply slight sharpening filter
        # normalized = normalized.filter(ImageFilter.SHARPEN)
        
        return normalized
        
    except Exception as e:
        logger.error(f"Error normalizing digit image: {e}")
        # Return a blank template as fallback
        return Image.new('L', (target_width, target_height), color=128)


def preprocess_number_region(image: Image.Image, 
                            invert_colors: bool = False,
                            threshold: int = 128) -> Image.Image:
    """
    Preprocess a number region for better digit extraction.
    
    Args:
        image: PIL Image of number region (pot/stack)
        invert_colors: Whether to invert colors (white text on dark background)
        threshold: Threshold for binarization
        
    Returns:
        Preprocessed PIL Image
    """
    try:
        # Convert to grayscale
        if image.mode != 'L':
            image = ImageOps.grayscale(image)
        
        # Enhance contrast
        image = ImageOps.autocontrast(image)
        
        # Binarize (threshold)
        def threshold_fn(x):
            return 255 if x > threshold else 0
        
        image = image.point(threshold_fn, mode='1')
        image = image.convert('L')  # Convert back to grayscale
        
        # Invert if needed (for white text on dark background)
        if invert_colors:
            image = ImageOps.invert(image)
        
        return image
        
    except Exception as e:
        logger.error(f"Error preprocessing number region: {e}")
        return image


def create_digit_templates_from_raw_samples(raw_samples_dir: str, 
                                          normalized_dir: str) -> Dict[str, str]:
    """
    Process raw digit sample images into normalized templates.
    
    Args:
        raw_samples_dir: Directory containing raw digit sample images
        normalized_dir: Directory to save normalized templates
        
    Returns:
        Dictionary mapping characters to normalized template file paths
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
            # Extract character from filename
            # Expected format: digit_0_1.png, symbol_dot_1.png, etc.
            filename = raw_file.stem  # Remove .png extension
            
            # Try to extract character
            character = None
            
            # Handle different naming patterns
            if filename.startswith('digit_'):
                # digit_0_1.png -> '0'
                parts = filename.split('_')
                if len(parts) >= 2:
                    character = parts[1]
            elif filename.startswith('symbol_'):
                # symbol_dot_1.png -> '.'
                parts = filename.split('_')
                if len(parts) >= 2:
                    symbol_name = parts[1]
                    symbol_map = {
                        'dot': '.',
                        'comma': ',',
                        'euro': '€',
                        'dollar': '$'
                    }
                    character = symbol_map.get(symbol_name)
            else:
                # Direct character naming: 0.png, dot.png, etc.
                if len(filename) == 1 and filename in DIGITS:
                    character = filename
                elif filename in ['dot', 'comma', 'euro', 'dollar']:
                    symbol_map = {
                        'dot': '.',
                        'comma': ',', 
                        'euro': '€',
                        'dollar': '$'
                    }
                    character = symbol_map.get(filename)
            
            if character and character in ALL_CHARACTERS:
                # Load and normalize the image
                raw_image = Image.open(raw_file)
                normalized_image = normalize_digit_image(raw_image)
                
                # Save normalized template with safe filename
                safe_filename_map = {
                    '.': 'dot',
                    ',': 'comma',
                    '€': 'euro', 
                    '$': 'dollar'
                }
                safe_name = safe_filename_map.get(character, character)
                
                normalized_file = normalized_path / f"{safe_name}.png"
                normalized_image.save(normalized_file)
                
                processed_templates[character] = str(normalized_file)
                logger.info(f"Created template: '{character}' from {raw_file.name}")
            else:
                logger.warning(f"Could not extract valid character from filename: {filename}")
                
        except Exception as e:
            logger.error(f"Error processing {raw_file}: {e}")
    
    logger.info(f"Created {len(processed_templates)} digit/symbol templates")
    return processed_templates


def load_digit_templates(template_dir: str) -> Dict[str, np.ndarray]:
    """
    Load digit and symbol templates from normalized directory.
    
    Args:
        template_dir: Directory containing normalized digit template images
        
    Returns:
        Dictionary mapping characters to numpy arrays (grayscale)
    """
    template_path = Path(template_dir)
    
    if not template_path.exists():
        logger.error(f"Template directory not found: {template_path}")
        return {}
    
    templates = {}
    
    # Filename to character mapping
    filename_map = {
        'dot.png': '.',
        'comma.png': ',',
        'euro.png': '€',
        'dollar.png': '$'
    }
    
    # Load all digit and symbol templates
    for template_file in template_path.glob("*.png"):
        try:
            filename = template_file.name
            
            # Determine character
            character = None
            
            if filename in filename_map:
                character = filename_map[filename]
            elif len(template_file.stem) == 1 and template_file.stem in DIGITS:
                character = template_file.stem  # '0.png' -> '0'
            
            if character and character in ALL_CHARACTERS:
                # Load image and convert to numpy array
                template_image = Image.open(template_file)
                
                # Ensure grayscale
                if template_image.mode != 'L':
                    template_image = ImageOps.grayscale(template_image)
                
                # Convert to numpy array
                template_array = np.array(template_image, dtype=np.float32)
                
                # Normalize to 0-1 range
                template_array = template_array / 255.0
                
                templates[character] = template_array
                logger.debug(f"Loaded template: '{character}' ({template_array.shape})")
            else:
                logger.warning(f"Could not map filename to character: {filename}")
                
        except Exception as e:
            logger.error(f"Error loading template {template_file}: {e}")
    
    logger.info(f"Loaded {len(templates)} digit/symbol templates")
    return templates


def get_digit_template_stats(template_dir: str) -> Dict:
    """
    Get statistics about available digit templates.
    
    Args:
        template_dir: Directory containing digit templates
        
    Returns:
        Dictionary with template statistics
    """
    templates = load_digit_templates(template_dir)
    
    available = list(templates.keys())
    missing_digits = [d for d in DIGITS if d not in available]
    missing_symbols = [s for s in SYMBOLS if s not in available]
    
    return {
        "total_possible": len(ALL_CHARACTERS),
        "available": len(available),
        "missing": len(ALL_CHARACTERS) - len(available),
        "coverage_percentage": len(available) / len(ALL_CHARACTERS) * 100,
        "available_characters": sorted(available),
        "missing_digits": missing_digits,
        "missing_symbols": missing_symbols,
        "digits_coverage": len([d for d in DIGITS if d in available]),
        "symbols_coverage": len([s for s in SYMBOLS if s in available])
    }


def extract_digits_from_regions():
    """
    Helper function to extract digit samples from pot/stack regions.
    This function helps create initial digit templates from existing regions.
    """
    print("🔍 EXTRACTING DIGITS FROM POT/STACK REGIONS")
    print("=" * 50)
    
    regions_to_check = [
        "output_regions_flop",
        "output_regions_turn", 
        "output_regions_river"
    ]
    
    digit_count = 0
    
    for region_dir in regions_to_check:
        region_path = Path(region_dir)
        
        if not region_path.exists():
            continue
            
        print(f"\n📁 Checking {region_dir}:")
        
        # Check pot and stack regions
        for region_type in ['pot_region', 'hero_stack_region']:
            region_file = region_path / f"{region_type}.png"
            
            if region_file.exists():
                try:
                    img = Image.open(region_file)
                    print(f"   {region_type}: {img.width}x{img.height}")
                    
                    # Save a copy for manual digit extraction
                    output_name = f"manual_extract_{region_dir.split('_')[2]}_{region_type}.png"
                    manual_dir = Path("digit_templates/manual_extraction")
                    manual_dir.mkdir(parents=True, exist_ok=True)
                    
                    img.save(manual_dir / output_name)
                    digit_count += 1
                    
                except Exception as e:
                    print(f"   ❌ Error processing {region_file}: {e}")
            else:
                print(f"   ❌ {region_type}: not found")
    
    if digit_count > 0:
        print(f"\n✅ Saved {digit_count} regions for manual digit extraction")
        print("📋 Next steps:")
        print("1. Open images in digit_templates/manual_extraction/")
        print("2. Manually crop individual digits and save as digit_0_1.png, etc.")
        print("3. Run create_digit_templates_from_raw_samples()")
    else:
        print("\n❌ No regions found for digit extraction")


def main():
    """Main function for testing digit template operations."""
    
    print("🔢 DIGIT TEMPLATES MODULE - FASE 4")
    print("=" * 50)
    
    # Directories
    raw_dir = "digit_templates/raw_samples"
    normalized_dir = "digit_templates/normalized"
    
    print(f"Raw samples directory: {raw_dir}")
    print(f"Normalized templates directory: {normalized_dir}")
    print()
    
    # Check if we have raw samples to process
    raw_path = Path(raw_dir)
    if raw_path.exists() and list(raw_path.glob("*.png")):
        print("📁 Processing raw digit samples into normalized templates...")
        templates_info = create_digit_templates_from_raw_samples(raw_dir, normalized_dir)
        
        if templates_info:
            print(f"✅ Created {len(templates_info)} digit/symbol templates")
        else:
            print("❌ No valid digit samples found")
    else:
        print("ℹ️  No raw digit samples found")
        print("💡 Running digit extraction helper...")
        extract_digits_from_regions()
    
    print()
    
    # Load and display template statistics
    print("📊 Digit Template Statistics:")
    stats = get_digit_template_stats(normalized_dir)
    
    print(f"   Available: {stats['available']}/{stats['total_possible']} ({stats['coverage_percentage']:.1f}%)")
    print(f"   Digits: {stats['digits_coverage']}/10")
    print(f"   Symbols: {stats['symbols_coverage']}/{len(SYMBOLS)}")
    
    if stats['available'] > 0:
        print(f"   Available: {stats['available_characters']}")
    
    if stats['missing_digits']:
        print(f"   Missing digits: {stats['missing_digits']}")
    
    if stats['missing_symbols']:
        print(f"   Missing symbols: {stats['missing_symbols']}")


if __name__ == "__main__":
    main()