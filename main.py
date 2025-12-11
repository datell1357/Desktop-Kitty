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
    main()
