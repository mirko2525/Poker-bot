#!/usr/bin/env python3
"""
Test script per verificare l'integrazione Groq AI nel poker bot
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

from poker_ai_advisor import PokerAIAdvisor


def test_groq_connection():
    """Test 1: Verifica connessione a Groq"""
    print("=" * 60)
    print("TEST 1: Connessione a Groq Cloud")
    print("=" * 60)
    
    try:
        advisor = PokerAIAdvisor()
        print("✅ PokerAIAdvisor inizializzato con successo")
        print(f"   Modello: {advisor.model}")
        return advisor
    except Exception as e:
        print(f"❌ Errore nell'inizializzazione: {e}")
        return None


def test_preflop_analysis(advisor):
    """Test 2: Analisi preflop con AA"""
    print("\n" + "=" * 60)
    print("TEST 2: Analisi Preflop - Pocket Aces")
    print("=" * 60)
    
    analysis = advisor.analyze_hand(
        hero_cards=["As", "Ah"],
        board_cards=[],
        pot_size=3.0,
        to_call=2.0,
        hero_stack=100.0,
        big_blind=1.0,
        players_in_hand=3,
        phase="PREFLOP",
        equity=85.0,
        suggested_action="RAISE",
        raise_amount=6.0
    )
    
    print("\n🎴 Situazione:")
    print("   Hero: As Ah")
    print("   Board: (vuoto)")
    print("   Equity: 85%")
    print("   Azione: RAISE $6.00")
    print("\n🤖 Analisi AI:")
    print(f"   {analysis}\n")


def test_flop_analysis(advisor):
    """Test 3: Analisi flop con flush draw"""
    print("\n" + "=" * 60)
    print("TEST 3: Analisi Flop - Flush Draw")
    print("=" * 60)
    
    analysis = advisor.analyze_hand(
        hero_cards=["9h", "8h"],
        board_cards=["7h", "5h", "2c"],
        pot_size=20.0,
        to_call=5.0,
        hero_stack=87.0,
        big_blind=1.0,
        players_in_hand=2,
        phase="FLOP",
        equity=55.0,
        suggested_action="CALL",
        raise_amount=0.0
    )
    
    print("\n🎴 Situazione:")
    print("   Hero: 9h 8h")
    print("   Board: 7h 5h 2c")
    print("   Equity: 55%")
    print("   Azione: CALL")
    print("\n🤖 Analisi AI:")
    print(f"   {analysis}\n")


def test_river_fold(advisor):
    """Test 4: Analisi river - situazione di fold"""
    print("\n" + "=" * 60)
    print("TEST 4: Analisi River - Mano Debole")
    print("=" * 60)
    
    analysis = advisor.analyze_hand(
        hero_cards=["2h", "7c"],
        board_cards=["Ac", "Kd", "Qh", "Js", "5s"],
        pot_size=60.0,
        to_call=25.0,
        hero_stack=72.0,
        big_blind=1.0,
        players_in_hand=2,
        phase="RIVER",
        equity=15.0,
        suggested_action="FOLD",
        raise_amount=0.0
    )
    
    print("\n🎴 Situazione:")
    print("   Hero: 2h 7c")
    print("   Board: Ac Kd Qh Js 5s")
    print("   Equity: 15%")
    print("   Azione: FOLD")
    print("\n🤖 Analisi AI:")
    print(f"   {analysis}\n")


def main():
    """Esegue tutti i test"""
    print("\n🚀 TEST INTEGRAZIONE GROQ AI - POKER BOT\n")
    
    # Test 1: Connessione
    advisor = test_groq_connection()
    if not advisor:
        print("\n❌ Test falliti: impossibile connettersi a Groq")
        return
    
    # Test 2-4: Analisi varie situazioni
    test_preflop_analysis(advisor)
    test_flop_analysis(advisor)
    test_river_fold(advisor)
    
    print("=" * 60)
    print("✅ TUTTI I TEST COMPLETATI CON SUCCESSO!")
    print("=" * 60)
    print("\n💡 L'AI Groq è ora integrata nel poker bot.")
    print("   Le analisi in italiano appariranno nel frontend!\n")


if __name__ == "__main__":
    main()
