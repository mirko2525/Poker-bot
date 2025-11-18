#!/usr/bin/env python3
"""
CARD RECOGNITION - FULL CARD SYSTEM
====================================

ORDINE CAPO: Sistema basato su matching di carte complete.

Vantaggi:
- Non serve ROI rank/suit precisa
- Grafica PokerStars (ombre, bordi) parte del pattern
- 52 template = veloce anche su CPU
- Più robusto contro variazioni

Pipeline:
1. Carica 52 template normalizzati
2. Crop carta intera dal tavolo
3. Normalize (resize + blur)
4. Match con tutti i 52 template (TM_CCOEFF_NORMED)
5. Ritorna best match con score
"""

import os
import glob
import cv2
import numpy as np
from typing import Dict, Tuple, Optional
from PIL import Image

TEMPLATES_DIR = "card_templates/pokerstars/full"

# ORDINE CAPO: Doppia soglia per confidenza
THRESHOLD_STRONG = 0.85  # Quasi certo
THRESHOLD_SOFT = 0.65    # Forse è lei, ma potrei sbagliare

class FullCardRecognizer:
    """
    Recognizer basato su full-card template matching.
    
    ORDINE CAPO - Doppia soglia:
    - strong (>0.85): carta sicura al 100%
    - weak (0.65-0.85): probabile ma non certissimo
    - none (<0.65): non riconosciuta / slot vuoto
    """
    
    def __init__(
        self, 
        templates_dir: str = TEMPLATES_DIR,
        threshold_strong: float = THRESHOLD_STRONG,
        threshold_soft: float = THRESHOLD_SOFT
    ):
        self.templates = self._load_templates(templates_dir)
        self.th_strong = threshold_strong
        self.th_soft = threshold_soft
        
        if self.templates:
            # Prendi dimensione dai template
            first_tmpl = next(iter(self.templates.values()))
            self.template_size = (first_tmpl.shape[1], first_tmpl.shape[0])  # (W, H)
            print(f"✅ FullCardRecognizer initialized")
            print(f"   Templates: {len(self.templates)}/52")
            print(f"   Size: {self.template_size[0]}×{self.template_size[1]}px")
            print(f"   Thresholds: strong={self.th_strong}, soft={self.th_soft}")
        else:
            self.template_size = None
            print(f"⚠️ No templates loaded!")
    
    def _load_templates(self, templates_dir: str) -> Dict[str, np.ndarray]:
        """
        Carica i 52 template normalizzati.
        
        Returns:
            Dict mapping card code (es: "Ah", "7c") → template image
        """
        templates = {}
        pattern = os.path.join(templates_dir, "*.png")
        
        for path in glob.glob(pattern):
            code = os.path.splitext(os.path.basename(path))[0]  # es: "Ah"
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            templates[code] = img
        
        return templates
    
    def normalize_card_crop(self, card_crop: np.ndarray) -> np.ndarray:
        """
        Normalizza un crop di carta per matching.
        
        Args:
            card_crop: Carta croppata dal tavolo (numpy array o PIL Image)
            
        Returns:
            Carta normalizzata (grayscale, resize, blur)
        """
        # Convert PIL to numpy if needed
        if isinstance(card_crop, Image.Image):
            card_crop = np.array(card_crop)
        
        # Grayscale if needed
        if len(card_crop.shape) == 3:
            card_crop = cv2.cvtColor(card_crop, cv2.COLOR_BGR2GRAY)
        
        # Resize a dimensione template
        card_norm = cv2.resize(card_crop, self.template_size, 
                               interpolation=cv2.INTER_AREA)
        
        # Blur leggero
        card_norm = cv2.GaussianBlur(card_norm, (3, 3), 0)
        
        return card_norm
    
    def recognize_card(
        self, 
        card_crop: np.ndarray,
        threshold: float = MATCH_THRESHOLD
    ) -> Tuple[Optional[str], float]:
        """
        Riconosce una carta usando template matching.
        
        Args:
            card_crop: Carta croppata dal tavolo
            threshold: Score minimo per match valido
            
        Returns:
            (card_code, score) es: ("Ah", 0.92) o (None, 0.0)
        """
        if not self.templates:
            return None, 0.0
        
        # Normalize crop
        card_norm = self.normalize_card_crop(card_crop)
        
        # Match con tutti i template
        best_code = None
        best_score = -1.0
        
        for code, tmpl in self.templates.items():
            # matchTemplate con TM_CCOEFF_NORMED
            # Ritorna valori [-1, 1], 1 = match perfetto
            res = cv2.matchTemplate(card_norm, tmpl, cv2.TM_CCOEFF_NORMED)
            score = float(res.max())
            
            if score > best_score:
                best_score = score
                best_code = code
        
        # Check threshold
        if best_score < threshold:
            return None, best_score
        
        return best_code, best_score
    
    def recognize_multiple(
        self,
        card_crops: list,
        threshold: float = MATCH_THRESHOLD
    ) -> list:
        """
        Riconosce multiple carte.
        
        Args:
            card_crops: Lista di crop di carte
            threshold: Score minimo
            
        Returns:
            Lista di (card_code, score)
        """
        results = []
        for crop in card_crops:
            code, score = self.recognize_card(crop, threshold)
            results.append((code, score))
        return results


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_card_from_table(
    screen: np.ndarray,
    x: int, y: int, w: int, h: int
) -> np.ndarray:
    """
    Estrae crop di una carta dal tavolo.
    
    Args:
        screen: Screenshot del tavolo (numpy array, any format)
        x, y, w, h: Bounding box della carta
        
    Returns:
        Crop della carta (numpy array)
    """
    # Grayscale if needed
    if len(screen.shape) == 3:
        screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    else:
        screen_gray = screen
    
    crop = screen_gray[y:y+h, x:x+w]
    return crop


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("\n" + "="*80)
    print("🎯 FULL-CARD RECOGNITION SYSTEM TEST")
    print("="*80 + "\n")
    
    # Initialize recognizer
    recognizer = FullCardRecognizer()
    
    if not recognizer.templates:
        print("❌ No templates found! Run normalize_fullcard_templates.py first")
        sys.exit(1)
    
    # Test con carte esempio se disponibili
    test_cards = [
        "test_4d.png",
        "test_7c.png",
        "test_Kd.png",
    ]
    
    print("\n" + "-"*80)
    print("TEST SU CARTE ESEMPIO")
    print("-"*80 + "\n")
    
    for test_file in test_cards:
        if not os.path.exists(test_file):
            continue
        
        # Load image
        img = cv2.imread(test_file)
        
        # Recognize
        code, score = recognizer.recognize_card(img)
        
        print(f"📸 {test_file:15s} → {code or 'None':3s} (score: {score:.3f})")
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETATO")
    print("="*80 + "\n")
