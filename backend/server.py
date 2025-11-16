from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timezone
import random


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


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

class DemoResponse(BaseModel):
    hand_number: int
    hand_state: HandState
    decision: Decision
    has_next: bool

# Original Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Poker Bot Logic - Mock Implementations
class MockStateProvider:
    def __init__(self):
        # Espansione a 8 mani per coprire scenari diversificati (Ordini Fase 2)
        # Mani organizzate in sequenza logica per creare una "storia di test"
        self.mock_hands = [
            # 1. Strong PREFLOP (AA) - Small pot, low to_call
            {
                "hero_cards": ["As", "Ad"],
                "board_cards": [],
                "hero_stack": 100.0,
                "pot_size": 3.0,
                "to_call": 2.0,
                "big_blind": 1.0,
                "players_in_hand": 3,
                "phase": "PREFLOP"
            },
            # 2. Marginal PREFLOP (KJo) - Large raise to call
            {
                "hero_cards": ["Kh", "Jd"],
                "board_cards": [],
                "hero_stack": 98.0,
                "pot_size": 12.0,
                "to_call": 8.0,
                "big_blind": 1.0,
                "players_in_hand": 4,
                "phase": "PREFLOP"
            },
            # 3. FLOP - Top pair top kicker, small pot
            {
                "hero_cards": ["Ah", "Ks"],
                "board_cards": ["Ad", "7c", "2s"],
                "hero_stack": 90.0,
                "pot_size": 15.0,
                "to_call": 3.0,
                "big_blind": 1.0,
                "players_in_hand": 3,
                "phase": "FLOP"
            },
            # 4. FLOP - Flush draw with interesting pot odds
            {
                "hero_cards": ["9h", "8h"],
                "board_cards": ["7h", "5h", "2c"],
                "hero_stack": 87.0,
                "pot_size": 20.0,
                "to_call": 5.0,
                "big_blind": 1.0,
                "players_in_hand": 2,
                "phase": "FLOP"
            },
            # 5. TURN - Completed straight draw, medium pot
            {
                "hero_cards": ["Qh", "Jd"],
                "board_cards": ["Kc", "Ts", "9h", "4d"],
                "hero_stack": 82.0,
                "pot_size": 30.0,
                "to_call": 10.0,
                "big_blind": 1.0,
                "players_in_hand": 2,
                "phase": "TURN"
            },
            # 6. RIVER - Weak hand, big pot, large to_call
            {
                "hero_cards": ["2h", "7c"],
                "board_cards": ["Ac", "Kd", "Qh", "Js", "5s"],
                "hero_stack": 72.0,
                "pot_size": 60.0,
                "to_call": 25.0,
                "big_blind": 1.0,
                "players_in_hand": 2,
                "phase": "RIVER"
            },
            # 7. Short stack situation (<10 BB) with good equity -> all-in testing
            {
                "hero_cards": ["Jh", "Jc"],
                "board_cards": [],
                "hero_stack": 8.5,
                "pot_size": 4.5,
                "to_call": 3.5,
                "big_blind": 1.0,
                "players_in_hand": 4,
                "phase": "PREFLOP"
            },
            # 8. Borderline situation where equity ≈ pot odds -> CALL/FOLD logic testing
            {
                "hero_cards": ["Tc", "9c"],
                "board_cards": ["8h", "7d", "2s"],
                "hero_stack": 47.0,
                "pot_size": 24.0,
                "to_call": 8.0,
                "big_blind": 1.0,
                "players_in_hand": 3,
                "phase": "FLOP"
            }
        ]
        self.current_index = 0
    
    def get_next_mock_hand(self):
        if self.current_index >= len(self.mock_hands):
            return None
        
        hand = self.mock_hands[self.current_index]
        self.current_index += 1
        return HandState(**hand)
    
    def reset_mock_hands(self):
        self.current_index = 0
    
    def has_next(self):
        return self.current_index < len(self.mock_hands)

