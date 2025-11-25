"""
ESEMPIO DI OVERLAY DESKTOP - Proof of Concept

Questo file mostra come creare un overlay sempre on top con sfondo trasparente
per visualizzare i consigli AI sopra i tavoli di poker.

INSTALLAZIONE RICHIESTA (sul PC desktop, non nel container):
pip install PyQt5

ARCHITETTURA:
1. Loop ogni 3-5 secondi:
   - Screenshot tavoli
   - Riconosci carte/stack/pot
   - POST a /api/poker/live/analyze
   - Aggiorna overlay

2. Overlay:
   - Sempre on top (WindowStaysOnTopHint)
   - Sfondo trasparente (WA_TranslucentBackground)
   - Box semitrasparente con info AI
"""

try:
    from PyQt5 import QtWidgets, QtCore, QtGui
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("⚠️ PyQt5 non installato. Questo è solo un esempio.")
    print("   Per usarlo su desktop: pip install PyQt5")


if PYQT_AVAILABLE:
    
    class PokerTableOverlay(QtWidgets.QWidget):
        """
        Overlay trasparente sempre on top per un tavolo di poker.
        
        Mostra:
        - Tavolo ID
        - Azione consigliata
        - Equity stimata
        - Confidenza
        - Commento AI (troncato)
        """
        
        def __init__(self, table_id: int = 1, x: int = 100, y: int = 100):
            super().__init__()
            self.table_id = table_id
            
            # Configurazione finestra
            self.setWindowFlags(
                QtCore.Qt.WindowStaysOnTopHint |  # Sempre on top
                QtCore.Qt.FramelessWindowHint |   # Senza bordi
                QtCore.Qt.Tool                     # Non appare nella taskbar
            )
            
            # Sfondo trasparente
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            
            # Layout
            layout = QtWidgets.QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            
            # Container con sfondo semitrasparente
            self.container = QtWidgets.QFrame()
            self.container.setStyleSheet("""
                QFrame {
                    background: rgba(0, 0, 0, 200);
                    border-radius: 10px;
                    border: 2px solid rgba(255, 215, 0, 180);
                }
            """)
            
            # Layout interno
            inner_layout = QtWidgets.QVBoxLayout()
            inner_layout.setSpacing(5)
            inner_layout.setContentsMargins(12, 10, 12, 10)
            
            # Header (Tavolo ID)
            self.header_label = QtWidgets.QLabel(f"🎴 TAVOLO {table_id}")
            self.header_label.setStyleSheet("""
                color: #FFD700;
                font-size: 13pt;
                font-weight: bold;
                padding: 2px;
            """)
            self.header_label.setAlignment(QtCore.Qt.AlignCenter)
            inner_layout.addWidget(self.header_label)
            
            # Azione consigliata
            self.action_label = QtWidgets.QLabel("Azione: ...")
            self.action_label.setStyleSheet("""
                color: white;
                font-size: 11pt;
                font-weight: bold;
            """)
            inner_layout.addWidget(self.action_label)
            
            # Equity
            self.equity_label = QtWidgets.QLabel("Equity: ...")
            self.equity_label.setStyleSheet("""
                color: #90EE90;
                font-size: 10pt;
            """)
            inner_layout.addWidget(self.equity_label)
            
            # Confidenza
            self.confidence_label = QtWidgets.QLabel("Confidenza: ...")
            self.confidence_label.setStyleSheet("""
                color: #87CEEB;
                font-size: 10pt;
            """)
            inner_layout.addWidget(self.confidence_label)
            
            # Separatore
            separator = QtWidgets.QFrame()
            separator.setFrameShape(QtWidgets.QFrame.HLine)
            separator.setStyleSheet("background-color: rgba(255, 255, 255, 50);")
            inner_layout.addWidget(separator)
            
            # Commento AI
            self.comment_label = QtWidgets.QLabel("💬 Caricamento...")
            self.comment_label.setWordWrap(True)
            self.comment_label.setStyleSheet("""
                color: #E0E0E0;
                font-size: 9pt;
                font-style: italic;
            """)
            self.comment_label.setMaximumWidth(300)
            inner_layout.addWidget(self.comment_label)
            
            self.container.setLayout(inner_layout)
            layout.addWidget(self.container)
            self.setLayout(layout)
            
            # Posiziona la finestra
            self.move(x, y)
            self.adjustSize()
        
        def update_from_api_response(self, response: dict):
            """
            Aggiorna l'overlay con la risposta dell'API.
            
            Args:
                response: dict con recommended_action, equity_estimate, confidence, ai_comment
            """
            action = response.get("recommended_action", "?")
            amount = response.get("recommended_amount", 0)
            equity = response.get("equity_estimate", 0)
            confidence = response.get("confidence", 0)
            comment = response.get("ai_comment", "")
            
            # Colore azione
            action_color = {
                "FOLD": "#FF4444",
                "CALL": "#FFB84D",
                "RAISE": "#44FF44"
            }.get(action, "white")
            
            # Aggiorna labels
            if action == "RAISE" and amount > 0:
                action_text = f"Azione: {action} ${amount:.2f}"
            else:
                action_text = f"Azione: {action}"
            
            self.action_label.setText(action_text)
            self.action_label.setStyleSheet(f"""
                color: {action_color};
                font-size: 11pt;
                font-weight: bold;
            """)
            
            self.equity_label.setText(f"Equity: {equity*100:.1f}%")
            self.confidence_label.setText(f"Confidenza: {confidence*100:.1f}%")
            
            # Tronca commento se troppo lungo
            if len(comment) > 150:
                comment = comment[:147] + "..."
            self.comment_label.setText(f"💬 {comment}")
            
            # Ridimensiona
            self.adjustSize()
    
    
    # ESEMPIO DI UTILIZZO
    if __name__ == "__main__":
        import sys
        
        app = QtWidgets.QApplication(sys.argv)
        
        # Crea overlay per tavolo 1
        overlay = PokerTableOverlay(table_id=1, x=100, y=100)
        
        # Simula risposta API
        example_response = {
            "recommended_action": "RAISE",
            "recommended_amount": 9.0,
            "equity_estimate": 0.68,
            "confidence": 0.82,
            "ai_comment": "La tua mano è forte su questo flop contro il range medio. Con top pair e ottimo kicker, alza per protezione e valore."
        }
        
        overlay.update_from_api_response(example_response)
        overlay.show()
        
        print("=" * 60)
        print("🎴 OVERLAY DESKTOP - ESEMPIO")
        print("=" * 60)
        print("L'overlay è ora visibile sullo schermo.")
        print("Caratteristiche:")
        print("  ✅ Sempre on top")
        print("  ✅ Sfondo trasparente")
        print("  ✅ Box semitrasparente nero con bordo oro")
        print("")
        print("Per integrare nel loop:")
        print("  1. Ogni 3-5 secondi, screenshot tavolo")
        print("  2. Riconosci carte/stack/pot")
        print("  3. POST a /api/poker/live/analyze")
        print("  4. overlay.update_from_api_response(response)")
        print("=" * 60)
        
        sys.exit(app.exec_())

else:
    # Fallback se PyQt5 non disponibile
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║  OVERLAY DESKTOP - ESEMPIO (PyQt5 non disponibile)        ║
    ╚════════════════════════════════════════════════════════════╝
    
    Questo file contiene il codice per creare un overlay desktop
    trasparente sempre on top.
    
    Per usarlo:
    1. Installa PyQt5 sul tuo PC: pip install PyQt5
    2. Esegui questo script: python overlay_desktop_example.py
    
    L'overlay mostrerà:
    - Tavolo ID
    - Azione consigliata (FOLD/CALL/RAISE)
    - Equity stimata
    - Livello di confidenza
    - Commento AI breve
    
    Integrazione nel loop:
    - Ogni 3-5 secondi:
      1. Screenshot tavolo
      2. Riconosci carte/stack/pot
      3. POST a /api/poker/live/analyze
      4. overlay.update_from_api_response(response)
    """)
