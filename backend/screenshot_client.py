"""
POKER SCREENSHOT CLIENT - Cattura automatica PokerStars

Questo programma:
1. Trova la finestra PokerStars sul tuo PC
2. Ogni 3 secondi cattura uno screenshot
3. Invia lo screenshot al backend Emergent
4. Il backend riconosce le carte con Vision AI
5. L'overlay mostra l'analisi AI

REQUISITI:
- pip install mss pygetwindow pillow requests

USO:
python screenshot_client.py
"""
import time
import io
import sys
import requests
from datetime import datetime
from PIL import Image
import mss
import mss.tools

try:
    import pygetwindow as gw
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    PYGETWINDOW_AVAILABLE = False
    print("⚠️ pygetwindow non disponibile. Userò screenshot dello schermo intero.")


# ⚠️ CONFIGURAZIONE - URL già impostato per Emergent
API_URL = "https://poker-assistant-2.preview.emergentagent.com/api"
WINDOW_TITLE_KEYWORDS = ["PokerStars", "Poker Stars", "Texas Hold", "No Limit Hold"]
SCREENSHOT_INTERVAL = 3  # Secondi tra screenshot
TABLE_ID = 1  # ID tavolo da monitorare


class PokerScreenshotClient:
    """Client per cattura e invio screenshot PokerStars."""
    
    def __init__(self, api_url: str, interval: int = 3):
        self.api_url = api_url
        self.interval = interval
        self.sct = mss.mss()
        self.stats = {
            "screenshots_taken": 0,
            "uploads_success": 0,
            "uploads_failed": 0
        }
    
    def find_pokerstars_window(self):
        """Trova la finestra di PokerStars."""
        if not PYGETWINDOW_AVAILABLE:
            return None
        
        try:
            windows = gw.getAllWindows()
            
            for window in windows:
                for keyword in WINDOW_TITLE_KEYWORDS:
                    if keyword.lower() in window.title.lower() and window.visible:
                        print(f"✅ Finestra trovata: '{window.title}'")
                        return window
            
            print(f"⚠️ Nessuna finestra PokerStars trovata")
            return None
            
        except Exception as e:
            print(f"❌ Errore ricerca finestra: {e}")
            return None
    
    def capture_window(self, window):
        """Cattura screenshot della finestra specifica."""
        try:
            # Ottieni coordinate finestra
            left = window.left
            top = window.top
            width = window.width
            height = window.height
            
            # Verifica che la finestra sia valida
            if width <= 0 or height <= 0:
                print(f"⚠️ Finestra con dimensioni invalide: {width}x{height}")
                return None
            
            # Cattura con mss
            monitor = {
                "left": left,
                "top": top,
                "width": width,
                "height": height
            }
            
            screenshot = self.sct.grab(monitor)
            
            # Converti in PIL Image
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            
            return img
            
        except Exception as e:
            print(f"❌ Errore cattura finestra: {e}")
            return None
    
    def capture_fullscreen(self):
        """Cattura screenshot dello schermo intero (fallback)."""
        try:
            monitor = self.sct.monitors[1]  # Monitor principale
            screenshot = self.sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            return img
        except Exception as e:
            print(f"❌ Errore cattura schermo: {e}")
            return None
    
    def upload_screenshot(self, image: Image.Image, table_id: int = 1) -> bool:
        """Invia screenshot al backend."""
        try:
            # Converti image in bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # Prepara file upload
            files = {
                'file': ('screenshot.png', img_byte_arr, 'image/png')
            }
            
            # Invia al backend
            upload_url = f"{self.api_url}/table/{table_id}/upload"
            
            response = requests.post(
                upload_url,
                files=files,
                timeout=10
            )
            
            if response.status_code == 200:
                self.stats["uploads_success"] += 1
                return True
            else:
                print(f"⚠️ Upload fallito: {response.status_code} - {response.text[:100]}")
                self.stats["uploads_failed"] += 1
                return False
                
        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout durante upload")
            self.stats["uploads_failed"] += 1
            return False
        except Exception as e:
            print(f"❌ Errore upload: {e}")
            self.stats["uploads_failed"] += 1
            return False
    
    def run(self):
        """Loop principale - cattura e invia screenshot."""
        print("\n" + "╔" + "═" * 68 + "╗")
        print("║" + " " * 18 + "POKER SCREENSHOT CLIENT" + " " * 27 + "║")
        print("╚" + "═" * 68 + "╝\n")
        
        print(f"🎯 Backend: {self.api_url}")
        print(f"⏱️  Intervallo: {self.interval} secondi")
        print(f"🎴 Tavolo ID: {TABLE_ID}")
        print(f"🔍 Parole chiave finestra: {', '.join(WINDOW_TITLE_KEYWORDS)}")
        print()
        
        if not PYGETWINDOW_AVAILABLE:
            print("⚠️ pygetwindow non disponibile - userò screenshot schermo intero")
            print("   Per catturare solo PokerStars: pip install pygetwindow")
        
        print("\n🛑 Per fermare: Ctrl+C\n")
        print("─" * 70)
        
        last_window = None
        window_check_counter = 0
        
        try:
            while True:
                cycle_start = time.time()
                
                # Ogni 10 cicli, ricontrolla la finestra
                if window_check_counter % 10 == 0:
                    if PYGETWINDOW_AVAILABLE:
                        last_window = self.find_pokerstars_window()
                
                window_check_counter += 1
                
                # Cattura screenshot
                if last_window and PYGETWINDOW_AVAILABLE:
                    image = self.capture_window(last_window)
                else:
                    image = self.capture_fullscreen()
                
                if image is None:
                    print(f"⚠️ [{datetime.now().strftime('%H:%M:%S')}] Cattura fallita")
                    time.sleep(self.interval)
                    continue
                
                self.stats["screenshots_taken"] += 1
                
                # Invia al backend
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"📸 [{timestamp}] Screenshot #{self.stats['screenshots_taken']} catturato", end=" ")
                
                success = self.upload_screenshot(image, table_id=TABLE_ID)
                
                if success:
                    print("→ ✅ Inviato")
                else:
                    print("→ ❌ Errore")
                
                # Mostra stats ogni 10 screenshot
                if self.stats["screenshots_taken"] % 10 == 0:
                    self._print_stats()
                
                # Aspetta il tempo rimanente
                elapsed = time.time() - cycle_start
                sleep_time = max(0, self.interval - elapsed)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print("\n\n👋 Chiusura client...")
            self._print_stats()
            print("\n✅ Client chiuso correttamente.\n")
    
    def _print_stats(self):
        """Stampa statistiche."""
        print()
        print("─" * 70)
        print(f"📊 STATISTICHE:")
        print(f"   Screenshot catturati: {self.stats['screenshots_taken']}")
        print(f"   Upload riusciti:      {self.stats['uploads_success']}")
        print(f"   Upload falliti:       {self.stats['uploads_failed']}")
        if self.stats['screenshots_taken'] > 0:
            success_rate = (self.stats['uploads_success'] / self.stats['screenshots_taken']) * 100
            print(f"   Tasso successo:       {success_rate:.1f}%")
        print("─" * 70)
        print()


def main():
    """Avvia il client screenshot."""
    
    # Verifica configurazione
    if not API_URL:
        print("❌ Errore: API_URL non configurato!")
        print("   Modifica la variabile API_URL nel file screenshot_client.py")
        sys.exit(1)
    
    print("\n💡 SUGGERIMENTO:")
    print("   Per migliori risultati, apri PokerStars in una finestra separata")
    print("   (non a schermo intero) così il client può catturare solo il tavolo.\n")
    
    # Crea e avvia client
    client = PokerScreenshotClient(
        api_url=API_URL,
        interval=SCREENSHOT_INTERVAL
    )
    
    client.run()


if __name__ == "__main__":
    main()
