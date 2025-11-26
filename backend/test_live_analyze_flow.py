#!/usr/bin/env python3
"""
Test completo del nuovo flusso LIVE ANALYZE

Simula il ciclo:
Screenshot → Stato JSON → AI Brain → Overlay

Testa diversi scenari poker per verificare che l'AI risponda correttamente.
"""
import requests
import json
from typing import Dict, Any


API_URL = "https://table-analyzer.preview.emergentagent.com/api/poker/live/analyze"


def test_scenario(name: str, table_state: Dict[str, Any]) -> None:
    """Testa un singolo scenario."""
    print("\n" + "=" * 70)
    print(f"📊 SCENARIO: {name}")
    print("=" * 70)
    
    print("\n📥 INPUT - Stato Tavolo:")
    print(json.dumps(table_state, indent=2, ensure_ascii=False))
    
    try:
        # Chiamata API
        response = requests.post(API_URL, json=table_state, timeout=15)
        response.raise_for_status()
        
        result = response.json()
        
        print("\n📤 OUTPUT - Analisi AI:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("\n" + "-" * 70)
        print(f"🎯 Azione:      {result['recommended_action']}", end="")
        if result['recommended_action'] == 'RAISE':
            print(f" ${result['recommended_amount']:.2f}")
        else:
            print()
        print(f"📈 Equity:      {result['equity_estimate']*100:.1f}%")
        print(f"🎚️  Confidenza:  {result['confidence']*100:.1f}%")
        print(f"\n💬 Commento AI:")
        print(f"   {result['ai_comment']}")
        print("-" * 70)
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERRORE nella chiamata API: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERRORE inaspettato: {e}")
        return False


def main():
    """Esegue tutti i test."""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "TEST LIVE ANALYZE - NUOVO FLUSSO" + " " * 20 + "║")
    print("╚" + "═" * 68 + "╝")
    
    scenarios = [
        # Scenario 1: Pocket Aces preflop - mano fortissima
        {
            "name": "1. Pocket Aces Preflop (Mano Premium)",
            "state": {
                "table_id": 1,
                "hero_cards": ["Ah", "Ad"],
                "board_cards": [],
                "hero_stack": 100.0,
                "pot_size": 3.0,
                "to_call": 2.0,
                "position": "BTN",
                "players": 3,
                "street": "PREFLOP",
                "last_action": "villain_raise",
                "big_blind": 1.0
            }
        },
        
        # Scenario 2: AK su flop rainbow - overcards
        {
            "name": "2. AK Overcard su Flop Rainbow",
            "state": {
                "table_id": 1,
                "hero_cards": ["As", "Kd"],
                "board_cards": ["7h", "8c", "2s"],
                "hero_stack": 95.5,
                "pot_size": 9.0,
                "to_call": 3.0,
                "position": "BTN",
                "players": 3,
                "street": "FLOP",
                "last_action": "villain_bet",
                "big_blind": 1.0
            }
        },
        
        # Scenario 3: Flush draw - mano con potenziale
        {
            "name": "3. Flush Draw con Position",
            "state": {
                "table_id": 1,
                "hero_cards": ["Qh", "Jh"],
                "board_cards": ["9h", "5h", "2c"],
                "hero_stack": 87.0,
                "pot_size": 15.0,
                "to_call": 5.0,
                "position": "CO",
                "players": 2,
                "street": "FLOP",
                "last_action": "villain_bet",
                "big_blind": 1.0
            }
        },
        
        # Scenario 4: Top pair top kicker al turn
        {
            "name": "4. Top Pair Top Kicker al Turn",
            "state": {
                "table_id": 1,
                "hero_cards": ["Ac", "Kh"],
                "board_cards": ["Ad", "7s", "3c", "9h"],
                "hero_stack": 82.0,
                "pot_size": 25.0,
                "to_call": 8.0,
                "position": "MP",
                "players": 2,
                "street": "TURN",
                "last_action": "villain_bet",
                "big_blind": 1.0
            }
        },
        
        # Scenario 5: Trash hand al river - fold spot
        {
            "name": "5. Mano Debole al River (Fold Spot)",
            "state": {
                "table_id": 1,
                "hero_cards": ["3h", "7c"],
                "board_cards": ["Ac", "Kd", "Qh", "Js", "9s"],
                "hero_stack": 65.0,
                "pot_size": 45.0,
                "to_call": 20.0,
                "position": "SB",
                "players": 2,
                "street": "RIVER",
                "last_action": "villain_bet",
                "big_blind": 1.0
            }
        },
        
        # Scenario 6: Set al flop - nuts
        {
            "name": "6. Set al Flop (Monster Hand)",
            "state": {
                "table_id": 1,
                "hero_cards": ["8d", "8s"],
                "board_cards": ["8h", "4c", "2s"],
                "hero_stack": 98.0,
                "pot_size": 12.0,
                "to_call": 4.0,
                "position": "EP",
                "players": 4,
                "street": "FLOP",
                "last_action": "villain_bet",
                "big_blind": 1.0
            }
        },
        
        # Scenario 7: Short stack all-in situation
        {
            "name": "7. Short Stack All-In Decision",
            "state": {
                "table_id": 1,
                "hero_cards": ["Jh", "Tc"],
                "board_cards": [],
                "hero_stack": 12.5,
                "pot_size": 5.0,
                "to_call": 8.0,
                "position": "BB",
                "players": 3,
                "street": "PREFLOP",
                "last_action": "villain_allin",
                "big_blind": 1.0
            }
        }
    ]
    
    results = []
    for scenario in scenarios:
        success = test_scenario(scenario["name"], scenario["state"])
        results.append((scenario["name"], success))
    
    # Summary
    print("\n\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 25 + "RIEPILOGO TEST" + " " * 29 + "║")
    print("╚" + "═" * 68 + "╝")
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    total = len(results)
    passed = sum(1 for _, s in results if s)
    print(f"\n📊 Risultato: {passed}/{total} test passati")
    
    if passed == total:
        print("\n🎉 TUTTI I TEST COMPLETATI CON SUCCESSO!")
        print("\n💡 Il nuovo flusso è funzionante:")
        print("   Screenshot → JSON → /api/poker/live/analyze → Overlay")
    else:
        print(f"\n⚠️ {total - passed} test falliti. Verifica i log.")


if __name__ == "__main__":
    main()
