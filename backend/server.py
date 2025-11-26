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

# --- MONGODB SETUP (OPZIONALE) ---
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

client = None
db = None

if MOTOR_AVAILABLE:
    try:
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=2000)
        db = client[db_name]
        print(f"✅ MongoDB configurato: {mongo_url}")
    except Exception as e:
        print(f"⚠️ Errore connessione MongoDB: {e}")
        db = MockDB()
else:
    db = MockDB()

# --- FINE SETUP DB ---

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Import Vision Analyzer Router
from vision_analyzer_api import vision_router
api_router.include_router(vision_router)

# --- MEMORIA GLOBALE PER OVERLAY ---
# Qui salviamo l'ultima analisi per mostrarla nell'overlay
LATEST_ANALYSIS = {
    "recommended_action": "IN ATTESA",
    "recommended_amount": 0.0,
    "equity_estimate": 0.0,
    "confidence": 0.0,
    "ai_comment": "In attesa della prima mano...",
    "timestamp": None
}

# --- MODELLI ---
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
    raise_amount: float = Field(default=0.0, description="Amount to raise")
    reason: Optional[str] = Field(default=None, description="Reason")
    equity: float = Field(..., description="Calculated equity percentage")
    pot_odds: Optional[float] = Field(default=None, description="Pot odds percentage")
    ai_analysis: Optional[str] = Field(default=None, description="AI analysis")

class DemoResponse(BaseModel):
    hand_number: int
    hand_state: HandState
    decision: Decision
    has_next: bool

class RecognizedCard(BaseModel):
    code: Optional[str] = Field(default=None)
    score: float = Field(...)
    conf: str = Field(...)
    bbox: Optional[Tuple[int, int, int, int]] = Field(default=None)

class TableCardsResponse(BaseModel):
    table_id: str
    image_path: str
    debug_image_path: Optional[str] = None
    updated_at: Optional[datetime]
    status: str
    hero: List[RecognizedCard]
    board: List[RecognizedCard]
    error: Optional[str] = None

class TableEquityResponse(BaseModel):
    table_id: str
    num_players: int
    hero_cards: List[str]
    board_cards: List[str]
    status: str
    hero_win: float
    hero_tie: float
    hero_lose: float
    error: Optional[str] = None

class LiveTableState(BaseModel):
    table_id: int
    hero_cards: List[str]
    board_cards: List[str] = []
    hero_stack: float
    pot_size: float
    to_call: float
    position: str
    players: int
    street: str
    last_action: str
    big_blind: float = 1.0

class LiveAnalysisResponse(BaseModel):
    table_id: int
    recommended_action: str
    recommended_amount: float
    equity_estimate: float
    confidence: float
    ai_comment: str

# --- RICONOSCIMENTO CARTE (OPZIONALE) ---
TABLE_SCREEN_PATH = ROOT_DIR / "data" / "screens" / "table1.png"
TABLE_DEBUG_PATH = ROOT_DIR / "data" / "screens" / "table1_debug.png"

try:
    import cv2
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
    print("✅ Modulo OpenCV caricato correttamente.")
except ImportError as e:
    print(f"⚠️ Modulo OpenCV non disponibile: {e}")
    RECOGNITION_AVAILABLE = False
    cv2 = None

TABLE_STATE: Dict[str, Any] = {
    "result": None,
    "error": None,
    "updated_at": None,
}

def save_table_debug_overlay(screen_bgr, recognition: Dict[str, Any], out_path: Path) -> None:
    if not RECOGNITION_AVAILABLE or cv2 is None: return
    
    debug = screen_bgr.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX

    def draw_group(cards, color):
        for c in cards:
            bbox = c.get("bbox")
            if not bbox: continue
            x, y, w, h = bbox
            cv2.rectangle(debug, (int(x), int(y)), (int(x + w), int(y + h)), color, 2)

    draw_group(recognition.get("hero", []), (0, 255, 0))
    draw_group(recognition.get("board", []), (255, 0, 0))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), debug)

