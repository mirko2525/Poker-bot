#!/usr/bin/env python3
"""
Tool per trovare automaticamente le coordinate della board zone
Cerca aree con pixel bianchi (carte) nello screenshot
"""

from PIL import Image, ImageDraw
import numpy as np

def find_white_regions(screenshot_path: str, output_path: str):
    """
    Trova regioni con pixel bianchi (carte) e visualizza
    """
    img = Image.open(screenshot_path)
    arr = np.array(img.convert('L'), dtype=np.float32)
    
    # Threshold per pixel bianchi (carte hanno sfondo bianco)
    white_mask = arr > 200
    
    # Trova bounding box delle regioni bianche nella parte centrale
    height, width = arr.shape
    
    # Cerca nella regione centrale (40-60% verticale, 20-80% orizzontale)
    y_start = int(height * 0.40)
    y_end = int(height * 0.60)
    x_start = int(width * 0.20)
    x_end = int(width * 0.80)
    
    central_region = white_mask[y_start:y_end, x_start:x_end]
    
    # Trova coordinate con white pixels nella regione centrale
    white_rows = np.any(central_region, axis=1)
    white_cols = np.any(central_region, axis=0)
    
    if not white_rows.any() or not white_cols.any():
        print("❌ Nessun pixel bianco trovato nella regione centrale!")
        return None
    
    # Trova min/max
    y_indices = np.where(white_rows)[0]
    x_indices = np.where(white_cols)[0]
    
    # Converti a coordinate assolute
    min_y = y_indices.min() + y_start
    max_y = y_indices.max() + y_start
    min_x = x_indices.min() + x_start
    max_x = x_indices.max() + x_start
    
    # Aggiungi margine
    margin = 20
    board_x = max(0, min_x - margin)
    board_y = max(0, min_y - margin)
    board_w = min_x, max_x + margin - board_x
    board_h = max_y + margin - board_y
    
    print(f"\n📍 COORDINATE RILEVATE:")
    print(f"   x={board_x}, y={board_y}")
    print(f"   width={board_w}, height={board_h}")
    
    # Visualizza
    vis_img = img.copy()
    draw = ImageDraw.Draw(vis_img)
    draw.rectangle([board_x, board_y, board_x + board_w, board_y + board_h],
                   outline="green", width=10)
    
    # Disegna 5 slot
    slot_width = board_w // 5
    for i in range(5):
        slot_x = board_x + (i * slot_width)
        draw.rectangle([slot_x, board_y, slot_x + slot_width, board_y + board_h],
                       outline="yellow", width=3)
    
    vis_img.save(output_path)
    print(f"✅ Visualizzazione salvata: {output_path}")
    
    return {
        'x': int(board_x),
        'y': int(board_y),
        'width': int(board_w),
        'height': int(board_h)
    }


if __name__ == "__main__":
    result = find_white_regions(
        "/app/Screenshot 2025-11-16 150959.png",
        "/app/backend/debug_auto_detected_zone.png"
    )
    
    if result:
        print(f"\n✅ Coordinate trovate automaticamente!")
        print(f"\nJSON config:")
        print(f'  "board_row": {{')
        print(f'    "x": {result["x"]},')
        print(f'    "y": {result["y"]},')
        print(f'    "width": {result["width"]},')
        print(f'    "height": {result["height"]}')
        print(f'  }}')