class MockEquityEngine:
    def __init__(self, enable_random=True):
        # Controllo randomness (Ordini Fase 2)
        self.enable_random = enable_random
        
        # Preflop equity table (simplified) - values in percentage
        # These represent equity vs random hand heads-up
        self.preflop_equity = {
            # Premium pairs
            "AA": 85, "KK": 82, "QQ": 80, "JJ": 77, "TT": 75,
            # Strong broadway
            "AK": 67, "AQ": 65, "AJ": 63, "AT": 60,
            "KQ": 63, "KJ": 60, "QJ": 58, "JT": 56,
            # Weak aces and kings
            "A9": 58, "A8": 57, "A7": 56, "A6": 55, "A5": 55,
            "A4": 54, "A3": 54, "A2": 53,
            "K9": 55, "K8": 54, "K7": 53, "K6": 52, "K5": 51,
            "K4": 50, "K3": 49, "K2": 48,
            "Q9": 52, "Q8": 51, "Q7": 50, "Q6": 49, "Q5": 48,
            "Q4": 47, "Q3": 46, "Q2": 45,
            "J9": 50, "J8": 49, "J7": 48, "J6": 47, "J5": 46,
            "J4": 45, "J3": 44, "J2": 43,
            "T9": 54, "T8": 53, "T7": 51, "T6": 49, "T5": 48,
            "T4": 47, "T3": 46, "T2": 45,
            # Pairs
            "22": 50, "33": 52, "44": 54, "55": 56, "66": 58,
            "77": 60, "88": 63, "99": 65,
            # Connectors and suited combos
            "98": 52, "87": 50, "76": 49, "65": 48, "54": 46,
            "97": 48, "86": 47, "75": 46, "64": 44, "53": 43,
            "96": 46, "85": 45, "74": 43, "63": 42, "52": 40,
            "95": 44, "84": 43, "73": 41, "62": 39, "42": 37,
            "94": 42, "83": 41, "72": 38, "32": 36,
            "93": 40, "82": 39, "92": 38, "43": 39
        }
    
    def compute_equity(self, hand_state: HandState) -> float:
        # Check if hero cards are unknown/unrecognized
        if not hand_state.hero_cards or any('?' in card for card in hand_state.hero_cards):
            # Return default equity for unknown hands (in decimal 0-1 range)
            return 0.50  # 50% default equity
        
        if hand_state.phase == "PREFLOP":
            return self._compute_preflop_equity(hand_state.hero_cards)
        else:
            return self._compute_postflop_equity(hand_state)
    
    def _compute_preflop_equity(self, hero_cards: List[str]) -> float:
        # Extract hand strength key
        card1_rank = hero_cards[0][0]
        card2_rank = hero_cards[1][0]
        
        # Convert face cards
        rank_values = {"A": 14, "K": 13, "Q": 12, "J": 11, "T": 10}
        
        for rank in [card1_rank, card2_rank]:
            if rank.isdigit():
                rank_values[rank] = int(rank)
        
        # Determine hand type
        if card1_rank == card2_rank:
            # Pocket pair
            hand_key = card1_rank + card2_rank
        else:
            # High card combination
            high_card = max(card1_rank, card2_rank, key=lambda x: rank_values.get(x, int(x) if x.isdigit() else 0))
            low_card = min(card1_rank, card2_rank, key=lambda x: rank_values.get(x, int(x) if x.isdigit() else 0))
            hand_key = high_card + low_card
        
        equity = self.preflop_equity.get(hand_key, 45)  # Default equity
        
        # Add randomness only if enabled (Ordini Fase 2)
        if self.enable_random:
            equity += random.uniform(-5, 5)
        
        # Convert to decimal 0-1 range (was percentage 0-100)
        equity_decimal = max(0.10, min(0.95, equity / 100.0))
        return equity_decimal
    
    def _compute_postflop_equity(self, hand_state: HandState) -> float:
        """
        Compute postflop equity based on hand strength and board texture.
        Returns value in decimal range 0-1 (not percentage).
        """
        # Start with preflop equity as base (already in decimal 0-1)
        base_equity_decimal = self._compute_preflop_equity(hand_state.hero_cards)
        
        # Convert to percentage for easier manipulation
        equity_pct = base_equity_decimal * 100.0
        
        # Analyze board interaction
        board_cards = hand_state.board_cards
        hero_ranks = [card[0] for card in hand_state.hero_cards]
        board_ranks = [card[0] for card in board_cards]
        
        # Check for pairs, trips with board (simplified)
        hero_on_board = len(set(hero_ranks) & set(board_ranks))
        
        if hero_on_board == 2:
            # Both hero cards on board (two pair or better)
            equity_pct = min(95, equity_pct + 15)
        elif hero_on_board == 1:
            # One hero card on board (pair)
            equity_pct = min(90, equity_pct + 8)
        elif hero_on_board == 0:
            # No pair - reduce equity slightly
            equity_pct = max(10, equity_pct - 10)
        
        # Adjust for phase (equity typically decreases as unknowns decrease)
        # But for strong hands, equity often holds or increases
        if hand_state.phase == "RIVER":
            # On river, equity is more certain
            # Strong hands stay strong, weak hands stay weak
            pass  # No adjustment
        elif hand_state.phase == "TURN":
            # On turn, small variance
            if self.enable_random:
                equity_pct += random.uniform(-3, 3)
        else:  # FLOP
            # On flop, more variance
            if self.enable_random:
                equity_pct += random.uniform(-5, 5)
        
        # Clamp and convert back to decimal
        equity_pct = max(5, min(95, equity_pct))
        return equity_pct / 100.0

