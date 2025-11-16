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
        print(f"   ✅ Extracted hero stack region: {stack_image.width}x{stack_image.height}")\n        print()\n        \n        # 6. Save all regions\n        print(f\"💾 Saving all regions to: {output_dir}\")\n        save_regions(hero_cards, board_cards, pot_image, stack_image, output_dir)\n        \n        # 7. Summary\n        print()\n        print(\"=\"*60)\n        print(\"ANALYSIS COMPLETE - SUMMARY\")\n        print(\"=\"*60)\n        print(f\"✅ Room config loaded: {room_config.room_name}\")\n        print(f\"✅ Screenshot processed: {Path(screenshot_path).name}\")\n        print(f\"✅ Table region cropped: {table_image.width}x{table_image.height}\")\n        print(f\"✅ Hero cards extracted: {len(hero_cards)}\")\n        print(f\"✅ Board cards extracted: {len(board_cards)}\")\n        print(f\"✅ Pot region extracted: {pot_image.width}x{pot_image.height}\")\n        print(f\"✅ Stack region extracted: {stack_image.width}x{stack_image.height}\")\n        print(f\"✅ All regions saved to: {Path(output_dir).absolute()}\")\n        \n        if warnings:\n            print()\n            print(f\"⚠️  Note: {len(warnings)} coordinate warnings detected\")\n            print(\"   Consider adjusting coordinates in the JSON config for better precision\")\n        \n        print()\n        print(\"🎉 FASE 3 - TABLE INPUT LAYER: SUCCESS!\")\n        return True\n        \n    except Exception as e:\n        print(f\"❌ Error during analysis: {e}\")\n        logger.error(f\"Analysis failed: {e}\", exc_info=True)\n        return False\n\n\ndef main():\n    \"\"\"Main function to run the screenshot analyzer.\"\"\"\n    \n    # Default paths\n    config_path = \"rooms/pokerstars_6max.json\"\n    screenshot_dir = Path(\"screenshots\")\n    output_dir = \"output_regions\"\n    \n    # Check if config exists\n    if not Path(config_path).exists():\n        print(f\"❌ Configuration file not found: {config_path}\")\n        print(\"   Please ensure pokerstars_6max.json exists in the rooms/ directory\")\n        return False\n    \n    # Look for screenshots\n    screenshot_files = list(screenshot_dir.glob(\"*.png\")) + list(screenshot_dir.glob(\"*.jpg\"))\n    \n    if not screenshot_files:\n        print(f\"❌ No screenshot files found in: {screenshot_dir}\")\n        print(\"   Please add at least one PNG or JPG screenshot to the screenshots/ directory\")\n        return False\n    \n    # Use the first screenshot found\n    screenshot_path = str(screenshot_files[0])\n    \n    print(f\"Using screenshot: {screenshot_path}\")\n    print(f\"Using config: {config_path}\")\n    print(f\"Output directory: {output_dir}\")\n    print()\n    \n    # Run the analysis\n    success = analyze_screenshot(config_path, screenshot_path, output_dir)\n    \n    if success:\n        print(\"\\n✅ Analysis completed successfully!\")\n        print(f\"Check {output_dir}/ for extracted region images\")\n        return True\n    else:\n        print(\"\\n❌ Analysis failed. Check the logs above for details.\")\n        return False\n\n\nif __name__ == \"__main__\":\n    success = main()\n    sys.exit(0 if success else 1)\n"