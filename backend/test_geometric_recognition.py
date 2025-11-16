#!/usr/bin/env python3
"""
TEST END-TO-END: Geometric Detection + Rank/Suit Recognition
=============================================================

Test completo del nuovo sistema:
1. Detection geometrica → estrae carte dalle posizioni calcolate
2. Recognition rank+suit → riconosce carte estratte

Usa screenshot ufficiali PokerStars con carte note.
"""

from PIL import Image
from pathlib import Path
import logging

from board_detector_geometric import detect_board_cards_geometric, visualize_board_detection
from card_recognition_ranksuit import recognize_card_ranksuit, load_rank_templates, load_suit_templates

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carte attese per ogni screenshot ufficiale
EXPECTED_CARDS = {
    "pokerstars_flop.png": {
        "phase": "FLOP",
        "board": ["?", "?", "?"],  # Da identificare manualmente
    },
    "pokerstars_flop_v2.png": {
        "phase": "FLOP",
        "board": ["?", "?", "?"],
    },
    "pokerstars_turn.png": {
        "phase": "TURN",
        "board": ["?", "?", "?", "?"],
    },
    "pokerstars_river.png": {
        "phase": "RIVER",
        "board": ["?", "?", "?", "?", "?"],
    },
}


def test_screenshot(screenshot_path: Path, phase: str, expected_cards: list = None):
    """
    Test completo su uno screenshot.
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"📸 TEST: {screenshot_path.name}")
    logger.info(f"{'='*80}")
    
    # Load screenshot
    screenshot = Image.open(screenshot_path)
    logger.info(f"Screenshot size: {screenshot.size}")
    
    # FASE 1: GEOMETRIC DETECTION
    logger.info(f"\n{'─'*80}")
    logger.info(f"📍 FASE 1: GEOMETRIC DETECTION ({phase})")
    logger.info(f"{'─'*80}")
    
    cards = detect_board_cards_geometric(screenshot, phase)
    logger.info(f"✅ Cards extracted: {len(cards)}")
    
    # Salva visualizzazione
    vis_output = f"/tmp/vis_{screenshot_path.stem}.png"
    visualize_board_detection(screenshot, phase, vis_output)
    
    # Salva carte estratte
    cards_dir = Path(f"/tmp/cards_{screenshot_path.stem}")
    cards_dir.mkdir(exist_ok=True)
    
    for i, card in enumerate(cards):
        card.save(cards_dir / f"card_{i+1}.png")
    
    logger.info(f"💾 Cards saved in: {cards_dir}")
    
    # FASE 2: RANK+SUIT RECOGNITION
    logger.info(f"\n{'─'*80}")
    logger.info(f"🔍 FASE 2: RANK+SUIT RECOGNITION")
    logger.info(f"{'─'*80}")
    
    # Load templates
    rank_templates = load_rank_templates()
    suit_templates = load_suit_templates()
    logger.info(f"Templates loaded: {len(rank_templates)} ranks, {len(suit_templates)} suits")
    
    # Recognize each card
    recognized_cards = []
    for i, card_img in enumerate(cards):
        logger.info(f"\n🃏 Card {i+1}/{len(cards)}:")
        
        result = recognize_card_ranksuit(card_img, rank_templates, suit_templates)
        
        if result:
            card_str, confidence = result
            logger.info(f"   ✅ RECOGNIZED: {card_str} ({confidence:.1%})")
            recognized_cards.append((card_str, confidence))
        else:
            logger.info(f"   ❌ NOT RECOGNIZED")
            recognized_cards.append((None, 0.0))
    
    # SUMMARY
    logger.info(f"\n{'='*80}")
    logger.info(f"📊 SUMMARY: {screenshot_path.name}")
    logger.info(f"{'='*80}")
    logger.info(f"Phase: {phase}")
    logger.info(f"Cards extracted: {len(cards)}")
    logger.info(f"Cards recognized: {sum(1 for c, _ in recognized_cards if c is not None)}/{len(cards)}")
    logger.info(f"Success rate: {sum(1 for c, _ in recognized_cards if c is not None)/len(cards)*100:.1f}%")
    
    if expected_cards and expected_cards[0] != "?":
        matches = sum(1 for i, (card, _) in enumerate(recognized_cards) if card == expected_cards[i])
        logger.info(f"Accuracy: {matches}/{len(expected_cards)} ({matches/len(expected_cards)*100:.1f}%)")
    
    logger.info(f"\n🎴 Recognized cards:")
    for i, (card, conf) in enumerate(recognized_cards):
        status = "✅" if card else "❌"
        expected_str = f" (expected: {expected_cards[i]})" if expected_cards and expected_cards[i] != "?" else ""
        logger.info(f"   {status} Card {i+1}: {card or 'None'} ({conf:.1%}){expected_str}")
    
    logger.info(f"{'='*80}\n")
    
    return recognized_cards


def main():
    """
    Test tutti gli screenshot ufficiali.
    """
    screenshots_dir = Path(__file__).parent / "screenshots"
    
    logger.info(f"\n{'#'*80}")
    logger.info(f"# GEOMETRIC DETECTION + RECOGNITION - FULL TEST")
    logger.info(f"{'#'*80}\n")
    
    all_results = {}
    
    for screenshot_name, test_config in EXPECTED_CARDS.items():
        screenshot_path = screenshots_dir / screenshot_name
        
        if not screenshot_path.exists():
            logger.warning(f"⚠️ Screenshot not found: {screenshot_path}")
            continue
        
        phase = test_config["phase"]
        expected = test_config["board"]
        
        results = test_screenshot(screenshot_path, phase, expected)
        all_results[screenshot_name] = results
    
    # FINAL SUMMARY
    logger.info(f"\n{'#'*80}")
    logger.info(f"# FINAL SUMMARY - ALL SCREENSHOTS")
    logger.info(f"{'#'*80}\n")
    
    total_cards = 0
    total_recognized = 0
    
    for screenshot_name, results in all_results.items():
        recognized_count = sum(1 for c, _ in results if c is not None)
        total_cards += len(results)
        total_recognized += recognized_count
        
        logger.info(f"{screenshot_name:30s} → {recognized_count}/{len(results)} recognized")
    
    logger.info(f"\n{'─'*80}")
    logger.info(f"TOTAL: {total_recognized}/{total_cards} cards recognized ({total_recognized/total_cards*100:.1f}%)")
    logger.info(f"{'─'*80}\n")
    
    if total_recognized == total_cards:
        logger.info("🎉 PERFECT SCORE! All cards recognized!")
    elif total_recognized >= total_cards * 0.8:
        logger.info("✅ GOOD: >80% recognition rate")
    else:
        logger.warning("⚠️ NEEDS IMPROVEMENT: <80% recognition rate")


if __name__ == "__main__":
    main()