class DecisionEngine:
    def __init__(self):
        # Costanti configurabili (Ordini Fase 2)
        # Importiamo le costanti dal file di configurazione
        from poker_config import (
            MARGIN, STRONG_EQUITY_THRESHOLD, ALLIN_STACK_BB_THRESHOLD,
            SHORT_STACK_BORDERLINE_BB, HIGH_EQUITY_FOR_ALLIN,
            RAISE_POT_MULTIPLIER, RAISE_NO_COST_MULTIPLIER
        )
        
        self.margin = MARGIN
        self.strong_equity_threshold = STRONG_EQUITY_THRESHOLD  
        self.allin_stack_bb_threshold = ALLIN_STACK_BB_THRESHOLD
        self.short_stack_borderline_bb = SHORT_STACK_BORDERLINE_BB
        self.high_equity_for_allin = HIGH_EQUITY_FOR_ALLIN
        self.raise_pot_multiplier = RAISE_POT_MULTIPLIER
        self.raise_no_cost_multiplier = RAISE_NO_COST_MULTIPLIER
    
    def decide_action(self, hand_state: HandState, equity: float) -> Decision:
        equity_fraction = equity / 100.0
        
        if hand_state.to_call == 0:
            return self._decide_no_cost_to_call(hand_state, equity, equity_fraction)
        else:
            return self._decide_cost_to_call(hand_state, equity, equity_fraction)
    
    def _decide_no_cost_to_call(self, hand_state: HandState, equity: float, equity_fraction: float) -> Decision:
        if equity_fraction < 0.15:
            return Decision(
                action="CALL",
                raise_amount=0.0,
                reason="Weak hand, but no cost to see next card",
                equity=equity
            )
        elif equity_fraction < 0.5:
            return Decision(
                action="CALL",
                raise_amount=0.0,
                reason="Decent hand, check to see next card",
                equity=equity
            )
        else:
            raise_amount = min(hand_state.hero_stack, hand_state.pot_size * self.raise_no_cost_multiplier)
            return Decision(
                action="RAISE",
                raise_amount=raise_amount,
                reason="Strong hand, small raise for value",
                equity=equity
            )
    
    def _decide_cost_to_call(self, hand_state: HandState, equity: float, equity_fraction: float) -> Decision:
        pot_odds = hand_state.to_call / (hand_state.pot_size + hand_state.to_call)
        hero_stack_bb = hand_state.hero_stack / hand_state.big_blind
        
        # Check for short stack all-in situation
        if hero_stack_bb < self.allin_stack_bb_threshold and equity_fraction > self.high_equity_for_allin:
            return Decision(
                action="RAISE",
                raise_amount=hand_state.hero_stack,
                reason=f"Short stack ({hero_stack_bb:.1f} BB) with strong equity - all-in",
                equity=equity,
                pot_odds=pot_odds * 100
            )
        
        # Compare equity vs pot odds
        if equity_fraction < pot_odds - self.margin:
            return Decision(
                action="FOLD",
                raise_amount=0.0,
                reason=f"Equity ({equity:.1f}%) insufficient vs pot odds ({pot_odds*100:.1f}%)",
                equity=equity,
                pot_odds=pot_odds * 100
            )
        
        elif equity_fraction <= pot_odds + self.margin:
            # Borderline situation
            if hero_stack_bb > self.short_stack_borderline_bb:
                return Decision(
                    action="CALL",
                    raise_amount=0.0,
                    reason=f"Borderline spot with decent stack ({hero_stack_bb:.1f} BB) - call",
                    equity=equity,
                    pot_odds=pot_odds * 100
                )
            else:
                return Decision(
                    action="FOLD",
                    raise_amount=0.0,
                    reason=f"Borderline spot with short stack ({hero_stack_bb:.1f} BB) - fold",
                    equity=equity,
                    pot_odds=pot_odds * 100
                )
        
        else:
            # Positive situation
            if equity_fraction < self.strong_equity_threshold:
                return Decision(
                    action="CALL",
                    raise_amount=0.0,
                    reason=f"Good equity ({equity:.1f}%) vs pot odds ({pot_odds*100:.1f}%) - call",
                    equity=equity,
                    pot_odds=pot_odds * 100
                )
            else:
                raise_amount = min(hand_state.hero_stack, hand_state.pot_size * self.raise_pot_multiplier)
                return Decision(
                    action="RAISE",
                    raise_amount=raise_amount,
                    reason=f"Strong equity ({equity:.1f}%) - raise for value",
                    equity=equity,
                    pot_odds=pot_odds * 100
                )

