from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional, Tuple
import uuid
from datetime import datetime, timezone
import random
import asyncio
import cv2

# --- MONGODB SETUP (OPZIONALE) ---
# Gestiamo il caso in cui Motor o MongoDB non siano disponibili
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    MOTOR_AVAILABLE = True
except ImportError:
    MOTOR_AVAILABLE = False
    print("⚠️ Libreria 'motor' non trovata. Modalità senza Database (In-Memory).")

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configurazione DB
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'poker_db')

class MockDB:
    """Database finto in memoria per quando MongoDB non c'è."""
    def __init__(self):
        self.status_checks = MockCollection()

class MockCollection:
    def __init__(self):
        self.data = []
    async def insert_one(self, doc):
        self.data.append(doc)
        return True
    def find(self, query, projection=None):
        return self
    async def to_list(self, length):
        return self.data[-length:]

# Inizializzazione Client DB
client = None
db = None

if MOTOR_AVAILABLE:
    try:
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=2000)
        db = client[db_name]
        print(f"✅ MongoDB configurato: {mongo_url}")
    except Exception as e:
        print(f"⚠️ Errore connessione MongoDB: {e}")
        print("   Passaggio a modalità In-Memory.")
        db = MockDB()
else:
    db = MockDB()

# --- FINE SETUP DB ---

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Import Vision Analyzer Router (nuovo sistema separato)
from vision_analyzer_api import vision_router
api_router.include_router(vision_router)


# Define Models for Poker Bot
class HandState(BaseModel):
    hero_cards: List[str] = Field(..., description="Player's hole cards")
    board_cards: List[str] = Field(..., description="Community cards on board")
    hero_stack: float = Field(..., description="Player's current stack")
    pot_size: float = Field(..., description="Current pot size")
    to_call: float = Field(..., description="Amount to call")
    big_blind: float = Field(..., description="Big blind value")
    players_in_hand: int = Field(..., description="Number of active players")
    phase: str = Field(..., description="Hand phase: PREFLOP, FLOP, TURN, RIVER")


class Decision(BaseModel):
    action: str = Field(..., description="FOLD, CALL, or RAISE")
    raise_amount: float = Field(default=0.0, description="Amount to raise if action is RAISE")
    reason: Optional[str] = Field(default=None, description="Reason for the decision")
    equity: float = Field(..., description="Calculated equity percentage")
    pot_odds: Optional[float] = Field(default=None, description="Pot odds percentage")
    ai_analysis: Optional[str] = Field(default=None, description="AI-powered analysis in Italian")


class DemoResponse(BaseModel):
    hand_number: int
    hand_state: HandState
    decision: Decision
    has_next: bool


# Models for table card recognition
class RecognizedCard(BaseModel):
    code: Optional[str] = Field(default=None, description="Recognized card code like 'Kd' or None")
    score: float = Field(..., description="Template matching score [0-1]")
    conf: str = Field(..., description="Confidence flag: strong | weak | none")
    bbox: Optional[Tuple[int, int, int, int]] = Field(default=None, description="Bounding box (x,y,w,h)")


class TableCardsResponse(BaseModel):
    table_id: str
    image_path: str
    debug_image_path: Optional[str] = None
    updated_at: Optional[datetime]
    status: str  # ok | pending | no_image | error
    hero: List[RecognizedCard]
    board: List[RecognizedCard]
    error: Optional[str] = None


class TableEquityResponse(BaseModel):
    table_id: str
    num_players: int
    hero_cards: List[str]
    board_cards: List[str]
    status: str  # ok | missing_cards | error
    hero_win: float
    hero_tie: float
    hero_lose: float
    error: Optional[str] = None


