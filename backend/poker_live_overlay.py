"""
POKER LIVE OVERLAY (WINDOWS)
Mostra i consigli dell'AI sopra il tavolo.
Versione con:
- bottone "Analizza ora" per catturare e analizzare lo schermo solo su richiesta
- finestra ridimensionabile tramite slider di scala
"""

import sys
import io
from typing import Optional

import requests
from PyQt5 import QtWidgets, QtCore

from screenshot_client import PokerClient

API_URL = "http://localhost:8001/api"


class Overlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # Configurazione finestra: Sempre in primo piano, senza bordi, trasparente
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.client: Optional[PokerClient] = None
        self.scale_factor: float = 1.0

        self.initUI()

        # Timer aggiornamento (ogni 1 secondo) solo per leggere l'ultima analisi
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()

        # Container principale con sfondo semi-trasparente
        self.container = QtWidgets.QFrame()
        self.container.setStyleSheet(
            """
            QFrame {
                background-color: rgba(20, 20, 30, 230);
                border: 2px solid #FFD700;
                border-radius: 15px;
            }
            """
        )

        in_layout = QtWidgets.QVBoxLayout()
        in_layout.setSpacing(6)

        # Header
        self.lbl_header = QtWidgets.QLabel("🤖 AI COACH")
        self.lbl_header.setAlignment(QtCore.Qt.AlignCenter)

        # RIGA CONTROLLI: bottone Analizza + slider dimensione
        controls_layout = QtWidgets.QHBoxLayout()

        self.btn_analyze = QtWidgets.QPushButton("Analizza ora")
        self.btn_analyze.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_analyze.setStyleSheet(
            """
            QPushButton {
                background-color: #303050;
                color: white;
                border-radius: 8px;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background-color: #3c3c70;
            }
            """
        )
        self.btn_analyze.clicked.connect(self.on_analyze_clicked)

        self.lbl_scale = QtWidgets.QLabel("Dim.")
        self.lbl_scale.setStyleSheet("color: #CCCCCC; font-size: 10px;")

        self.scale_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.scale_slider.setRange(80, 220)  # 80% - 220%
        self.scale_slider.setValue(140)
        self.scale_slider.setFixedWidth(140)
        self.scale_slider.valueChanged.connect(self.on_scale_changed)

        controls_layout.addWidget(self.btn_analyze)
        controls_layout.addStretch()
        controls_layout.addWidget(self.lbl_scale)
        controls_layout.addWidget(self.scale_slider)

        # Azione Consigliata (Grande)
        self.lbl_action = QtWidgets.QLabel("IN ATTESA...")
        self.lbl_action.setAlignment(QtCore.Qt.AlignCenter)

        # Equity e Confidenza
        stats_layout = QtWidgets.QHBoxLayout()
        self.lbl_equity = QtWidgets.QLabel("Eq: --%")
        self.lbl_conf = QtWidgets.QLabel("Conf: --%")
        stats_layout.addWidget(self.lbl_equity)
        stats_layout.addWidget(self.lbl_conf)

        # Info carte lette
        self.lbl_cards = QtWidgets.QLabel("Hero: --  Board: --")
        self.lbl_cards.setWordWrap(True)
        self.lbl_cards.setAlignment(QtCore.Qt.AlignCenter)

        # Commento AI
        self.lbl_comment = QtWidgets.QLabel("Clicca 'Analizza ora' per iniziare l'analisi...")
        self.lbl_comment.setWordWrap(True)
        self.lbl_comment.setAlignment(QtCore.Qt.AlignCenter)

        # Componi layout interno
        in_layout.addWidget(self.lbl_header)
        in_layout.addLayout(controls_layout)
        in_layout.addWidget(self.lbl_action)
        in_layout.addLayout(stats_layout)
        in_layout.addWidget(self.lbl_cards)
        in_layout.addWidget(self.lbl_comment)

        self.container.setLayout(in_layout)
        layout.addWidget(self.container)

        self.setLayout(layout)
        self.resize(320, 200)
        self.move(50, 50)  # Posizione iniziale

        # Applica stile iniziale in base alla scala
        self.apply_scale()
        self.set_idle_style()

    # --------------------
    # Dimensione dinamica
    # --------------------
    def on_scale_changed(self, value: int):
        self.scale_factor = max(0.7, min(1.8, value / 100.0))
        self.apply_scale()

    def apply_scale(self):
        header_size = int(16 * self.scale_factor)
        action_size = int(24 * self.scale_factor)
        comment_size = max(11, int(13 * self.scale_factor))
        small_size = max(10, int(12 * self.scale_factor))

        self.lbl_header.setStyleSheet(
            f"color: #FFD700; font-weight: bold; font-size: {header_size}px;"
        )
        # colore e font di lbl_action vengono gestiti da set_action_style
        self.lbl_equity.setStyleSheet(
            f"color: #00FF00; font-weight: bold; font-size: {small_size}px;"
        )
        self.lbl_conf.setStyleSheet(
            f"color: #00FFFF; font-weight: bold; font-size: {small_size}px;"
        )
        self.lbl_comment.setStyleSheet(
            f"color: #DDDDDD; font-size: {comment_size}px; font-style: italic;"
        )

        # Ridimensiona finestra (base più grande per leggibilità)
        self.resize(int(380 * self.scale_factor), int(240 * self.scale_factor))

    def set_action_style(self, color: str, base_size: int = 24):
        size = int(base_size * self.scale_factor)
        self.lbl_action.setStyleSheet(
            f"color: {color}; font-size: {size}px; font-weight: 900;"
        )

    def set_idle_style(self):
        self.set_action_style("white", base_size=24)

    # --------------------
    # Logica di analisi
    # --------------------
    def on_analyze_clicked(self):
        self.lbl_comment.setText("Catturo il tavolo e analizzo...")
        QtWidgets.QApplication.processEvents()
        self.analyze_now()

    def analyze_now(self):
        """Cattura uno screenshot e lo invia a /api/vision/analyze una sola volta."""
        # Inizializza client di cattura se necessario
        if self.client is None:
            try:
                self.client = PokerClient()
            except Exception as e:
                self.lbl_comment.setText(f"Errore inizializzazione client: {e}")
                return

        img = self.client.capture()
        if img is None:
            self.lbl_comment.setText("Impossibile catturare la finestra PokerStars.")
            return

        try:
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format="PNG")
            img_byte_arr.seek(0)
            files = {"file": ("screen.png", img_byte_arr, "image/png")}

            res = requests.post(f"{API_URL}/vision/analyze", files=files, timeout=30)
            if res.status_code == 200:
                payload = res.json()
                analysis = payload.get("analysis", {})
                if analysis:
                    self.apply_analysis(analysis)
                else:
                    self.lbl_comment.setText("Analisi vuota dal server.")
            else:
                self.lbl_comment.setText(f"Errore server: {res.status_code}")
        except Exception as e:
            self.lbl_comment.setText(f"Errore invio: {e}")

    def apply_analysis(self, data: dict):
        """Applica un dizionario di analisi AI alla UI dell'overlay."""
        action = data.get("recommended_action", "---")
        amount = data.get("recommended_amount", 0) or 0
        equity = float(data.get("equity_estimate", 0) or 0) * 100
        conf = float(data.get("confidence", 0) or 0) * 100
        comment = data.get("ai_comment", "")
        hero_cards = data.get("hero_cards") or []
        board_cards = data.get("board_cards") or []

        # Mostra sempre le carte lette da Vision (debug + fiducia)
        hero_str = " ".join(hero_cards) if hero_cards else "--"
        board_str = " ".join(board_cards) if board_cards else "--"
        self.lbl_cards.setText(f"Hero: {hero_str}    Board: {board_str}")

        action_text = action
        if action == "RAISE" and amount > 0:
            try:
                action_text += f" ${float(amount):.2f}"
            except (TypeError, ValueError):
                pass

        # Colori dinamici
        if action == "FOLD":
            color = "#FF4444"
        elif action == "CALL":
            color = "#FFFF00"
        elif action == "RAISE":
            color = "#00FF00"
        else:
            color = "white"

        self.lbl_action.setText(action_text)
        self.set_action_style(color)

        self.lbl_equity.setText(f"Eq: {equity:.1f}%")
        self.lbl_conf.setText(f"Conf: {conf:.0f}%")
        if comment:
            self.lbl_comment.setText(comment)

    def update_data(self):
        """Legge periodicamente l'ultima analisi dal backend (leggero)."""
        try:
            response = requests.get(f"{API_URL}/poker/live/latest", timeout=1)
            if response.status_code == 200:
                data = response.json()
                if data:
                    self.apply_analysis(data)
        except Exception:
            # Se il server è spento o errore di rete
            self.lbl_action.setText("OFFLINE")
            self.set_action_style("gray", base_size=20)

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
