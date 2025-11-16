#!/usr/bin/env python3
"""
Create Mock Screenshot for Testing - Fase 3

Crea una screenshot simulata di un tavolo PokerStars per testare
il sistema di region extraction senza dipendere da screenshot reali.
"""

from PIL import Image, ImageDraw, ImageFont
import json
from pathlib import Path


def create_mock_pokerstars_screenshot():
    """
    Create a mock PokerStars table screenshot for testing purposes.
    """
    
    # Create a large screenshot (1920x1080)
    width, height = 1920, 1080
    screenshot = Image.new('RGB', (width, height), color='#2d5a2d')  # Dark green background
    draw = ImageDraw.Draw(screenshot)
    
    # Load configuration to get regions
    config_path = Path('rooms/pokerstars_6max.json')
    with open(config_path) as f:
        config = json.load(f)
    
    # Draw table region background (felt green)
    table_region = config['table_region']
    tx, ty, tw, th = table_region
    draw.rectangle([tx, ty, tx+tw, ty+th], fill='#0d4d0d', outline='#ffd700', width=3)
    
    # Draw hero cards
    for i, card_region in enumerate(config['hero_cards']):
        x, y, w, h = card_region
        # Card background (white)
        draw.rectangle([x, y, x+w, y+h], fill='white', outline='black', width=2)
        
        # Card content (mock)
        if i == 0:
            # Ace of Spades
            draw.text((x+10, y+10), 'A', fill='black', anchor='lt')
            draw.text((x+20, y+30), '♠', fill='black', anchor='lt')
        else:
            # King of Hearts  
            draw.text((x+10, y+10), 'K', fill='red', anchor='lt')
            draw.text((x+20, y+30), '♥', fill='red', anchor='lt')
    
    # Draw board cards
    board_cards_content = [('7', '♣', 'black'), ('T', '♦', 'red'), ('2', '♠', 'black'), ('?', '', 'gray'), ('?', '', 'gray')]
    for i, card_region in enumerate(config['board_cards']):
        x, y, w, h = card_region
        # Card background
        if i < 3:  # Flop cards are visible
            draw.rectangle([x, y, x+w, y+h], fill='white', outline='black', width=2)
            rank, suit, color = board_cards_content[i]
            draw.text((x+10, y+10), rank, fill=color, anchor='lt')
            if suit:
                draw.text((x+20, y+30), suit, fill=color, anchor='lt')
        else:  # Turn and River are hidden
            draw.rectangle([x, y, x+w, y+h], fill='#0066cc', outline='#004499', width=2)
    
    # Draw pot region
    pot_x, pot_y, pot_w, pot_h = config['pot']
    draw.rectangle([pot_x, pot_y, pot_x+pot_w, pot_y+pot_h], fill='#333333', outline='white', width=1)
    draw.text((pot_x+5, pot_y+5), '$24.50', fill='white', anchor='lt')
    
    # Draw hero stack region
    stack_x, stack_y, stack_w, stack_h = config['hero_stack']
    draw.rectangle([stack_x, stack_y, stack_x+stack_w, stack_y+stack_h], fill='#444444', outline='white', width=1)
    draw.text((stack_x+5, stack_y+5), '$87.25', fill='yellow', anchor='lt')
    
    # Add some table elements for realism
    # Dealer button
    draw.ellipse([700, 400, 720, 420], fill='white', outline='black', width=2)
    draw.text((710, 410), 'D', fill='black', anchor='mm')
    
    # Player positions (simplified)
    positions = [
        (500, 200, 'Player1'),
        (800, 200, 'Player2'), 
        (1000, 400, 'Player3'),
        (800, 600, 'Player4'),
        (500, 600, 'Player5'),
        (300, 400, 'Player6')
    ]
    
    for px, py, pname in positions:
        if pname != 'Player4':  # Player4 is the hero position
            draw.rectangle([px-50, py-20, px+50, py+20], fill='#666666', outline='white', width=1)
            draw.text((px, py), pname, fill='white', anchor='mm')\n    \n    return screenshot\n\n\ndef main():\n    \"\"\"Create and save mock screenshot.\"\"\"\n    print(\"Creating mock PokerStars screenshot for testing...\")\n    \n    # Create screenshots directory if it doesn't exist\n    screenshots_dir = Path('screenshots')\n    screenshots_dir.mkdir(exist_ok=True)\n    \n    # Create mock screenshot\n    mock_screenshot = create_mock_pokerstars_screenshot()\n    \n    # Save it\n    output_path = screenshots_dir / 'mock_pokerstars_table.png'\n    mock_screenshot.save(output_path)\n    \n    print(f\"✅ Mock screenshot created: {output_path}\")\n    print(f\"   Dimensions: {mock_screenshot.width}x{mock_screenshot.height}\")\n    print(\"   Content: A♠ K♥ vs 7♣ T♦ 2♠, Pot: $24.50, Stack: $87.25\")\n    print()\n    print(\"You can now run: python analyze_screenshot.py\")\n\n\nif __name__ == \"__main__\":\n    main()\n"