# NEW: Models for Live Analyze (AI Brain)
class LiveTableState(BaseModel):
    """Input model per /api/poker/live/analyze"""
    table_id: int = Field(..., description="ID del tavolo")
    hero_cards: List[str] = Field(..., description="Carte dell'hero (es. ['As', 'Kd'])")
    board_cards: List[str] = Field(default=[], description="Carte sul board")
    hero_stack: float = Field(..., description="Stack hero in dollari")
    pot_size: float = Field(..., description="Dimensione piatto")
    to_call: float = Field(..., description="Quanto bisogna chiamare")
    position: str = Field(..., description="Posizione (BTN, SB, BB, EP, MP, CO)")
    players: int = Field(..., description="Numero giocatori in mano")
    street: str = Field(..., description="Fase: PREFLOP, FLOP, TURN, RIVER")
    last_action: str = Field(..., description="Ultima azione (es. 'villain_bet')")
    big_blind: float = Field(default=1.0, description="Valore big blind")


class LiveAnalysisResponse(BaseModel):
    """Output model per /api/poker/live/analyze"""
    table_id: int
    recommended_action: str = Field(..., description="FOLD, CALL, or RAISE")
    recommended_amount: float = Field(..., description="Importo in dollari (0 se FOLD/CALL)")
    equity_estimate: float = Field(..., description="Stima equity 0-1")
    confidence: float = Field(..., description="Livello confidenza 0-1")
    ai_comment: str = Field(..., description="Spiegazione AI in italiano")


# Initialize table recognition components (Fase tavolo reale)
TABLE_SCREEN_PATH = ROOT_DIR / "data" / "screens" / "table1.png"
TABLE_DEBUG_PATH = ROOT_DIR / "data" / "screens" / "table1_debug.png"

# Importazioni condizionali per evitare crash se mancano librerie
try:
    from card_recognition_fullcard import FullCardRecognizer
    from card_recognition_hero_back import HeroBackRecognizer
    from pokerstars_layout_real import (
        PokerStarsLayout2048x1279,
        recognize_table_cards_pokerstars,
    )
    RECOGNITION_AVAILABLE = True
    TABLE_LAYOUT = PokerStarsLayout2048x1279()
    CARD_RECOGNIZER = FullCardRecognizer()
    HERO_BACK_TEMPLATES_DIR = ROOT_DIR / "card_templates" / "pokerstars" / "hero_back"
    HERO_BACK_RECOGNIZER = HeroBackRecognizer(HERO_BACK_TEMPLATES_DIR)
except ImportError as e:
    print(f"⚠️ Moduli riconoscimento non disponibili: {e}")
    RECOGNITION_AVAILABLE = False


# In-memory state for last recognized table
TABLE_STATE: Dict[str, Any] = {
    "result": None,
    "error": None,
    "updated_at": None,
}


def save_table_debug_overlay(screen_bgr, recognition: Dict[str, Any], out_path: Path) -> None:
    """Disegna rettangoli su hero/board + codice/conf/score e salva PNG di debug."""
    debug = screen_bgr.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX

    def draw_group(cards, color):
        for c in cards:
            bbox = c.get("bbox")
            if not bbox:
                continue

            code = c.get("code") or "??"
            conf = c.get("conf") or "none"
            score = c.get("score", 0.0)
            try:
                score_f = float(score)
            except (TypeError, ValueError):
                score_f = 0.0

            x, y, w, h = bbox

            # rettangolo
            cv2.rectangle(
                debug,
                (int(x), int(y)),
                (int(x + w), int(y + h)),
                color,
                2,
            )

            # etichetta sopra la carta
            label = f"{code} {conf} {score_f:.2f}"
            text_scale = 0.5
            text_thickness = 1

            (tw, th), _ = cv2.getTextSize(label, font, text_scale, text_thickness)
            text_x = int(x)
            text_y = int(y) - 5
            if text_y - th < 0:
                text_y = int(y + h + th + 5)

            cv2.putText(
                debug,
                label,
                (text_x, text_y),
                font,
                text_scale,
                color,
                text_thickness,
                cv2.LINE_AA,
            )

    # Hero in verde, board in blu
    draw_group(recognition.get("hero", []), (0, 255, 0))
    draw_group(recognition.get("board", []), (255, 0, 0))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), debug)


