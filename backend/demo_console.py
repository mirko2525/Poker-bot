#!/usr/bin/env python3
"""
DEMO 1 CONSOLE UFFICIALE - Poker Bot

Questo demo utilizza gli stessi moduli backend del web demo:
- MockStateProvider: Fornisce mani mock predefinite
- MockEquityEngine: Simula calcoli equity
- DecisionEngine: Applica logica decisionale FOLD/CALL/RAISE

Ordini del Capo - Fase 2: Console demo con output formattato e logica cleanup.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the path so we can import server modules
sys.path.append(str(Path(__file__).parent))

from server import MockStateProvider, MockEquityEngine, DecisionEngine, HandState

def main():
    """
    Funzione principale del DEMO 1 Console Ufficiale.
    
    Workflow esatto come specificato nei documenti:
    1. Avvio con header
    2. Loop sulle mani mock
    3. Per ogni mano: mostra stato, calcola equity, decide azione, attende input
    4. Fine demo con messaggio finale
    """
    
    # Inizializzazione moduli backend (stessa logica del web demo)
    provider = MockStateProvider()
    equity_engine = MockEquityEngine(enable_random=True)  # Randomness abilitata per demo
    decision_engine = DecisionEngine()
    
    # Header iniziale (come specificato)
    print("====================================")
    print("DEMO BOT POKER – MOCK WORKFLOW V1")
    print("====================================")
    print()
    print("Console Demo Ufficiale - Fase 2")
    print("Utilizzo: MockStateProvider + MockEquityEngine + DecisionEngine")
    print()
    
    hand_count = 0
    total_hands = len(provider.mock_hands)
    
    # Loop principale sulle mani mock
    while provider.has_next():
        hand_count += 1
        
        # 1. Ottieni prossima mano mock
        hand_state = provider.get_next_mock_hand()
        
        if hand_state is None:
            break
            
        # 2. Stampa informazioni mano
        print(f"===== Mano {hand_count}/{total_hands} =====")
        print(f"Fase: {hand_state.phase}")
        print(f"Carte Hero: {' '.join(hand_state.hero_cards)}")
        
        # Board cards (o "nessuna" per preflop)
        if hand_state.board_cards and len(hand_state.board_cards) > 0:
            print(f"Carte Board: {' '.join(hand_state.board_cards)}")
        else:
            print("Carte Board: nessuna")
            
        print(f"Piatto: ${hand_state.pot_size:.2f}")
        print(f"Da chiamare: ${hand_state.to_call:.2f}")
        print(f"Stack Hero: ${hand_state.hero_stack:.2f}")
        print(f"Giocatori in mano: {hand_state.players_in_hand}")
        print()
        
        # 3. Calcola equity
        equity = equity_engine.compute_equity(hand_state)
        print(f"Equity stimata: {equity:.1f}%")
        
        # 4. Calcola decisione
        decision = decision_engine.decide_action(hand_state, equity)
        
        # 5. Mostra decisione
        print(f"Azione consigliata: {decision.action}")
        if decision.action == "RAISE" and decision.raise_amount > 0:
            print(f"Importo raise: ${decision.raise_amount:.2f}")
        if decision.reason:
            print(f"Ragione: {decision.reason}")
        
        print()
        print("-" * 50)
        
        # 6. Attendi input utente per continuare
        input("Premi INVIO per continuare alla prossima mano...")
        print()
    
    # Fine demo
    print("Fine DEMO 1 – Nessun'altra mano mock disponibile.")
    print("Grazie per aver testato il Poker Bot Console Demo!")
    print()


if __name__ == "__main__":
    main()
