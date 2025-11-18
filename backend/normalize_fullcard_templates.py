#!/usr/bin/env python3
"""
NORMALIZE FULL-CARD TEMPLATES - ORDINE CAPO
============================================

Converte le 52 carte PokerStars in template normalizzati per matching.

Input:  card_templates_raw/deck52/*.png (naming italiano: 2cuori.png, Apicche.png, etc.)
Output: card_templates/pokerstars/full/*.png (naming standard: 2h.png, As.png, etc.)

Pipeline:
1. Carica carta raw
2. Grayscale
3. Resize a dimensione standard (prima carta = reference)
4. Gaussian blur (3x3) per ridurre rumore
5. Salva con nome standard (es: Ah.png)
"""

import os
import re
import glob
import cv2

INPUT_DIR = "card_templates_raw/deck52"
OUT_DIR = "card_templates/pokerstars/full"

os.makedirs(OUT_DIR, exist_ok=True)

# Mapping nome italiano → simbolo standard
SUITS_MAP_IT_SHORT = {
    "cuori": "h",
    "fiori": "c",
    "picche": "s",
    "quadri": "d",
    "cuadri": "d",  # typo protection
}

TARGET_SIZE = None  # (W, H) - prendo dalla prima carta

print("🎯 NORMALIZZAZIONE FULL-CARD TEMPLATES\n")

png_paths = sorted(glob.glob(os.path.join(INPUT_DIR, "*.png")))
print(f"Trovate {len(png_paths)} carte\n")

processed = 0
for path in png_paths:
    fname = os.path.basename(path)
    name, _ = os.path.splitext(fname)  # es: "2cuori" o "Apicche"
    
    # Separa rank e seme
    # Pattern: rank (2-9, T, J, Q, K, A) + seme (cuori, fiori, picche, quadri)
    m = re.match(r"([2-9TJQKA])(.+)", name, re.IGNORECASE)
    if not m:
        print(f"⚠️ Nome NON riconosciuto, skip: {fname}")
        continue
    
    rank_ch, suit_it = m.groups()
    rank_ch = rank_ch.upper()
    suit_it = suit_it.lower()
    
    # Fix typo comuni
    if suit_it == "cuadri":
        suit_it = "quadri"
    
    if suit_it not in SUITS_MAP_IT_SHORT:
        print(f"⚠️ Seme sconosciuto, skip: {fname} (suit={suit_it})")
        continue
    
    suit_short = SUITS_MAP_IT_SHORT[suit_it]  # h/c/s/d
    code = f"{rank_ch}{suit_short}"            # es: "Ah", "Td"
    
    # Carica immagine
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"❌ Errore lettura: {path}")
        continue
    
    h, w = img.shape[:2]
    
    # Fissa dimensione target sulla prima carta
    if TARGET_SIZE is None:
        TARGET_SIZE = (w, h)  # (W, H)
        print(f"📐 TARGET_SIZE fissata: {TARGET_SIZE[0]}×{TARGET_SIZE[1]}px\n")
    
    # Resize tutte alla stessa dimensione
    tmpl = cv2.resize(img, TARGET_SIZE, interpolation=cv2.INTER_AREA)
    
    # Blur leggero per ridurre rumore
    tmpl = cv2.GaussianBlur(tmpl, (3, 3), 0)
    
    # Salva
    out_path = os.path.join(OUT_DIR, f"{code}.png")
    cv2.imwrite(out_path, tmpl)
    
    print(f"✅ {fname:15s} → {code}.png")
    processed += 1

print(f"\n{'='*60}")
print(f"✅ NORMALIZZAZIONE COMPLETA")
print(f"{'='*60}")
print(f"Template processati: {processed}/52")
print(f"Dimensione standard: {TARGET_SIZE[0]}×{TARGET_SIZE[1]}px")
print(f"Output directory: {OUT_DIR}")
print(f"{'='*60}\n")

# Verifica che abbiamo tutti i 52 template
output_files = sorted(glob.glob(os.path.join(OUT_DIR, "*.png")))
if len(output_files) == 52:
    print("💣 DECK COMPLETO! PRONTO PER LA GUERRA! 🃏")
else:
    print(f"⚠️ Attenzione: solo {len(output_files)}/52 template generati")
