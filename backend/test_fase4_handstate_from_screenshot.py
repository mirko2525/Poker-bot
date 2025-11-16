#!/usr/bin/env python3
"""
Test Fase 4 - HandState from Screenshot - Validation Script

Test completo della pipeline Fase 4: Screenshot PokerStars → HandState completo
Validazione end-to-end dell'integrazione visione-logica poker.

Ordini del Capo - Fase 4: Validation finale screenshot → HandState → EquityEngine → DecisionEngine.
"""

import sys
from pathlib import Path
from typing import Dict, List
import json

# Import Fase 4 modules
from vision_to_handstate import VisionPokerEngine

# Import existing poker logic (Fasi 1-2)  
from server import MockEquityEngine, DecisionEngine

def test_complete_pipeline_on_screenshot(screenshot_path: str, 
                                       engine: VisionPokerEngine,
                                       equity_engine: MockEquityEngine,
                                       decision_engine: DecisionEngine) -> Dict:
    """
    Test complete pipeline: Screenshot → HandState → Equity → Decision.
    
    Args:
        screenshot_path: Path to screenshot
        engine: Vision poker engine
        equity_engine: Equity calculation engine
        decision_engine: Decision logic engine
        
    Returns:
        Dictionary with complete test results
    """
    
    screenshot_name = Path(screenshot_path).name
    print(f"🧪 TESTING COMPLETE PIPELINE: {screenshot_name}")
    print("=" * 60)
    
    results = {
        "screenshot": screenshot_name,
        "vision_success": False,
        "handstate": None,
        "equity": None,
        "decision": None,
        "pipeline_success": False
    }
    
    try:
        # Step 1: Screenshot → HandState (Fase 4)
        print("📷 Step 1: Converting screenshot to HandState...")
        handstate = engine.screenshot_to_handstate(screenshot_path)
        
        if handstate:
            print(f"   ✅ HandState created successfully")
            print(f"      Phase: {handstate.phase}")
            print(f"      Hero cards: {handstate.hero_cards}")
            print(f"      Board cards: {handstate.board_cards}")
            print(f"      Pot: ${handstate.pot_size:.2f}")
            print(f"      Stack: ${handstate.hero_stack:.2f}")
            
            results["vision_success"] = True
            results["handstate"] = {
                "phase": handstate.phase,
                "hero_cards": handstate.hero_cards,
                "board_cards": handstate.board_cards,
                "pot_size": handstate.pot_size,
                "hero_stack": handstate.hero_stack,
                "players_in_hand": handstate.players_in_hand
            }
        else:
            print(f"   ❌ Failed to create HandState")
            return results
        
        print()
        
        # Step 2: HandState → Equity (Fase 2)
        print("⚖️  Step 2: Calculating equity...")
        equity = equity_engine.compute_equity(handstate)
        
        print(f"   ✅ Equity calculated: {equity:.1f}%")
        results["equity"] = equity
        print()
        
        # Step 3: HandState + Equity → Decision (Fase 2)
        print("🎯 Step 3: Making decision...")
        decision = decision_engine.decide_action(handstate, equity)
        
        print(f"   ✅ Decision made: {decision.action}")
        if decision.action == "RAISE" and decision.raise_amount > 0:
            print(f"      Raise amount: ${decision.raise_amount:.2f}")
        if decision.reason:
            print(f"      Reason: {decision.reason}")
        
        results["decision"] = {
            "action": decision.action,
            "raise_amount": decision.raise_amount,
            "reason": decision.reason,
            "equity": decision.equity
        }
        
        results["pipeline_success"] = True
        print()
        print("🎉 COMPLETE PIPELINE SUCCESS!")
        
    except Exception as e:
        print(f"❌ Pipeline error: {e}")
        results["error"] = str(e)
    
    return results


