# Poker Bot – Texas Hold'em Live Advisor 🎴

Advisor per Texas Hold'em che legge il tavolo da **screenshot reali di PokerStars** e produce in tempo reale:

- stato della mano (`HandState`)
- stima di equity
- azione consigliata (FOLD / CALL / RAISE)

Progetto strutturato a fasi ("Ordini del Capo"), con focus su:
OCR template-based, modularità e simulazione di un sistema di supporto alle decisioni (non un bot che gioca al posto tuo).

> ⚠️ **Disclaimer**  
> Questo progetto è un **advisor didattico/sperimentale**.  
> Non invia click, non automatizza puntate, non viola i ToS delle poker room.  
> È pensato solo per studio di visione artificiale, equity e logica decisionale.

---

## 🚀 Funzionalità principali

- 🔍 **Visione tavolo** da screenshot (room PokerStars 6-max)
- 🃏 Riconoscimento **board cards** tramite template matching
- 🔢 Pipeline OCR per **pot** e **stack** (struttura pronta, template numerici in sviluppo)
- 🧠 Calcolo **equity mock** (Monte Carlo semplificato / logica mock)
- 🎯 **DecisionEngine**: FOLD / CALL / RAISE in base a equity + contesto
- 🖥️ **Live Advisor V1**: demo da console (`backend/live_advisor.py`) che integra tutto:
  `Screenshot → Visione → HandState → Equity → Decisione`

---

## 🧱 Architettura del progetto

```text
Poker-bot/
├── backend/
│   ├── vision_to_handstate.py     # VisionPokerEngine: screenshot → HandState
│   ├── server.py                  # HandState, Decision, MockEquityEngine, DecisionEngine, FastAPI (future)
│   ├── live_advisor.py            # Fase 5: Live Advisor V1 (demo console)
│   ├── card_recognition.py        # Riconoscimento carte da regioni ritagliate
│   ├── card_templates.py          # Gestione template carte (52 carte, template matching)
│   ├── digit_templates.py         # Gestione template cifre (0–9, simboli)
│   ├── number_recognition.py      # OCR numerico per pot e stack
│   ├── table_layout.py            # Definizione layout tavolo (regioni, coordinate)
│   ├── table_capture_static.py    # Cattura screenshot statici
│   ├── table_region_cutter.py     # Ritaglio delle regioni (hero cards, board, pot, stack…)
│   ├── poker_config.py            # Parametri di decisione (soglie equity, margini, ecc.)
│   ├── requirements.txt           # Dipendenze Python
│   └── rooms/
│       └── pokerstars_6max.json   # Config visione per tavolo PokerStars 6-max
│
├── frontend/
│   ├── src/                       # Frontend React (demo / futura UI advisor)
│   ├── public/
│   └── package.json
│
├── screenshots/                   # Screenshot reali di test (PokerStars)
│   ├── pokerstars_preflop.png
│   ├── pokerstars_flop_v2.png
│   ├── pokerstars_turn.png
│   └── pokerstars_river.png
│
├── card_templates/                # Template carte (dentro backend/)
└── digit_templates/               # Template cifre (dentro backend/)
```

**Nota**: il file `.env` è ignorato da Git (`.gitignore`) e non viene committato.

---

## 🛠️ Setup Backend

### 1. Clona il repository

```bash
git clone https://github.com/mirko2525/Poker-bot.git
cd Poker-bot
```

### 2. Crea un virtualenv (opzionale ma consigliato)

```bash
python -m venv .venv
source .venv/bin/activate   # su Windows: .venv\Scripts\activate
```

### 3. Installa le dipendenze

```bash
cd backend
pip install -r requirements.txt
```

---

## ▶️ Live Advisor V1 – Demo da console

Questa è la demo della **FASE 5**: sistema integrato end-to-end.

Da dentro `backend/`:

```bash
python live_advisor.py
```

**Cosa fa:**

