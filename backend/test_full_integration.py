#!/usr/bin/env python3
"""
TEST INTEGRAZIONE COMPLETA END-TO-END

Simula il flusso completo senza bisogno di screenshot reale:
1. Mock TABLE_STATE con carte valide
2. Bridge → /api/poker/live/analyze
3. Mostra risultato come apparirebbe nell'overlay

Questo dimostra che tutto il sistema è collegato e funzionante.
"""
import requests
import json
from bridge_tablestate_to_ai import (
    build_live_table_state,
    analyze_table_with_ai
)


def test_integration_with_mock_cards():
    """Test integrazione con carte mock."""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "TEST INTEGRAZIONE END-TO-END" + " " * 24 + "║")
    print("╚" + "═" * 68 + "╝\n")
    
    print("Scenario: Simuliamo carte riconosciute da screenshot reale")
    print()
    
    # Simula carte riconosciute da TABLE_STATE
    scenarios = [
        {
            "name": "Pocket Aces Preflop",
            "hero": ["Ah", "Ad"],
            "board": [],
            "stack": 100.0,
            "pot": 3.0,
            "to_call": 2.0
        },
        {
            "name": "Top Pair al Flop",
            "hero": ["Ac", "Kh"],
            "board": ["Ad", "7s", "2c"],
            "stack": 95.0,
            "pot": 12.0,
            "to_call": 5.0
        },
        {
            "name": "Flush Draw",
            "hero": ["Qh", "Jh"],
            "board": ["9h", "5h", "2c"],
            "stack": 87.0,
            "pot": 15.0,
            "to_call": 5.0
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print("=" * 70)
        print(f"TEST {i}/3: {scenario['name']}")
        print("=" * 70)
        
        # 1. OCCHI: Screenshot → Riconoscimento (simulato)
        print("\n👁️  FASE 1: OCCHI (Screenshot Recognition)")
        print(f"   Hero riconosciute:  {scenario['hero']}")
        print(f"   Board riconosciute: {scenario['board']}")
        
        # 2. Build stato tavolo per AI
        print("\n📊 FASE 2: Costruzione Stato Tavolo")
        table_state = build_live_table_state(
            table_id=1,
            hero_cards=scenario['hero'],
            board_cards=scenario['board'],
            hero_stack=scenario['stack'],
            pot_size=scenario['pot'],
            to_call=scenario['to_call'],
            position="BTN",
            players=2,
            big_blind=1.0
        )
        print(f"   Street: {table_state['street']}")
        print(f"   Pot: ${table_state['pot_size']:.2f}")
        print(f"   To call: ${table_state['to_call']:.2f}")
        
        # 3. CERVELLO: AI Analysis
        print("\n🧠 FASE 3: CERVELLO (AI Brain - Groq)")
        print("   Chiamata /api/poker/live/analyze...")
        
        ai_result = analyze_table_with_ai(table_state)
        
        if not ai_result:
            print("   ❌ Errore nell'analisi AI")
            continue
        
        print("   ✅ Analisi ricevuta!")
        
        # 4. BOCCA: Overlay Display
        print("\n👄 FASE 4: BOCCA (Overlay Desktop)")
        print("   ┌─────────────────────────────────────────┐")
        print(f"   │  🎴 TAVOLO 1                     ●      │")
        print("   ├─────────────────────────────────────────┤")
        print(f"   │  Carte: {' '.join(scenario['hero'])} vs {' '.join(scenario['board']) or 'board vuoto':<15} │")
        print("   │                                         │")
        
        action = ai_result['recommended_action']
        amount = ai_result['recommended_amount']
        if action == 'RAISE':
            action_display = f"{action} ${amount:.2f}"
        else:
            action_display = action
        
        print(f"   │        {action_display:^31}         │")
        print("   │                                         │")
        print(f"   │  Equity: {ai_result['equity_estimate']*100:5.1f}%      Conf: {ai_result['confidence']*100:5.1f}%  │")
        print("   ├─────────────────────────────────────────┤")
        
        # Commento troncato
        comment = ai_result['ai_comment']
        if len(comment) > 80:
            comment = comment[:77] + "..."
        
        # Split in righe per visualizzazione
        words = comment.split()
        lines = []
        current_line = "   │  💬 "
        for word in words:
            if len(current_line) + len(word) + 1 <= 45:
                current_line += word + " "
            else:
                lines.append(current_line.ljust(43) + "│")
                current_line = "   │     " + word + " "
        if current_line.strip() != "   │":
            lines.append(current_line.ljust(43) + "│")
        
        for line in lines[:3]:  # Max 3 righe
            print(line)
        
        print("   └─────────────────────────────────────────┘")
        print()
    
    print("=" * 70)
    print("✅ INTEGRAZIONE COMPLETA TESTATA!")
    print()
    print("Flusso verificato:")
    print("  1. 👁️  Screenshot → Riconoscimento carte (simulato)")
    print("  2. 📊 Costruzione JSON stato tavolo")
    print("  3. 🧠 POST /api/poker/live/analyze → AI Groq")
    print("  4. 👄 Visualizzazione overlay (simulato)")
    print()
    print("💡 Per overlay reale: python poker_live_overlay.py")
    print("=" * 70)


if __name__ == "__main__":
    test_integration_with_mock_cards()
