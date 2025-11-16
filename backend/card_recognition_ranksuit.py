#!/usr/bin/env python3
"""
CARD RECOGNITION - RANK+SUIT SYSTEM
Fase 6 - Sistema basato su template separati rank (13) + suit (4).

FASE 6 FIX FINALE: Unified pipeline
- Template e live recognition usano STESSA normalize_card_image()
- NO green removal, solo grayscale + resize
- Template generati da carte raw, live usa carte raw
- Tutto passa dalla stessa trasformazione

Ordini del Capo:
- Carica rank_templates e suit_templates separati
- Normalizza la carta con normalize_card_image()
- Estrae rank_region e suit_region dalla carta normalizzata
- MSE matching separato per ciascuno
- Combina confidence per decisione finale
"""

from pathlib import Path
from PIL import Image, ImageOps
import numpy as np
from typing import Dict, Tuple, Optional, List
import logging
from card_normalization import normalize_card_image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Recognition thresholds (da Capo)
RANK_MSE_THRESHOLD = 0.08
SUIT_MSE_THRESHOLD = 0.08
MIN_COMBINED_CONFIDENCE = 0.85

# Card dimensions (from our config)
CARD_WIDTH = 89
CARD_HEIGHT = 118

# Rank region coordinates (top-left corner, upper portion)
RANK_X = 0
RANK_Y = 0
RANK_WIDTH = int(CARD_WIDTH * 0.35)  # ~31px
RANK_HEIGHT = int(CARD_HEIGHT * 0.25)  # ~29px

# Suit region coordinates (CALIBRATED - Fase 6 fix v4)
# Using 0.10-0.45 (larger region) to capture different card layouts
# Some suits are higher (10-30%), others lower (25-45%)
SUIT_X = 0
SUIT_Y = int(CARD_HEIGHT * 0.10)  # 12px
SUIT_Y_END = int(CARD_HEIGHT * 0.45)  # 53px
SUIT_WIDTH = int(CARD_WIDTH * 0.35)  # 31px
SUIT_HEIGHT = SUIT_Y_END - SUIT_Y  # 41px


def load_rank_templates(ranks_dir: str = "card_templates/ranks") -> Dict[str, np.ndarray]:
    """
    Carica template dei ranks (A, K, Q, ..., 2).
    
    Returns:
        Dict mapping rank symbol to normalized numpy array [0-1]
    """
    base_dir = Path(__file__).resolve().parent
    ranks_path = base_dir / ranks_dir
    
    if not ranks_path.exists():
        logger.warning(f"Ranks directory not found: {ranks_path}")
        return {}
    
    templates = {}
    rank_files = ranks_path.glob("*.png")
    
    for rank_file in rank_files:
        rank_symbol = rank_file.stem  # A, K, Q, ..., 2
        
        try:
            img = Image.open(rank_file)
            gray = ImageOps.grayscale(img)
            arr = np.array(gray, dtype=np.float32) / 255.0
            
            templates[rank_symbol] = arr
            
        except Exception as e:
            logger.error(f"Error loading rank template {rank_file.name}: {e}")
    
    logger.info(f"Loaded {len(templates)} rank templates")
    return templates


def load_suit_templates(suits_dir: str = "card_templates/suits") -> Dict[str, np.ndarray]:
    """
    Carica template dei suits (clubs, diamonds, hearts, spades).
    
    Returns:
        Dict mapping suit letter (c/d/h/s) to normalized numpy array [0-1]
    """
    base_dir = Path(__file__).resolve().parent
    suits_path = base_dir / suits_dir
    
    if not suits_path.exists():
        logger.warning(f"Suits directory not found: {suits_path}")
        return {}
    
    # Mapping nome file → lettera suit
    suit_map = {
        'clubs': 'c',
        'diamonds': 'd',
        'hearts': 'h',
        'spades': 's'
    }
    
    templates = {}
    
    for suit_name, suit_letter in suit_map.items():
        suit_file = suits_path / f"{suit_name}.png"
        
        if not suit_file.exists():
            continue
        
        try:
            img = Image.open(suit_file)
            gray = ImageOps.grayscale(img)
            arr = np.array(gray, dtype=np.float32) / 255.0
            
            templates[suit_letter] = arr
            
        except Exception as e:
            logger.error(f"Error loading suit template {suit_name}: {e}")
    
    logger.info(f"Loaded {len(templates)} suit templates")
    return templates


