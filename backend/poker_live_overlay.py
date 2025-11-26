"""
POKER LIVE OVERLAY (WINDOWS)
Mostra i consigli dell'AI sopra il tavolo.
"""
import sys
import time
import requests
from PyQt5 import QtWidgets, QtCore, QtGui
from screenshot_client import PokerClient


API_URL = "http://localhost:8001/api"

class Overlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # Configurazione finestra: Sempre in primo piano, senza bordi, trasparente
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint | 
            QtCore.Qt.FramelessWindowHint | 
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.client: PokerClient | None = None

        
        self.initUI()
        
        # Timer aggiornamento (ogni 1 secondo)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        
        # Container principale con sfondo semi-trasparente
        self.container = QtWidgets.QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background-color: rgba(20, 20, 30, 230);
                border: 2px solid #FFD700;
                border-radius: 15px;
            }
        """)
        
        in_layout = QtWidgets.QVBoxLayout()
        
        # Header
        self.lbl_header = QtWidgets.QLabel("🤖 AI COACH")
        self.lbl_header.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 14px;")
        self.lbl_header.setAlignment(QtCore.Qt.AlignCenter)
        in_layout.addWidget(self.lbl_header)
        
        # Azione Consigliata (Grande)
        self.lbl_action = QtWidgets.QLabel("IN ATTESA...")
        self.lbl_action.setStyleSheet("color: white; font-size: 24px; font-weight: 900;")
        self.lbl_action.setAlignment(QtCore.Qt.AlignCenter)
        in_layout.addWidget(self.lbl_action)
        
        # Equity e Confidenza
        stats_layout = QtWidgets.QHBoxLayout()
        self.lbl_equity = QtWidgets.QLabel("Eq: --%")
        self.lbl_equity.setStyleSheet("color: #00FF00; font-weight: bold;")
        self.lbl_conf = QtWidgets.QLabel("Conf: --%")
        self.lbl_conf.setStyleSheet("color: #00FFFF; font-weight: bold;")
        stats_layout.addWidget(self.lbl_equity)
        stats_layout.addWidget(self.lbl_conf)
        in_layout.addLayout(stats_layout)
        
        # Commento AI
        self.lbl_comment = QtWidgets.QLabel("Avvia il client per iniziare l'analisi...")
        self.lbl_comment.setStyleSheet("color: #DDDDDD; font-size: 11px; font-style: italic;")
        self.lbl_comment.setWordWrap(True)
        self.lbl_comment.setAlignment(QtCore.Qt.AlignCenter)
        in_layout.addWidget(self.lbl_comment)
        
        self.container.setLayout(in_layout)
        layout.addWidget(self.container)
        
        self.setLayout(layout)
        self.resize(320, 200)
        self.move(50, 50) # Posizione iniziale

    def update_data(self):
        try:
            # Chiama il server per ottenere l'ultima analisi
            response = requests.get(f"{API_URL}/poker/live/latest", timeout=1)
            if response.status_code == 200:
                data = response.json()
                
                action = data.get("recommended_action", "---")
                amount = data.get("recommended_amount", 0)
                equity = data.get("equity_estimate", 0) * 100
                conf = data.get("confidence", 0) * 100
                comment = data.get("ai_comment", "")
                
                # Aggiorna UI
                action_text = action
                if action == "RAISE" and amount > 0:
                    action_text += f" ${amount:.2f}"
                
                self.lbl_action.setText(action_text)
                
                # Colori dinamici
                if action == "FOLD":
                    self.lbl_action.setStyleSheet("color: #FF4444; font-size: 24px; font-weight: 900;")
                elif action == "CALL":
                    self.lbl_action.setStyleSheet("color: #FFFF00; font-size: 24px; font-weight: 900;")
                elif action == "RAISE":
                    self.lbl_action.setStyleSheet("color: #00FF00; font-size: 24px; font-weight: 900;")
                else:
                    self.lbl_action.setStyleSheet("color: white; font-size: 24px; font-weight: 900;")
                
                self.lbl_equity.setText(f"Eq: {equity:.1f}%")
                self.lbl_conf.setText(f"Conf: {conf:.0f}%")
                self.lbl_comment.setText(comment)
                
        except Exception as e:
            # Se il server è spento o errore
            self.lbl_action.setText("OFFLINE")
            self.lbl_action.setStyleSheet("color: gray; font-size: 20px;")

    # Permette di trascinare la finestra con il mouse
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = event.globalPos() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = Overlay()
    ex.show()
    sys.exit(app.exec_())