# Initialize the poker bot components (Fase 2: Sincronizzazione parametri)
mock_state_provider = MockStateProvider()
equity_engine = MockEquityEngine(enable_random=True)  # Randomness per web demo
decision_engine = DecisionEngine()


# Add poker bot routes
@api_router.get("/poker/demo/start")
async def start_demo():
    """Reset demo and get first hand"""
    mock_state_provider.reset_mock_hands()
    return {"message": "Demo started", "total_hands": len(mock_state_provider.mock_hands)}

@api_router.get("/poker/demo/next", response_model=DemoResponse)
async def get_next_hand():
    """Get next demo hand with analysis"""
    hand_state = mock_state_provider.get_next_mock_hand()
    
    if hand_state is None:
        raise HTTPException(status_code=404, detail="No more demo hands available")
    
    # Compute equity
    equity = equity_engine.compute_equity(hand_state)
    
    # Make decision
    decision = decision_engine.decide_action(hand_state, equity)
    
    return DemoResponse(
        hand_number=mock_state_provider.current_index,
        hand_state=hand_state,
        decision=decision,
        has_next=mock_state_provider.has_next()
    )

@api_router.get("/poker/demo/status")
async def get_demo_status():
    """Get current demo status"""
    return {
        "current_hand": mock_state_provider.current_index,
        "total_hands": len(mock_state_provider.mock_hands),
        "has_next": mock_state_provider.has_next()
    }

# Original routes
@api_router.get("/")
async def root():
    return {"message": "Poker Bot Demo API - Ready"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()