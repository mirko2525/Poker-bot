#!/usr/bin/env python3
"""
FASE 6.1 - HERO CARDS HELPER
Script helper per facilitare la creazione di template hero cards.
"""

from pathlib import Path
from PIL import Image, ImageOps
import sys

def analyze_hero_cards_from_screenshot(screenshot_name: str):
    """
    Analizza hero cards da uno screenshot e prepara per template creation.
    
    Args:
        screenshot_name: Nome dello screenshot (es: 'pokerstars_hero_1')
    """
    base_dir = Path(__file__).resolve().parent
    
    # 1. Check if screenshot exists
    screenshot_path = base_dir / "screenshots" / f"{screenshot_name}.png"
    if not screenshot_path.exists():
        print(f"❌ Screenshot not found: {screenshot_path}")
        return False
    
    print(f"✅ Found screenshot: {screenshot_name}.png")
    
    # 2. Extract regions
    print(f"\n🔧 Extracting regions...")
    from table_layout import load_room_config
    from table_capture_static import load_table_image
    from table_region_cutter import cut_hero_cards, save_regions
    
    config = load_room_config('rooms/pokerstars_6max.json')
    table_img = load_table_image(str(screenshot_path), config)
    hero_cards = cut_hero_cards(table_img, config)
    
    # Save to temp directory
    output_dir = f"output_regions_{screenshot_name}"
    save_regions(hero_cards, [], None, None, output_dir)
    
    print(f"✅ Regions saved to: {output_dir}/")
    print(f"   - hero_card_1.png")
    print(f"   - hero_card_2.png")
    
    # 3. Analyze hero cards
    print(f"\n🔍 Analyzing hero cards...")
    hero1_path = base_dir / output_dir / "hero_card_1.png"
    hero2_path = base_dir / output_dir / "hero_card_2.png"
    
    for i, hero_path in enumerate([hero1_path, hero2_path], 1):
        if hero_path.exists():
            img = Image.open(hero_path)
            gray = ImageOps.grayscale(img)
            
            print(f"\n  hero_card_{i}:")
            print(f"    Size: {img.width}x{img.height}")
            print(f"    Mode: {img.mode}")
            print(f"    Brightness: {gray.getextrema()}")
    
    # 4. Instructions for next step
    print(f"\n" + "=" * 70)
    print(f"📋 NEXT STEPS:")
    print(f"=" * 70)
    print(f"")
    print(f"1. Open the extracted images:")
    print(f"   {output_dir}/hero_card_1.png")
    print(f"   {output_dir}/hero_card_2.png")
    print(f"")
    print(f"2. Identify the cards visually (e.g., Ah, Ks, etc.)")
    print(f"")
    print(f"3. Copy/rename to card_templates/raw_samples/ with format:")
    print(f"   <card_code>_hero_<n>.png")
    print(f"   Examples:")
    print(f"     Ah_hero_1.png  (Ace of Hearts)")
    print(f"     Ks_hero_1.png  (King of Spades)")
    print(f"     Qd_hero_1.png  (Queen of Diamonds)")
    print(f"     Jc_hero_1.png  (Jack of Clubs)")
    print(f"")
    print(f"4. Run: python card_templates.py")
    print(f"")
    print(f"5. Test: python live_advisor.py")
    print(f"")
    print(f"=" * 70)
    
    return True


def quick_template_from_region(region_file: str, card_code: str):
    """
    Quick helper to create template from a region file.
    
    Args:
        region_file: Path to hero_card_X.png
        card_code: Card code (e.g., 'Ah', 'Ks')
    """
    base_dir = Path(__file__).resolve().parent
    source_path = base_dir / region_file
    
    if not source_path.exists():
        print(f"❌ Source file not found: {source_path}")
        return False
    
    # Validate card code
    if len(card_code) != 2:
        print(f"❌ Invalid card code: {card_code}")
        print(f"   Format: <rank><suit>")
        print(f"   Examples: Ah, Ks, Qd, Jc, Tc, 9s, 8h, 7d, 6c, 5s, 4h, 3d, 2c")
        return False
    
    # Copy to raw_samples
    raw_samples_dir = base_dir / "card_templates" / "raw_samples"
    raw_samples_dir.mkdir(parents=True, exist_ok=True)
    
    # Find next available number
    existing = list(raw_samples_dir.glob(f"{card_code}_hero_*.png"))
    next_num = len(existing) + 1
    
    dest_name = f"{card_code}_hero_{next_num}.png"
    dest_path = raw_samples_dir / dest_name
    
    # Copy file
    img = Image.open(source_path)
    img.save(dest_path)
    
    print(f"✅ Template created: {dest_name}")
    print(f"   Source: {region_file}")
    print(f"   Dest: {dest_path}")
    print(f"")
    print(f"🔧 Next step: Run 'python card_templates.py' to generate normalized template")
    
    return True


def main():
    """Main function with CLI interface."""
    
    print("=" * 70)
    print("🃏 FASE 6.1 - HERO CARDS HELPER")
    print("=" * 70)
    print()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python fase6_hero_helper.py analyze <screenshot_name>")
        print("  python fase6_hero_helper.py create <region_file> <card_code>")
        print()
        print("Examples:")
        print("  python fase6_hero_helper.py analyze pokerstars_hero_1")
        print("  python fase6_hero_helper.py create output_regions_hero_1/hero_card_1.png Ah")
        print()
        return
    
    command = sys.argv[1]
    
    if command == "analyze":
        if len(sys.argv) < 3:
            print("❌ Missing screenshot name")
            print("Usage: python fase6_hero_helper.py analyze <screenshot_name>")
            return
        
        screenshot_name = sys.argv[2]
        analyze_hero_cards_from_screenshot(screenshot_name)
    
    elif command == "create":
        if len(sys.argv) < 4:
            print("❌ Missing arguments")
            print("Usage: python fase6_hero_helper.py create <region_file> <card_code>")
            return
        
        region_file = sys.argv[2]
        card_code = sys.argv[3]
        quick_template_from_region(region_file, card_code)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: analyze, create")


if __name__ == "__main__":
    main()