- carica la config `rooms/pokerstars_6max.json`
- inizializza:
  - `VisionPokerEngine`
  - `MockEquityEngine`
  - `DecisionEngine`
- cicla sui 4 screenshot in `screenshots/`:
  - `pokerstars_preflop.png`
  - `pokerstars_flop_v2.png`
  - `pokerstars_turn.png`
  - `pokerstars_river.png`
- per ogni screenshot stampa:
  - **Phase** (PREFLOP / FLOP / TURN / RIVER)
  - **Hero cards** (per ora spesso `["??", "??"]` – template in sviluppo)
  - **Board cards** riconosciute (es. `['6d', 'Ah', '2c']`)
  - **Pot size** (per ora default in molti casi)
  - **Hero stack** (default finché OCR numerico non è addestrato)
  - **Equity stimata**
  - **Azione consigliata** (FOLD / CALL / RAISE)

**Esempio di output:**

```
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

---

## 🌐 Frontend (WIP)

Il frontend React (cartella `frontend/`) è pensato per:

- visualizzare lo stato mano,
- mostrare equity e azione consigliata,
- in futuro chiamare un endpoint FastAPI tipo `/api/poker/live/advice`.

**Setup tipico:**

```bash
cd frontend
yarn install
yarn dev
```

Al momento il frontend è in fase di integrazione con il backend (Live Advisor V1 parte da console).

---

## 📊 Stato attuale (FASE 5 – LIVE ADVISOR V1)

### Completato:

- ✅ Lettura tavolo da screenshot statici (PokerStars 6-max)
- ✅ Board recognition (template-based per 2c, 3c, 6d, Ac, Ah)
- ✅ VisionPokerEngine → HandState stabile con fallback
- ✅ MockEquityEngine corretto (equity 0-100%, calcoli accurati)
- ✅ DecisionEngine integrato (logica FOLD/CALL/RAISE)
- ✅ Demo Live Advisor da console (`live_advisor.py`) funzionante end-to-end

### Limitazioni note (accettate per questa versione):

- 🟡 **Hero cards**: template ancora parziali → spesso `["??", "??"]`
- 🟡 **Pot/stack**: OCR numerico con struttura pronta ma template cifre da completare → valori spesso di default (3.0 / 100.0)
- 🟡 Alcuni screenshot edge-case (river/turn) possono richiedere nuovi sample e tuning

---

## 🧭 Roadmap

### Prossime fasi previste:

**Fase 6 – Qualità visione**
- Template reali per hero cards (croppati da screenshot reali)
- Template reali per pot/stack (OCR numerico stabile)
- Miglioramento coverage carte (verso 52/52)

**Fase 7 – API & UI**
- Endpoint FastAPI `/api/poker/live/advice`
- Integrazione frontend React → dashboard "Live Advisor"

**Fase 8 – Live Capture**
- Cattura schermo automatica (es. con mss/pyautogui)
- Aggiornamento periodico HandState + Decisione

**Fase 9 – Multi-tavolo**
- Riconoscimento fino a 8 tavoli
- Numerazione tavoli e overlay consigli per ogni tavolo

---

## 🧪 Testing

### Verifica import e dipendenze

```bash
cd backend
python check_imports.py
```

### Test equity engine

```bash
python test_equity.py
```

### Test card recognition

```bash
python card_recognition.py
```

### Test complete pipeline

```bash
python live_advisor.py
```

---

## 🤝 Contributing

Questo è un progetto educativo. Contributi benvenuti per:

- Migliorare template recognition
- Aggiungere support per altre poker room
- Ottimizzare equity calculation
- Estendere decision logic

---

## 📜 Licenza

Progetto per uso personale/educativo. Non utilizzare per violare i Terms of Service delle poker room.

---

**Fase 5 - Live Advisor V1 Complete** 🎉

*Sistema end-to-end funzionante: Screenshot → Vision → Equity → Decision*
