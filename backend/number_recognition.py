#!/usr/bin/env python3
"""
Number Recognition Module - Fase 4

OCR per numeri di pot e stack usando template matching.
Estrazione di cifre e ricostruzione numeri float.

Ordini del Capo - Fase 4: Template-based OCR per valori numerici poker.
"""

import numpy as np
from PIL import Image, ImageOps
from typing import Dict, List, Optional, Tuple
import logging
import re

from digit_templates import (
    load_digit_templates, preprocess_number_region,
    DIGIT_TEMPLATE_WIDTH, DIGIT_TEMPLATE_HEIGHT
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Recognition parameters
DIGIT_MSE_THRESHOLD = 0.15  # Threshold for digit matching
MIN_DIGIT_CONFIDENCE = 0.6  # Minimum confidence for digit recognition
DIGIT_SPACING_THRESHOLD = 5  # Max pixels between digits in same number


def calculate_digit_mse(image1: np.ndarray, image2: np.ndarray) -> float:
    """
    Calculate MSE between two digit images.
    
    Args:
        image1: First digit array (normalized 0-1)
        image2: Second digit array (normalized 0-1)
        
    Returns:
        MSE value (lower is better match)
    """
    try:
        if image1.shape != image2.shape:
            return float('inf')
        
        mse = np.mean((image1 - image2) ** 2)
        return float(mse)
        
    except Exception as e:
        logger.error(f"Error calculating digit MSE: {e}")
        return float('inf')


def normalize_digit_for_recognition(digit_image: Image.Image) -> np.ndarray:
    """
    Normalize a digit region for recognition.
    
    Args:
        digit_image: PIL Image of digit region
        
    Returns:
        Normalized numpy array (0-1 range)
    """
    try:
        # Resize to standard digit template size
        normalized = digit_image.resize(
            (DIGIT_TEMPLATE_WIDTH, DIGIT_TEMPLATE_HEIGHT), 
            Image.Resampling.LANCZOS
        )
        
        # Convert to grayscale if needed
        if normalized.mode != 'L':
            normalized = ImageOps.grayscale(normalized)
        
        # Convert to numpy array and normalize to 0-1
        digit_array = np.array(normalized, dtype=np.float32) / 255.0
        
        return digit_array
        
    except Exception as e:
        logger.error(f"Error normalizing digit for recognition: {e}")
        return np.zeros((DIGIT_TEMPLATE_HEIGHT, DIGIT_TEMPLATE_WIDTH), dtype=np.float32)


def recognize_digit(digit_image: Image.Image, 
                   templates: Dict[str, np.ndarray]) -> Tuple[Optional[str], float]:
    """
    Recognize a single digit using template matching.
    
    Args:
        digit_image: PIL Image of digit to recognize
        templates: Dictionary of digit templates
        
    Returns:
        Tuple of (character or None, confidence_score)
    """
    if not templates:
        return None, 0.0
    
    try:
        digit_array = normalize_digit_for_recognition(digit_image)
        
        best_char = None
        best_mse = float('inf')
        
        # Compare with all digit templates
        for char, template in templates.items():
            mse = calculate_digit_mse(digit_array, template)
            
            if mse < best_mse:
                best_mse = mse
                best_char = char
        
        # Calculate confidence
        max_possible_mse = 1.0
        normalized_mse = min(best_mse / max_possible_mse, 1.0)
        confidence = 1.0 - normalized_mse
        
        # Check if match is good enough
        if best_mse <= DIGIT_MSE_THRESHOLD and confidence >= MIN_DIGIT_CONFIDENCE:
            logger.debug(f"Recognized digit: '{best_char}' (MSE: {best_mse:.4f}, Confidence: {confidence:.3f})")
            return best_char, confidence
        else:
            logger.debug(f"No confident digit match (Best: '{best_char}', MSE: {best_mse:.4f}, Confidence: {confidence:.3f})")
            return None, confidence
            
    except Exception as e:
        logger.error(f"Error recognizing digit: {e}")
        return None, 0.0


def segment_number_image(number_image: Image.Image, 
                        min_digit_width: int = 8,
                        max_digit_width: int = 24) -> List[Image.Image]:
    """
    Segment a number image into individual digit images.
    
    Args:
        number_image: PIL Image containing a number
        min_digit_width: Minimum width for a digit
        max_digit_width: Maximum width for a digit
        
    Returns:
        List of digit images
    """
    try:
        # Convert to grayscale
        if number_image.mode != 'L':
            number_image = ImageOps.grayscale(number_image)
        
        # Preprocess the image
        processed = preprocess_number_region(number_image, invert_colors=False)
        
        # Convert to numpy array for analysis
        img_array = np.array(processed)
        
        # Find vertical projection (sum of pixels in each column)
        vertical_projection = np.sum(img_array, axis=0)
        
        # Find transitions (background to foreground and vice versa)
        # Use a threshold to determine what's background vs foreground
        threshold = np.mean(vertical_projection) * 0.5
        
        # Find start and end positions of potential digits
        segments = []
        start_pos = None
        
        for col in range(len(vertical_projection)):
            if vertical_projection[col] > threshold:  # Foreground pixel column
                if start_pos is None:
                    start_pos = col
            else:  # Background pixel column
                if start_pos is not None:
                    width = col - start_pos
                    if min_digit_width <= width <= max_digit_width:
                        # Extract digit region
                        digit_region = number_image.crop((start_pos, 0, col, number_image.height))
                        segments.append(digit_region)
                    start_pos = None
        
        # Handle case where number ends without background
        if start_pos is not None:
            width = number_image.width - start_pos
            if min_digit_width <= width <= max_digit_width:
                digit_region = number_image.crop((start_pos, 0, number_image.width, number_image.height))
                segments.append(digit_region)
        
        logger.debug(f"Segmented number into {len(segments)} potential digits")
        return segments
        
    except Exception as e:
        logger.error(f"Error segmenting number image: {e}")
        # Fallback: return the whole image as a single segment
        return [number_image]


def recognize_number(number_image: Image.Image, 
                    templates: Dict[str, np.ndarray]) -> Tuple[Optional[float], str, List[float]]:
    """
    Recognize a complete number from an image.
    
    Args:
        number_image: PIL Image containing a number
        templates: Dictionary of digit/symbol templates
        
    Returns:
        Tuple of (parsed_number or None, raw_string, confidence_scores)
    """
    try:
        # Segment the image into digits
        digit_images = segment_number_image(number_image)
        
        if not digit_images:
            logger.debug("No digit segments found")
            return None, "", []
        
        # Recognize each digit
        recognized_chars = []
        confidence_scores = []
        
        for digit_img in digit_images:
            char, confidence = recognize_digit(digit_img, templates)
            recognized_chars.append(char if char else '?')
            confidence_scores.append(confidence)
        
        # Build raw string
        raw_string = ''.join(recognized_chars)
        
        # Try to parse as number
        parsed_number = parse_number_string(raw_string)
        
        logger.debug(f"Number recognition: '{raw_string}' -> {parsed_number}")
        return parsed_number, raw_string, confidence_scores
        
    except Exception as e:
        logger.error(f"Error recognizing number: {e}")
        return None, "", []


def parse_number_string(raw_string: str) -> Optional[float]:
    """
    Parse a string of recognized characters into a float number.
    
    Args:
        raw_string: String of recognized characters
        
    Returns:
        Parsed float number or None if parsing fails
    """
    try:
        # Remove unknown characters
        cleaned = raw_string.replace('?', '')
        
        # Handle different decimal separators
        cleaned = cleaned.replace(',', '.')
        
        # Remove currency symbols
        cleaned = cleaned.replace('€', '').replace('$', '')
        
        # Remove spaces
        cleaned = cleaned.strip()
        
        if not cleaned:
            return None
        
        # Try to parse as float
        # Handle cases like "12.50", "5", ".67", etc.
        if re.match(r'^\\d*\\.?\\d+$', cleaned):
            return float(cleaned)
        elif re.match(r'^\\.\\d+$', cleaned):  # .67
            return float(cleaned)
        else:
            logger.debug(f"Could not parse number string: '{cleaned}'")
            return None
            
    except (ValueError, AttributeError) as e:
        logger.debug(f"Error parsing number string '{raw_string}': {e}")
        return None


def test_number_recognition_on_regions(output_regions_dir: str, 
                                     templates: Dict[str, np.ndarray]) -> None:
    """
    Test number recognition on pot and stack regions.
    
    Args:
        output_regions_dir: Directory containing extracted regions
        templates: Digit templates dictionary
    """
    from pathlib import Path
    
    regions_path = Path(output_regions_dir)
    
    if not regions_path.exists():
        print(f"❌ Regions directory not found: {regions_path}")
        return
    
    print(f"🧪 Testing number recognition on: {output_regions_dir}")
    
    # Find pot and stack regions
    pot_file = regions_path / "pot_region.png"
    stack_file = regions_path / "hero_stack_region.png"
    
    number_files = []
    if pot_file.exists():
        number_files.append(("pot", pot_file))
    if stack_file.exists():
        number_files.append(("stack", stack_file))
    
    if not number_files:
        print("❌ No number regions found")
        return
    
    print(f"📁 Found {len(number_files)} number regions")
    
    # Test each number region
    for region_type, file_path in number_files:
        try:
            print(f"\\n🔍 Analyzing {region_type} region:")
            
            number_img = Image.open(file_path)
            print(f"   Image size: {number_img.width}x{number_img.height}")
            
            # Recognize the number
            parsed_number, raw_string, confidences = recognize_number(number_img, templates)
            
            if parsed_number is not None:
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                print(f"   ✅ Recognized: {parsed_number} (raw: '{raw_string}', confidence: {avg_confidence:.3f})")
            else:
                print(f"   ❌ Could not parse number (raw: '{raw_string}')")
                
        except Exception as e:
            print(f"   ❌ Error processing {region_type}: {e}")


def create_mock_digit_templates() -> Dict[str, np.ndarray]:
    """
    Create mock digit templates for testing when no real templates exist.
    
    Returns:
        Dictionary with basic digit templates
    """
    templates = {}
    
    # Create simple mock templates (just for testing structure)
    for digit in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        # Create a simple pattern for each digit
        mock_array = np.random.random((DIGIT_TEMPLATE_HEIGHT, DIGIT_TEMPLATE_WIDTH)).astype(np.float32)
        templates[digit] = mock_array
    
    # Add decimal point
    templates['.'] = np.random.random((DIGIT_TEMPLATE_HEIGHT, DIGIT_TEMPLATE_WIDTH)).astype(np.float32)
    
    logger.info("Created mock digit templates for testing")
    return templates


def main():
    """Main function for testing number recognition."""
    
    print("🔢 NUMBER RECOGNITION MODULE - FASE 4")
    print("=" * 50)
    
    # Load digit templates
    templates_dir = "digit_templates/normalized"
    print(f"Loading digit templates from: {templates_dir}")
    
    templates = load_digit_templates(templates_dir)
    
    if not templates:
        print("❌ No digit templates found!")
        print("💡 Creating mock templates for structure testing...")
        templates = create_mock_digit_templates()
    else:
        print(f"✅ Loaded {len(templates)} digit/symbol templates")
    
    print()
    
    # Test on available region outputs
    test_directories = [
        "output_regions_flop",
        "output_regions_turn", 
        "output_regions_river"
    ]
    
    for test_dir in test_directories:
        from pathlib import Path
        if Path(test_dir).exists():
            test_number_recognition_on_regions(test_dir, templates)
        else:
            print(f"⏩ Skipping {test_dir} (not found)")
    
    print()
    print("🔧 Next steps:")
    print("1. Create digit templates from manual extraction")
    print("2. Tune DIGIT_MSE_THRESHOLD and MIN_DIGIT_CONFIDENCE")
    print("3. Test number parsing with different formats")


if __name__ == "__main__":
    main()