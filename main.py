import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QFontDatabase
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "Tw-Cen-MT-Bold.ttf")
    
    font_id = QFontDatabase.addApplicationFont(font_path)
    
    if font_id == -1:
        print("Aviso: No se encontró el archivo en fonts/Tw-Cen-MT-Bold.ttf")

    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()