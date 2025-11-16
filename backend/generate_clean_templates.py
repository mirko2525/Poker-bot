#!/usr/bin/env python3
"""
TEMPLATE GENERATOR - ORDINE CAPO FASE 6.2
==========================================

Rigenera template rank/suit SERI da screenshot ufficiali PokerStars.

Pipeline UNICA:
1. Usa board_detector_geometric per estrarre carte
2. Passa ogni carta per normalize_card_for_template() 
3. Salva in card_templates/ranks e card_templates/suits

NO più template strani o generati a caso.
Ogni template deve provenire da VERE carte PokerStars estratte con geometria corretta.
"""

from PIL import Image
from pathlib import Path
import logging

from board_detector_geometric import detect_board_cards_geometric
from card_normalization import normalize_card_for_template

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CARTE CONOSCIUTE negli screenshot ufficiali
# ============================================================================
# Questi sono gli screenshot "puliti" con carte note

KNOWN_CARDS = {
    "pokerstars_flop.png": {
        "phase": "FLOP",
        "cards": ["Ah", "6d", "2c"]  # slot 1, 2, 3 - ORDINE CORRETTO DA SINISTRA A DESTRA
    },
    # NOTE: Altri screenshot da identificare manualmente
    # "pokerstars_turn.png": {...},
    # "pokerstars_river.png": {...},
}

# Mapping rank symbol → filename
RANK_SYMBOLS = {
    '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
    'T': 'T', 'J': 'J', 'Q': 'Q', 'K': 'K', 'A': 'A'
}

# Mapping suit symbol → filename
SUIT_SYMBOLS = {
    'c': 'clubs',
    'd': 'diamonds',
    'h': 'hearts',
    's': 'spades'
}


def extract_rank_region(card_normalized: Image.Image) -> Image.Image:
    """
    Estrae region del rank dalla carta normalizzata.
    Top-left corner: 0-35% width, 0-25% height
    """
    w, h = card_normalized.size
    rank_w = int(w * 0.35)
    rank_h = int(h * 0.25)
    return card_normalized.crop((0, 0, rank_w, rank_h))


def extract_suit_region(card_normalized: Image.Image) -> Image.Image:
    """
    Estrae region del suit dalla carta normalizzata.
    Below rank: 0-35% width, 10-45% height
    """
    w, h = card_normalized.size
    suit_w = int(w * 0.35)
    suit_y_start = int(h * 0.10)
    suit_y_end = int(h * 0.45)
    return card_normalized.crop((0, suit_y_start, suit_w, suit_y_end))


def generate_templates_from_screenshots():
    """
    Pipeline completa: genera template da screenshot ufficiali.
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"🎯 TEMPLATE GENERATION - ORDINE CAPO FASE 6.2")
    logger.info(f"{'='*80}\n")
    
    screenshots_dir = Path(__file__).parent / "screenshots"
    templates_dir = Path(__file__).parent / "card_templates"
    
    # Crea directories
    ranks_dir = templates_dir / "ranks"
    suits_dir = templates_dir / "suits"
    ranks_dir.mkdir(parents=True, exist_ok=True)
    suits_dir.mkdir(parents=True, exist_ok=True)
    
    # Raccogli tutti i template
    rank_templates = {}  # rank_symbol → list of normalized images
    suit_templates = {}  # suit_name → list of normalized images
    
    # Process each screenshot
    for screenshot_name, config in KNOWN_CARDS.items():
        screenshot_path = screenshots_dir / screenshot_name
        
        if not screenshot_path.exists():
            logger.warning(f"⚠️ Screenshot not found: {screenshot_path}")
            continue
        
        logger.info(f"\n{'─'*80}")
        logger.info(f"📸 Processing: {screenshot_name}")
        logger.info(f"{'─'*80}")
        
        # Load screenshot
        screenshot = Image.open(screenshot_path)
        phase = config["phase"]
        known_cards = config["cards"]
        
        # Extract cards using geometric detection
        logger.info(f"Phase: {phase}")
        cards_extracted = detect_board_cards_geometric(screenshot, phase)
        
        if len(cards_extracted) != len(known_cards):
            logger.error(f"❌ Mismatch: extracted {len(cards_extracted)}, expected {len(known_cards)}")
            continue
        
        # Process each card
        for i, (card_img, card_name) in enumerate(zip(cards_extracted, known_cards)):
            rank_symbol = card_name[0].upper()
            suit_symbol = card_name[1].lower()
            
            logger.info(f"\nCard {i+1}: {card_name}")
            
            # PIPELINE UNICA: normalize
            card_normalized = normalize_card_for_template(card_img)
            logger.info(f"  ✅ Normalized: {card_normalized.size} mode={card_normalized.mode}")
            
            # Extract regions
            rank_region = extract_rank_region(card_normalized)
            suit_region = extract_suit_region(card_normalized)
            
            logger.info(f"  ✅ Rank region: {rank_region.size}")
            logger.info(f"  ✅ Suit region: {suit_region.size}")
            
            # Store
            if rank_symbol not in rank_templates:
                rank_templates[rank_symbol] = []
            rank_templates[rank_symbol].append(rank_region)
            
            suit_name = SUIT_SYMBOLS[suit_symbol]
            if suit_name not in suit_templates:
                suit_templates[suit_name] = []
            suit_templates[suit_name].append(suit_region)
    
    # Save templates (prendi il primo campione per ogni rank/suit)
    logger.info(f"\n{'='*80}")
    logger.info(f"💾 SAVING TEMPLATES")
    logger.info(f"{'='*80}\n")
    
    logger.info("RANK TEMPLATES:")
    for rank_symbol, samples in sorted(rank_templates.items()):
        # Prendi il primo campione (o fai media se vuoi)
        template = samples[0]
        output_path = ranks_dir / f"{rank_symbol}.png"
        template.save(output_path)
        logger.info(f"  ✅ {rank_symbol:2s} → {output_path.name} ({len(samples)} samples)")
    
    logger.info("\nSUIT TEMPLATES:")
    for suit_name, samples in sorted(suit_templates.items()):
        # Prendi il primo campione
        template = samples[0]
        output_path = suits_dir / f"{suit_name}.png"
        template.save(output_path)
        logger.info(f"  ✅ {suit_name:8s} → {output_path.name} ({len(samples)} samples)")
    
    logger.info(f"\n{'='*80}")
    logger.info(f"✅ TEMPLATE GENERATION COMPLETE")
    logger.info(f"{'='*80}")
    logger.info(f"Rank templates: {len(rank_templates)}")
    logger.info(f"Suit templates: {len(suit_templates)}")
    logger.info(f"\nTemplates saved in:")
    logger.info(f"  {ranks_dir}")
    logger.info(f"  {suits_dir}")
    logger.info(f"{'='*80}\n")


if __name__ == "__main__":
    generate_templates_from_screenshots()
