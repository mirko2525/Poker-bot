from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio
from shared_state import SharedState # Import memoria condivisa

# --- SETUP BASE ---
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Import Vision Analyzer Router (IL CUORE DEL SISTEMA)
from vision_analyzer_api import vision_router
api_router.include_router(vision_router)

# --- GROQ AI (OPZIONALE - DISABILITATO SE MANCA) ---
try:
    from poker_ai_advisor import PokerAIAdvisor
    # Test import Groq
    from groq import Groq
    ai_advisor = PokerAIAdvisor()
    print("✅ Groq AI Advisor caricato (Opzionale)")
except ImportError:
    print("⚠️ Libreria 'groq' non trovata. Il modulo 'Live Analyze' classico sarà disabilitato.")
    print("   (Nessun problema: stiamo usando Vision AI!)")
    ai_advisor = None
except Exception as e:
    print(f"⚠️ Errore inizializzazione Groq: {e}")
    ai_advisor = None

# --- ENDPOINT PER OVERLAY ---
@api_router.get("/poker/live/latest")
async def get_latest_analysis():
    """L'Overlay chiama questo endpoint per sapere cosa mostrare."""
    return SharedState.latest_analysis

# --- ROUTES BASE ---
@api_router.get("/")
async def root():
    return {"message": "Poker Bot Vision API - Ready"}

app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
