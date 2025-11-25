"""
VISION ANALYZER API - Endpoint dedicato per analisi screenshot manuale

File separato e pulito per non mischiare con il resto del codice.
Gestisce upload screenshot e analisi con Gemini Vision.

Endpoint: POST /api/vision/analyze
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from typing import Dict, Any
import logging

# Import del modulo Vision AI
from poker_vision_ai import PokerVisionAI

logger = logging.getLogger(__name__)

# Router dedicato
vision_router = APIRouter(prefix="/vision", tags=["Vision AI"])

# Directory per screenshot temporanei
TEMP_DIR = Path(__file__).parent / "data" / "temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)


@vision_router.post("/analyze")
async def analyze_screenshot(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Analizza uno screenshot di un tavolo poker con Gemini Vision AI.
    
    Upload manuale dall'utente (es. da iPhone).
    
    Args:
        file: Immagine PNG/JPG del tavolo poker
    
    Returns:
        JSON con:
        - hero_cards: ["As", "Kd"]
        - board_cards: ["7h", "8h", "2c"]
        - street: "FLOP"
        - recommended_action: "FOLD" | "CALL" | "RAISE"
        - equity_estimate: 0.65
        - confidence: 0.80
        - ai_comment: "Analisi in italiano..."
    """
    try:
        # Valida tipo file
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="File deve essere un'immagine (PNG, JPG, JPEG)"
            )
        
        # Salva temporaneamente
        temp_path = TEMP_DIR / f"upload_{file.filename}"
        
        contents = await file.read()
        with open(temp_path, "wb") as f:
            f.write(contents)
        
        logger.info(f"📸 Screenshot ricevuto: {file.filename} ({len(contents)} bytes)")
        
        # Inizializza Vision AI
        vision_ai = PokerVisionAI()
        
        # Analisi
        logger.info("🧠 Analisi con Gemini Vision...")
        result = await vision_ai.analyze_poker_table(str(temp_path), table_id=999)
        
        logger.info(f"✅ Analisi completata: {result.get('recommended_action')}")
        
        # Cleanup (opzionale, tieni se vuoi vedere gli upload)
        # temp_path.unlink()
        
        return {
            "status": "success",
            "message": "Analisi completata",
            "analysis": result
        }
        
    except Exception as e:
        logger.error(f"❌ Errore analisi Vision: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Errore durante l'analisi: {str(e)}"
        )


@vision_router.get("/health")
async def health_check():
    """Health check per Vision API."""
    return {
        "status": "online",
        "service": "Vision AI Analyzer",
        "model": "Gemini 2.0 Flash"
    }
