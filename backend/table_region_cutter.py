"""
Table Region Cutter Module - Fase 3

This module implements functions to cut specific regions from poker table images.
Extracts hero cards, board cards, pot, and hero stack regions using Pillow.

Ordini del Capo - Fase 3: Region extraction without actual card/number recognition.
"""

from PIL import Image
from typing import List, Optional
import logging

from table_layout import RoomConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cut_hero_cards(table_image: Image.Image, room_config: RoomConfig) -> List[Image.Image]:
    """
    Extract hero card regions from the table image.
    
    Args:
        table_image: PIL Image of the cropped table
        room_config: Room configuration with hero card coordinates
        
    Returns:
        List of PIL Images for hero cards (should be 2 cards)
    """
    hero_cards = []
    
    # Get table region offset for coordinate adjustment
    table_x, table_y, _, _ = room_config.table_region
    
    for i, card_coords in enumerate(room_config.hero_cards):
        try:
            # Adjust coordinates relative to table region
            x, y, width, height = card_coords
            x_rel = x - table_x
            y_rel = y - table_y
            
            # Ensure coordinates are within table image bounds
            x_rel = max(0, min(x_rel, table_image.width))
            y_rel = max(0, min(y_rel, table_image.height))
            x2 = min(x_rel + width, table_image.width)
            y2 = min(y_rel + height, table_image.height)
            
            # Crop the card region
            card_image = table_image.crop((x_rel, y_rel, x2, y2))
            hero_cards.append(card_image)
            
            logger.debug(f"Cut hero card {i+1}: ({x_rel}, {y_rel}) to ({x2}, {y2}) -> {card_image.width}x{card_image.height}")
            
        except Exception as e:
            logger.error(f"Error cutting hero card {i+1}: {e}")
            # Create a blank image as fallback
            blank_card = Image.new('RGB', (60, 85), color='gray')
            hero_cards.append(blank_card)
    
    logger.info(f"Extracted {len(hero_cards)} hero cards")
    return hero_cards


def cut_board_cards(table_image: Image.Image, room_config: RoomConfig) -> List[Image.Image]:
    """
    Extract board card regions from the table image.
    
    Args:
        table_image: PIL Image of the cropped table
        room_config: Room configuration with board card coordinates
        
    Returns:
        List of PIL Images for board cards (flop, turn, river - 5 total)
    """
    board_cards = []
    
    # Get table region offset for coordinate adjustment
    table_x, table_y, _, _ = room_config.table_region
    
    for i, card_coords in enumerate(room_config.board_cards):
        try:
            # Adjust coordinates relative to table region
            x, y, width, height = card_coords
            x_rel = x - table_x
            y_rel = y - table_y
            
            # Ensure coordinates are within table image bounds
            x_rel = max(0, min(x_rel, table_image.width))
            y_rel = max(0, min(y_rel, table_image.height))
            x2 = min(x_rel + width, table_image.width)
            y2 = min(y_rel + height, table_image.height)
            
            # Crop the card region
            card_image = table_image.crop((x_rel, y_rel, x2, y2))
            board_cards.append(card_image)
            
            card_names = ['Flop 1', 'Flop 2', 'Flop 3', 'Turn', 'River']
            card_name = card_names[i] if i < len(card_names) else f'Board {i+1}'
            logger.debug(f"Cut {card_name}: ({x_rel}, {y_rel}) to ({x2}, {y2}) -> {card_image.width}x{card_image.height}")
            
        except Exception as e:
            logger.error(f"Error cutting board card {i+1}: {e}")
            # Create a blank image as fallback
            blank_card = Image.new('RGB', (60, 85), color='gray')
            board_cards.append(blank_card)
    
    logger.info(f"Extracted {len(board_cards)} board cards")
    return board_cards


