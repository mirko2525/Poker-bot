# shared_state.py
# Memoria condivisa per passare i dati dalla Vision AI all'Overlay
from datetime import datetime

class SharedState:
    latest_analysis = {
        "recommended_action": "IN ATTESA",
        "recommended_amount": 0.0,
        "equity_estimate": 0.0,
        "confidence": 0.0,
        "ai_comment": "Avvia il client per iniziare...",
        "timestamp": None
    }

    @classmethod
    def update(cls, result):
        cls.latest_analysis = {
            "recommended_action": result.get("recommended_action", "N/A"),
            "recommended_amount": result.get("recommended_amount", 0.0),
            "equity_estimate": result.get("equity_estimate", 0.0),
            "confidence": result.get("confidence", 0.0),
            "ai_comment": result.get("ai_comment", ""),
            "timestamp": datetime.now().isoformat()
        }
