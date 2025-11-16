# 🃏 Poker Bot - Texas Hold'em Live Advisor

Sistema completo per l'analisi e il supporto decisionale nel poker Texas Hold'em tramite computer vision e algoritmi di calcolo equity.

## 🎯 Obiettivo

Analizzare screenshot di tavoli poker in tempo reale e fornire consigli basati su:
- Riconoscimento automatico delle carte (board e hero cards)
- Calcolo equity della mano
- Decisioni ottimali (FOLD, CALL, RAISE) basate su pot odds e hand strength

## ✨ Features

### Fase 1-2: Core Logic
- ✅ **HandState Model**: Rappresentazione completa dello stato di una mano
- ✅ **MockEquityEngine**: Calcolo equity preflop e postflop
- ✅ **DecisionEngine**: Logica decisionale con parametri configurabili
- ✅ **Demo Console**: Testing interattivo delle decisioni

### Fase 3: Table Input Layer
- ✅ **Table Layout Config**: Calibrazione coordinate PokerStars
- ✅ **Screenshot Capture**: Caricamento e ritaglio tavolo
- ✅ **Region Extraction**: Estrazione automatica regioni (hero cards, board, pot, stack)

### Fase 4: Computer Vision (OCR)
- ✅ **Card Recognition**: Template matching per riconoscimento carte
- ✅ **Card Templates**: Database template normalizzati (64x96px)
- ✅ **Number Recognition**: OCR per valori pot e stack
- ✅ **Digit Templates**: Template per cifre 0-9 e simboli (., €, $)

### Fase 5: Live Advisor V1 🎉
- ✅ **VisionPokerEngine**: Integrazione completa screenshot → HandState
- ✅ **Live Advisor Console**: Demo end-to-end da screenshot reale
- ✅ **Gestione Fallback**: Sistema robusto con default sensati per dati mancanti

## 🏗️ Architettura

```
Screenshot PokerStars
    ↓
[VisionPokerEngine]
    ├── Table Layout Detection
    ├── Region Extraction
    ├── Card Recognition (Template Matching)
    └── Number Recognition (OCR)
    ↓
HandState
    ↓
[EquityEngine] → Equity %
    ↓
[DecisionEngine] → FOLD / CALL / RAISE
    ↓
Consiglio Finale
```

## 📂 Struttura Repository

```
poker-bot/
├── backend/                    # Backend Python FastAPI
│   ├── vision_to_handstate.py  # VisionPokerEngine (Fase 4)
│   ├── server.py               # FastAPI + HandState + EquityEngine + DecisionEngine
│   ├── live_advisor.py         # Demo console Fase 5
│   ├── card_recognition.py     # Template matching carte
│   ├── card_templates.py       # Gestione template carte
│   ├── digit_templates.py      # Gestione template cifre
│   ├── number_recognition.py   # OCR numeri
│   ├── table_layout.py         # Config layout tavoli
│   ├── table_capture_static.py # Cattura screenshot
│   ├── table_region_cutter.py  # Estrazione regioni
│   ├── poker_config.py         # Parametri decisione
│   ├── check_imports.py        # Verifica dipendenze
│   ├── requirements.txt        # Dipendenze Python
│   ├── rooms/
│   │   └── pokerstars_6max.json    # Config PokerStars 6-max
│   ├── screenshots/                # Screenshot di test
│   ├── card_templates/             # Template carte
│   │   ├── raw_samples/            # Campioni originali
│   │   └── normalized/             # Template normalizzati (gitignored)
│   └── digit_templates/            # Template cifre
│       ├── raw_samples/
│       └── normalized/ (gitignored)
│
├── frontend/                   # Frontend React
│   ├── src/
│   ├── public/
│   └── package.json
│
└── tests/                      # Test directory
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Yarn

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Verify imports
python check_imports.py

# Run Live Advisor demo
python live_advisor.py
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
yarn install

# Start development server
yarn dev
```

### Run Full Stack

```bash
# Terminal 1 - Backend
cd backend
python server.py

# Terminal 2 - Frontend
cd frontend
yarn dev
```

## 🎮 Usage

### Live Advisor Console Demo

```bash
cd backend
python live_advisor.py
```