def calculate_mse(image1: np.ndarray, image2: np.ndarray) -> float:
    """
    Calcola Mean Squared Error tra due immagini normalizzate.
    """
    if image1.shape != image2.shape:
        return float('inf')
    
    return np.mean((image1 - image2) ** 2)


def extract_rank_region(card_image: Image.Image) -> Image.Image:
    """
    Estrae la regione del rank dalla carta (top-left, upper portion).
    """
    return card_image.crop((RANK_X, RANK_Y, RANK_X + RANK_WIDTH, RANK_Y + RANK_HEIGHT))


def extract_suit_region(card_image: Image.Image) -> Image.Image:
    """
    Estrae la regione del suit dalla carta (top-left, below rank).
    """
    return card_image.crop((SUIT_X, SUIT_Y, SUIT_X + SUIT_WIDTH, SUIT_Y + SUIT_HEIGHT))


def normalize_region(region_image: Image.Image) -> np.ndarray:
    """
    Normalizza una regione per il matching.
    Converte in grayscale e scala [0-1].
    """
    gray = ImageOps.grayscale(region_image)
    arr = np.array(gray, dtype=np.float32) / 255.0
    return arr


def recognize_card_ranksuit(
    card_image: Image.Image,
    rank_templates: Dict[str, np.ndarray],
    suit_templates: Dict[str, np.ndarray]
) -> Tuple[Optional[str], float]:
    """
    Riconosce una carta usando matching separato di rank e suit.
    
    UNIFIED PIPELINE: card_image passa da normalize_card_image() PRIMA di tutto.
    
    Args:
        card_image: PIL Image della carta completa (RAW, con verde o altro)
        rank_templates: Dict dei template rank
        suit_templates: Dict dei template suit
    
    Returns:
        Tuple (card_code, confidence):
        - card_code: "Ah", "7d", etc. oppure None se non riconosciuta
        - confidence: valore 0-1
    """
    if not rank_templates or not suit_templates:
        logger.warning("Templates not loaded")
        return None, 0.0
    
    try:
        # STEP 1: NORMALIZE with single source of truth
        # Same transformation used for template generation
        normalized_card = normalize_card_image(card_image)
        
        # Check for empty card position
        # Capo's info: carte hanno SFONDO BIANCO, tavolo verde NO white pixels
        # Use image WITHOUT autocontrast for accurate white detection
        card_no_contrast = normalize_card_image(card_image, use_autocontrast=False)
        card_arr = np.array(card_no_contrast, dtype=np.float32)
        
        # Count WHITE pixels (carta = sfondo bianco)
        # White = brightness > 200 (out of 255)
        white_pixels = np.sum(card_arr > 200)
        total_pixels = card_arr.size
        white_ratio = white_pixels / total_pixels
        
        # Real cards have >20% white pixels (sfondo bianco della carta)
        # Green table has <5% white pixels (solo riflessi/ombre)
        if white_ratio < 0.15:
            logger.debug(f"Empty position: white_ratio={white_ratio:.3f} (threshold: 0.15)")
            return None, 0.0
        
        # Extract regions from NORMALIZED card
        rank_region = extract_rank_region(normalized_card)
        suit_region = extract_suit_region(normalized_card)
        
        # Convert to arrays for matching
        rank_arr = normalize_region(rank_region)
        suit_arr = normalize_region(suit_region)
        
        # Rank matching
        best_rank = None
        best_rank_mse = float('inf')
        
        for rank_symbol, rank_template in rank_templates.items():
            mse = calculate_mse(rank_arr, rank_template)
            
            if mse < best_rank_mse:
                best_rank_mse = mse
                best_rank = rank_symbol
        
        # Suit matching
        best_suit = None
        best_suit_mse = float('inf')
        
        for suit_letter, suit_template in suit_templates.items():
            mse = calculate_mse(suit_arr, suit_template)
            
            if mse < best_suit_mse:
                best_suit_mse = mse
                best_suit = suit_letter
        
        # Check thresholds
        if best_rank_mse > RANK_MSE_THRESHOLD:
            logger.debug(f"Rank MSE too high: {best_rank_mse:.4f} > {RANK_MSE_THRESHOLD}")
            return None, 0.0
        
        if best_suit_mse > SUIT_MSE_THRESHOLD:
            logger.debug(f"Suit MSE too high: {best_suit_mse:.4f} > {SUIT_MSE_THRESHOLD}")
            return None, 0.0
        
        # Calculate confidences
        rank_conf = 1.0 - min(best_rank_mse, 1.0)
        suit_conf = 1.0 - min(best_suit_mse, 1.0)
        
        # Combined confidence
        combined_conf = 0.5 * rank_conf + 0.5 * suit_conf
        
        # Decision
        if combined_conf >= MIN_COMBINED_CONFIDENCE:
            card_code = f"{best_rank}{best_suit}"
            logger.debug(f"Recognized: {card_code} (rank_conf={rank_conf:.3f}, suit_conf={suit_conf:.3f}, combined={combined_conf:.3f})")
            return card_code, combined_conf
        else:
            logger.debug(f"Combined confidence too low: {combined_conf:.3f} < {MIN_COMBINED_CONFIDENCE}")
            return None, combined_conf
            
    except Exception as e:
        logger.error(f"Error recognizing card: {e}")
        return None, 0.0


