#!/usr/bin/env python3
"""
Coordinate Calibration Helper - Fase 3

Tool interattivo per calibrare manualmente le coordinate degli screenshot PokerStars reali.
Mostra l'immagine con sovrapposizioni per identificare le coordinate corrette.
"""

from PIL import Image, ImageDraw, ImageFont
import json
from pathlib import Path

def create_coordinate_overlay(image_path: str, config_path: str, output_path: str = "coordinate_overlay.png"):
    """
    Crea un'immagine con overlay delle coordinate per calibrazione visiva.
    """
    
    # Carica immagine e configurazione
    image = Image.open(image_path)
    with open(config_path) as f:
        config = json.load(f)
    
    # Crea una copia per disegnare
    overlay_image = image.copy()
    draw = ImageDraw.Draw(overlay_image)
    
    # Colori per le diverse regioni
    colors = {
        'table_region': 'yellow',
        'hero_cards': 'red',
        'board_cards': 'blue', 
        'hero_stack': 'green',
        'pot': 'orange'
    }
    
    # Disegna table region
    if 'table_region' in config:
        x, y, w, h = config['table_region']
        draw.rectangle([x, y, x+w, y+h], outline=colors['table_region'], width=3)
        draw.text((x+10, y+10), 'TABLE', fill=colors['table_region'])
    
    # Disegna hero cards
    if 'hero_cards' in config:
        for i, (x, y, w, h) in enumerate(config['hero_cards']):
            draw.rectangle([x, y, x+w, y+h], outline=colors['hero_cards'], width=2)
            draw.text((x+5, y+5), f'H{i+1}', fill=colors['hero_cards'])
    
    # Disegna board cards
    if 'board_cards' in config:
        for i, (x, y, w, h) in enumerate(config['board_cards']):
            draw.rectangle([x, y, x+w, y+h], outline=colors['board_cards'], width=2)
            draw.text((x+5, y+5), f'B{i+1}', fill=colors['board_cards'])
    
    # Disegna hero stack
    if 'hero_stack' in config:
        x, y, w, h = config['hero_stack']
        draw.rectangle([x, y, x+w, y+h], outline=colors['hero_stack'], width=2)
        draw.text((x+5, y+5), 'STACK', fill=colors['hero_stack'])
    
    # Disegna pot
    if 'pot' in config:
        x, y, w, h = config['pot']
        draw.rectangle([x, y, x+w, y+h], outline=colors['pot'], width=2)
        draw.text((x+5, y+5), 'POT', fill=colors['pot'])
    
    # Aggiungi legenda
    legend_y = 50
    for region, color in colors.items():
        draw.text((50, legend_y), f"{region.upper()}: {color}", fill=color)
        legend_y += 30
    
    # Salva immagine overlay
    overlay_image.save(output_path)
    print(f"✅ Coordinate overlay created: {output_path}")
    print(f"   Original image: {image.width}x{image.height}")
    
    return overlay_image

def suggest_coordinates(image_path: str):
    """
    Suggerisci coordinate basate sulla risoluzione dell'immagine.
    """
    
    image = Image.open(image_path)
    w, h = image.width, image.height
    
    print(f"📐 Image resolution: {w}x{h}")
    print()
    print("🎯 Suggested coordinates for PokerStars 6-max (adjust as needed):")
    
    # Proporzioni basate sull'analisi visuale degli screenshot
    suggested = {
        "room_name": "PokerStars 6-Max Calibrated",
        "resolution": [w, h],
        "table_region": [int(w*0.09), int(h*0.07), int(w*0.82), int(h*0.84)],
        "hero_cards": [
            [int(w*0.44), int(h*0.82), int(w*0.029), int(h*0.062)],
            [int(w*0.48), int(h*0.82), int(w*0.029), int(h*0.062)]
        ],
        "board_cards": [
            [int(w*0.37), int(h*0.435), int(w*0.029), int(h*0.062)],
            [int(w*0.41), int(h*0.435), int(w*0.029), int(h*0.062)],
            [int(w*0.45), int(h*0.435), int(w*0.029), int(h*0.062)],
            [int(w*0.49), int(h*0.435), int(w*0.029), int(h*0.062)],
            [int(w*0.53), int(h*0.435), int(w*0.029), int(h*0.062)]
        ],
        "hero_stack": [int(w*0.42), int(h*0.90), int(w*0.08), int(h*0.025)],
        "pot": [int(w*0.44), int(h*0.39), int(w*0.06), int(h*0.022)]
    }
    
    print(json.dumps(suggested, indent=2))
    
    return suggested

def main():
    """Funzione principale per calibrazione coordinate."""
    
    print("🎯 COORDINATE CALIBRATION HELPER - FASE 3")
    print("=" * 50)
    
    # Lista screenshot disponibili
    screenshots_dir = Path("screenshots")
    screenshots = list(screenshots_dir.glob("pokerstars_*.png"))
    
    if not screenshots:
        print("❌ No PokerStars screenshots found in screenshots/ directory")
        return
    
    # Usa il primo screenshot per calibrazione
    screenshot_path = str(screenshots[0])
    config_path = "rooms/pokerstars_6max.json"
    
    print(f"📷 Using screenshot: {screenshot_path}")
    print(f"⚙️  Config file: {config_path}")
    print()
    
    # Suggerisci coordinate iniziali
    suggested_config = suggest_coordinates(screenshot_path)
    
    # Salva configurazione suggerita
    with open("rooms/pokerstars_6max_suggested.json", "w") as f:
        json.dump(suggested_config, f, indent=2)
    
    print()
    print(f"💾 Suggested config saved to: rooms/pokerstars_6max_suggested.json")
    
    # Crea overlay visivo con configurazione attuale
    if Path(config_path).exists():
        print("🎨 Creating overlay with current configuration...")
        create_coordinate_overlay(screenshot_path, config_path, "current_overlay.png")
    
    # Crea overlay con configurazione suggerita
    print("🎨 Creating overlay with suggested configuration...")
    create_coordinate_overlay(screenshot_path, "rooms/pokerstars_6max_suggested.json", "suggested_overlay.png")
    
    print()
    print("🔧 Next steps:")
    print("1. Review suggested_overlay.png to see proposed coordinates")
    print("2. Adjust coordinates in pokerstars_6max_suggested.json if needed")
    print("3. Copy pokerstars_6max_suggested.json to pokerstars_6max.json")
    print("4. Run analyze_screenshot.py to test extraction")

if __name__ == "__main__":
    main()