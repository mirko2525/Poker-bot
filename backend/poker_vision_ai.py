"""
POKER VISION AI - Riconoscimento carte con Gemini Vision

Elimina il template matching! L'AI vede direttamente lo screenshot
e riconosce tutto: carte hero, board, stack, pot, fase di gioco.

Architettura:
Screenshot → Gemini Vision → JSON con carte + Equity Calculator matematico
"""
import os
import base64
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Carica env
load_dotenv()

from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
from equity_calculator import EquityCalculator


class PokerVisionAI:
    """
    AI Vision per analisi completa tavoli poker.
    
    Un unico modello fa tutto:
    - Riconosce carte hero e board
    - Legge stack, pot, to_call
    - Analizza situazione strategica
    - Suggerisce azione
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inizializza Vision AI.
        
        Args:
            api_key: Emergent LLM key (se None, usa env EMERGENT_LLM_KEY)
        """
        self.api_key = api_key or os.environ.get("EMERGENT_LLM_KEY")
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY non trovata")
        
        # Usa Gemini 2.0 Flash (veloce e gratis)
        self.model = "gemini-2.0-flash"
        self.provider = "gemini"
        
        # Equity calculator matematico (Monte Carlo)
        self.equity_calc = EquityCalculator()
    
    def _encode_image_base64(self, image_path: str) -> str:
        """Converte immagine in base64, con resize se troppo grande."""
        from PIL import Image
        import io
        
        # Carica immagine
        img = Image.open(image_path)
        
        # Resize se troppo grande (Gemini preferisce immagini più piccole)
        max_size = 2048
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            print(f"   Immagine ridimensionata a {img.width}x{img.height}")
        
        # Converti in JPG per ridurre dimensione
        buffer = io.BytesIO()
        img = img.convert("RGB")  # Rimuovi alpha channel se presente
        img.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        
        return base64.b64encode(buffer.read()).decode('utf-8')
    
    async def analyze_poker_table(
        self,
        screenshot_path: str,
        table_id: int = 1
    ) -> Dict[str, Any]:
        """
        Analizza screenshot tavolo poker e ritorna tutto.
        
        Args:
            screenshot_path: Path allo screenshot
            table_id: ID tavolo
        
        Returns:
            dict con:
                - hero_cards: ["As", "Kd"]
                - board_cards: ["7h", "8h", "2c"]
                - street: "FLOP"
                - hero_stack: 95.0
                - pot_size: 12.0
                - to_call: 5.0
                - recommended_action: "FOLD" | "CALL" | "RAISE"
                - recommended_amount: 9.0
                - equity_estimate: 0.30
                - confidence: 0.80
                - ai_comment: "Analisi in italiano..."
        """
        # Encode immagine
        image_base64 = self._encode_image_base64(screenshot_path)
        
        # Crea chat session
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"poker_vision_{table_id}",
            system_message=self._build_system_prompt()
        ).with_model(self.provider, self.model)
        
        # Crea messaggio con immagine
        image_content = ImageContent(image_base64=image_base64)
        
        user_message = UserMessage(
            text=self._build_analysis_prompt(),
            file_contents=[image_content]
        )
        
        try:
            # Chiamata AI
            response = await chat.send_message(user_message)
            
            # Parse JSON dalla risposta
            import json
            
            # Rimuovi markdown code blocks se presenti
            response_text = response.strip()
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                json_lines = []
                in_json = False
                for line in lines:
                    if line.strip().startswith("```"):
                        in_json = not in_json
                        continue
                    if in_json:
                        json_lines.append(line)
                response_text = "\n".join(json_lines)
            
            result = json.loads(response_text)
            
            # Validazione campi obbligatori
            required_fields = [
                "hero_cards", "board_cards", "street",
                "recommended_action", "recommended_amount",
                "equity_estimate", "confidence", "ai_comment"
            ]
            
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Campo mancante: {field}")
            
            # Normalizza azione
            result["recommended_action"] = result["recommended_action"].upper()
            
            # 🎯 CALCOLO EQUITY MATEMATICO (sostituisce stima AI)
            if len(result["hero_cards"]) == 2 and len(result["board_cards"]) <= 5:
                try:
                    # Calcola equity con Monte Carlo
                    equity_math = self.equity_calc.get_equity_percentage(
                        result["hero_cards"],
                        result["board_cards"],
                        num_opponents=1
                    )
                    
                    # Sostituisci equity AI con equity matematica
                    result["equity_estimate_ai"] = result["equity_estimate"]  # Backup
                    result["equity_estimate"] = equity_math
                    result["equity_method"] = "monte_carlo"
                    
                    print(f"   🎲 Equity calcolata: {equity_math*100:.1f}% (Monte Carlo)")
                    
                except Exception as e:
                    print(f"   ⚠️ Fallback su equity AI: {e}")
                    result["equity_method"] = "ai_estimate"
            else:
                result["equity_method"] = "ai_estimate"
            
            # Aggiungi metadata
            result["table_id"] = table_id
            result["recognition_method"] = "vision_ai"
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"⚠️ Errore parsing JSON: {e}")
            print(f"Response: {response[:200]}...")
            return self._create_fallback_response(table_id)
        
        except Exception as e:
            print(f"❌ Errore Vision AI: {e}")
            return self._create_fallback_response(table_id)
    
    def _build_system_prompt(self) -> str:
        """Sistema prompt per Vision AI."""
        return """Sei un esperto analista di poker Texas Hold'em con visione artificiale.

Il tuo compito è analizzare screenshot di tavoli poker e fornire:
1. Riconoscimento carte (hero e board)
2. Lettura valori (stack, pot, to call)
3. Analisi strategica
4. Raccomandazione azione

IMPORTANTE:
- Rispondi SOLO con JSON valido
- Non aggiungere testo extra
- Usa notazione carte standard (As = Asso Picche, Kh = Re Cuori, etc)
- Analisi in italiano
- Sii preciso nel riconoscimento"""
    
    def _build_analysis_prompt(self) -> str:
        """Prompt per analisi screenshot."""
        return """Analizza questo screenshot di un tavolo poker Texas Hold'em.

Identifica:
1. **Carte Hero** (le 2 carte del giocatore in basso)
2. **Carte Board** (le carte comunitarie al centro, max 5)
3. **Street** (PREFLOP se board vuoto, FLOP se 3 carte, TURN se 4, RIVER se 5)
4. **Stack Hero** (chip del giocatore in basso, stima se non chiaro)
5. **Pot Size** (dimensione piatto al centro)
6. **To Call** (quanto deve chiamare il giocatore, 0 se check disponibile)

Poi fornisci:
- **Azione consigliata**: FOLD, CALL, CHECK o RAISE
- **Importo raise** (se RAISE, quanto in dollari, altrimenti 0)
- **Equity stimata** (metti un valore ragionevole 0-1, verrà ricalcolato matematicamente dopo)
- **Confidenza** (quanto sei sicuro 0-1, esempio 0.80 = molto sicuro)
- **Commento AI** (spiegazione breve in italiano, 3-5 frasi)
  ⚠️ IMPORTANTE: NON menzionare percentuali di equity nel commento!
  L'equity verrà calcolata matematicamente dopo, quindi non scrivere "hai 32% equity" o simili.
  Concentrati su: forza mano, pot odds, posizione, range avversario, strategia.

Rispondi SOLO con questo JSON (niente altro testo):

{
  "hero_cards": ["As", "Kd"],
  "board_cards": ["7h", "8h", "2c"],
  "street": "FLOP",
  "hero_stack": 95.0,
  "pot_size": 12.0,
  "to_call": 5.0,
  "recommended_action": "FOLD",
  "recommended_amount": 0.0,
  "equity_estimate": 0.30,
  "confidence": 0.80,
  "ai_comment": "La tua mano non ha migliorato con questo board. Con solo overcard e pot odds sfavorevoli (29%), il fold è la scelta corretta per preservare lo stack."
}

NOTE CRITICHE PER EQUITY:
- hero_cards: array di 2 stringhe (es. ["Qs", "Jc"])
- board_cards: array di 0-5 stringhe
- street: "PREFLOP" | "FLOP" | "TURN" | "RIVER"
- Valori numerici: float
- recommended_action: "FOLD" | "CALL" | "CHECK" | "RAISE"
- Tutto in italiano nel commento

⚠️ REGOLA CRITICA PER IL COMMENTO:
NON menzionare MAI percentuali di equity nel commento AI!
Frasi VIETATE: "hai 32% equity", "equity bassa", "solo 40% di vincita", etc.

Il commento deve parlare di:
- Forza della mano (es. "mano debole", "top pair", "draw forte")
- Pot odds (es. "devi chiamare $5 per vincere $15")
- Posizione e dinamiche
- Range avversario probabile
- Strategia generale

Esempio CORRETTO: "La tua mano è debole su questo board. Con un piccolo stack, è meglio conservare le chips per situazioni più favorevoli."

Esempio SBAGLIATO: "La tua mano ha solo il 32% di equity, quindi fold." ❌

Se non riesci a leggere qualcosa con certezza, fai una stima ragionevole."""
    
    def _create_fallback_response(self, table_id: int) -> Dict[str, Any]:
        """Risposta fallback se Vision fallisce."""
        return {
            "table_id": table_id,
            "hero_cards": [],
            "board_cards": [],
            "street": "UNKNOWN",
            "hero_stack": 100.0,
            "pot_size": 10.0,
            "to_call": 0.0,
            "recommended_action": "CHECK",
            "recommended_amount": 0.0,
            "equity_estimate": 0.5,
            "confidence": 0.1,
            "ai_comment": "⚠️ Impossibile analizzare lo screenshot. Verifica che il tavolo poker sia visibile e ben inquadrato.",
            "recognition_method": "vision_ai",
            "error": "Vision AI fallback"
        }


