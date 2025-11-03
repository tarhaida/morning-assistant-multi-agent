"""
Utility functions for the Morning Assistant project.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from paths import CONFIG_FILE_PATH, REASONING_CONFIG_FILE_PATH


def load_config(config_path: Path = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = CONFIG_FILE_PATH
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_reasoning_strategies(config_path: Path = REASONING_CONFIG_FILE_PATH) -> Dict[str, Any]:
    """
    Load reasoning strategies from YAML file.
    
    Args:
        config_path: Path to reasoning config file
        
    Returns:
        Reasoning strategies dictionary
    """
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def save_json(data: Dict[str, Any], filepath: Path):
    """
    Save data to JSON file.
    
    Args:
        data: Data to save
        filepath: Path to save file
    """
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def load_json(filepath: Path) -> Dict[str, Any]:
    """
    Load data from JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Data dictionary
    """
    with open(filepath, 'r') as f:
        return json.load(f)


def get_timestamp() -> str:
    """
    Get current timestamp string.
    
    Returns:
        Timestamp in YYYYMMDD_HHMMSS format
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def format_date(date_str: str = None) -> str:
    """
    Format date for display.
    
    Args:
        date_str: Date string (defaults to today)
        
    Returns:
        Formatted date string
    """
    if date_str is None:
        return datetime.now().strftime("%A, %B %d, %Y")
    return date_str
