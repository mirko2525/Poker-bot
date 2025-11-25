"""
🎴 POKER LIVE OVERLAY - Programma Desktop Completo

Integrazione end-to-end:
1. Loop ogni 3 secondi
2. Screenshot → Riconoscimento carte (TABLE_STATE)
3. POST /api/poker/live/analyze
4. Overlay sempre on top con analisi AI

REQUISITI (sul PC desktop):
- pip install PyQt5
- pip install requests
- Backend attivo su localhost:8001

USO:
python poker_live_overlay.py
"""
import sys
import time
import requests
from typing import Optional, Dict, Any

# Prova import PyQt5
try:
    from PyQt5 import QtWidgets, QtCore, QtGui
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("❌ PyQt5 non installato!")
    print("   Installa con: pip install PyQt5")
    sys.exit(1)

# Import del bridge
from bridge_tablestate_to_ai import table_state_to_ai_analysis


class PokerLiveOverlay(QtWidgets.QWidget):
    """
    Overlay desktop per tavolo poker con analisi AI in tempo reale.
    
    Features:
    - Sempre on top
    - Sfondo trasparente
    - Aggiornamento automatico ogni X secondi
    - Colori dinamici in base all'azione
    """
    
    def __init__(self, table_id: int = 1, x: int = 50, y: int = 50, update_interval: int = 3):
        super().__init__()
        
        self.table_id = table_id
        self.update_interval = update_interval  # Secondi tra aggiornamenti
        
        # Configurazione finestra
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # Setup UI
        self._setup_ui()
        
        # Posiziona
        self.move(x, y)
        self.adjustSize()
        
        # Timer per aggiornamento automatico
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_analysis)
        self.timer.start(update_interval * 1000)  # Converti in millisecondi
        
        # Primo aggiornamento immediato
        QtCore.QTimer.singleShot(100, self.update_analysis)
    
    def _setup_ui(self):
        """Crea l'interfaccia overlay."""
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Container principale
        self.container = QtWidgets.QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background: rgba(10, 10, 10, 230);
                border-radius: 12px;
                border: 3px solid rgba(255, 215, 0, 200);
            }
        """)
        
        inner_layout = QtWidgets.QVBoxLayout()
        inner_layout.setSpacing(6)
        inner_layout.setContentsMargins(14, 12, 14, 12)
        
        # Header
        header_layout = QtWidgets.QHBoxLayout()
        
        self.table_label = QtWidgets.QLabel(f"🎴 TAVOLO {self.table_id}")
        self.table_label.setStyleSheet("""
            color: #FFD700;
            font-size: 14pt;
            font-weight: bold;
        """)
        header_layout.addWidget(self.table_label)
        
        # Status indicator
        self.status_indicator = QtWidgets.QLabel("●")
        self.status_indicator.setStyleSheet("color: #00FF00; font-size: 16pt;")
        self.status_indicator.setToolTip("Status: Online")
        header_layout.addWidget(self.status_indicator)
        
        inner_layout.addLayout(header_layout)
        
        # Separatore
        sep1 = QtWidgets.QFrame()
        sep1.setFrameShape(QtWidgets.QFrame.HLine)
        sep1.setStyleSheet("background-color: rgba(255, 215, 0, 100); max-height: 2px;")
        inner_layout.addWidget(sep1)
        
        # Carte riconosciute
        self.cards_label = QtWidgets.QLabel("Carte: caricamento...")
        self.cards_label.setStyleSheet("""
            color: #87CEEB;
            font-size: 10pt;
            font-family: monospace;
        """)
        inner_layout.addWidget(self.cards_label)
        
        # Azione consigliata (BIG)
        self.action_label = QtWidgets.QLabel("AZIONE: ...")
        self.action_label.setStyleSheet("""
            color: white;
            font-size: 16pt;
            font-weight: bold;
            padding: 4px;
        """)
        self.action_label.setAlignment(QtCore.Qt.AlignCenter)
        inner_layout.addWidget(self.action_label)
        
        # Stats (equity + confidence)
        stats_layout = QtWidgets.QHBoxLayout()
        
        self.equity_label = QtWidgets.QLabel("Equity: ?%")
        self.equity_label.setStyleSheet("color: #90EE90; font-size: 11pt; font-weight: bold;")
        stats_layout.addWidget(self.equity_label)
        
        stats_layout.addStretch()
        
        self.confidence_label = QtWidgets.QLabel("Conf: ?%")
        self.confidence_label.setStyleSheet("color: #FFA500; font-size: 11pt; font-weight: bold;")
        stats_layout.addWidget(self.confidence_label)
        
        inner_layout.addLayout(stats_layout)
        
        # Separatore
        sep2 = QtWidgets.QFrame()
        sep2.setFrameShape(QtWidgets.QFrame.HLine)
        sep2.setStyleSheet("background-color: rgba(255, 255, 255, 50); max-height: 1px;")
        inner_layout.addWidget(sep2)
        
        # Commento AI
        self.comment_label = QtWidgets.QLabel("💬 In attesa di analisi...")
        self.comment_label.setWordWrap(True)
        self.comment_label.setStyleSheet("""
            color: #E0E0E0;
            font-size: 9pt;
            font-style: italic;
            padding: 4px;
        """)
        self.comment_label.setMaximumWidth(350)
        inner_layout.addWidget(self.comment_label)
        
        # Timestamp ultimo aggiornamento
        self.timestamp_label = QtWidgets.QLabel("Aggiornato: mai")
        self.timestamp_label.setStyleSheet("""
            color: #808080;
            font-size: 8pt;
        """)
        self.timestamp_label.setAlignment(QtCore.Qt.AlignRight)
        inner_layout.addWidget(self.timestamp_label)
        
        self.container.setLayout(inner_layout)
        layout.addWidget(self.container)
        self.setLayout(layout)
    
    def update_analysis(self):
        """
        Aggiorna l'overlay con nuova analisi AI.
        Chiamato automaticamente dal timer.
        """
        try:
            # Indica caricamento
            self.status_indicator.setStyleSheet("color: #FFA500; font-size: 16pt;")
            self.status_indicator.setToolTip("Status: Aggiornamento...")
            
            # Chiama bridge per ottenere analisi
            result = table_state_to_ai_analysis(self.table_id)
            
            if result:
                self._display_analysis(result)
                self.status_indicator.setStyleSheet("color: #00FF00; font-size: 16pt;")
                self.status_indicator.setToolTip("Status: Online")
            else:
                self._display_error("Analisi non disponibile")
                self.status_indicator.setStyleSheet("color: #FF4444; font-size: 16pt;")
                self.status_indicator.setToolTip("Status: Errore")
                
        except Exception as e:
            print(f"❌ Errore update: {e}")
            self._display_error(f"Errore: {str(e)[:50]}")
            self.status_indicator.setStyleSheet("color: #FF4444; font-size: 16pt;")
            self.status_indicator.setToolTip(f"Status: Errore - {e}")
    
    def _display_analysis(self, result: Dict[str, Any]):
        """Mostra i risultati dell'analisi nell'overlay."""
        action = result.get("recommended_action", "?")
        amount = result.get("recommended_amount", 0)
        equity = result.get("equity_estimate", 0)
        confidence = result.get("confidence", 0)
        comment = result.get("ai_comment", "")
        
        # Aggiorna carte (se disponibili dal result, altrimenti placeholder)
        # In futuro possiamo passare hero/board dal bridge
        self.cards_label.setText("Carte: riconosciute")
        
        # Azione con colore dinamico
        action_colors = {
            "FOLD": "#FF4444",
            "CALL": "#FFB84D",
            "RAISE": "#44FF44",
            "CHECK": "#87CEEB"
        }
        action_color = action_colors.get(action, "white")
        
        if action == "RAISE" and amount > 0:
            action_text = f"{action} ${amount:.2f}"
        else:
            action_text = action
        
        self.action_label.setText(action_text)
        self.action_label.setStyleSheet(f"""
            color: {action_color};
            font-size: 16pt;
            font-weight: bold;
            padding: 4px;
        """)
        
        # Equity e confidence
        equity_color = "#44FF44" if equity > 0.6 else "#FFB84D" if equity > 0.4 else "#FF4444"
        self.equity_label.setText(f"Equity: {equity*100:.1f}%")
        self.equity_label.setStyleSheet(f"color: {equity_color}; font-size: 11pt; font-weight: bold;")
        
        conf_color = "#44FF44" if confidence > 0.7 else "#FFB84D" if confidence > 0.5 else "#FF4444"
        self.confidence_label.setText(f"Conf: {confidence*100:.1f}%")
        self.confidence_label.setStyleSheet(f"color: {conf_color}; font-size: 11pt; font-weight: bold;")
        
        # Commento (troncato se troppo lungo)
        if len(comment) > 180:
            comment = comment[:177] + "..."
        self.comment_label.setText(f"💬 {comment}")
        
        # Timestamp
        current_time = time.strftime("%H:%M:%S")
        self.timestamp_label.setText(f"Aggiornato: {current_time}")
        
        # Ridimensiona
        self.adjustSize()
    
    def _display_error(self, message: str):
        """Mostra messaggio di errore."""
        self.action_label.setText("ERRORE")
        self.action_label.setStyleSheet("""
            color: #FF4444;
            font-size: 16pt;
            font-weight: bold;
        """)
        self.comment_label.setText(f"⚠️ {message}")
        self.equity_label.setText("Equity: ?%")
        self.confidence_label.setText("Conf: ?%")
        
        current_time = time.strftime("%H:%M:%S")
        self.timestamp_label.setText(f"Errore alle: {current_time}")


def main():
    """Avvia l'applicazione overlay."""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 18 + "POKER LIVE OVERLAY - v1.0" + " " * 25 + "║")
    print("╚" + "═" * 68 + "╝\n")
    
    print("🎴 Avvio overlay desktop con analisi AI in tempo reale...")
    print(f"🔄 Aggiornamento automatico ogni 3 secondi")
    print(f"🧠 AI Brain: Groq Llama-3.3-70B")
    print(f"📡 Backend: https://ee995408-c4e3-44e3-8067-f634e9d33e68.preview.emergentagent.com")
    print("\n" + "─" * 70)
    print("💡 L'overlay apparirà sempre on top sopra i tavoli poker.")
    print("   Mostra: azione consigliata, equity, confidenza, commento AI")
    print("\n🛑 Per chiudere: Ctrl+C nella console o chiudi la finestra overlay")
    print("─" * 70 + "\n")
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Crea overlay per tavolo 1
    # Posizione: modifica x,y per posizionarlo sopra il tuo tavolo
    overlay = PokerLiveOverlay(
        table_id=1,
        x=100,        # Posizione X (sinistra)
        y=100,        # Posizione Y (alto)
        update_interval=3  # Secondi tra aggiornamenti
    )
    
    overlay.show()
    
    print("✅ Overlay attivo!")
    print("   Se non vedi l'overlay, verifica:")
    print("   - Backend attivo: sudo supervisorctl status backend")
    print("   - Screenshot disponibile: ls /app/backend/data/screens/")
    print()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Overlay chiuso dall'utente. Arrivederci!")
        sys.exit(0)