def test_all_screenshots():
    """Test the complete pipeline on all available screenshots."""
    
    print("🎯 FASE 4 - COMPLETE PIPELINE TESTING")
    print("=" * 70)
    print()
    
    # Initialize engines
    print("⚙️  Initializing engines...")
    vision_engine = VisionPokerEngine()
    equity_engine = MockEquityEngine(enable_random=False)  # Deterministic for testing
    decision_engine = DecisionEngine()
    
    # Check vision engine readiness
    status = vision_engine.get_engine_status()
    print(f"Vision engine status:")
    print(f"  Room config: {'✅' if status['room_config_loaded'] else '❌'}")
    print(f"  Card templates: {status['card_templates']}")
    print(f"  Digit templates: {status['digit_templates']}")
    print()
    
    # Screenshots to test
    screenshots = [
        "screenshots/pokerstars_preflop.png",
        "screenshots/pokerstars_flop.png", 
        "screenshots/pokerstars_turn.png",
        "screenshots/pokerstars_river.png"
    ]
    
    # Test each screenshot
    all_results = []
    success_count = 0
    
    for screenshot_path in screenshots:
        if Path(screenshot_path).exists():
            result = test_complete_pipeline_on_screenshot(
                screenshot_path, vision_engine, equity_engine, decision_engine
            )
            all_results.append(result)
            
            if result["pipeline_success"]:
                success_count += 1
            
            print()
        else:
            print(f"⏩ Skipping {screenshot_path} (not found)")
    
    # Final summary
    print("=" * 70)
    print("FINAL RESULTS SUMMARY")
    print("=" * 70)
    
    total_tests = len(all_results)
    print(f"Pipeline Success Rate: {success_count}/{total_tests} ({success_count/total_tests*100:.1f}%)")
    print()
    
    # Detailed results
    for result in all_results:
        status = "✅" if result["pipeline_success"] else "❌"
        screenshot = result["screenshot"]
        
        print(f"{status} {screenshot}:")
        
        if result["pipeline_success"]:
            handstate = result["handstate"]
            decision = result["decision"]
            
            print(f"    Phase: {handstate['phase']}")
            print(f"    Cards recognized: {len([c for c in handstate['hero_cards'] + handstate['board_cards'] if c != '??'])}")
            print(f"    Equity: {result['equity']:.1f}%")
            print(f"    Decision: {decision['action']}")
        else:
            if "error" in result:
                print(f"    Error: {result['error']}")
            else:
                print(f"    Vision failed to create HandState")
        print()
    
    # Final assessment
    if success_count == total_tests:
        print("🏆 FASE 4 COMPLETAMENTO: 100% SUCCESS!")
        print()
        print("✅ Pipeline completa funzionante:")
        print("   1. Screenshot recognition (Fase 3 + Fase 4)")  
        print("   2. HandState creation (Fase 4)")
        print("   3. Equity calculation (Fase 2)")
        print("   4. Decision making (Fase 2)")
        print()
        print("🚀 Ready for production integration!")
        
    else:
        print(f"⚠️  FASE 4 PARZIALMENTE COMPLETA: {success_count}/{total_tests}")
        print("🔧 Areas needing improvement:")
        
        failed_results = [r for r in all_results if not r["pipeline_success"]]
        for result in failed_results:
            print(f"   - {result['screenshot']}: Need better recognition templates")
    
    return all_results


def save_test_results(results: List[Dict], output_file: str = "fase4_test_results.json"):
    """Save test results to JSON file for analysis."""
    
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📊 Test results saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error saving results: {e}")


def main():
    """Main function for Fase 4 complete testing."""
    
    print("🔬 FASE 4 - HANDSTATE FROM SCREENSHOT VALIDATION")
    print("=" * 70)
    print()
    print("Obiettivo: Validare pipeline completa Screenshot → HandState → Decision")
    print("Pipeline: Fase 3 (regions) + Fase 4 (recognition) + Fase 2 (logic)")
    print()
    
    # Run complete tests
    results = test_all_screenshots()
    
    # Save results for analysis
    save_test_results(results)
    
    print("\n" + "=" * 70)
    print("TEST COMPLETATO - FASE 4")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    results = main()
    
    # Exit with appropriate code
    success_count = sum(1 for r in results if r["pipeline_success"])
    sys.exit(0 if success_count == len(results) else 1)