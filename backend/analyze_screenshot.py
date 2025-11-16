#!/usr/bin/env python3
"""
Analyze Screenshot Script - Fase 3

Test script per verificare che il cropping funzioni correttamente.
Carica configurazione room, screenshot, e salva tutte le regioni estratte.

Ordini del Capo - Fase 3: Manually launch to verify cropping works correctly.
"""

import sys
import logging
from pathlib import Path

# Import our table processing modules
from table_layout import load_room_config, validate_coordinates
from table_capture_static import load_table_image, get_image_info
from table_region_cutter import (
    cut_hero_cards, cut_board_cards, 
    cut_pot_region, cut_hero_stack_region, 
    save_regions
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def analyze_screenshot(config_path: str, screenshot_path: str, output_dir: str = "output_regions") -> bool:
    """
    Analyze a poker table screenshot and extract all regions.
    
    Args:
        config_path: Path to the room configuration JSON
        screenshot_path: Path to the screenshot image
        output_dir: Directory to save extracted regions
        
    Returns:
        True if successful, False otherwise
    """
    
    print("="*60)
    print("POKER TABLE SCREENSHOT ANALYZER - FASE 3")
    print("="*60)
    print()
    
    try:
        # 1. Load room configuration
        print(f"📁 Loading room configuration: {config_path}")
        room_config = load_room_config(config_path)
        print(f"✅ Loaded config for: {room_config.room_name}")
        print(f"   Table region: {room_config.table_region}")
        print(f"   Hero cards: {len(room_config.hero_cards)} regions")
        print(f"   Board cards: {len(room_config.board_cards)} regions")
        print()
        
        # 2. Get screenshot information
        print(f"📷 Analyzing screenshot: {screenshot_path}")
        image_info = get_image_info(screenshot_path)
        if image_info:
            print(f"   Dimensions: {image_info['width']}x{image_info['height']}")
            print(f"   Format: {image_info['format']}")
            print(f"   Size: {image_info['size_bytes']:,} bytes")
        else:
            print("   ❌ Could not read image information")
            return False
        print()
        
        # 3. Validate coordinates
        print("🔍 Validating coordinates against image bounds...")
        warnings = validate_coordinates(room_config, image_info['width'], image_info['height'])
        if warnings:
            print("⚠️  Coordinate validation warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        else:
            print("✅ All coordinates are within image bounds")
        print()
        
        # 4. Load and crop table image
        print("✂️  Loading and cropping table region...")
        table_image = load_table_image(screenshot_path, room_config)
        print(f"✅ Table image loaded: {table_image.width}x{table_image.height}")
        print()
        
        # 5. Extract all regions
        print("🃏 Extracting card and region areas...")
        
        # Hero cards
        print("   Cutting hero cards...")
        hero_cards = cut_hero_cards(table_image, room_config)
        print(f"   ✅ Extracted {len(hero_cards)} hero cards")
        
        # Board cards  
        print("   Cutting board cards...")
        board_cards = cut_board_cards(table_image, room_config)
        print(f"   ✅ Extracted {len(board_cards)} board cards")
        
        # Pot region
        print("   Cutting pot region...")
        pot_image = cut_pot_region(table_image, room_config)
        print(f"   ✅ Extracted pot region: {pot_image.width}x{pot_image.height}")
        
        # Hero stack region
        print("   Cutting hero stack region...")
        stack_image = cut_hero_stack_region(table_image, room_config)
        print(f"   ✅ Extracted hero stack region: {stack_image.width}x{stack_image.height}")
        print()
        
        # 6. Save all regions
        print(f"💾 Saving all regions to: {output_dir}")
        save_regions(hero_cards, board_cards, pot_image, stack_image, output_dir)
        
        # 7. Summary
        print()
        print("="*60)
        print("ANALYSIS COMPLETE - SUMMARY")
        print("="*60)
        print(f"✅ Room config loaded: {room_config.room_name}")
        print(f"✅ Screenshot processed: {Path(screenshot_path).name}")
        print(f"✅ Table region cropped: {table_image.width}x{table_image.height}")
        print(f"✅ Hero cards extracted: {len(hero_cards)}")
        print(f"✅ Board cards extracted: {len(board_cards)}")
        print(f"✅ Pot region extracted: {pot_image.width}x{pot_image.height}")
        print(f"✅ Stack region extracted: {stack_image.width}x{stack_image.height}")
        print(f"✅ All regions saved to: {Path(output_dir).absolute()}")
        
        if warnings:
            print()
            print(f"⚠️  Note: {len(warnings)} coordinate warnings detected")
            print("   Consider adjusting coordinates in the JSON config for better precision")
        
        print()
        print("🎉 FASE 3 - TABLE INPUT LAYER: SUCCESS!")
        return True
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        logger.error(f"Analysis failed: {e}", exc_info=True)
        return False


def main():
    """Main function to run the screenshot analyzer."""
    
    # Default paths
    config_path = "rooms/pokerstars_6max.json"
    screenshot_dir = Path("screenshots")
    output_dir = "output_regions"
    
    # Check if config exists
    if not Path(config_path).exists():
        print(f"❌ Configuration file not found: {config_path}")
        print("   Please ensure pokerstars_6max.json exists in the rooms/ directory")
        return False
    
    # Look for screenshots
    screenshot_files = list(screenshot_dir.glob("*.png")) + list(screenshot_dir.glob("*.jpg"))
    
    if not screenshot_files:
        print(f"❌ No screenshot files found in: {screenshot_dir}")
        print("   Please add at least one PNG or JPG screenshot to the screenshots/ directory")
        return False
    
    # Use the first screenshot found
    screenshot_path = str(screenshot_files[0])
    
    print(f"Using screenshot: {screenshot_path}")
    print(f"Using config: {config_path}")
    print(f"Output directory: {output_dir}")
    print()
    
    # Run the analysis
    success = analyze_screenshot(config_path, screenshot_path, output_dir)
    
    if success:
        print("\n✅ Analysis completed successfully!")
        print(f"Check {output_dir}/ for extracted region images")
        return True
    else:
        print("\n❌ Analysis failed. Check the logs above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)