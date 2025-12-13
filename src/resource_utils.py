import sys
import os
from pathlib import Path

def get_base_path():
    """
    Returns the base path for bundled resources (Read-Only).
    If frozen via PyInstaller, returns sys._MEIPASS.
    Otherwise, returns the project root directory.
    """
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_data_path():
    """
    Returns the path for persistent data storage (Read/Write).
    Target: User Documents/Desktop Kitty
    """
    # Get User Documents folder
    # This works on Windows
    docs_dir = Path.home() / "Documents"
    app_dir = docs_dir / "Desktop Kitty"
    
    # Create if not exists
    if not app_dir.exists():
        try:
            app_dir.mkdir(parents=True, exist_ok=True)
            print(f"DEBUG: Created data directory at {app_dir}")
        except Exception as e:
            print(f"DEBUG: Error creating data dir: {e}")
            # Fallback to local execution dir if documents fails
            if getattr(sys, 'frozen', False):
                return os.path.dirname(sys.executable)
            return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
    return str(app_dir)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = get_base_path()
    return os.path.join(base_path, relative_path)
