#!/usr/bin/env python3
"""
FASE 6.2 - DIGIT TEMPLATES HELPER
Script helper per facilitare la creazione di digit templates reali.
"""

from pathlib import Path
from PIL import Image, ImageOps
import sys

def extract_number_regions_for_manual_crop():
    """
    Extract pot and stack regions from all screenshots for manual digit cropping.
    """
    base_dir = Path(__file__).resolve().parent
    manual_extraction_dir = base_dir / "digit_templates" / "manual_extraction"
    manual_extraction_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("🔢 EXTRACTING NUMBER REGIONS FOR MANUAL CROPPING")
    print("=" * 70)
    print()
    
    # List of output_regions directories
    region_dirs = [
        'output_regions_preflop',
        'output_regions_flop',
        'output_regions_flop_v2',
        'output_regions_turn',
        'output_regions_river',
    ]
    
    extracted_count = 0
    
    for region_dir in region_dirs:
        region_path = base_dir / region_dir
        if not region_path.exists():
            continue
        
        # Extract pot_region
        pot_file = region_path / "pot_region.png"
        if pot_file.exists():
            dest_name = f"manual_extract_{region_dir.split('_')[-1]}_pot.png"
            dest_path = manual_extraction_dir / dest_name
            
            img = Image.open(pot_file)
            img.save(dest_path)
            
            print(f"✅ {dest_name}")
            print(f"   Source: {pot_file}")
            print(f"   Size: {img.width}x{img.height}")
            extracted_count += 1
        
        # Extract hero_stack_region
        stack_file = region_path / "hero_stack_region.png"
        if stack_file.exists():
            dest_name = f"manual_extract_{region_dir.split('_')[-1]}_stack.png"
            dest_path = manual_extraction_dir / dest_name
            
            img = Image.open(stack_file)
            img.save(dest_path)
            
            print(f"✅ {dest_name}")
            print(f"   Source: {stack_file}")
            print(f"   Size: {img.width}x{img.height}")
            extracted_count += 1
        
        print()
    
    print("=" * 70)
    print(f"📊 SUMMARY: Extracted {extracted_count} number regions")
    print("=" * 70)
    print()
    print("📋 NEXT STEPS:")
    print("=" * 70)
    print()
    print("1. Open the extracted images in digit_templates/manual_extraction/")
    print()
    print("2. For each image, visually identify the numbers (e.g., '4.90', '0.67', '12.5')")
    print()
    print("3. Manually crop individual digits and save as:")
    print("   digit_templates/raw_samples/digit_0_1.png")
    print("   digit_templates/raw_samples/digit_4_1.png")
    print("   digit_templates/raw_samples/digit_9_1.png")
    print("   digit_templates/raw_samples/symbol_dot_1.png")
    print("   etc.")
    print()
    print("   Naming convention:")
    print("     digit_<N>_<version>.png  for digits 0-9")
    print("     symbol_dot_<version>.png for decimal point")
    print("     symbol_comma_<version>.png for comma (if needed)")
    print()
    print("4. Run: python digit_templates.py")
    print()
    print("5. Test: python number_recognition.py")
    print()
    print("6. Verify in: python live_advisor.py")
    print()
    print("=" * 70)


def analyze_number_region(region_file: str):
    """
    Analyze a number region image for debugging.
    
    Args:
        region_file: Path to pot_region.png or hero_stack_region.png
    """
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / region_file
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    print("=" * 70)
    print(f"🔍 ANALYZING: {region_file}")
    print("=" * 70)
    print()
    
    img = Image.open(file_path)
    gray = ImageOps.grayscale(img)
    
    print(f"📐 Image info:")
    print(f"   Size: {img.width}x{img.height}")
    print(f"   Mode: {img.mode}")
    print(f"   Extrema (min/max): {gray.getextrema()}")
    print()
    
    # Try preprocessing
    from digit_templates import preprocess_number_region
    from number_recognition import segment_number_image
    
    print(f"🔧 Trying preprocessing (inverted)...")
    processed = preprocess_number_region(img, invert_colors=True)
    
    print(f"   Processed size: {processed.width}x{processed.height}")
    
    # Try segmentation
    print(f"🔧 Trying segmentation...")
    segments = segment_number_image(processed, min_digit_width=5, max_digit_width=35)
    
    print(f"   Found {len(segments)} segments")
    for i, seg in enumerate(segments):
        print(f"     Segment {i}: {seg.width}x{seg.height}")
    
    print()
    print(f"💡 TIP: If segments look good, manually refine and save to:")
    print(f"   digit_templates/raw_samples/")
    print()
    
    return True


def main():
    """Main CLI interface."""
    
    print()
    print("=" * 70)
    print("🔢 FASE 6.2 - DIGIT TEMPLATES HELPER")
    print("=" * 70)
    print()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python fase6_digit_helper.py extract")
        print("  python fase6_digit_helper.py analyze <region_file>")
        print()
        print("Examples:")
        print("  python fase6_digit_helper.py extract")
        print("  python fase6_digit_helper.py analyze output_regions_flop/pot_region.png")
        print()
        return
    
    command = sys.argv[1]
    
    if command == "extract":
        extract_number_regions_for_manual_crop()
    
    elif command == "analyze":
        if len(sys.argv) < 3:
            print("❌ Missing region file")
            print("Usage: python fase6_digit_helper.py analyze <region_file>")
            return
        
        region_file = sys.argv[2]
        analyze_number_region(region_file)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: extract, analyze")


if __name__ == "__main__":
    main()
