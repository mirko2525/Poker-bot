# 🎴 Poker AI Assistant - Client PC

Guida completa per usare il sistema sul tuo PC Windows.

---

## 📋 REQUISITI

### Software necessario:
- **Python 3.8+** installato
- **PokerStars** (app desktop o browser)
- Connessione internet

---

## 🚀 INSTALLAZIONE RAPIDA

### 1. Installa le dipendenze

```powershell
# Apri PowerShell nella cartella backend
cd C:\Users\mirko\Desktop\Poker-bot-main\backend

# Installa tutte le dipendenze in un colpo solo
pip install mss pygetwindow pillow requests PyQt5
```

### 2. Verifica l'installazione

```powershell
python --version
# Dovrebbe mostrare Python 3.8 o superiore
```

---

## 🎮 AVVIO SISTEMA

### Avvia 2 finestre PowerShell separate:

#### **FINESTRA 1 - Screenshot Client**
```powershell
cd C:\Users\mirko\Desktop\Poker-bot-main\backend
python screenshot_client.py
```

**Cosa fa:**
- Trova automaticamente la finestra PokerStars
- Cattura screenshot ogni 3 secondi
- Invia al backend Emergent
- Mostra statistiche upload

#### **FINESTRA 2 - Overlay AI**
```powershell
cd C:\Users\mirko\Desktop\Poker-bot-main\backend
python poker_live_overlay.py
```

**Cosa fa:**
- Mostra overlay sempre on top
- Si aggiorna ogni 3 secondi con analisi AI
- Visualizza: azione consigliata, equity, confidenza, commento AI

---

## 📊 COSA VEDRAI

### Screenshot Client (Finestra 1):
```
╔════════════════════════════════════════╗
║      POKER SCREENSHOT CLIENT           ║
╚════════════════════════════════════════╝

🎯 Backend: https://poker-assistant-2.preview.emergentagent.com/api
⏱️  Intervallo: 3 secondi
🎴 Tavolo ID: 1

✅ Finestra trovata: 'PokerStars - No Limit Hold'em'
📸 [20:15:30] Screenshot #1 catturato → ✅ Inviato
📸 [20:15:33] Screenshot #2 catturato → ✅ Inviato
📸 [20:15:36] Screenshot #3 catturato → ✅ Inviato
```

### Overlay AI (Finestra 2):
```
┌─────────────────────────────────┐
│  🎴 TAVOLO 1              ●     │
├─────────────────────────────────┤
│  Carte: As Kd vs 7h 8h 2c       │
│                                 │
│          FOLD                   │  ← Rosso se FOLD
│                                 │
│  Equity: 30.0%   Conf: 80.0%   │
├─────────────────────────────────┤
│  💬 La mano non ha migliorato   │
│     con questo board. Le pot    │
│     odds non giustificano...    │
└─────────────────────────────────┘
```

---

## ⚙️ CONFIGURAZIONE

### Modifica intervallo aggiornamento

In `screenshot_client.py` (riga 26):
```python
SCREENSHOT_INTERVAL = 3  # Cambia a 5 per catture più lente
```

In `poker_live_overlay.py` (riga ~280):
```python
update_interval=3  # Cambia a 5 per aggiornamenti più lenti
```

### Posiziona overlay sopra il tavolo

In `poker_live_overlay.py` (riga ~280):
```python
overlay = PokerLiveOverlay(
    table_id=1,
    x=100,        # ← Pixel da sinistra (modifica qui)
    y=100,        # ← Pixel dall'alto (modifica qui)
    update_interval=3
)
```

---

## 🐛 RISOLUZIONE PROBLEMI

### ❌ "pygetwindow non disponibile"
```powershell
pip install pygetwindow
```

### ❌ "PyQt5 non installato"
```powershell
pip install PyQt5
```

### ❌ "Nessuna finestra PokerStars trovata"
**Soluzione:**
- Assicurati che PokerStars sia aperto
- La finestra deve essere VISIBILE (non minimizzata)
- Prova a rinominare la finestra con parole chiave: "PokerStars", "Texas Hold"

### ❌ "Upload fallito: 500"
**Soluzione:**
- Verifica che il backend Emergent sia online
- Apri nel browser: https://poker-assistant-2.preview.emergentagent.com/api/
- Dovrebbe mostrare: `{"message": "Poker Bot Demo API - Ready"}`

### ❌ "Hero: [] Board: []" (carte non riconosciute)
**Soluzione con Vision AI (nuovo sistema):**
- Il sistema ora usa Gemini Vision AI per riconoscere le carte
- Funziona meglio con PokerStars WEB (nel browser)
- Assicurati che le carte siano ben visibili nello screenshot

---

## 🔄 AGGIORNAMENTO CODICE

### Quando scarichi una nuova versione da GitHub:

```powershell
# 1. Ferma i client (Ctrl+C in entrambe le finestre)

# 2. Scarica nuova versione da GitHub

# 3. Riavvia i client
cd C:\Users\mirko\Desktop\Poker-bot-main\backend
python screenshot_client.py  # Finestra 1
python poker_live_overlay.py  # Finestra 2
```

**Non serve modificare nulla!** Gli URL sono già configurati. ✅

---

## 🎯 VERSIONE WEB vs DESKTOP

### PokerStars WEB (Consigliato con Vision AI)
- ✅ Migliore riconoscimento con Gemini Vision
- ✅ Layout più standard
- ✅ Funziona su qualsiasi sistema operativo
- ⚠️ Richiede browser aperto

### PokerStars Desktop App
- ✅ Performance migliori
- ✅ Finestra dedicata
- ⚠️ Riconoscimento carte con template matching (meno affidabile)

---

## 📞 SUPPORTO

### Test rapido sistema:
```powershell
# Test API backend
curl https://poker-assistant-2.preview.emergentagent.com/api/

# Test analisi AI (con dati mock)
cd C:\Users\mirko\Desktop\Poker-bot-main\backend
python test_live_analyze_flow.py
```

### Visualizza screenshot catturati:
```
https://poker-assistant-2.preview.emergentagent.com/api/table/1/screenshot
https://poker-assistant-2.preview.emergentagent.com/api/table/1/screenshot?debug=true
```

---

## 🎉 PRONTO!

Tutto è configurato e pronto all'uso. Basta:
1. Aprire PokerStars
2. Avviare `screenshot_client.py`
3. Avviare `poker_live_overlay.py`
4. Giocare! L'AI ti guiderà in tempo reale 🤖🎴

---

**Buona fortuna ai tavoli! 🍀**
