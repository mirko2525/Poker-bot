#!/usr/bin/env python3
"""
LIVE ADVISOR V1 - FASE 5
Demo da console: Screenshot → Visione → Equity → Decisione

Ordini del Capo - Fase 5: Sistema integrato end-to-end per consigliare azioni poker
basandosi su screenshot reali.
"""

import sys
from pathlib import Path
import logging

# Aggiungi backend directory al path per garantire che i moduli siano trovati
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import moduli esistenti
from vision_to_handstate import VisionPokerEngine
from server import HandState, Decision, MockEquityEngine, DecisionEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurazione
ROOM_CONFIG_PATH = "rooms/pokerstars_6max.json"
SCREENSHOTS_DEMO = [
    "screenshots/pokerstars_preflop.png",
    "screenshots/pokerstars_flop_v2.png",
    "screenshots/pokerstars_turn.png",
    "screenshots/pokerstars_river.png",
]


def stampa_hand_state_e_decisione(hand_state: HandState, equity: float, decision: Decision) -> None:
    """
    Stampa HandState e Decisione in modo leggibile per l'umano.
    
    Args:
        hand_state: Stato della mano riconosciuto
        equity: Equity calcolata (0-1 range)
        decision: Decisione consigliata
    """
    print(f"📊 Phase: {hand_state.phase}")
    print(f"🃏 Hero cards: {hand_state.hero_cards}")
    print(f"🎴 Board: {hand_state.board_cards}")
    print(f"💰 Pot size: ${hand_state.pot_size:.2f}")
    print(f"💵 Hero stack: ${hand_state.hero_stack:.2f}")
    print(f"👥 Players in hand: {hand_state.players_in_hand}")
    print()
    print(f"📈 Equity stimata: {equity:.2%}")
    print(f"▲ Azione consigliata: {decision.action}", end="")
    
    # Gestione robusta di raise_amount (potrebbe non esistere o essere 0)
    raise_amount = getattr(decision, "raise_amount", 0)
    if decision.action == "RAISE" and raise_amount > 0:
        print(f" (raise: ${raise_amount:.2f})")
    else:
        print()
    
    # Gestione robusta di reason (potrebbe non esistere o essere None)
    reason = getattr(decision, "reason", None)
    if reason:
        print(f"💡 Motivo: {reason}")


def run_live_advisor_demo() -> None:
    """
    Esegue la demo del Live Advisor su screenshot reali.
    
    Per ogni screenshot:
    1. Estrae HandState tramite VisionPokerEngine
    2. Calcola equity tramite MockEquityEngine
    3. Decide azione tramite DecisionEngine
    4. Stampa risultato leggibile
    """
    base_dir = Path(__file__).resolve().parent
    
    print("\n🔧 Inizializzazione motori...")
    
    # 1) Inizializza motore di visione
    room_config_path = base_dir / ROOM_CONFIG_PATH
    if not room_config_path.exists():
        logger.error(f"Room config non trovato: {room_config_path}")
        return
    
    vision_engine = VisionPokerEngine(config_path=str(room_config_path))
    print(f"   ✅ VisionPokerEngine inizializzato")
    
    # Verifica stato engine
    engine_status = vision_engine.get_engine_status()
    print(f"      - Card templates: {engine_status['card_templates']}")
    print(f"      - Digit templates: {engine_status['digit_templates']}")
    print(f"      - Ready: {engine_status['fully_ready']}")
    
    # 2) Inizializza motore di equity e decisione
    equity_engine = MockEquityEngine()
    decision_engine = DecisionEngine()
    print(f"   ✅ EquityEngine e DecisionEngine inizializzati")
    
    # 3) Loop sugli screenshot demo
    print(f"\n📸 Processando {len(SCREENSHOTS_DEMO)} screenshot...\n")
    
    success_count = 0
    fail_count = 0
    
    for rel_path in SCREENSHOTS_DEMO:
        screenshot_path = base_dir / rel_path
        
        if not screenshot_path.exists():
            print(f"❌ Screenshot non trovato: {rel_path}")
            fail_count += 1
            continue
        
        print("=" * 60)
        print(f"🖼️  Screenshot: {screenshot_path.name}")
        print("=" * 60)
        
        try:
            # a) Visione → HandState
            hand_state = vision_engine.screenshot_to_handstate(str(screenshot_path))
            
            if not hand_state:
                print(f"❌ Impossibile creare HandState da {screenshot_path.name}")
                fail_count += 1
                continue
            
            # b) Equity (mock)
            equity = equity_engine.compute_equity(hand_state)
            
            # c) Decisione
            decision = decision_engine.decide_action(hand_state, equity)
            
            # d) Output leggibile
            stampa_hand_state_e_decisione(hand_state, equity, decision)
            
            success_count += 1
            
        except Exception as e:
            logger.error(f"Errore processando {screenshot_path.name}: {e}")
            fail_count += 1
        
        print()
    
    # Summary finale
    print("=" * 60)
    print(f"📊 RIEPILOGO DEMO")
    print("=" * 60)
    print(f"   ✅ Successi: {success_count}/{len(SCREENSHOTS_DEMO)}")
    print(f"   ❌ Fallimenti: {fail_count}/{len(SCREENSHOTS_DEMO)}")
    
    if success_count == len(SCREENSHOTS_DEMO):
        print("\n🎉 🎉 🎉 FASE 5 - LIVE ADVISOR V1 COMPLETA! 🎉 🎉 🎉")
        print("   Tutti gli screenshot processati con successo!")
        print("   Il sistema end-to-end funziona correttamente.")
    elif success_count > 0:
        print("\n⚠️  Demo parzialmente funzionante.")
        print("   Alcuni screenshot hanno avuto problemi.")
    else:
        print("\n❌ Demo fallita - nessuno screenshot processato correttamente.")


def main():
    """Main function per Live Advisor demo."""
    
    print("=" * 60)
    print("🃏 LIVE ADVISOR V1 – DEMO DA SCREENSHOT 🃏")
    print("=" * 60)
    print()
    print("Sistema integrato: Screenshot → Visione → Equity → Decisione")
    print("Fase 5 - Ordini del Capo")
    print()
    
    run_live_advisor_demo()
    
    print("\n" + "=" * 60)
    print("🔧 Next Steps:")
    print("   1. Migliorare card templates per hero cards")
    print("   2. Creare digit templates REALI per pot/stack")
    print("   3. (Futuro) Integrazione con FastAPI endpoint")
    print("   4. (Futuro) Cattura automatica schermo")
    print("=" * 60)


if __name__ == "__main__":
    main()
