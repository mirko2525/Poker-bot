"""
VISION ANALYZER API - Endpoint dedicato per analisi screenshot manuale
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from typing import Dict, Any
import logging
from equity_calculator import EquityCalculator
from poker_config import (
    MARGIN,
    STRONG_EQUITY_THRESHOLD,
    RAISE_POT_MULTIPLIER,
    RAISE_NO_COST_MULTIPLIER,
)
from typing import Optional


from shared_state import SharedState # Import memoria condivisa

# Import del modulo Vision AI
from poker_vision_ai import PokerVisionAI


def _compute_math_equity_and_decision(vision_result: Dict[str, Any]) -> Dict[str, Any]:
    """Calcola equity matematica (HU) + decisione FOLD/CALL/RAISE.

    Usa EquityCalculator (Monte Carlo) e le costanti di poker_config.
    Ignora completamente equity/azione proposte da Gemini.
    """
    hero_cards = vision_result.get("hero_cards") or []
    board_cards = vision_result.get("board_cards") or []
    hero_stack = float(vision_result.get("hero_stack") or 0.0)
    pot_size = float(vision_result.get("pot_size") or 0.0)
    to_call = float(vision_result.get("to_call") or 0.0)
    street: str = (vision_result.get("street") or "").upper() or "UNKNOWN"

    # Calcolo equity HU (num_opponents=1)
    equity_calc = EquityCalculator()
    equity_math = equity_calc.get_equity_percentage(hero_cards, board_cards, num_opponents=1)

    # Pot odds di base (se c'è da chiamare)
    pot_odds = None
    if to_call > 0 and (pot_size + to_call) > 0:
        pot_odds = to_call / (pot_size + to_call)

    # Decisione semplice HU basata su equity vs pot odds
    action = "CHECK"
    amount = 0.0

    if to_call <= 0:
        # Nessun costo per vedere: decidiamo se bet/raise o check
        if equity_math >= STRONG_EQUITY_THRESHOLD:
            action = "RAISE"
            amount = max(0.0, pot_size * RAISE_NO_COST_MULTIPLIER)
        else:
            action = "CHECK"
            amount = 0.0
    else:
        # C'è una bet da affrontare → confronto equity vs pot odds
        if pot_odds is not None and equity_math + MARGIN < pot_odds:
            # Equity insufficiente rispetto alle odds → fold
            action = "FOLD"
            amount = 0.0
        elif equity_math >= STRONG_EQUITY_THRESHOLD:
            # Mano molto forte → raise per valore
            action = "RAISE"
            amount = max(to_call * 2, pot_size * RAISE_POT_MULTIPLIER)
        else:
            # Spot intermedio → call
            action = "CALL"
            amount = to_call

    # Costruiamo risultato finale sovrascrivendo sempre i campi decisionali
    result = dict(vision_result)  # copy
    result["equity_estimate"] = float(equity_math)
    result["recommended_action"] = action
    result["recommended_amount"] = float(amount)

    # Confidence derivata da quanto equity supera pot_odds (se definite)
    confidence = 0.5
    try:
        if pot_odds is not None:
            margin = max(0.0, equity_math - pot_odds)
            # normalizziamo con un fattore (es. 0.25) per comprimere tra 0.5 e 1.0
            confidence = max(0.5, min(1.0, 0.5 + margin / 0.25))
        else:
            # se non ci sono pot odds (to_call=0), usiamo equity vs soglia forte
            margin = max(0.0, equity_math - STRONG_EQUITY_THRESHOLD)
            confidence = max(0.5, min(1.0, 0.5 + margin / 0.25))
    except Exception:
        confidence = 0.5

    result["confidence"] = float(confidence)

    # Log per confronto debugging: equity gemini vs matematica
    equity_gemini = vision_result.get("equity_estimate")
    logger.info(
        "🎯 Equity math=%.3f, equity_gemini=%s, action=%s, amount=%.2f, pot=%.2f, to_call=%.2f",
        equity_math,
        str(equity_gemini),
        action,
        amount,
        pot_size,
        to_call,
    )

    return result



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
        
        # Analisi Vision (lettura tavolo)
        logger.info("🧠 Analisi con Gemini Vision (lettura stato tavolo)...")
        vision_result = await vision_ai.analyze_poker_table(str(temp_path), table_id=999)

        # Calcolo equity matematica + decisione HU (Fase 1)
        math_result = _compute_math_equity_and_decision(vision_result)

        # --- AGGIORNAMENTO MEMORIA PER OVERLAY ---
        SharedState.update(math_result)
        logger.info(
            "✅ Analisi completata (math-driven) e salvata per Overlay: %s",
            math_result.get("recommended_action"),
        )
        # -----------------------------------------

        return {
            "status": "success",
            "message": "Analisi completata",
            "analysis": math_result,
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
