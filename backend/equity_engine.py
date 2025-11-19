from typing import List, Dict


def compute_equity_stub(
    hero_cards: List[str],
    board_cards: List[str],
    num_players: int,
) -> Dict[str, float]:
    """Stub temporaneo per il calcolo dell'equity.

    In futuro qui inseriremo la vera logica (Montecarlo / enumerazione completa).
    Per ora ritorna un valore fittizio ma coerente come struttura.
    """
    # TODO: sostituire con calcolo reale
    return {
        "win": 0.50,
        "tie": 0.05,
        "lose": 0.45,
    }
