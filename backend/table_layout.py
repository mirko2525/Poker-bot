"""
Table Layout Configuration Module - Fase 3

This module handles loading and managing poker room layout configurations
for table screenshot processing and region extraction.

Ordini del Capo - Fase 3: Bridge between JSON configuration and Python code.
"""

import json
from dataclasses import dataclass
from typing import List, Tuple
from pathlib import Path


@dataclass
class RoomConfig:
    """
    Dataclass to hold poker room layout configuration.
    
    Coordinates are in pixels relative to the entire screen.
    Format: [x, y, width, height]
    """
    room_name: str
    table_region: Tuple[int, int, int, int]  # [x, y, width, height] for entire table
    hero_cards: List[Tuple[int, int, int, int]]  # List of [x, y, w, h] for each hero card
    board_cards: List[Tuple[int, int, int, int]]  # List of [x, y, w, h] for flop/turn/river
    hero_stack: Tuple[int, int, int, int]  # [x, y, w, h] for hero stack region
    pot: Tuple[int, int, int, int]  # [x, y, w, h] for pot region


def load_room_config(config_path: str) -> RoomConfig:
    """
    Load room configuration from JSON file.
    
    Args:
        config_path: Path to the JSON configuration file
        
    Returns:
        RoomConfig: Loaded configuration object
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If JSON is invalid or missing required fields
    """
    
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Validate required fields
        required_fields = ['table_region', 'hero_cards', 'board_cards', 'hero_stack', 'pot']
        for field in required_fields:
            if field not in config_data:
                raise ValueError(f"Missing required field '{field}' in configuration")
        
        # Convert lists to tuples for immutable coordinates
        table_region = tuple(config_data['table_region'])
        hero_cards = [tuple(card) for card in config_data['hero_cards']]
        board_cards = [tuple(card) for card in config_data['board_cards']]
        hero_stack = tuple(config_data['hero_stack'])
        pot = tuple(config_data['pot'])
        
        # Validate coordinate formats
        if len(table_region) != 4:
            raise ValueError("table_region must have 4 values: [x, y, width, height]")
        
        if len(hero_cards) != 2:
            raise ValueError("hero_cards must contain exactly 2 card regions")
        
        if len(board_cards) != 5:
            raise ValueError("board_cards must contain exactly 5 card regions (flop/turn/river)")
        
        # Validate that all coordinates are 4-element tuples
        for i, card in enumerate(hero_cards):
            if len(card) != 4:
                raise ValueError(f"hero_cards[{i}] must have 4 values: [x, y, width, height]")
        
        for i, card in enumerate(board_cards):
            if len(card) != 4:
                raise ValueError(f"board_cards[{i}] must have 4 values: [x, y, width, height]")
        
        if len(hero_stack) != 4:
            raise ValueError("hero_stack must have 4 values: [x, y, width, height]")
        
        if len(pot) != 4:
            raise ValueError("pot must have 4 values: [x, y, width, height]")
        
        return RoomConfig(
            room_name=config_data.get('room_name', 'Unknown Room'),
            table_region=table_region,
            hero_cards=hero_cards,
            board_cards=board_cards,
            hero_stack=hero_stack,
            pot=pot
        )
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {e}")
    except Exception as e:
        raise ValueError(f"Error loading configuration: {e}")


def validate_coordinates(room_config: RoomConfig, image_width: int, image_height: int) -> List[str]:
    """
    Validate that all coordinates are within image bounds.
    
    Args:
        room_config: The room configuration to validate
        image_width: Width of the source image
        image_height: Height of the source image
        
    Returns:
        List of warning messages for coordinates that are out of bounds
    """
    warnings = []
    
    def check_region(name: str, region: Tuple[int, int, int, int]):
        x, y, w, h = region
        if x < 0 or y < 0:
            warnings.append(f"{name}: negative coordinates ({x}, {y})")
        if x + w > image_width:
            warnings.append(f"{name}: right edge ({x + w}) exceeds image width ({image_width})")
        if y + h > image_height:
            warnings.append(f"{name}: bottom edge ({y + h}) exceeds image height ({image_height})")
    
    # Check table region
    check_region("Table region", room_config.table_region)
    
    # Check hero cards
    for i, card_region in enumerate(room_config.hero_cards):
        check_region(f"Hero card {i+1}", card_region)
    
    # Check board cards
    for i, card_region in enumerate(room_config.board_cards):
        check_region(f"Board card {i+1}", card_region)
    
    # Check hero stack
    check_region("Hero stack", room_config.hero_stack)
    
    # Check pot
    check_region("Pot", room_config.pot)
    
    return warnings
