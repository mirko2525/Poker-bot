#!/usr/bin/env python3
"""
Test script per verificare il fix dell'empty check
Testa il riconoscimento carte con lo screenshot fornito dall'utente
"""

import sys
from pathlib import Path
from PIL import Image
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import moduli del bot
from card_detector_simple import cut_board_cards_slot_based
from card_recognition_ranksuit import recognize_card_rank_suit

def test_screenshot_recognition(screenshot_path: str):
    """
    Test completo: Detection + Recognition
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"🎯 TEST RICONOSCIMENTO CARTE - FIX EMPTY CHECK")
    logger.info(f"{'='*80}\n")
    
    # Load screenshot
    screenshot = Image.open(screenshot_path)
    logger.info(f"✅ Screenshot caricato: {screenshot.size}")
    
    # Room config PokerStars (Dresda III)
    room_config = {
        'board_zone': {
            'x': 985,
            'y': 793, 
            'w': 1084,
            'h': 380
        }
    }
    
    # FASE 1: DETECTION (Slot-Based)
    logger.info(f"\n{'─'*80}")
    logger.info(f"📍 FASE 1: DETECTION (Slot-Based)")
    logger.info(f"{'─'*80}")
    
    cards = cut_board_cards_slot_based(screenshot, room_config)
    logger.info(f"\n✅ Carte estratte dalla Fase 1: {len(cards)}")
    
    if len(cards) == 0:
        logger.error("❌ FASE 1 FALLITA: Nessuna carta trovata!")
        return
    
    # FASE 2: RECOGNITION (Rank+Suit Matching)
    logger.info(f"\n{'─'*80}")
    logger.info(f"🔍 FASE 2: RECOGNITION (Rank+Suit Matching)")
    logger.info(f"{'─'*80}\n")
    
    recognized_cards = []
    for i, card_img in enumerate(cards):
        logger.info(f"\n🃏 Carta {i+1}/{len(cards)}:")
        
        result = recognize_card_rank_suit(card_img)
        
        if result:
            card_str, confidence = result
            logger.info(f"   ✅ RICONOSCIUTA: {card_str} (confidence: {confidence:.1%})")
            recognized_cards.append((card_str, confidence))
        else:
            logger.warning(f"   ❌ NON RICONOSCIUTA (Empty o confidence bassa)")
    
    # SUMMARY
    logger.info(f"\n{'='*80}")
    logger.info(f"📊 SUMMARY FINALE")
    logger.info(f"{'='*80}")
    logger.info(f"Carte estratte (Fase 1):    {len(cards)}")
    logger.info(f"Carte riconosciute (Fase 2): {len(recognized_cards)}")
    logger.info(f"Success rate:                {len(recognized_cards)}/{len(cards)} = {len(recognized_cards)/len(cards)*100:.1f}%")
    
    if recognized_cards:
        logger.info(f"\n🎴 Carte board riconosciute:")
        for card_str, conf in recognized_cards:
            logger.info(f"   • {card_str} ({conf:.1%})")
    
    logger.info(f"\n{'='*80}\n")
    
    # Verifica attesa: 3 carte board (7♦, A♠, 9♠)
    if len(recognized_cards) >= 3:
        logger.info("✅ TEST PASSED: Almeno 3 carte riconosciute!")
        return True
    else:
        logger.error("❌ TEST FAILED: Meno di 3 carte riconosciute")
        return False


if __name__ == "__main__":
    # Screenshot fornito dall'utente
    screenshot_path = "/app/Screenshot 2025-11-16 150959.png"
    
    if not Path(screenshot_path).exists():
        logger.error(f"❌ Screenshot non trovato: {screenshot_path}")
        sys.exit(1)
    
    success = test_screenshot_recognition(screenshot_path)
    sys.exit(0 if success else 1)