def recognize_cards_ranksuit(
    card_images: List[Image.Image],
    rank_templates: Dict[str, np.ndarray],
    suit_templates: Dict[str, np.ndarray]
) -> List[Tuple[Optional[str], float]]:
    """
    Riconosce multiple carte.
    
    Returns:
        Lista di tuple (card_code, confidence)
    """
    results = []
    
    for card_image in card_images:
        card_code, confidence = recognize_card_ranksuit(card_image, rank_templates, suit_templates)
        results.append((card_code, confidence))
    
    return results


def filter_recognized_cards(recognition_results: List[Tuple[Optional[str], float]]) -> List[str]:
    """
    Filtra solo le carte riconosciute con successo.
    Rimuove duplicati mantenendo la prima occorrenza.
    """
    recognized = []
    seen_cards = set()
    
    for card_code, confidence in recognition_results:
        if card_code is not None:
            if card_code not in seen_cards:
                recognized.append(card_code)
                seen_cards.add(card_code)
            else:
                logger.warning(f"Duplicate card detected: {card_code} - keeping first occurrence")
    
    return recognized


def main():
    """Test del nuovo sistema rank+suit."""
    
    print("=" * 70)
    print("🃏 CARD RECOGNITION - RANK+SUIT SYSTEM TEST")
    print("=" * 70)
    print()
    
    # Load templates
    rank_templates = load_rank_templates()
    suit_templates = load_suit_templates()
    
    print(f"Rank templates: {sorted(rank_templates.keys())}")
    print(f"Suit templates: {sorted(suit_templates.keys())}")
    print()
    
    # Test su screenshot noti
    test_cases = [
        ("output_regions_flop_v2", "FLOP V2", ['6d', 'Ah', '2c']),
        ("output_regions_deck_1", "DECK 1", ['5c', 'Ah', '4h', 'Qc', '2c', 'As']),
    ]
    
    for region_dir, name, expected_cards in test_cases:
        region_path = Path(region_dir)
        if not region_path.exists():
            print(f"⏭️  Skipping {name} (directory not found)")
            continue
        
        print(f"📋 Testing: {name}")
        print(f"   Expected: {expected_cards}")
        print("-" * 70)
        
        # Test board cards
        board_images = []
        for i in range(1, 6):
            img_path = region_path / f"board_card_{i}.png"
            if img_path.exists():
                board_images.append(Image.open(img_path))
        
        if board_images:
            results = recognize_cards_ranksuit(board_images, rank_templates, suit_templates)
            recognized = filter_recognized_cards(results)
            
            print(f"   Recognized: {recognized}")
            
            # Check accuracy
            correct = sum(1 for card in recognized if card in expected_cards)
            print(f"   Accuracy: {correct}/{len(expected_cards)} correct")
        
        print()
    
    print("=" * 70)


if __name__ == "__main__":
    main()
