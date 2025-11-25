# 🧠 Vision AI Analyzer - Guida Rapida

Sistema **separato e pulito** per analizzare screenshot poker manualmente con Gemini Vision.

---

## 🌐 ACCESSO WEB (iPhone, iPad, qualsiasi dispositivo)

### URL Principale:
```
https://poker-assistant-2.preview.emergentagent.com/vision
```

---

## 📱 COME USARE DALL'iPHONE:

### 1. **Apri PokerStars**
- App mobile o versione web nel browser
- Entra in un tavolo

### 2. **Fai Screenshot**
- Premi: **Power Button + Volume Up**
- Lo screenshot viene salvato in Foto

### 3. **Apri Vision Analyzer**
```
Safari → https://poker-assistant-2.preview.emergentagent.com/vision
```

### 4. **Carica e Analizza**
1. Tap su "📁 Scegli File"
2. Seleziona lo screenshot dalle Foto
3. Tap su "🧠 Analizza con AI"
4. Aspetta 3-5 secondi

### 5. **Vedi Risultati**
- ✅ Carte riconosciute (hero + board)
- ✅ Azione consigliata (FOLD/CALL/RAISE)
- ✅ Equity stimata
- ✅ Confidenza AI
- ✅ Analisi strategica in italiano

---

## 🎯 COSA MOSTRA:

### Esempio Output:
```
🎴 Carte Riconosciute
Hero: As Kd
Board (FLOP): 7h 8h 2c

🎯 Azione Consigliata
FOLD

📊 Stats
Equity: 30.5%
Confidenza: 85.2%

💰 Situazione Tavolo
Stack: $95.00
Pot: $12.00
To Call: $5.00

🤖 Analisi AI
"La tua mano non ha migliorato con questo board.
Con solo overcard e pot odds sfavorevoli (29%),
il fold è la scelta corretta per preservare lo stack..."
```

---

## 📁 FILES CREATI (Sistema Separato):

### Backend:
- **`vision_analyzer_api.py`** - Endpoint dedicato (nuovo)
- **`poker_vision_ai.py`** - Modulo Gemini Vision (già esistente)

### Frontend:
- **`src/pages/VisionAnalyzer.jsx`** - Pagina upload (nuovo)

### Modifiche Minime:
- **`server.py`** - Aggiunta 1 import + 1 riga per router
- **`App.js`** - Aggiunta 1 import + 1 route

---

## 🔧 API ENDPOINT:

### POST `/api/vision/analyze`
Upload e analizza screenshot.

**Request:**
```
Content-Type: multipart/form-data
file: <image.png>
```

**Response:**
```json
{
  "status": "success",
  "message": "Analisi completata",
  "analysis": {
    "hero_cards": ["As", "Kd"],
    "board_cards": ["7h", "8h", "2c"],
    "street": "FLOP",
    "hero_stack": 95.0,
    "pot_size": 12.0,
    "to_call": 5.0,
    "recommended_action": "FOLD",
    "recommended_amount": 0.0,
    "equity_estimate": 0.305,
    "confidence": 0.852,
    "ai_comment": "Analisi in italiano..."
  }
}
```

### GET `/api/vision/health`
Health check del servizio.

---

## 💡 VANTAGGI:

✅ **Universale** - Funziona su qualsiasi dispositivo (iPhone, Android, PC)  
✅ **No installazione** - Solo browser  
✅ **Gemini Vision** - Riconosce carte automaticamente  
✅ **Analisi completa** - Non solo carte, ma strategia completa  
✅ **Italiano** - Commenti AI in italiano  
✅ **Separato** - Non interferisce con il resto del codice  

---

## ⚠️ LIMITAZIONI:

- ❌ **Non è automatico** - Devi fare screenshot manualmente
- ❌ **Non è real-time** - Un'analisi alla volta
- ⏱️ **Tempo analisi** - 3-5 secondi per screenshot

Per sistema **automatico real-time** serve il client PC.

---

## 🎮 CONFRONTO SISTEMI:

### Vision Analyzer (iPhone/Web) 📱
- ✅ Funziona ovunque
- ✅ Zero installazione
- ❌ Manuale (screenshot uno alla volta)

### Client Desktop (PC) 🖥️
- ✅ Completamente automatico
- ✅ Real-time (ogni 3 secondi)
- ✅ Overlay sempre on top
- ❌ Solo su PC

---

## 🚀 PRONTO!

Vai su iPhone e apri:
```
https://poker-assistant-2.preview.emergentagent.com/vision
```

Buon divertimento! 🎴🤖