async def update_table_cards_once() -> None:
    if not RECOGNITION_AVAILABLE or cv2 is None: return

    if not TABLE_SCREEN_PATH.exists():
        TABLE_STATE["result"] = None
        TABLE_STATE["error"] = "Screenshot not found"
        return

    screen_bgr = cv2.imread(str(TABLE_SCREEN_PATH))
    if screen_bgr is None:
        TABLE_STATE["result"] = None
        TABLE_STATE["error"] = "Failed to read image"
        return

    try:
        recognition = recognize_table_cards_pokerstars(
            screen_bgr, TABLE_LAYOUT, CARD_RECOGNIZER, HERO_BACK_RECOGNIZER
        )
        try:
            save_table_debug_overlay(screen_bgr, recognition, TABLE_DEBUG_PATH)
        except Exception:
            pass

        TABLE_STATE["result"] = recognition
        TABLE_STATE["error"] = None
        TABLE_STATE["updated_at"] = datetime.now(timezone.utc)
    except Exception as exc:
        logger.error(f"Recognition error: {exc}")
        TABLE_STATE["error"] = str(exc)

def build_table_cards_response(table_id: str) -> "TableCardsResponse":
    state = TABLE_STATE
    result = state.get("result") or {}
    
    hero_cards = []
    for c in result.get("hero", []):
        hero_cards.append(RecognizedCard(
            code=c.get("code"), score=float(c.get("score", 0)), conf=str(c.get("conf", "none"))
        ))

    board_cards = []
    for c in result.get("board", []):
        board_cards.append(RecognizedCard(
            code=c.get("code"), score=float(c.get("score", 0)), conf=str(c.get("conf", "none"))
        ))

    return TableCardsResponse(
        table_id=table_id,
        image_path=str(TABLE_SCREEN_PATH),
        status="ok" if result else "pending",
        hero=hero_cards,
        board=board_cards,
        error=state.get("error")
    )

@api_router.post("/table/{table_id}/screenshot", response_model=TableCardsResponse)
async def upload_table_screenshot(table_id: str, file: UploadFile = File(...)) -> TableCardsResponse:
    if table_id != "1": raise HTTPException(status_code=404, detail="Unknown table_id")
    
    TABLE_SCREEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    contents = await file.read()
    with open(TABLE_SCREEN_PATH, "wb") as f:
        f.write(contents)

    await update_table_cards_once()
    return build_table_cards_response(table_id)

@api_router.post("/table/{table_id}/upload")
async def upload_table_screenshot_simple(table_id: str, file: UploadFile = File(...)):
    return await upload_table_screenshot(table_id, file)

@api_router.get("/table/{table_id}/cards", response_model=TableCardsResponse)
async def get_table_cards(table_id: str) -> TableCardsResponse:
    return build_table_cards_response(table_id)

async def table_cards_watcher() -> None:
    while True:
        await update_table_cards_once()
        await asyncio.sleep(5)

# --- AI ADVISOR ---
from poker_ai_advisor import PokerAIAdvisor
try:
    ai_advisor = PokerAIAdvisor()
    print("✅ Groq AI Advisor initialized successfully")
except Exception as e:
    print(f"⚠️ AI Advisor initialization failed: {e}")
    ai_advisor = None

@api_router.post("/poker/live/analyze", response_model=LiveAnalysisResponse)
async def live_analyze(table_state: LiveTableState):
    global LATEST_ANALYSIS
    
    if not ai_advisor:
        raise HTTPException(status_code=503, detail="AI Advisor non disponibile")
    
    try:
        result = ai_advisor.analyze_table_state(table_state.model_dump())
        
        # Salva in memoria per l'overlay
        LATEST_ANALYSIS = {
            "recommended_action": result["recommended_action"],
            "recommended_amount": result["recommended_amount"],
            "equity_estimate": result["equity_estimate"],
            "confidence": result["confidence"],
            "ai_comment": result["ai_comment"],
            "timestamp": datetime.now().isoformat()
        }
        
        return LiveAnalysisResponse(
            table_id=table_state.table_id,
            recommended_action=result["recommended_action"],
            recommended_amount=result["recommended_amount"],
            equity_estimate=result["equity_estimate"],
            confidence=result["confidence"],
            ai_comment=result["ai_comment"]
        )
    except Exception as e:
        logger.error(f"AI Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/poker/live/latest")
async def get_latest_analysis():
    """Endpoint per l'overlay desktop"""
    return LATEST_ANALYSIS

# --- ROUTES BASE ---
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
    return StatusCheck(client_name=input.client_name)

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    return []

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

@app.on_event("startup")
async def startup_event() -> None:
    loop = asyncio.get_event_loop()
    loop.create_task(table_cards_watcher())

@app.on_event("shutdown")
async def shutdown_db_client():
    if client: client.close()
