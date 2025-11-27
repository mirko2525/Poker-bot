"""
POKER VISION AI - Riconoscimento carte con Gemini Vision

Versione Cross-Platform (Windows/Linux/Mac)
"""

import os
import base64
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

# Carica variabili d'ambiente
from dotenv import load_dotenv
load_dotenv()

# Gestione importazione libreria speciale
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
except ImportError:
    print("\n❌ ERRORE CRITICO: Libreria 'emergentintegrations' mancante.")
    print("   Se sei su Windows, esegui: install_windows.bat")
    print("   Oppure: pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/\n")
    # Non usciamo subito per permettere il debug, ma le funzioni falliranno
    LlmChat = None


class PokerVisionAI:
    """AI Vision per analisi completa tavoli poker."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("EMERGENT_LLM_KEY")
        
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY non trovata nel file .env")
        
        if LlmChat is None:
            raise ImportError("Libreria emergentintegrations non installata")
            
        self.model = "gemini-2.0-flash"
        self.provider = "gemini"
    
    def _encode_image_base64(self, image_path: str) -> str:
        from PIL import Image
        import io
        
        try:
            img = Image.open(image_path)
            
            # Resize intelligente
            max_size = 2048
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            buffer = io.BytesIO()
            img = img.convert("RGB")
            img.save(buffer, format="JPEG", quality=85)
            buffer.seek(0)
            
            return base64.b64encode(buffer.read()).decode("utf-8")
        except Exception as e:
            raise ValueError(f"Impossibile aprire immagine {image_path}: {e}")
    
    async def analyze_poker_table(self, screenshot_path: str, table_id: int = 1) -> Dict[str, Any]:
        """Analizza screenshot e ritorna dati strutturati."""
        
        # Verifica esistenza file
        if not os.path.exists(screenshot_path):
            print(f"❌ File non trovato: {screenshot_path}")
            return self._create_fallback_response(table_id)

        try:
            image_base64 = self._encode_image_base64(screenshot_path)
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"poker_vision_{table_id}",
                system_message=self._build_system_prompt(),
            ).with_model(self.provider, self.model)
            
            image_content = ImageContent(image_base64=image_base64)
            user_message = UserMessage(
                text=self._build_analysis_prompt(),
                file_contents=[image_content],
            )
            
            response = await chat.send_message(user_message)
            
            # Pulizia JSON
            response_text = response.strip()
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                # Rimuovi prima e ultima riga se sono backticks
                if lines[0].startswith("```"): lines.pop(0)
                if lines and lines[-1].startswith("```"): lines.pop()
                response_text = "\n".join(lines)
            
            result = json.loads(response_text)
            
            # Normalizzazione
            if "recommended_action" in result:
                result["recommended_action"] = result["recommended_action"].upper()
            
            result["table_id"] = table_id
            result["recognition_method"] = "vision_ai"
            
            return result
            
        except Exception as e:
            print(f"❌ Errore Vision AI: {e}")
            return self._create_fallback_response(table_id)
    
    def _build_system_prompt(self) -> str:
        return (
            "Sei un esperto analista di poker. "
            "Devi leggere con MASSIMA PRECISIONE le carte dal tavolo. "
            "Rispondi SOLO con JSON valido. Analisi in italiano."
        )
    
    def _build_analysis_prompt(self) -> str:
        return """Analizza lo screenshot del tavolo poker.

1. Identifica con precisione ASSOLUTA le carte di hero e del board.
   - Usa ESCLUSIVAMENTE questi rank: ["2","3","4","5","6","7","8","9","T","J","Q","K","A"]
   - Usa ESCLUSIVAMENTE questi semi: ["s","h","d","c"] (s = picche, h = cuori, d = quadri, c = fiori)
   - Ogni carta deve essere nel formato "RankSuit", per esempio: "As", "Kd", "7h".

2. EVITA ERRORI COMUNI:
   - NON confondere il K (K) con il 7.
   - NON confondere il 7 con il J.
   - NON confondere l'Asso (A) con il 4.
   - Se sei incerto tra due rank, scegli quello PIÙ COERENTE con le altre carte del tavolo.

3. Campi da restituire nel JSON:
   - hero_cards: array di 2 stringhe, es. ["As", "Kd"]
   - board_cards: array di 0-5 stringhe, es. ["7h", "8h", "2c"]
   - street: una di ["PREFLOP","FLOP","TURN","RIVER"]
   - hero_stack: float (stack effettivo di hero in chips o bb)
   - pot_size: float (piatto attuale)
   - to_call: float (importo che hero deve mettere per continuare)

4. Lascia all'esterno del modello il calcolo tecnico dell'equity e dell'azione.
   - NON sei tu a decidere se foldare/callare/raisare.
   - Puoi comunque fornire un commento strategico in italiano nel campo ai_comment.

Rispondi SOLO JSON, ad esempio:
{
  "hero_cards": ["As", "Kd"],
  "board_cards": ["7h", "8h", "2c"],
  "street": "FLOP",
  "hero_stack": 95.0,
  "pot_size": 12.0,
  "to_call": 5.0,
  "ai_comment": "Commento strategico in italiano..."
}"""

    def _create_fallback_response(self, table_id: int) -> Dict[str, Any]:
        return {
            "table_id": table_id,
            "hero_cards": [],
            "board_cards": [],
            "street": "UNKNOWN",
            "recommended_action": "CHECK",
            "equity_estimate": 0.5,
            "ai_comment": "Errore analisi immagine.",
            "error": "Vision AI failed"
        }

# --- TEST LOCALE ---
if __name__ == "__main__":
    async def test_local():
        print("\n--- TEST POKER VISION AI (LOCALE) ---")
        
        # Cerca immagine test
        current_dir = Path(__file__).parent
        img_path = current_dir / "data" / "screens" / "table1.png"
        
        # Se non esiste in data/screens, cerca nella root
        if not img_path.exists():
            img_path = current_dir / "table1.png"
            
        if not img_path.exists():
            print("❌ Nessuna immagine 'table1.png' trovata per il test.")
            print(f"   Cercato in: {img_path}")
            return

        try:
            bot = PokerVisionAI()
            print(f"📸 Analisi di: {img_path.name}")
            res = await bot.analyze_poker_table(str(img_path))
            print(json.dumps(res, indent=2))
        except Exception as e:
            print(f"❌ Errore: {e}")

    asyncio.run(test_local())