async def update_table_cards_once() -> None:
    """Legge lo screenshot del tavolo e aggiorna TABLE_STATE."""
    if not RECOGNITION_AVAILABLE:
        return

    if not TABLE_SCREEN_PATH.exists():
        msg = f"Screenshot file not found: {TABLE_SCREEN_PATH}"
        # logger.warning(msg) # Rimosso per ridurre log
        TABLE_STATE["result"] = None
        TABLE_STATE["error"] = msg
        TABLE_STATE["updated_at"] = None
        return

    screen_bgr = cv2.imread(str(TABLE_SCREEN_PATH))
    if screen_bgr is None:
        msg = f"Failed to read screenshot image at {TABLE_SCREEN_PATH}"
        logger.error(msg)
        TABLE_STATE["result"] = None
        TABLE_STATE["error"] = msg
        TABLE_STATE["updated_at"] = None
        return

    try:
        recognition = recognize_table_cards_pokerstars(
            screen_bgr,
            TABLE_LAYOUT,
            CARD_RECOGNIZER,
            HERO_BACK_RECOGNIZER,
        )
        hero_codes = [card.get("code") for card in recognition.get("hero", [])]
        board_codes = [card.get("code") for card in recognition.get("board", [])]
        logger.info(
            "Table recognition updated - hero: %s | board: %s",
            hero_codes,
            board_codes,
        )

        # Salva crop hero per debug (hero_1.png, hero_2.png)
        try:
            debug_dir = ROOT_DIR / "data" / "screens"
            debug_dir.mkdir(parents=True, exist_ok=True)
            for i, card in enumerate(recognition.get("hero", [])):
                bbox = card.get("bbox")
                if not bbox:
                    continue
                x, y, w_box, h_box = bbox
                crop = screen_bgr[y:y + h_box, x:x + w_box]
                hero_path = debug_dir / f"hero_{i+1}.png"
                cv2.imwrite(str(hero_path), crop)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to save hero crops: %s", exc)

        # Salva overlay di debug
        try:
            save_table_debug_overlay(screen_bgr, recognition, TABLE_DEBUG_PATH)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to save debug overlay: %s", exc)

        TABLE_STATE["result"] = recognition
        TABLE_STATE["error"] = None
        TABLE_STATE["updated_at"] = datetime.now(timezone.utc)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Error during table cards recognition: %s", exc)
        # Manteniamo l'ultimo stato valido in caso di errore
        TABLE_STATE["error"] = str(exc)


def build_table_cards_response(table_id: str) -> "TableCardsResponse":
    """Costruisce la risposta TableCardsResponse a partire da TABLE_STATE."""
    state = TABLE_STATE
    result = state.get("result") or {}
    error = state.get("error")
    updated_at = state.get("updated_at")

    if result and not error:
        status = "ok"
    elif not result and error:
        if "not found" in str(error).lower():
            status = "no_image"
        else:
            status = "error"
    else:
        status = "pending"

    hero_raw = result.get("hero", [])
    board_raw = result.get("board", [])

    hero_cards: List[RecognizedCard] = []
    for card in hero_raw:
        bbox_val = card.get("bbox")
        hero_cards.append(
            RecognizedCard(
                code=card.get("code"),
                score=float(card.get("score", 0.0)),
                conf=str(card.get("conf", "none")),
                bbox=tuple(bbox_val) if bbox_val is not None else None,
            )
        )

    board_cards: List[RecognizedCard] = []
    for card in board_raw:
        bbox_val = card.get("bbox")
        board_cards.append(
            RecognizedCard(
                code=card.get("code"),
                score=float(card.get("score", 0.0)),
                conf=str(card.get("conf", "none")),
                bbox=tuple(bbox_val) if bbox_val is not None else None,
            )
        )

    return TableCardsResponse(
        table_id=table_id,
        image_path=str(TABLE_SCREEN_PATH),
        debug_image_path=str(TABLE_DEBUG_PATH),
        updated_at=updated_at,
        status=status,
        hero=hero_cards,
        board=board_cards,
        error=error,
    )


