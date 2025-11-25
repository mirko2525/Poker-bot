"""
Poker AI Advisor using Groq Cloud (Llama-3.3-70B)
Analizza la situazione di gioco e fornisce consigli in italiano

NUOVA ARCHITETTURA:
- analyze_table_state(): Il "cervello" che riceve JSON stato tavolo e ritorna decisione completa
- analyze_hand(): Metodo legacy per la demo (manteniamo per retrocompatibilità)
"""
import os
import json
from typing import List, Optional, Dict, Any
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
    
    def analyze_table_state(self, table_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        NUOVO METODO - Il "cervello" dell'advisor.
        
        Riceve lo stato completo del tavolo e ritorna:
        - Azione consigliata (FOLD/CALL/RAISE)
        - Importo del raise
        - Stima equity (0-1)
        - Livello di confidenza (0-1)
        - Commento AI in italiano
        
        Args:
            table_state: Dizionario con:
                - table_id: ID del tavolo
                - hero_cards: Lista carte hero (es. ["As", "Kd"])
                - board_cards: Lista carte board (es. ["7h", "8h", "2c"])
                - hero_stack: Stack dell'hero in dollari
                - pot_size: Dimensione piatto in dollari
                - to_call: Quanto bisogna chiamare
                - position: Posizione (es. "BTN", "SB", "BB", "EP", "MP", "CO")
                - players: Numero giocatori in mano
                - street: Fase (PREFLOP, FLOP, TURN, RIVER)
                - last_action: Ultima azione avversario (es. "villain_bet", "villain_raise")
                - big_blind: Valore del big blind (opzionale, default 1.0)
        
        Returns:
            Dizionario con:
                - recommended_action: "FOLD" | "CALL" | "RAISE"
                - recommended_amount: float (0 se FOLD/CALL)
                - equity_estimate: float (0-1)
                - confidence: float (0-1)
                - ai_comment: str (spiegazione in italiano)
        """
        # Costruisci prompt per Groq
        prompt = self._build_table_analysis_prompt(table_state)
        
        try:
            # Chiamata a Groq
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Sei un coach esperto di poker Texas Hold'em. "
                            "Analizza lo stato del tavolo e rispondi SOLO con JSON valido. "
                            "Non aggiungere testo extra, solo il JSON richiesto."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,  # Basso per risposte più consistenti
                max_completion_tokens=600,
                top_p=0.9,
                stream=False
            )
            
            # Estrai risposta
            raw_response = completion.choices[0].message.content.strip()
            
            # Prova a parsare JSON
            # Groq potrebbe wrappare il JSON in ```json ... ```, rimuoviamo
            if raw_response.startswith("```"):
                # Trova il contenuto tra i backticks
                lines = raw_response.split("\n")
                json_lines = []
                in_json = False
                for line in lines:
                    if line.strip().startswith("```"):
                        in_json = not in_json
                        continue
                    if in_json:
                        json_lines.append(line)
                raw_response = "\n".join(json_lines)
            
            result = json.loads(raw_response)
            
            # Validazione campi obbligatori
            required_fields = ["recommended_action", "recommended_amount", "equity_estimate", "confidence", "ai_comment"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Campo mancante nella risposta AI: {field}")
            
            # Normalizza l'azione
            result["recommended_action"] = result["recommended_action"].upper()
            
            return result
            
        except json.JSONDecodeError as e:
            # Fallback se JSON parsing fallisce
            print(f"⚠️ Errore parsing JSON da Groq: {e}")
            print(f"Raw response: {raw_response[:200]}...")
            return self._create_fallback_response(table_state)
        
        except Exception as e:
            # Fallback generico
            print(f"⚠️ Errore nell'analisi AI: {e}")
            return self._create_fallback_response(table_state)
    
    def _build_table_analysis_prompt(self, table_state: Dict[str, Any]) -> str:
        """Costruisce il prompt per l'analisi del tavolo."""
        
        # Formatta carte
        hero_str = ", ".join(table_state.get("hero_cards", [])) or "Non note"
        board_str = ", ".join(table_state.get("board_cards", [])) or "Nessuna carta"
        
        # Calcola pot odds se possibile
        to_call = table_state.get("to_call", 0)
        pot_size = table_state.get("pot_size", 0)
        pot_odds = (to_call / (pot_size + to_call) * 100) if (pot_size + to_call) > 0 else 0
        
        # Stack in BB
        bb = table_state.get("big_blind", 1.0)
        stack_bb = table_state.get("hero_stack", 100) / bb
        
        prompt = f"""Analizza questo stato di tavolo poker e rispondi SOLO in formato JSON.

STATO TAVOLO:
- Tavolo ID: {table_state.get("table_id", "1")}
- Fase: {table_state.get("street", "PREFLOP")}
- Tue carte: {hero_str}
- Board: {board_str}
- Piatto: ${pot_size:.2f}
- Da chiamare: ${to_call:.2f}
- Tuo stack: ${table_state.get("hero_stack", 100):.2f} ({stack_bb:.1f} BB)
- Posizione: {table_state.get("position", "Unknown")}
- Giocatori in mano: {table_state.get("players", 2)}
- Ultima azione avversario: {table_state.get("last_action", "unknown")}
- Pot odds: {pot_odds:.1f}%

RISPONDI SOLO CON QUESTO JSON (niente altro testo):

{{
  "recommended_action": "FOLD|CALL|RAISE",
  "recommended_amount": 0.0,
  "equity_estimate": 0.5,
  "confidence": 0.7,
  "ai_comment": "Spiegazione breve in italiano (3-5 frasi): analisi mano, considerazioni strategiche, ragionamento decisione."
}}

REGOLE:
- recommended_action: deve essere "FOLD", "CALL" o "RAISE"
- recommended_amount: importo in dollari del raise (0 se FOLD o CALL)
- equity_estimate: probabilità di vincere a showdown (0.0 a 1.0)
- confidence: quanto sei sicuro della decisione (0.0 a 1.0)
- ai_comment: spiegazione concisa in italiano

Rispondi SOLO con il JSON, niente altro."""
        
        return prompt
    
    def _create_fallback_response(self, table_state: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una risposta fallback se l'AI fallisce."""
        to_call = table_state.get("to_call", 0)
        
        return {
            "recommended_action": "CALL" if to_call > 0 else "CHECK",
            "recommended_amount": to_call,
            "equity_estimate": 0.5,
            "confidence": 0.3,
            "ai_comment": "⚠️ Analisi AI temporaneamente non disponibile. Usando strategia conservativa: call/check per vedere la prossima carta."
        }
    
    async def analyze_hand_async(self, *args, **kwargs) -> str:
        """Versione async dell'analisi (per compatibilità futura)."""
        # Per ora, Groq sync è sufficientemente veloce
        # In futuro si può implementare con async Groq client
        return self.analyze_hand(*args, **kwargs)


# Esempio di utilizzo
if __name__ == "__main__":
    from dotenv import load_dotenv
    from pathlib import Path
    
    # Load env
    load_dotenv(Path(__file__).parent / '.env')
    
    # Test del NUOVO metodo analyze_table_state
    advisor = PokerAIAdvisor()
    
    print("=" * 60)
    print("TEST NUOVO METODO: analyze_table_state()")
    print("=" * 60)
    
    table_state = {
        "table_id": 1,
        "hero_cards": ["As", "Kd"],
        "board_cards": ["7h", "8h", "2c"],
        "hero_stack": 95.50,
        "pot_size": 9.00,
        "to_call": 3.00,
        "position": "BTN",
        "players": 3,
        "street": "FLOP",
        "last_action": "villain_bet",
        "big_blind": 1.0
    }
    
    print("\n📊 Input stato tavolo:")
    print(json.dumps(table_state, indent=2, ensure_ascii=False))
    
    print("\n🤖 Chiamata a Groq AI...")
    result = advisor.analyze_table_state(table_state)
    
    print("\n✅ Risultato analisi:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print(f"Azione consigliata: {result['recommended_action']}")
    if result['recommended_action'] == 'RAISE':
        print(f"Importo raise: ${result['recommended_amount']:.2f}")
    print(f"Equity stimata: {result['equity_estimate']*100:.1f}%")
    print(f"Confidenza: {result['confidence']*100:.1f}%")
    print(f"\n💬 Commento AI:\n{result['ai_comment']}")
    print("=" * 60)
