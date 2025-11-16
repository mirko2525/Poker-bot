"""
Configurazione Poker Bot - Costanti Configurabili

Questo file contiene tutte le costanti configurabili per il DecisionEngine e MockEquityEngine.
Ordini del Capo - Fase 2: Rendere i parametri "magici" facilmente modificabili.
"""

# ===== DECISION ENGINE CONSTANTS =====

# Margine per confronto equity vs pot odds (5%)
MARGIN = 0.05

# Soglia equity per essere considerata "forte" (65%)
STRONG_EQUITY_THRESHOLD = 0.65

# Soglia stack in BB per considerare all-in con short stack (10 BB)
ALLIN_STACK_BB_THRESHOLD = 10

# Soglia stack in BB per situazioni borderline (20 BB)
SHORT_STACK_BORDERLINE_BB = 20

# Equity minima per all-in con short stack (55%)
HIGH_EQUITY_FOR_ALLIN = 0.55

# Moltiplicatore pot per calcolo raise (0.75x pot)
RAISE_POT_MULTIPLIER = 0.75

# Moltiplicatore pot per raise quando non c'è costo per vedere (0.5x pot)
RAISE_NO_COST_MULTIPLIER = 0.5

# ===== MOCK EQUITY ENGINE CONSTANTS =====

# Range randomness per rendere più realistici i calcoli equity
EQUITY_RANDOM_RANGE_PREFLOP = 5.0  # +/- 5% per preflop
EQUITY_RANDOM_RANGE_POSTFLOP = 10.0  # +/- 10% per postflop

# Boost equity per hitting the board
BOARD_HIT_EQUITY_BOOST = 15.0

# Moltiplicatori equity per fasi
PHASE_MULTIPLIERS = {
    "FLOP": 0.8,
    "TURN": 0.9,
    "RIVER": 1.0
}

# Limiti equity (min/max)
MIN_EQUITY = 5.0
MAX_EQUITY_PREFLOP = 95.0
MAX_EQUITY_POSTFLOP = 95.0
