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
from card_recognition_ranksuit import recognize_card_ranksuit, load_rank_templates, load_suit_templates

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
    
    # Room config PokerStars - COORDINATE OTTIMIZZATE per screenshot 130313
    room_config = {
        'zones': {
            'board_row': {
                'x': 1180,
                'y': 950, 
                'width': 500,
                'height': 150
            },
            'hero_row': {
                'x': 1200,
                'y': 1330,
                'width': 240,
                'height': 150
            }
        },
        'detection_params': {
            'max_board_cards': 4,
            'max_hero_cards': 2,
            'card_white_threshold': 0.15
        }
    }
    
    # FASE 1: DETECTION (Slot-Based)
    logger.info(f"\n{'─'*80}")
    logger.info(f"📍 FASE 1: DETECTION - BOARD CARDS (Slot-Based)")
    logger.info(f"{'─'*80}")
    
    board_cards = cut_board_cards_slot_based(screenshot, room_config)
    logger.info(f"\n✅ Board cards estratte: {len(board_cards)}")
    
    logger.info(f"\n{'─'*80}")
    logger.info(f"📍 FASE 1: DETECTION - HERO CARDS (Slot-Based)")
    logger.info(f"{'─'*80}")
    
    from card_detector_simple import cut_hero_cards_slot_based
    hero_cards = cut_hero_cards_slot_based(screenshot, room_config)
    logger.info(f"\n✅ Hero cards estratte: {len(hero_cards)}")
    
    # Combina tutte le carte per il test
    cards = board_cards + hero_cards
    logger.info(f"\n✅ TOTALE carte estratte dalla Fase 1: {len(cards)}")
    
    if len(cards) == 0:
        logger.error("❌ FASE 1 FALLITA: Nessuna carta trovata!")
        return
    
    # Load templates per recognition
    logger.info("\n📚 Caricamento template...")
    rank_templates = load_rank_templates()
    suit_templates = load_suit_templates()
    logger.info(f"   ✅ {len(rank_templates)} rank templates")
    logger.info(f"   ✅ {len(suit_templates)} suit templates")
    
    # FASE 2: RECOGNITION (Rank+Suit Matching)
    logger.info(f"\n{'─'*80}")
    logger.info(f"🔍 FASE 2: RECOGNITION (Rank+Suit Matching)")
    logger.info(f"{'─'*80}\n")
    
    # Salva carte estratte per debug
    debug_dir = Path("/app/backend/debug_extracted")
    debug_dir.mkdir(exist_ok=True)
    for i, card_img in enumerate(cards):
        card_img.save(debug_dir / f"card_{i+1}.png")
    logger.info(f"💾 Carte estratte salvate in: {debug_dir}/\n")
    
    recognized_cards = []
    for i, card_img in enumerate(cards):
        logger.info(f"\n🃏 Carta {i+1}/{len(cards)}:")
        
        result = recognize_card_ranksuit(card_img, rank_templates, suit_templates)
        
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
    logger.info(f"Carte estratte (Fase 1):    {len(cards)} ({len(board_cards)} board + {len(hero_cards)} hero)")
    logger.info(f"Carte riconosciute (Fase 2): {len(recognized_cards)}")
    logger.info(f"Success rate:                {len(recognized_cards)}/{len(cards)} = {len(recognized_cards)/len(cards)*100:.1f}%")
    
    if recognized_cards:
        logger.info(f"\n🎴 Board Cards (attese: 7♣, 3♠, 9♥, Q♠, 10♣):")
        for i, (card_str, conf) in enumerate(recognized_cards[:len(board_cards)]):
            logger.info(f"   {i+1}. {card_str} ({conf:.1%})")
        
        if len(recognized_cards) > len(board_cards):
            logger.info(f"\n🃏 Hero Cards (attese: 3♦, 4♥):")
            for i, (card_str, conf) in enumerate(recognized_cards[len(board_cards):]):
                logger.info(f"   {i+1}. {card_str} ({conf:.1%})")
    
    logger.info(f"\n{'='*80}\n")
    
    # Verifica attesa: 5 board + 2 hero = 7 carte totali
    if len(recognized_cards) >= 5:
        logger.info("✅ TEST PASSED: Almeno 5 carte riconosciute!")
        return True
    else:
        logger.error("❌ TEST FAILED: Meno di 5 carte riconosciute")
        return False


if __name__ == "__main__":
    # Screenshot fornito dall'utente
    screenshot_path = "/app/Screenshot 2025-11-16 130313.png"
    
    if not Path(screenshot_path).exists():
        logger.error(f"❌ Screenshot non trovato: {screenshot_path}")
        sys.exit(1)
    
    success = test_screenshot_recognition(screenshot_path)
    sys.exit(0 if success else 1)
