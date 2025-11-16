"""
Static Screenshot Handler Module - Fase 3

This module handles loading and processing static screenshots of poker tables.
Uses Pillow (PIL) to crop table regions from full screenshots.

Ordini del Capo - Fase 3: Static screenshot handling with table region extraction.
"""

from PIL import Image
from pathlib import Path
from typing import Optional
import logging

from table_layout import RoomConfig, validate_coordinates

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_table_image(image_path: str, room_config: RoomConfig) -> Image.Image:
    """
    Load a screenshot and crop it to the table region.
    
    Args:
        image_path: Path to the screenshot image file
        room_config: Room configuration with table region coordinates
        
    Returns:
        PIL Image object of the cropped table area
        
    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If image cannot be processed or coordinates are invalid
    """
    
    image_file = Path(image_path)
    
    if not image_file.exists():
        raise FileNotFoundError(f"Screenshot file not found: {image_path}")
    
    try:
        # Load the full screenshot
        full_image = Image.open(image_file)
        logger.info(f"Loaded screenshot: {image_file.name} ({full_image.width}x{full_image.height})")
        
        # Validate coordinates against full image
        warnings = validate_coordinates(room_config, full_image.width, full_image.height)
        if warnings:
            logger.warning("Coordinate validation warnings:")
            for warning in warnings:
                logger.warning(f"  - {warning}")
        
        # Extract table region coordinates
        x, y, width, height = room_config.table_region
        
        # Ensure coordinates are within bounds
        x = max(0, min(x, full_image.width))
        y = max(0, min(y, full_image.height))
        x2 = min(x + width, full_image.width)
        y2 = min(y + height, full_image.height)
        
        # Crop to table region
        table_image = full_image.crop((x, y, x2, y2))
        
        logger.info(f"Cropped table region: ({x}, {y}) to ({x2}, {y2}) -> {table_image.width}x{table_image.height}")
        
        return table_image
        
    except Exception as e:
        raise ValueError(f"Error processing image {image_path}: {e}")


def save_debug_image(image: Image.Image, output_path: str, prefix: str = "") -> None:
    """
    Save an image with optional prefix for debugging purposes.
    
    Args:
        image: PIL Image to save
        output_path: Directory path for saving
        prefix: Optional prefix for filename
    """
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{prefix}debug_table.png" if prefix else "debug_table.png"
    save_path = output_dir / filename
    
    image.save(save_path)
    logger.info(f"Saved debug image: {save_path}")


def get_image_info(image_path: str) -> dict:
    """
    Get basic information about an image file.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary with image information (width, height, format, mode)
    """
    try:
        with Image.open(image_path) as img:
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'size_bytes': Path(image_path).stat().st_size
            }
    except Exception as e:
        logger.error(f"Error reading image info for {image_path}: {e}")
        return {}
