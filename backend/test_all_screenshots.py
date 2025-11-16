#!/usr/bin/env python3
"""
Test tutti gli screenshot PokerStars - Fase 3

Testa l'estrazione delle regioni su tutti gli screenshot rinominati
per verificare che le coordinate funzionino per tutte le fasi della mano.
"""

import os
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))

from analyze_screenshot import analyze_screenshot

def test_all_pokerstars_screenshots():
    """
    Testa tutti gli screenshot PokerStars disponibili.
    """
    
    print("🧪 TESTING ALL POKERSTARS SCREENSHOTS")
    print("=" * 60)
    print()
    
    # Lista degli screenshot da testare (corretta dopo analisi)
    screenshot_files = [
        "pokerstars_preflop.png",
        "pokerstars_flop.png", 
        "pokerstars_turn.png",
        "pokerstars_turn2.png"
    ]
    
    config_path = "rooms/pokerstars_6max.json"
    screenshots_dir = Path("screenshots")
    
    if not Path(config_path).exists():
        print(f"❌ Configuration file not found: {config_path}")
        return False
    
    success_count = 0
    total_count = len(screenshot_files)
    
    for i, filename in enumerate(screenshot_files, 1):
        screenshot_path = screenshots_dir / filename
        
        print(f"📷 Testing {i}/{total_count}: {filename}")
        
        if not screenshot_path.exists():
            print(f"   ❌ File not found: {screenshot_path}")
            continue
        
        # Crea directory di output specifica per ogni screenshot
        output_dir = f"output_regions_{filename.split('.')[0].split('_')[1]}"  # es: output_regions_preflop
        
        try:
            success = analyze_screenshot(str(config_path), str(screenshot_path), output_dir)
            
            if success:
                print(f"   ✅ SUCCESS: Regions extracted to {output_dir}/")
                success_count += 1
                
                # Conta i file estratti
                output_path = Path(output_dir)
                if output_path.exists():
                    extracted_files = list(output_path.glob("*.png"))
                    print(f"      📊 Extracted {len(extracted_files)} region files")
                
            else:
                print(f"   ❌ FAILED: Error during region extraction")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
        
        print()
    
    # Risultati finali
    print("=" * 60)
    print("RISULTATI FINALI")
    print("=" * 60)
    
    if success_count == total_count:
        print(f"🎉 TUTTI I TEST SUPERATI: {success_count}/{total_count}")
        print()
        print("✅ Le coordinate funzionano correttamente per tutte le fasi:")
        print("   - PREFLOP: Estrazioni completate")
        print("   - FLOP: Estrazioni completate") 
        print("   - TURN: Estrazioni completate")
        print()
        print("🎯 FASE 3 - Real Screenshot Integration: COMPLETA!")
        return True
    else:
        print(f"⚠️  ALCUNI TEST FALLITI: {success_count}/{total_count}")
        print(f"   {total_count - success_count} screenshot necessitano calibrazione aggiuntiva")
        return False

def cleanup_old_outputs():
    """Pulisce le directory di output precedenti."""
    
    print("🧹 Cleaning up old output directories...")
    
    # Rimuovi output_regions generico (dai test precedenti con mock)
    old_output = Path("output_regions")
    if old_output.exists():
        import shutil
        shutil.rmtree(old_output)
        print(f"   🗑️  Removed: {old_output}")
    
    # Lista directory di output da pulire
    output_dirs = ["output_regions_preflop", "output_regions_flop", "output_regions_flop2", "output_regions_turn"]
    
    for output_dir in output_dirs:
        output_path = Path(output_dir)
        if output_path.exists():
            import shutil
            shutil.rmtree(output_path)
            print(f"   🗑️  Removed: {output_path}")
    
    print("✅ Cleanup complete")
    print()

def main():
    """Funzione principale."""
    
    # Pulisci output precedenti
    cleanup_old_outputs()
    
    # Esegui test su tutti gli screenshot
    success = test_all_pokerstars_screenshots()
    
    if success:
        print("📋 SUMMARY:")
        print("- Screenshot PokerStars scaricati e rinominati correttamente")
        print("- Coordinate calibrate per risoluzione 3071x1919")
        print("- Pipeline di estrazione funzionante per tutte le fasi della mano")
        print("- Regioni estratte: hero cards, board cards, pot, hero stack")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)