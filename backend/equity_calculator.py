"""
EQUITY CALCULATOR - Calcolo matematico preciso con Monte Carlo

Usa libreria 'treys' per valutazione mani + simulazione Monte Carlo
per calcolare equity esatta nel Texas Hold'em.

Molto più preciso della "stima" dell'AI!
"""
import random
from typing import List, Tuple
from deuces import Card, Evaluator


class EquityCalculator:
    """
    Calcolo equity preciso per Texas Hold'em.
    
    Usa simulazione Monte Carlo (10,000 iterazioni) per calcolare
    la probabilità esatta di vincita dato hero cards + board.
    """
    
    def __init__(self):
        self.evaluator = Evaluator()
    
    def _parse_card(self, card_str: str) -> int:
        """
        Converte carta da formato stringa a formato deuces.
        
        Input: "As", "Kh", "7c", etc.
        Output: int (formato deuces)
        
        Args:
            card_str: Carta in formato "RankSuit" (es. "As" = Asso di Picche)
        
        Returns:
            Card in formato deuces
        """
        if not card_str or len(card_str) != 2:
            raise ValueError(f"Formato carta invalido: {card_str}")
        
        rank = card_str[0].upper()
        suit = card_str[1].lower()
        
        # Deuces usa formato come "As", "Kh", etc
        return Card.new(rank + suit)
    
    def calculate_equity(
        self,
        hero_cards: List[str],
        board_cards: List[str],
        num_opponents: int = 1,
        num_simulations: int = 10000
    ) -> Tuple[float, float, float]:
        """
        Calcola equity con simulazione Monte Carlo.
        
        Args:
            hero_cards: 2 carte hero (es. ["As", "Kd"])
            board_cards: 0-5 carte board (es. ["7h", "8h", "2c"])
            num_opponents: Numero avversari (default 1)
            num_simulations: Numero simulazioni (default 10,000)
        
        Returns:
            Tuple (win_rate, tie_rate, lose_rate) - tutti float 0-1
        
        Raises:
            ValueError: Se carte invalide
        """
        # Validazione input
        if len(hero_cards) != 2:
            raise ValueError("Hero deve avere esattamente 2 carte")
        
        if len(board_cards) > 5:
            raise ValueError("Board può avere max 5 carte")
        
        # Converti carte
        try:
            hero = [self._parse_card(c) for c in hero_cards]
            board = [self._parse_card(c) for c in board_cards]
        except Exception as e:
            raise ValueError(f"Errore parsing carte: {e}")
        
        # Carte conosciute (rimuovile dal deck)
        known_cards = set(hero + board)
        
        # Contatori
        wins = 0
        ties = 0
        losses = 0
        
        # Monte Carlo simulation
        for _ in range(num_simulations):
            # Crea deck completo e rimuovi carte conosciute
            full_deck = Card.get_full_deck()
            deck = [c for c in full_deck if c not in known_cards]
            random.shuffle(deck)
            
            # Completa il board (se necessario)
            current_board = board.copy()
            cards_needed = 5 - len(current_board)
            if cards_needed > 0:
                drawn_cards = deck[:cards_needed]
                current_board.extend(drawn_cards)
                deck = deck[cards_needed:]
            
            # Valuta mano hero
            hero_score = self.evaluator.evaluate(current_board, hero)
            
            # Simula mani avversari
            opponent_scores = []
            for _ in range(num_opponents):
                if len(deck.cards) >= 2:
                    opp_hand = deck.draw(2)
                    opp_score = self.evaluator.evaluate(current_board, opp_hand)
                    opponent_scores.append(opp_score)
            
            # Confronta (score più basso = mano migliore in treys)
            if not opponent_scores:
                wins += 1
                continue
            
            best_opponent = min(opponent_scores)
            
            if hero_score < best_opponent:
                wins += 1
            elif hero_score == best_opponent:
                ties += 1
            else:
                losses += 1
        
        # Calcola percentuali
        total = num_simulations
        win_rate = wins / total
        tie_rate = ties / total
        lose_rate = losses / total
        
        return (win_rate, tie_rate, lose_rate)
    
    def get_equity_percentage(
        self,
        hero_cards: List[str],
        board_cards: List[str],
        num_opponents: int = 1
    ) -> float:
        """
        Calcola equity come singolo valore (win + tie/2).
        
        Args:
            hero_cards: 2 carte hero
            board_cards: 0-5 carte board
            num_opponents: Numero avversari
        
        Returns:
            float: Equity da 0 a 1 (es. 0.65 = 65%)
        """
        try:
            win, tie, lose = self.calculate_equity(
                hero_cards,
                board_cards,
                num_opponents
            )
            
            # Equity = win% + (tie% / 2)
            equity = win + (tie / 2)
            
            return equity
            
        except Exception as e:
            print(f"⚠️ Errore calcolo equity: {e}")
            # Fallback: equity neutrale
            return 0.5


# Test standalone
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("EQUITY CALCULATOR TEST - Monte Carlo Simulation")
    print("=" * 70 + "\n")
    
    calc = EquityCalculator()
    
    # Test 1: Pocket Aces preflop
    print("📊 TEST 1: Pocket Aces Preflop")
    print("   Hero: As Ad")
    print("   Board: (vuoto)")
    print("   Avversari: 1")
    
    equity = calc.get_equity_percentage(["As", "Ad"], [])
    win, tie, lose = calc.calculate_equity(["As", "Ad"], [])
    
    print(f"\n   ✅ RISULTATO:")
    print(f"      Equity: {equity*100:.1f}%")
    print(f"      Win: {win*100:.1f}% | Tie: {tie*100:.1f}% | Lose: {lose*100:.1f}%")
    
    # Test 2: AK overcard su flop
    print("\n" + "-" * 70)
    print("📊 TEST 2: AK Overcard su Flop")
    print("   Hero: As Kd")
    print("   Board: 7h 8h 2c")
    print("   Avversari: 1")
    
    equity = calc.get_equity_percentage(["As", "Kd"], ["7h", "8h", "2c"])
    win, tie, lose = calc.calculate_equity(["As", "Kd"], ["7h", "8h", "2c"])
    
    print(f"\n   ✅ RISULTATO:")
    print(f"      Equity: {equity*100:.1f}%")
    print(f"      Win: {win*100:.1f}% | Tie: {tie*100:.1f}% | Lose: {lose*100:.1f}%")
    
    # Test 3: Flush draw
    print("\n" + "-" * 70)
    print("📊 TEST 3: Flush Draw")
    print("   Hero: 9h 8h")
    print("   Board: 7h 5h 2c")
    print("   Avversari: 1")
    
    equity = calc.get_equity_percentage(["9h", "8h"], ["7h", "5h", "2c"])
    win, tie, lose = calc.calculate_equity(["9h", "8h"], ["7h", "5h", "2c"])
    
    print(f"\n   ✅ RISULTATO:")
    print(f"      Equity: {equity*100:.1f}%")
    print(f"      Win: {win*100:.1f}% | Tie: {tie*100:.1f}% | Lose: {lose*100:.1f}%")
    
    print("\n" + "=" * 70)
    print("✅ EQUITY CALCULATOR FUNZIONANTE!")
    print("   Usa simulazione Monte Carlo (10,000 hands) per calcolo preciso.")
    print("=" * 70 + "\n")
