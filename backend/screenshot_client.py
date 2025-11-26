"""
POKER SCREENSHOT CLIENT (VISION ONLY)
Invia screenshot direttamente all'endpoint Vision AI.
"""
import time
import io
import requests
from PIL import Image
import mss

# Configurazione
API_URL = "http://localhost:8001/api/vision/analyze"
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
        print(f"✅ Client Vision avviato.")
        print(f"🎯 Target: {API_URL}")

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
                monitor = {"left": window.left, "top": window.top, "width": window.width, "height": window.height}
                sct_img = self.sct.grab(monitor)
                print(f"📸 Finestra: {window.title}", end=" -> ")
            else:
                sct_img = self.sct.grab(self.sct.monitors[1])
                print("📸 Schermo intero", end=" -> ")
            
            return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        except Exception as e:
            print(f"❌ Errore cattura: {e}")
            return None

    def send_to_vision(self, img):
        try:
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            files = {'file': ('screen.png', img_byte_arr, 'image/png')}
            
            # Chiamata diretta a Vision AI
            res = requests.post(API_URL, files=files, timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                analysis = data.get("analysis", {})
                action = analysis.get("recommended_action", "???")
                print(f"✅ {action}")
            else:
                print(f"⚠️ Server: {res.status_code}")
                
        except Exception as e:
            print(f"❌ Errore invio: {e}")

    def run(self):
        print("🚀 Loop attivo (Ctrl+C per stop)...")
        while True:
            img = self.capture()
            if img:
                self.send_to_vision(img)
            time.sleep(INTERVAL)

if __name__ == "__main__":
    client = PokerClient()
    client.run()
