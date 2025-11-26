"""
POKER SCREENSHOT CLIENT (WINDOWS)
Cattura automatica e invio al server locale.
"""
import time
import io
import sys
import requests
from datetime import datetime
from PIL import Image
import mss
import mss.tools

# Configurazione per Localhost
API_URL = "http://localhost:8001/api"
TABLE_ID = 1
INTERVAL = 3

try:
    import pygetwindow as gw
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    PYGETWINDOW_AVAILABLE = False
    print("⚠️ pygetwindow non trovato. Userò screenshot schermo intero.")

class PokerClient:
    def __init__(self):
        self.sct = mss.mss()
        print(f"✅ Client avviato. Target: {API_URL}")

    def find_poker_window(self):
        if not PYGETWINDOW_AVAILABLE: return None
        titles = ["PokerStars", "Table", "Hold'em", "Omaha"]
        for w in gw.getAllWindows():
            for t in titles:
                if t.lower() in w.title.lower() and w.visible:
                    return w
        return None

    def capture(self):
        window = self.find_poker_window()
        try:
            if window:
                # Cattura finestra specifica
                monitor = {"left": window.left, "top": window.top, "width": window.width, "height": window.height}
                sct_img = self.sct.grab(monitor)
                print(f"📸 Cattura finestra: {window.title}")
            else:
                # Fallback: Schermo intero (Monitor 1)
                sct_img = self.sct.grab(self.sct.monitors[1])
                print("📸 Cattura schermo intero (Finestra poker non trovata)")
            
            return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        except Exception as e:
            print(f"❌ Errore cattura: {e}")
            return None

    def send_to_server(self, img):
        try:
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            files = {'file': ('screen.png', img_byte_arr, 'image/png')}
            res = requests.post(f"{API_URL}/table/{TABLE_ID}/upload", files=files, timeout=5)
            
            if res.status_code == 200:
                data = res.json()
                print(f"✅ Inviato! Server dice: {data.get('message', 'OK')}")
                
                # Triggera analisi AI immediata
                try:
                    # Recupera stato carte
                    cards_res = requests.get(f"{API_URL}/table/{TABLE_ID}/cards")
                    cards_data = cards_res.json()
                    
                    # Costruisci payload per AI (semplificato per ora)
                    ai_payload = {
                        "table_id": TABLE_ID,
                        "hero_cards": [c['code'] for c in cards_data.get('hero', []) if c['code']],
                        "board_cards": [c['code'] for c in cards_data.get('board', []) if c['code']],
                        "hero_stack": 100, "pot_size": 10, "to_call": 0, # Valori default se non letti
                        "street": "FLOP", "position": "BTN", "players": 2
                    }
                    
                    # Se abbiamo carte, chiediamo analisi
                    if ai_payload['hero_cards']:
                        print("🧠 Richiedo analisi AI...")
                        requests.post(f"{API_URL}/poker/live/analyze", json=ai_payload)
                except:
                    pass
            else:
                print(f"⚠️ Errore server: {res.status_code}")
        except Exception as e:
            print(f"❌ Errore connessione: {e}")

    def run(self):
        print("🚀 Avvio loop di cattura (Ctrl+C per fermare)...")
        while True:
            img = self.capture()
            if img:
                self.send_to_server(img)
            time.sleep(INTERVAL)

if __name__ == "__main__":
    client = PokerClient()
    client.run()
