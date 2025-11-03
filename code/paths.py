"""
Path configurations for the Morning Assistant project.
Defines all directory paths used throughout the application.
"""

import os
from pathlib import Path

# Root directory (project root)
# Find the project root by looking for characteristic files
def find_project_root():
    """Find the project root by looking for config directory or requirements.txt"""
    current_path = Path(__file__).parent.absolute()
    
    # Search up the directory tree to find the project root
    search_path = current_path
    while search_path != search_path.parent:  # Don't go above filesystem root
        if (search_path / "config").exists() and (search_path / "config" / "config.yaml").exists():
            return search_path
        if (search_path / "requirements.txt").exists():
            return search_path
        search_path = search_path.parent
    
    # If we're in the code directory, try going up one level
    if current_path.name == "code":
        return current_path.parent
    
    # If we're in agents directory, go up two levels
    if current_path.name == "agents":
        return current_path.parent.parent
    
    # Fallback to the original method
    return Path(__file__).parent.parent.absolute()

ROOT_DIR = find_project_root()

# Main directories
CODE_DIR = ROOT_DIR / "code"
CONFIG_DIR = ROOT_DIR / "config"
DATA_DIR = ROOT_DIR / "data"
OUTPUTS_DIR = ROOT_DIR / "outputs"

# Config files
CONFIG_FILE_PATH = CONFIG_DIR / "config.yaml"
REASONING_CONFIG_FILE_PATH = CONFIG_DIR / "reasoning.yaml"

# Ensure directories exist
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Convert to strings for compatibility
def get_path_str(path: Path) -> str:
    """Convert Path object to string."""
    return str(path)
