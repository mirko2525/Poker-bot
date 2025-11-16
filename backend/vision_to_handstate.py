#!/usr/bin/env python3
"""
Vision to HandState Integration Module - Fase 4

Integrazione completa: da screenshot PokerStars a HandState completo.
Collega tutti i moduli Fase 3 (regioni) + Fase 4 (riconoscimento) → oggetto HandState.

Ordini del Capo - Fase 4: Screenshot → HandState per EquityEngine & DecisionEngine.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import logging
from PIL import Image

# Import Phase 3 modules (table processing)
from table_layout import load_room_config, RoomConfig
from table_capture_static import load_table_image
from table_region_cutter import (
    cut_hero_cards, cut_board_cards, 
    cut_pot_region, cut_hero_stack_region
)

# Import Phase 4 modules (recognition)  
from card_templates import load_card_templates
from card_recognition import recognize_cards, filter_recognized_cards
from digit_templates import load_digit_templates
from number_recognition import recognize_number

# Import core logic (HandState)
from server import HandState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default file paths
DEFAULT_CONFIG_PATH = "rooms/pokerstars_6max.json"
DEFAULT_CARD_TEMPLATES_DIR = "card_templates/normalized"
DEFAULT_DIGIT_TEMPLATES_DIR = "digit_templates/normalized"


class VisionPokerEngine:
    """
    Main engine for converting poker screenshots to HandState objects.
    """
    
    def __init__(self, 
                 config_path: str = DEFAULT_CONFIG_PATH,
                 card_templates_dir: str = DEFAULT_CARD_TEMPLATES_DIR,
                 digit_templates_dir: str = DEFAULT_DIGIT_TEMPLATES_DIR):
        """
        Initialize the vision poker engine.
        
        Args:
            config_path: Path to room configuration JSON
            card_templates_dir: Directory with card templates
            digit_templates_dir: Directory with digit templates
        """
        self.config_path = config_path
        self.card_templates_dir = card_templates_dir
        self.digit_templates_dir = digit_templates_dir
        
        # Load configurations and templates
        self.room_config = None
        self.card_templates = {}
        self.digit_templates = {}
        
        self._load_configurations()
    
    def _load_configurations(self):
        """Load room config and templates."""
        try:
            # Load room configuration
            if Path(self.config_path).exists():
                self.room_config = load_room_config(self.config_path)
                logger.info(f"Loaded room config: {self.room_config.room_name}")
            else:
                logger.error(f"Room config not found: {self.config_path}")
            
            # Load card templates
            self.card_templates = load_card_templates(self.card_templates_dir)
            logger.info(f"Loaded {len(self.card_templates)} card templates")
            
            # Load digit templates
            self.digit_templates = load_digit_templates(self.digit_templates_dir)
            logger.info(f"Loaded {len(self.digit_templates)} digit templates")
            
        except Exception as e:
            logger.error(f"Error loading configurations: {e}")
    
    def extract_regions_from_screenshot(self, screenshot_path: str) -> Dict:
        """
        Extract all regions from a poker screenshot.
        
        Args:
            screenshot_path: Path to poker screenshot
            
        Returns:
            Dictionary with extracted region images
        """
        if not self.room_config:
            raise ValueError("Room configuration not loaded")
        
        try:
            # Load and crop table image
            table_image = load_table_image(screenshot_path, self.room_config)
            
            # Extract all regions
            regions = {}
            regions['hero_cards'] = cut_hero_cards(table_image, self.room_config)
            regions['board_cards'] = cut_board_cards(table_image, self.room_config)
            regions['pot_region'] = cut_pot_region(table_image, self.room_config)
            regions['hero_stack_region'] = cut_hero_stack_region(table_image, self.room_config)
            
            logger.info(f"Extracted regions from {Path(screenshot_path).name}")
            return regions
            
        except Exception as e:
            logger.error(f"Error extracting regions: {e}")
            return {}
    
    def recognize_cards_from_regions(self, card_images: List[Image.Image]) -> List[str]:
        """
        Recognize cards from card region images.
        
        Args:
            card_images: List of PIL Images containing cards
            
        Returns:
            List of recognized card codes
        """
        if not self.card_templates:
            logger.warning("No card templates loaded")
            return []
        
        try:
            # Recognize all cards
            recognition_results = recognize_cards(card_images, self.card_templates)
            
            # Filter out unrecognized cards
            recognized_cards = filter_recognized_cards(recognition_results)
            
            logger.debug(f"Recognized {len(recognized_cards)}/{len(card_images)} cards")
            return recognized_cards
            
        except Exception as e:
            logger.error(f"Error recognizing cards: {e}")
            return []
    
    def recognize_number_from_region(self, number_image: Image.Image) -> Optional[float]:
        """
        Recognize a number from a pot/stack region image.
        
        Args:
            number_image: PIL Image containing a number
            
        Returns:
            Recognized number as float or None
        """
        if not self.digit_templates:
            logger.warning("No digit templates loaded")
            return None
        
        try:
            parsed_number, raw_string, confidences = recognize_number(
                number_image, self.digit_templates
            )
            
            if parsed_number is not None:
                logger.debug(f"Recognized number: {parsed_number} (raw: '{raw_string}')")
            else:
                logger.debug(f"Could not parse number (raw: '{raw_string}')")
            
            return parsed_number
            
        except Exception as e:
            logger.error(f"Error recognizing number: {e}")
            return None
    
    def screenshot_to_handstate(self, screenshot_path: str, 
                              default_big_blind: float = 1.0,
                              default_players_in_hand: int = 2) -> Optional[HandState]:
        """
        Convert a poker screenshot directly to a HandState object.
        
        Args:
            screenshot_path: Path to poker screenshot
            default_big_blind: Default big blind value if not recognized
            default_players_in_hand: Default number of players if not detected
            
        Returns:
            HandState object or None if conversion fails
        """
        try:
            logger.info(f"Converting screenshot to HandState: {Path(screenshot_path).name}")
            
            # Step 1: Extract regions
            regions = self.extract_regions_from_screenshot(screenshot_path)
            
            if not regions:
                logger.error("Failed to extract regions from screenshot")
                return None
            
            # Step 2: Recognize hero cards
            hero_cards_recognized = []
            if 'hero_cards' in regions and regions['hero_cards']:
                hero_cards_recognized = self.recognize_cards_from_regions(regions['hero_cards'])
            
            # Step 3: Recognize board cards
            board_cards_recognized = []
            if 'board_cards' in regions and regions['board_cards']:
                board_cards_recognized = self.recognize_cards_from_regions(regions['board_cards'])
            
            # Step 4: Recognize pot amount
            pot_size = None
            if 'pot_region' in regions and regions['pot_region']:
                pot_size = self.recognize_number_from_region(regions['pot_region'])
            
            # Step 5: Recognize hero stack
            hero_stack = None
            if 'hero_stack_region' in regions and regions['hero_stack_region']:
                hero_stack = self.recognize_number_from_region(regions['hero_stack_region'])
            
            # Step 6: Determine hand phase based on board cards
            phase = self._determine_hand_phase(len(board_cards_recognized))
            
            # Step 7: Create HandState with available data
            handstate = self._create_handstate_from_recognized_data(
                hero_cards=hero_cards_recognized,
                board_cards=board_cards_recognized,
                pot_size=pot_size,
                hero_stack=hero_stack,
                phase=phase,
                default_big_blind=default_big_blind,
                default_players_in_hand=default_players_in_hand
            )
            
            if handstate:
                logger.info(f"Successfully created HandState: {phase} phase, {len(hero_cards_recognized)} hero cards, {len(board_cards_recognized)} board cards")
            else:
                logger.error("Failed to create HandState from recognized data")
            
            return handstate
            
        except Exception as e:
            logger.error(f"Error converting screenshot to HandState: {e}")
            return None
    
    def _determine_hand_phase(self, num_board_cards: int) -> str:
        """Determine hand phase based on number of board cards."""
        if num_board_cards == 0:
            return "PREFLOP"
        elif num_board_cards == 3:
            return "FLOP"
        elif num_board_cards == 4:
            return "TURN"
        elif num_board_cards == 5:
            return "RIVER"
        else:
            logger.warning(f"Unusual number of board cards: {num_board_cards}")
            return "UNKNOWN"
    
    def _create_handstate_from_recognized_data(self,
                                             hero_cards: List[str],
                                             board_cards: List[str], 
                                             pot_size: Optional[float],
                                             hero_stack: Optional[float],
                                             phase: str,
                                             default_big_blind: float,
                                             default_players_in_hand: int) -> Optional[HandState]:
        """
        Create HandState object from recognized data with sensible defaults.
        """
        try:
            # Use recognized values or reasonable defaults
            handstate_data = {
                "hero_cards": hero_cards if len(hero_cards) >= 2 else ["??", "??"],
                "board_cards": board_cards,
                "hero_stack": hero_stack if hero_stack is not None else 100.0,
                "pot_size": pot_size if pot_size is not None else 3.0,
                "to_call": 0.0,  # Default - would need more advanced detection
                "big_blind": default_big_blind,
                "players_in_hand": default_players_in_hand,
                "phase": phase
            }
            
            # Create and validate HandState
            handstate = HandState(**handstate_data)
            
            return handstate
            
        except Exception as e:
            logger.error(f"Error creating HandState: {e}")
            return None
    
    def get_engine_status(self) -> Dict:
        """Get status of the vision engine."""
        return {
            "room_config_loaded": self.room_config is not None,
            "room_name": self.room_config.room_name if self.room_config else None,
            "card_templates": len(self.card_templates),
            "digit_templates": len(self.digit_templates),
            "ready_for_cards": len(self.card_templates) > 0,
            "ready_for_numbers": len(self.digit_templates) > 0,
            "fully_ready": (
                self.room_config is not None and 
                len(self.card_templates) > 0 and 
                len(self.digit_templates) > 0
            )
        }


def test_vision_engine_on_screenshots():
    """Test the vision engine on available screenshots."""
    
    print("🎯 TESTING VISION ENGINE - SCREENSHOT TO HANDSTATE")
    print("=" * 60)
    
    # Initialize engine
    engine = VisionPokerEngine()
    
    # Check engine status
    status = engine.get_engine_status()
    print(f"Engine Status:")
    print(f"  Room config: {'✅' if status['room_config_loaded'] else '❌'}")
    print(f"  Card templates: {status['card_templates']}")
    print(f"  Digit templates: {status['digit_templates']}")
    print(f"  Fully ready: {'✅' if status['fully_ready'] else '❌'}")
    print()
    
    # Test on available screenshots
    screenshot_files = [
        "screenshots/pokerstars_preflop.png",
        "screenshots/pokerstars_flop.png",
        "screenshots/pokerstars_turn.png", 
        "screenshots/pokerstars_river.png"
    ]
    
    for screenshot_path in screenshot_files:
        if Path(screenshot_path).exists():
            print(f"🧪 Testing: {Path(screenshot_path).name}")
            
            try:
                handstate = engine.screenshot_to_handstate(screenshot_path)
                
                if handstate:
                    print(f"  ✅ HandState created:")
                    print(f"     Phase: {handstate.phase}")
                    print(f"     Hero cards: {handstate.hero_cards}")
                    print(f"     Board cards: {handstate.board_cards}")
                    print(f"     Pot: ${handstate.pot_size:.2f}")
                    print(f"     Hero stack: ${handstate.hero_stack:.2f}")
                    print(f"     Players: {handstate.players_in_hand}")
                else:
                    print(f"  ❌ Failed to create HandState")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
            
            print()
        else:
            print(f"⏩ Skipping {screenshot_path} (not found)")


def main():
    """Main function for testing vision to handstate conversion."""
    
    print("🔗 VISION TO HANDSTATE MODULE - FASE 4")
    print("=" * 50)
    
    # Test the complete pipeline
    test_vision_engine_on_screenshots()
    
    print("📋 Summary:")
    print("- Vision engine integrates Phase 3 (regions) + Phase 4 (recognition)")
    print("- screenshot_to_handstate() is the main entry point")  
    print("- HandState objects are ready for EquityEngine & DecisionEngine")
    print()
    print("🔧 Next steps:")
    print("1. Add more card templates for complete recognition")
    print("2. Add digit templates for pot/stack recognition")
    print("3. Integrate with existing demo for full pipeline testing")


if __name__ == "__main__":
    main()