Output per ogni screenshot:
```
============================================================
🖼️  Screenshot: pokerstars_flop_v2.png
============================================================
📊 Phase: FLOP
🃏 Hero cards: ['??', '??']
🎴 Board: ['6d', 'Ah', '2c']
💰 Pot size: $3.00
💵 Hero stack: $100.00
👥 Players in hand: 2

📈 Equity stimata: 50.00%
▲ Azione consigliata: CALL
💡 Motivo: Weak hand, but no cost to see next card
```

### Verifica Import

```bash
python check_imports.py
```

Verifica che tutti i moduli siano importabili e inizializzabili.

## 🧪 Testing

### Test Card Recognition

```bash
python card_recognition.py
```

Output: riconoscimento carte su tutte le regioni estratte.

### Test Number Recognition

```bash
python number_recognition.py
```

Output: riconoscimento pot e stack dalle regioni.

### Test Complete Pipeline

```bash
python live_advisor.py
```

Test end-to-end: screenshot → HandState → decisione.

## 📊 Status Features

| Feature | Status | Note |
|---------|--------|------|
| HandState Model | ✅ Complete | Pydantic models |
| EquityEngine | ✅ V1 (Mock) | Simplified equity calculation |
| DecisionEngine | ✅ Complete | Configurable parameters |
| Table Layout | ✅ PokerStars 6-max | JSON config |
| Region Extraction | ✅ Complete | Hero/board/pot/stack |
| Card Recognition | 🟡 Partial | 4/52 templates (6d, Ah, 2c, Ac) |
| Number Recognition | 🟡 Structure only | Needs real digit templates |
| VisionEngine | ✅ Complete | Full integration |
| Live Advisor | ✅ V1 Complete | Console demo |
| API Endpoint | 🔲 Planned | `/api/poker/live/advice` |
| Auto Screenshot | 🔲 Planned | Periodic capture |

## 🔧 Configuration

### Poker Decision Parameters

Edit `backend/poker_config.py`:

```python
MARGIN = 0.05                           # Margine per decisioni borderline
STRONG_EQUITY_THRESHOLD = 0.65          # Soglia equity per raise aggressivo
ALLIN_STACK_BB_THRESHOLD = 10           # Soglia BB per all-in
RAISE_POT_MULTIPLIER = 0.75             # Moltiplicatore pot per raise
```

### Room Coordinates

Calibra coordinate tavolo in `backend/rooms/pokerstars_6max.json`:

```json
{
  "room_name": "PokerStars 6-Max",
  "resolution": [3071, 1919],
  "table_region": [276, 134, 2518, 1611],
  "hero_cards": [[1351, 1573, 89, 118], ...],
  "board_cards": [[1136, 834, 89, 118], ...],
  ...
}
```

## 🛠️ Development

### Add Card Templates

1. Extract card from screenshot → `card_templates/raw_samples/Kh_1.png`
2. Run: `python card_templates.py`
3. Normalized template created in `card_templates/normalized/`

### Add Digit Templates

1. Extract digits from pot/stack → `digit_templates/raw_samples/digit_5_1.png`
2. Run: `python digit_templates.py`
3. Normalized template created in `digit_templates/normalized/`

## 📈 Roadmap

### Next Steps (V2)
- [ ] Complete card templates (52 cards)
- [ ] Real digit templates from PokerStars font
- [ ] API endpoint `/api/poker/live/advice`
- [ ] Frontend Live Advisor UI
- [ ] Auto screenshot capture (mss/pyautogui)
- [ ] Multi-table support (up to 8 tables)

### Future Enhancements
- [ ] Real equity calculator (Monte Carlo simulation)
- [ ] Hand history logging
- [ ] Advanced opponent modeling
- [ ] Range analysis
- [ ] Tournament mode (ICM considerations)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is for educational purposes only. Use responsibly and in compliance with poker room terms of service.

## ⚠️ Disclaimer

This software is intended as an educational tool for understanding poker concepts and computer vision. Using automated tools at online poker sites may violate their terms of service. Use at your own risk.

## 🎓 Credits

- Poker logic: Based on standard Texas Hold'em mathematics
- Computer vision: Template matching with PIL/NumPy
- FastAPI backend + React frontend

---

**Fase 5 - Live Advisor V1 Complete** 🎉
