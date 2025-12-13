import sys
from PyQt6.QtWidgets import QApplication
from src.pet_entity import PetEntity

def main():
    app = QApplication(sys.argv)
    
    # Ensure clean exit
    app.setQuitOnLastWindowClosed(False)
    
    pet = PetEntity()
    pet.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    import os
    import traceback
    
    # Debug log path: user documents or next to exe
    log_file = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "debug.log")
    
    try:
        main()
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"CRITICAL ERROR: {str(e)}\n")
            f.write(traceback.format_exc())
            f.write("\n")
        sys.exit(1)
