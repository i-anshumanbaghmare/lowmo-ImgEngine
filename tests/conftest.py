"""
pytest configuration file - sets up Python path for imports
"""
import sys
from pathlib import Path

# Add src directory to Python path so imports work
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))