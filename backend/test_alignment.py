#!/usr/bin/env python3
"""
Test di Allineamento Console vs Web Demo
Ordini Fase 2: Verificare che entrambi i demo usino esattamente la stessa logica backend.
"""

import sys
import os
from pathlib import Path
import json
import requests

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent))

from server import MockStateProvider, MockEquityEngine, DecisionEngine

def test_alignment():
    """
    Verifica allineamento tra console demo e web API.
    Confronta le stesse mani processate da entrambi i sistemi.
    """
    
    print("="*60)
    print("TEST ALLINEAMENTO CONSOLE vs WEB DEMO")
    print("="*60)
    print()
    
    # Inizializza provider console (senza randomness per test deterministic)
    console_provider = MockStateProvider()
    console_equity_engine = MockEquityEngine(enable_random=False)
    console_decision_engine = DecisionEngine()
    
    # Reset web demo
    try:
        start_response = requests.get("http://localhost:8001/api/poker/demo/start")
        print(f"✅ Web demo avviato: {start_response.json()}")
    except Exception as e:
        print(f"❌ Errore avvio web demo: {e}")
        return
    
    print()
    
    mismatches = 0
    total_hands = len(console_provider.mock_hands)
    
    # Confronta mano per mano
    for hand_num in range(1, total_hands + 1):
        print(f"--- Confronto Mano {hand_num}/{total_hands} ---")
        
        # Console logic
        console_hand = console_provider.get_next_mock_hand()
        console_equity = console_equity_engine.compute_equity(console_hand)
        console_decision = console_decision_engine.decide_action(console_hand, console_equity)
        
        # Web API logic
        try:
            api_response = requests.get("http://localhost:8001/api/poker/demo/next")
            api_data = api_response.json()
            
            web_hand = api_data['hand_state']
            web_decision = api_data['decision']
            
            # Confronta dati hand state
            hand_match = (
                console_hand.hero_cards == web_hand['hero_cards'] and
                console_hand.board_cards == web_hand['board_cards'] and
                console_hand.phase == web_hand['phase'] and
                console_hand.pot_size == web_hand['pot_size']
            )
            
            # Confronta decisioni (azione e importo raise)
            decision_match = (
                console_decision.action == web_decision['action'] and
                abs(console_decision.raise_amount - web_decision['raise_amount']) < 0.01
            )
            
            if hand_match and decision_match:
                print(f"✅ ALLINEATO: {console_hand.phase} {' '.join(console_hand.hero_cards)} → {console_decision.action}")
            else:
                print("❌ DISALLINEATO:")
                if not hand_match:
                    print(f"   Hand State: Console={console_hand.hero_cards} vs Web={web_hand['hero_cards']}")
                if not decision_match:
                    print(f"   Decisione: Console={console_decision.action}({console_decision.raise_amount:.2f}) vs Web={web_decision['action']}({web_decision['raise_amount']:.2f})")
                mismatches += 1
            
        except Exception as e:
            print(f"❌ Errore API: {e}")
            mismatches += 1
    
    print()
    print("="*60)
    print("RISULTATI TEST ALLINEAMENTO")
    print("="*60)
    
    if mismatches == 0:
        print(f"🎉 SUCCESSO COMPLETO: Tutti i {total_hands} confronti sono allineati!")
        print("📋 Console Demo e Web Demo usano esattamente la stessa logica backend.")
        print("✅ Fase 2 - Requisito Allineamento: SUPERATO")
    else:
        print(f"⚠️  ATTENZIONE: {mismatches}/{total_hands} mani disallineate")
        print("🔧 Richiedono revisione della sincronizzazione logica.")
    
    print()


if __name__ == "__main__":
    test_alignment()