# Test standalone
if __name__ == "__main__":
    import asyncio
    
    async def test_vision():
        print("\n" + "=" * 70)
        print("TEST POKER VISION AI")
        print("=" * 70 + "\n")
        
        vision_ai = PokerVisionAI()
        
        # Usa screenshot esistente
        screenshot_path = "/app/backend/data/screens/table1.png"
        
        if not Path(screenshot_path).exists():
            print(f"❌ Screenshot non trovato: {screenshot_path}")
            return
        
        print(f"📸 Analisi screenshot: {screenshot_path}")
        print("🧠 Chiamata Gemini Vision...")
        
        result = await vision_ai.analyze_poker_table(screenshot_path)
        
        print("\n✅ RISULTATO:")
        print(f"   Hero: {result.get('hero_cards', [])}")
        print(f"   Board: {result.get('board_cards', [])}")
        print(f"   Street: {result.get('street')}")
        print(f"   Stack: ${result.get('hero_stack', 0):.2f}")
        print(f"   Pot: ${result.get('pot_size', 0):.2f}")
        print(f"   To Call: ${result.get('to_call', 0):.2f}")
        print(f"\n   Azione: {result.get('recommended_action')}", end="")
        if result.get('recommended_action') == 'RAISE':
            print(f" ${result.get('recommended_amount', 0):.2f}")
        else:
            print()
        print(f"   Equity: {result.get('equity_estimate', 0)*100:.1f}%")
        print(f"   Confidenza: {result.get('confidence', 0)*100:.1f}%")
        print(f"\n   💬 {result.get('ai_comment', '')}")
        print("\n" + "=" * 70)
    
    asyncio.run(test_vision())
