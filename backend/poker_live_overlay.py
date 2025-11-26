"""
POKER LIVE OVERLAY (WINDOWS)
Mostra i consigli dell'AI sopra il tavolo.
"""
import sys
import time
import requests
from PyQt5 import QtWidgets, QtCore, QtGui

API_URL = "http://localhost:8001/api"

class Overlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.initUI()
        
        # Timer aggiornamento
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(2000) # Ogni 2 secondi

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        self.container = QtWidgets.QFrame()
        self.container.setStyleSheet("background: rgba(0, 0, 0, 200); border: 2px solid gold; border-radius: 10px;")
        
        in_layout = QtWidgets.QVBoxLayout()
        
        self.lbl_action = QtWidgets.QLabel("IN ATTESA...")
        self.lbl_action.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        self.lbl_action.setAlignment(QtCore.Qt.AlignCenter)
        
        self.lbl_info = QtWidgets.QLabel("Avvia il client per analizzare")
        self.lbl_info.setStyleSheet("color: #ddd; font-size: 12px;")
        self.lbl_info.setWordWrap(True)
        
        in_layout.addWidget(self.lbl_action)
        in_layout.addWidget(self.lbl_info)
        self.container.setLayout(in_layout)
        
        layout.addWidget(self.container)
        self.setLayout(layout)
        self.resize(300, 150)
        self.move(50, 50)

    def update_data(self):
        try:
            # Qui dovremmo chiamare un endpoint che ci dà l'ultima analisi salvata
            # Per ora simuliamo leggendo l'analisi live se disponibile
            # (In un sistema reale, il server dovrebbe salvare l'ultima analisi in memoria)
            pass 
            # Nota: Per semplicità, questo overlay è un placeholder. 
            # L'analisi vera viene stampata nella console del client per ora.
        except:
            pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = Overlay()
    ex.show()
    sys.exit(app.exec_())
