#!/usr/bin/env python3
"""
Test Completamento Fase 3 - Verificatore Criteri

Verifica che tutti i 6 criteri di completamento della Fase 3 siano soddisfatti
secondo le specifiche degli "Ordini del Capo".
"""

import json
from pathlib import Path
import sys

def test_fase3_completion():
    """
    Verifica i 6 criteri di completamento per la Fase 3.
    
    Returns:
        bool: True se tutti i criteri sono soddisfatti
    """
    
    print("=" * 70)
    print("TEST COMPLETAMENTO FASE 3 - TABLE INPUT LAYER")
    print("=" * 70)
    print()
    
    criteria_passed = 0
    total_criteria = 6
    
    # 1. A functional JSON file describing the table layout exists
    print("1️⃣  JSON Layout Configuration...")
    json_path = Path("rooms/pokerstars_6max.json")
    if json_path.exists():
        try:
            with open(json_path) as f:
                config = json.load(f)
            
            required_fields = ['table_region', 'hero_cards', 'board_cards', 'hero_stack', 'pot']
            missing_fields = [field for field in required_fields if field not in config]
            
            if not missing_fields:
                print(f"   ✅ JSON config exists and is valid: {json_path}")
                print(f"      - Room: {config.get('room_name', 'N/A')}")
                print(f"      - Hero cards: {len(config['hero_cards'])} regions")
                print(f"      - Board cards: {len(config['board_cards'])} regions")
                criteria_passed += 1
            else:
                print(f"   ❌ JSON config missing fields: {missing_fields}")
        except Exception as e:
            print(f"   ❌ JSON config invalid: {e}")
    else:
        print(f"   ❌ JSON config not found: {json_path}")
    print()
    
    # 2. A Python module (table_layout.py) can load this configuration
    print("2️⃣  Python Configuration Loader...")
    layout_module = Path("table_layout.py")
    if layout_module.exists():
        try:
            from table_layout import load_room_config, RoomConfig
            room_config = load_room_config("rooms/pokerstars_6max.json")
            
            if isinstance(room_config, RoomConfig):
                print(f"   ✅ table_layout.py can load configuration successfully")
                print(f"      - Loaded room: {room_config.room_name}")
                print(f"      - Table region: {room_config.table_region}")
                criteria_passed += 1
            else:
                print(f"   ❌ Invalid RoomConfig object returned")
        except Exception as e:
            print(f"   ❌ Error loading configuration: {e}")
    else:
        print(f"   ❌ table_layout.py module not found")
    print()
    
    # 3. At least one real screenshot is available for testing
    print("3️⃣  Screenshot Availability...")
    screenshot_dir = Path("screenshots")
    if screenshot_dir.exists():
        screenshots = list(screenshot_dir.glob("*.png")) + list(screenshot_dir.glob("*.jpg"))
        if screenshots:
            print(f"   ✅ Screenshots available for testing:")
            for screenshot in screenshots:
                size_mb = screenshot.stat().st_size / (1024 * 1024)
                print(f"      - {screenshot.name} ({size_mb:.2f} MB)")
            criteria_passed += 1
        else:
            print(f"   ❌ No PNG or JPG files found in {screenshot_dir}")
    else:
        print(f"   ❌ Screenshots directory not found: {screenshot_dir}")
    print()
    
    # 4. A module (table_capture_static.py) can crop the table from a screenshot
    print("4️⃣  Static Screenshot Handler...")
    capture_module = Path("table_capture_static.py")
    if capture_module.exists():
        try:
            from table_capture_static import load_table_image
            from table_layout import load_room_config
            
            # Test with available screenshot
            screenshots = list(Path("screenshots").glob("*.png")) + list(Path("screenshots").glob("*.jpg"))
            if screenshots:
                room_config = load_room_config("rooms/pokerstars_6max.json")
                table_image = load_table_image(str(screenshots[0]), room_config)
                
                print(f"   ✅ table_capture_static.py can crop table regions")
                print(f"      - Source: {screenshots[0].name}")
                print(f"      - Cropped table: {table_image.width}x{table_image.height}")
                criteria_passed += 1
            else:
                print(f"   ❌ No screenshots available for testing")
        except Exception as e:
            print(f"   ❌ Error in table capture: {e}")
    else:
        print(f"   ❌ table_capture_static.py module not found")
    print()
    
    # 5. A module (table_region_cutter.py) can crop specific regions
    print("5️⃣  Region Cutter Module...")
    cutter_module = Path("table_region_cutter.py")
    if cutter_module.exists():
        try:
            from table_region_cutter import (
                cut_hero_cards, cut_board_cards, 
                cut_pot_region, cut_hero_stack_region
            )
            from table_capture_static import load_table_image
            from table_layout import load_room_config
            
            # Test region cutting
            screenshots = list(Path("screenshots").glob("*.png")) + list(Path("screenshots").glob("*.jpg"))
            if screenshots:
                room_config = load_room_config("rooms/pokerstars_6max.json")
                table_image = load_table_image(str(screenshots[0]), room_config)
                
                hero_cards = cut_hero_cards(table_image, room_config)
                board_cards = cut_board_cards(table_image, room_config)
                pot_image = cut_pot_region(table_image, room_config)
                stack_image = cut_hero_stack_region(table_image, room_config)
                
                print(f"   ✅ table_region_cutter.py can extract all regions")
                print(f"      - Hero cards: {len(hero_cards)} extracted")
                print(f"      - Board cards: {len(board_cards)} extracted")
                print(f"      - Pot region: {pot_image.width}x{pot_image.height}")
                print(f"      - Stack region: {stack_image.width}x{stack_image.height}")
                criteria_passed += 1
            else:
                print(f"   ❌ No screenshots available for testing")
        except Exception as e:
            print(f"   ❌ Error in region cutting: {e}")
    else:
        print(f"   ❌ table_region_cutter.py module not found")
    print()
    
    # 6. A test script (analyze_screenshot.py) successfully demonstrates the pipeline
    print("6️⃣  Test Script Pipeline...")
    test_script = Path("analyze_screenshot.py")
    output_dir = Path("output_regions")
    
    if test_script.exists():
        if output_dir.exists() and any(output_dir.glob("*.png")):
            extracted_files = list(output_dir.glob("*.png"))
            
            # Check for expected files
            expected_files = [
                "hero_card_1.png", "hero_card_2.png",
                "board_card_1.png", "board_card_2.png", "board_card_3.png", 
                "board_card_4.png", "board_card_5.png",
                "pot_region.png", "hero_stack_region.png"
            ]
            
            found_files = [f.name for f in extracted_files]
            missing_files = [f for f in expected_files if f not in found_files]
            
            if not missing_files:
                print(f"   ✅ analyze_screenshot.py successfully demonstrates pipeline")
                print(f"      - Output directory: {output_dir}")
                print(f"      - Extracted files: {len(extracted_files)}")
                print(f"      - All expected regions present")
                criteria_passed += 1
            else:
                print(f"   ❌ Missing extracted files: {missing_files}")
        else:
            print(f"   ❌ No extracted regions found in {output_dir}")
    else:
        print(f"   ❌ analyze_screenshot.py script not found")
    print()
    
    # Final Results
    print("=" * 70)
    print("RISULTATI FASE 3 - TABLE INPUT LAYER")
    print("=" * 70)
    
    if criteria_passed == total_criteria:
        print(f"🎉 SUCCESSO COMPLETO: {criteria_passed}/{total_criteria} criteri soddisfatti!")
        print()
        print("✅ Tutti i deliverables Fase 3 sono stati completati:")
        print("   1. JSON Layout Configuration funzionante")
        print("   2. Python module per caricare configurazioni")
        print("   3. Screenshot reale disponibile per testing") 
        print("   4. Module per croppare tavolo da screenshot")
        print("   5. Module per estrarre regioni specifiche")
        print("   6. Test script che dimostra l'intera pipeline")
        print()
        print("🚀 FASE 3 COMPLETATA - Ready for Fase 4!")
        return True
    else:
        print(f"⚠️  INCOMPLETA: {criteria_passed}/{total_criteria} criteri soddisfatti")
        print(f"   Mancano {total_criteria - criteria_passed} deliverables per completare Fase 3")
        return False


def main():
    """Esegue il test di completamento."""
    success = test_fase3_completion()
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)