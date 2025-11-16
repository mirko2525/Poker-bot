#!/usr/bin/env python3
"""
Test completo del MockEquityEngine per verificare equity corrette.
"""

from server import HandState, MockEquityEngine

def test_equity():
    """Test equity calculation for various scenarios."""
    
    engine = MockEquityEngine(enable_random=False)
    
    print("=" * 70)
    print("🎲 MOCK EQUITY ENGINE - TEST COMPLETO")
    print("=" * 70)
    print()
    
    # Premium Pairs
    print("📊 PREMIUM PAIRS (Preflop)")
    print("-" * 70)
    
    pairs_preflop = [
        ("AA", ["Ah", "As"], 85),
        ("KK", ["Kh", "Ks"], 82),
        ("QQ", ["Qh", "Qs"], 80),
        ("JJ", ["Jh", "Js"], 77),
        ("TT", ["Th", "Ts"], 75),
    ]
    
    for name, cards, expected in pairs_preflop:
        hs = HandState(
            hero_cards=cards, board_cards=[], phase="PREFLOP",
            pot_size=3.0, hero_stack=100.0, to_call=1.0, big_blind=1.0, players_in_hand=2
        )
        equity = engine.compute_equity(hs)
        status = "✅" if abs(equity * 100 - expected) < 1 else "❌"
        print(f"  {status} {name}: {equity:.1%} (atteso: {expected}%)")
    
    print()
    
    # Broadway Hands
    print("🎴 BROADWAY HANDS (Preflop)")
    print("-" * 70)
    
    broadway = [
        ("AKo", ["Ah", "Ks"], 67),
        ("AQo", ["Ah", "Qs"], 65),
        ("AJo", ["Ah", "Js"], 63),
        ("KQo", ["Kh", "Qs"], 63),
        ("KJo", ["Kh", "Js"], 60),
    ]
    
    for name, cards, expected in broadway:
        hs = HandState(
            hero_cards=cards, board_cards=[], phase="PREFLOP",
            pot_size=3.0, hero_stack=100.0, to_call=1.0, big_blind=1.0, players_in_hand=2
        )
        equity = engine.compute_equity(hs)
        status = "✅" if abs(equity * 100 - expected) < 1 else "❌"
        print(f"  {status} {name}: {equity:.1%} (atteso: {expected}%)")
    
    print()
    
    # Weak Hands
    print("💩 WEAK HANDS (Preflop)")
    print("-" * 70)
    
    weak = [
        ("72o", ["7h", "2s"], 38),
        ("82o", ["8h", "2s"], 39),
        ("92o", ["9h", "2s"], 38),
        ("32o", ["3h", "2s"], 36),
    ]
    
    for name, cards, expected in weak:
        hs = HandState(
            hero_cards=cards, board_cards=[], phase="PREFLOP",
            pot_size=3.0, hero_stack=100.0, to_call=1.0, big_blind=1.0, players_in_hand=2
        )
        equity = engine.compute_equity(hs)
        status = "✅" if abs(equity * 100 - expected) < 3 else "❌"
        print(f"  {status} {name}: {equity:.1%} (atteso: ~{expected}%)")
    
    print()
    
    # Postflop Scenarios
    print("🎯 POSTFLOP SCENARIOS")
    print("-" * 70)
    
    postflop = [
        ("AA flop miss (K72)", ["Ah", "As"], ["Kd", "7c", "2h"], "FLOP", 75),
        ("AA flop set (AK7)", ["Ah", "As"], ["Ac", "Kc", "7h"], "FLOP", 90),
        ("KK flop overpair (972)", ["Kh", "Ks"], ["9d", "7c", "2h"], "FLOP", 72),
        ("72o flop miss (AKQ)", ["7h", "2s"], ["Ah", "Kc", "Qh"], "FLOP", 10),
        ("72o flop pair (7KQ)", ["7h", "2s"], ["7c", "Kc", "Qh"], "FLOP", 45),
        ("AK flop top pair (AQ9)", ["Ah", "Ks"], ["Ac", "Qc", "9h"], "FLOP", 75),
        ("AK flop miss (872)", ["Ah", "Ks"], ["8c", "7c", "2h"], "FLOP", 40),
    ]
    
    for name, hero, board, phase, expected in postflop:
        hs = HandState(
            hero_cards=hero, board_cards=board, phase=phase,
            pot_size=10.0, hero_stack=100.0, to_call=0.0, big_blind=1.0, players_in_hand=2
        )
        equity = engine.compute_equity(hs)
        status = "✅" if abs(equity * 100 - expected) < 10 else "❌"
        print(f"  {status} {name:25s}: {equity:.1%} (atteso: ~{expected}%)")
    
    print()
    print("=" * 70)
    print("✅ Test completato!")
    print("=" * 70)


if __name__ == "__main__":
    test_equity()