def cut_pot_region(table_image: Image.Image, room_config: RoomConfig) -> Image.Image:
    """
    Extract pot amount region from the table image.
    
    Args:
        table_image: PIL Image of the cropped table
        room_config: Room configuration with pot coordinates
        
    Returns:
        PIL Image of the pot region
    """
    try:
        # Get table region offset for coordinate adjustment
        table_x, table_y, _, _ = room_config.table_region
        
        # Adjust coordinates relative to table region
        x, y, width, height = room_config.pot
        x_rel = x - table_x
        y_rel = y - table_y
        
        # Ensure coordinates are within table image bounds
        x_rel = max(0, min(x_rel, table_image.width))
        y_rel = max(0, min(y_rel, table_image.height))
        x2 = min(x_rel + width, table_image.width)
        y2 = min(y_rel + height, table_image.height)
        
        # Crop the pot region
        pot_image = table_image.crop((x_rel, y_rel, x2, y2))
        
        logger.debug(f"Cut pot region: ({x_rel}, {y_rel}) to ({x2}, {y2}) -> {pot_image.width}x{pot_image.height}")
        logger.info("Extracted pot region")
        
        return pot_image
        
    except Exception as e:
        logger.error(f"Error cutting pot region: {e}")
        # Create a blank image as fallback
        blank_pot = Image.new('RGB', (100, 25), color='gray')
        return blank_pot


def cut_hero_stack_region(table_image: Image.Image, room_config: RoomConfig) -> Image.Image:
    """
    Extract hero stack region from the table image.
    
    Args:
        table_image: PIL Image of the cropped table
        room_config: Room configuration with hero stack coordinates
        
    Returns:
        PIL Image of the hero stack region
    """
    try:
        # Get table region offset for coordinate adjustment
        table_x, table_y, _, _ = room_config.table_region
        
        # Adjust coordinates relative to table region
        x, y, width, height = room_config.hero_stack
        x_rel = x - table_x
        y_rel = y - table_y
        
        # Ensure coordinates are within table image bounds
        x_rel = max(0, min(x_rel, table_image.width))
        y_rel = max(0, min(y_rel, table_image.height))
        x2 = min(x_rel + width, table_image.width)
        y2 = min(y_rel + height, table_image.height)
        
        # Crop the hero stack region
        stack_image = table_image.crop((x_rel, y_rel, x2, y2))
        
        logger.debug(f"Cut hero stack region: ({x_rel}, {y_rel}) to ({x2}, {y2}) -> {stack_image.width}x{stack_image.height}")
        logger.info("Extracted hero stack region")
        
        return stack_image
        
    except Exception as e:
        logger.error(f"Error cutting hero stack region: {e}")
        # Create a blank image as fallback
        blank_stack = Image.new('RGB', (120, 30), color='gray')
        return blank_stack


def save_regions(hero_cards: List[Image.Image], board_cards: List[Image.Image], 
                pot_image: Image.Image, stack_image: Image.Image, 
                output_dir: str) -> None:
    """
    Save all extracted regions to files with clear naming convention.
    
    Args:
        hero_cards: List of hero card images
        board_cards: List of board card images  
        pot_image: Pot region image
        stack_image: Hero stack region image
        output_dir: Directory to save the images
    """
    from pathlib import Path
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Save hero cards
        for i, card_image in enumerate(hero_cards):
            filename = f"hero_card_{i+1}.png"
            card_image.save(output_path / filename)
            logger.info(f"Saved {filename}")
        
        # Save board cards
        for i, card_image in enumerate(board_cards):
            filename = f"board_card_{i+1}.png"
            card_image.save(output_path / filename)
            logger.info(f"Saved {filename}")
        
        # Save pot region
        pot_image.save(output_path / "pot_region.png")
        logger.info("Saved pot_region.png")
        
        # Save hero stack region
        stack_image.save(output_path / "hero_stack_region.png")
        logger.info("Saved hero_stack_region.png")
        
        logger.info(f"All regions saved to {output_path}")
        
    except Exception as e:
        logger.error(f"Error saving regions: {e}")
