"""
Poker AI Advisor using Groq Cloud (Llama-3.3-70B)
Analizza la situazione di gioco e fornisce consigli in italiano
"""
import os
from typing import List, Optional
from groq import Groq


class PokerAIAdvisor:
    """
    Consulente AI per poker che usa Groq Cloud con Llama-3.3-70B
    per fornire analisi dettagliate delle mani in italiano.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inizializza il consulente AI.
        
        Args:
            api_key: Chiave API Groq (se None, usa variabile ambiente GROQ_API_KEY)
        """
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY non trovata nelle variabili d'ambiente")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"
    
    def analyze_hand(
        self,
        hero_cards: List[str],
        board_cards: List[str],
        pot_size: float,
        to_call: float,
        hero_stack: float,
        big_blind: float,
        players_in_hand: int,
        phase: str,
        equity: float,
        suggested_action: str,
        raise_amount: float = 0.0
    ) -> str:
        """
        Analizza una mano di poker e fornisce un consiglio dettagliato in italiano.
        
        Args:
            hero_cards: Carte dell'hero (es. ["As", "Kh"])
            board_cards: Carte sul board (es. ["Qd", "Jc", "Ts"])
            pot_size: Dimensione del piatto
            to_call: Quanto bisogna chiamare
            hero_stack: Stack dell'hero
            big_blind: Valore del big blind
            players_in_hand: Numero di giocatori ancora in mano
            phase: Fase della mano (PREFLOP, FLOP, TURN, RIVER)
            equity: Equity stimata (0-100)
            suggested_action: Azione suggerita dal bot (FOLD, CALL, RAISE)
            raise_amount: Importo del raise suggerito
        
        Returns:
            Analisi dettagliata in italiano
        """
        # Costruisci il prompt per l'AI
        prompt = self._build_poker_prompt(
            hero_cards=hero_cards,
            board_cards=board_cards,
            pot_size=pot_size,
            to_call=to_call,
            hero_stack=hero_stack,
            big_blind=big_blind,
            players_in_hand=players_in_hand,
            phase=phase,
            equity=equity,
            suggested_action=suggested_action,
            raise_amount=raise_amount
        )
        
        try:
            # Chiamata all'API Groq
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Sei un esperto coach di poker Texas Hold'em. "
                            "Fornisci analisi chiare, concrete e strategiche in italiano. "
                            "Sii conciso ma completo (max 4-5 frasi). "
                            "Usa terminologia poker italiana quando appropriato."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Basso per risposte più consistenti
                max_completion_tokens=300,  # Limitato per risposte concise
                top_p=0.9,
                stream=False,
                stop=None
            )
            
            # Estrai la risposta
            analysis = completion.choices[0].message.content.strip()
            return analysis
            
        except Exception as e:
            # Fallback in caso di errore
            return f"⚠️ Errore nell'analisi AI: {str(e)}"
    
    def _build_poker_prompt(
        self,
        hero_cards: List[str],
        board_cards: List[str],
        pot_size: float,
        to_call: float,
        hero_stack: float,
        big_blind: float,
        players_in_hand: int,
        phase: str,
        equity: float,
        suggested_action: str,
        raise_amount: float
    ) -> str:
        """Costruisce il prompt dettagliato per l'analisi poker."""
        
        # Formatta le carte in modo leggibile
        hero_str = ", ".join(hero_cards) if hero_cards else "Non note"
        board_str = ", ".join(board_cards) if board_cards else "Nessuna carta sul board"
        
        # Calcola pot odds
        pot_odds = (to_call / (pot_size + to_call) * 100) if to_call > 0 else 0
        
        # Stack in BB
        stack_bb = hero_stack / big_blind if big_blind > 0 else 0
        
        # Costruisci il prompt
        prompt = f"""Analizza questa situazione di poker Texas Hold'em:

SITUAZIONE:
- Fase: {phase}
- Tue carte: {hero_str}
- Board: {board_str}
- Piatto: ${pot_size:.2f}
- Da chiamare: ${to_call:.2f}
- Tuo stack: ${hero_stack:.2f} ({stack_bb:.1f} BB)
- Giocatori in mano: {players_in_hand}

DATI TECNICI:
- Equity stimata: {equity:.1f}%
- Pot odds: {pot_odds:.1f}%
- Azione suggerita: {suggested_action}"""
        
        if suggested_action == "RAISE" and raise_amount > 0:
            prompt += f" (${raise_amount:.2f})"
        
        prompt += """

Fornisci un'analisi concisa che includa:
1. Valutazione della forza della mano nel contesto
2. Considerazioni strategiche chiave
3. Supporto alla decisione suggerita (o alternative se opportuno)

Rispondi in italiano, massimo 4-5 frasi."""
        
        return prompt
    
    async def analyze_hand_async(self, *args, **kwargs) -> str:
        """Versione async dell'analisi (per compatibilità futura)."""
        # Per ora, Groq sync è sufficientemente veloce
        # In futuro si può implementare con async Groq client
        return self.analyze_hand(*args, **kwargs)


# Esempio di utilizzo
if __name__ == "__main__":
    # Test del servizio
    advisor = PokerAIAdvisor()
    
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
    
    print("🤖 Analisi AI:")
    print(analysis)
