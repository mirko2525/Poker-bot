"""
BRIDGE: TABLE_STATE → AI Analysis

Questo script collega il riconoscimento carte esistente (TABLE_STATE)
con il nuovo endpoint AI (/api/poker/live/analyze).

Ogni X secondi:
1. Legge TABLE_STATE (carte riconosciute dallo screenshot)
2. Converte in formato LiveTableState
3. Chiama /api/poker/live/analyze
4. Ritorna analisi AI

Può essere usato sia come:
- Modulo importabile da altri script
- Script standalone per test
"""
import requests
import time
from typing import Dict, Any, Optional
from pathlib import Path


API_URL = "https://poker-ai-assist.preview.emergentagent.com/api"


def get_recognized_cards() -> Dict[str, Any]:
    """
    Recupera le carte riconosciute dal tavolo.
    Chiama l'endpoint /api/table/1/cards che ritorna TABLE_STATE.
    
    Returns:
        dict con 'status', 'hero', 'board', ecc.
    """
    try:
        response = requests.get(f"{API_URL}/table/1/cards", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Errore recupero carte: {e}")
        return {"status": "error", "error": str(e)}


def extract_card_codes(cards_list: list) -> list:
    """
    Estrae i codici delle carte con confidenza 'strong'.
    
    Args:
        cards_list: Lista di RecognizedCard dal TABLE_STATE
    
    Returns:
        Lista di codici carte (es. ["As", "Kd"])
    """
    return [
        card["code"]
        for card in cards_list
        if card.get("code") and card.get("conf") == "strong"
    ]


def build_live_table_state(
    table_id: int,
    hero_cards: list,
    board_cards: list,
    hero_stack: float = 100.0,
    pot_size: float = 10.0,
    to_call: float = 5.0,
    position: str = "BTN",
    players: int = 2,
    big_blind: float = 1.0
) -> Dict[str, Any]:
    """
    Costruisce il JSON per /api/poker/live/analyze.
    
    Parametri come stack, pot, to_call devono essere estratti
    dallo screenshot (OCR numeri) - per ora usiamo valori di esempio.
    
    Args:
        table_id: ID del tavolo
        hero_cards: Carte hero riconosciute
        board_cards: Carte board riconosciute
        ... altri parametri di gioco
    
    Returns:
        dict pronto per POST a /api/poker/live/analyze
    """
    # Determina la street in base al numero di carte board
    num_board = len(board_cards)
    if num_board == 0:
        street = "PREFLOP"
    elif num_board == 3:
        street = "FLOP"
    elif num_board == 4:
        street = "TURN"
    elif num_board == 5:
        street = "RIVER"
    else:
        street = "UNKNOWN"
    
    return {
        "table_id": table_id,
        "hero_cards": hero_cards,
        "board_cards": board_cards,
        "hero_stack": hero_stack,
        "pot_size": pot_size,
        "to_call": to_call,
        "position": position,
        "players": players,
        "street": street,
        "last_action": "villain_bet",  # Questo andrebbe riconosciuto
        "big_blind": big_blind
    }


def analyze_table_with_ai(table_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Invia lo stato tavolo all'AI e ritorna l'analisi.
    
    Args:
        table_state: dict con formato LiveTableState
    
    Returns:
        dict con recommended_action, equity_estimate, ecc.
        None se errore
    """
    try:
        response = requests.post(
            f"{API_URL}/poker/live/analyze",
            json=table_state,
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Errore chiamata AI: {e}")
        return None


def table_state_to_ai_analysis(table_id: int = 1) -> Optional[Dict[str, Any]]:
    """
    FUNZIONE PRINCIPALE: Collega TABLE_STATE → AI Analysis
    
    Flow completo:
    1. Recupera carte riconosciute da TABLE_STATE
    2. Costruisce LiveTableState
    3. Chiama AI
    4. Ritorna analisi
    
    Args:
        table_id: ID del tavolo da analizzare
    
    Returns:
        dict con analisi AI o None se errore
    """
    # 1. Recupera carte riconosciute
    print(f"🔍 Recupero stato tavolo {table_id}...")
    table_cards = get_recognized_cards()
    
    if table_cards.get("status") != "ok":
        print(f"⚠️ Tavolo non riconosciuto: {table_cards.get('status')}")
        return None
    
    # 2. Estrai carte con confidenza alta
    hero_cards = extract_card_codes(table_cards.get("hero", []))
    board_cards = extract_card_codes(table_cards.get("board", []))
    
    print(f"   Hero: {hero_cards}")
    print(f"   Board: {board_cards}")
    
    # Verifica minima
    if len(hero_cards) < 2:
        print(f"⚠️ Non abbastanza carte hero riconosciute ({len(hero_cards)}/2)")
        return None
    
    # 3. Costruisci stato tavolo per AI
    # NOTA: stack, pot, to_call andrebbero estratti da OCR numerico
    # Per ora usiamo valori mock
    table_state = build_live_table_state(
        table_id=table_id,
        hero_cards=hero_cards,
        board_cards=board_cards,
        hero_stack=95.0,  # TODO: OCR numerico
        pot_size=12.0,    # TODO: OCR numerico
        to_call=5.0,      # TODO: OCR numerico
        position="BTN",   # TODO: Rilevamento posizione
        players=2,        # TODO: Conteggio giocatori attivi
        big_blind=1.0
    )
    
    print(f"📊 Stato tavolo costruito: {table_state['street']}")
    
    # 4. Chiama AI
    print(f"🧠 Chiamata AI per analisi...")
    ai_result = analyze_table_with_ai(table_state)
    
    if ai_result:
        print(f"✅ Analisi ricevuta: {ai_result['recommended_action']}")
        return ai_result
    else:
        print(f"❌ Errore nell'analisi AI")
        return None


# Esempio di utilizzo standalone
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("BRIDGE TEST: TABLE_STATE → AI Analysis")
    print("=" * 70 + "\n")
    
    # Test singolo
    result = table_state_to_ai_analysis(table_id=1)
    
    if result:
        print("\n" + "─" * 70)
        print("📤 RISULTATO ANALISI AI:")
        print("─" * 70)
        print(f"🎯 Azione:      {result['recommended_action']}", end="")
        if result['recommended_action'] == 'RAISE':
            print(f" ${result['recommended_amount']:.2f}")
        else:
            print()
        print(f"📈 Equity:      {result['equity_estimate']*100:.1f}%")
        print(f"🎚️  Confidenza:  {result['confidence']*100:.1f}%")
        print(f"\n💬 Commento AI:")
        print(f"   {result['ai_comment']}")
        print("─" * 70)
    else:
        print("\n❌ Impossibile ottenere analisi.")
        print("   Verifica che:")
        print("   1. Backend sia attivo (sudo supervisorctl status backend)")
        print("   2. Screenshot tavolo disponibile (/app/backend/data/screens/table1.png)")
        print("   3. Carte riconosciute correttamente")
    
    print("\n" + "=" * 70)
    print("💡 Questo bridge può essere importato in altri script:")
    print("   from bridge_tablestate_to_ai import table_state_to_ai_analysis")
    print("   result = table_state_to_ai_analysis(table_id=1)")
    print("=" * 70 + "\n")