@api_router.post("/table/{table_id}/screenshot", response_model=TableCardsResponse)
async def upload_table_screenshot(table_id: str, file: UploadFile = File(...)) -> TableCardsResponse:
    """Carica uno screenshot tavolo, aggiorna il riconoscimento e ritorna le carte."""
    if table_id != "1":
        raise HTTPException(status_code=404, detail="Unknown table_id")

    if file.content_type not in ("image/png", "image/jpeg", "image/jpg"):
        raise HTTPException(status_code=400, detail="File must be PNG or JPEG")

    # Salva il file come TABLE_SCREEN_PATH
    TABLE_SCREEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    contents = await file.read()
    with open(TABLE_SCREEN_PATH, "wb") as f:
        f.write(contents)

    # Aggiorna subito il riconoscimento (niente attesa watcher)
    await update_table_cards_once()

    return build_table_cards_response(table_id)


@api_router.post("/table/{table_id}/upload")
async def upload_table_screenshot_simple(table_id: str, file: UploadFile = File(...)):
    """Endpoint semplificato per upload da client desktop."""
    return await upload_table_screenshot(table_id, file)


@api_router.get("/table/{table_id}/cards", response_model=TableCardsResponse)
async def get_table_cards(table_id: str) -> TableCardsResponse:
    """Ritorna le 7 carte riconosciute per il tavolo specificato (stato corrente)."""
    if table_id != "1":
        raise HTTPException(status_code=404, detail="Unknown table_id")

    return build_table_cards_response(table_id)


async def table_cards_watcher() -> None:
    """Loop che aggiorna le carte del tavolo ogni 5 secondi."""
    while True:
        await update_table_cards_once()
        await asyncio.sleep(5)


# Initialize AI Advisor (Groq Cloud integration)
from poker_ai_advisor import PokerAIAdvisor
try:
    ai_advisor = PokerAIAdvisor()
    print("✅ Groq AI Advisor initialized successfully")
except Exception as e:
    print(f"⚠️ AI Advisor initialization failed: {e}. Will continue without AI analysis.")
    ai_advisor = None


# NEW: Live Analyze Endpoint - Il "cervello" del sistema
@api_router.post("/poker/live/analyze", response_model=LiveAnalysisResponse)
async def live_analyze(table_state: LiveTableState):
    """
    🧠 ENDPOINT PRINCIPALE - Live Poker Analysis
    """
    if not ai_advisor:
        raise HTTPException(
            status_code=503,
            detail="AI Advisor non disponibile. Verificare GROQ_API_KEY."
        )
    
    try:
        # Converti Pydantic model a dict
        table_dict = table_state.model_dump()
        
        # Chiama l'AI brain
        logger.info(f"🧠 Analyzing table {table_state.table_id} - {table_state.street} - Hero: {table_state.hero_cards}")
        result = ai_advisor.analyze_table_state(table_dict)
        
        # Costruisci risposta
        response = LiveAnalysisResponse(
            table_id=table_state.table_id,
            recommended_action=result["recommended_action"],
            recommended_amount=result["recommended_amount"],
            equity_estimate=result["equity_estimate"],
            confidence=result["confidence"],
            ai_comment=result["ai_comment"]
        )
        
        logger.info(
            f"✅ Analysis complete for table {table_state.table_id}: "
            f"{response.recommended_action} (equity: {response.equity_estimate*100:.1f}%, "
            f"confidence: {response.confidence*100:.1f}%)"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in live analyze: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Errore nell'analisi AI: {str(e)}"
        )


# Original routes
@api_router.get("/")
async def root():
    return {"message": "Poker Bot Demo API - Ready"}


class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    if db:
        await db.status_checks.insert_one(doc)
    return status_obj


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    if not db:
        return []
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    return status_checks


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup_event() -> None:
    """Startup hook: avvia il watcher delle carte tavolo."""
    loop = asyncio.get_event_loop()
    loop.create_task(table_cards_watcher())


@app.on_event("shutdown")
async def shutdown_db_client():
    if client:
        client.close()
