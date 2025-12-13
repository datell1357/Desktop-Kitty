import ctypes
import atexit
import os

# Windows API Constants (Cursor IDs)
OCR_NORMAL = 32512
OCR_IBEAM = 32513
OCR_WAIT = 32514
OCR_CROSS = 32515
OCR_UP = 32516
OCR_SIZE = 32640  # OBSOLETE: Use OCR_SIZEALL
OCR_ICON = 32641  # OBSOLETE: Use OCR_NORMAL
OCR_SIZENWSE = 32642
OCR_SIZENESW = 32643
OCR_SIZEWE = 32644
OCR_SIZENS = 32645
OCR_SIZEALL = 32646
OCR_NO = 32648
OCR_HAND = 32649
OCR_APPSTARTING = 32650
OCR_HELP = 32651

# List of all cursors to replace
ALL_CURSORS = [
    OCR_NORMAL, OCR_IBEAM, OCR_WAIT, OCR_CROSS, OCR_UP,
    OCR_SIZENWSE, OCR_SIZENESW, OCR_SIZEWE, OCR_SIZENS, 
    OCR_SIZEALL, OCR_NO, OCR_HAND, OCR_APPSTARTING, OCR_HELP
]

SPI_SETCURSORS = 0x0057
SPIF_SENDCHANGE = 0x0002
SPIF_UPDATEINIFILE = 0x0001

# Load User32 DLL
user32 = ctypes.windll.user32

def set_system_cursor(file_path):
    """
    Sets ALL system cursors to the cursor loaded from file_path.
    """
    if not os.path.exists(file_path):
        print(f"CURSOR_DEBUG: File not found: {file_path}")
        return False
        
    success_count = 0
    try:
        for cursor_id in ALL_CURSORS:
            # IMPORTANT: SetSystemCursor consumes (destroys) the hcursor passed to it.
            # We must load a fresh copy for EAHC system cursor we want to replace.
            hcursor = user32.LoadCursorFromFileW(file_path)
            
            if not hcursor:
                # If loading fails once (e.g. file lock?), it might fail for all, but let's try continue.
                print(f"CURSOR_DEBUG: Failed to load cursor for ID {cursor_id}")
                continue
                
            # Replace system cursor
            result = user32.SetSystemCursor(hcursor, cursor_id)
            
            if result:
                success_count += 1
            else:
                 print(f"CURSOR_DEBUG: Failed to set cursor ID {cursor_id}")

        return success_count > 0
        
    except Exception as e:
        print(f"CURSOR_DEBUG: Error setting cursor: {e}")
        return False

def restore_system_cursor():
    """
    Restores all system cursors to system defaults.
    """
    try:
        # SystemParametersInfoW with SPI_SETCURSORS and null resets cursors
        user32.SystemParametersInfoW(SPI_SETCURSORS, 0, None, SPIF_SENDCHANGE | SPIF_UPDATEINIFILE)
    except Exception as e:
        print(f"CURSOR_DEBUG: Error restoring cursor: {e}")

# Register cleanup on exit
atexit.register(restore_system_cursor)
