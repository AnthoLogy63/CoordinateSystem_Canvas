"""
main.py

Punto de entrada principal del sistema.

Este módulo se encarga de:
- Inicializar la aplicación Qt.
- Crear la ventana principal.
- Ejecutar el ciclo de eventos de la interfaz gráfica.
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main() -> None:
    """
    Ejecuta la aplicación.

    Crea la instancia de QApplication, inicializa la ventana
    principal del sistema y lanza el ciclo principal de ejecución.

    Raises:
        SystemExit: Se produce al cerrar la aplicación.
    """
    app = QApplication(sys.argv)

    # Crear y mostrar la ventana principal
    window = MainWindow()
    window.showMaximized()

    # Iniciar el ciclo de eventos
    sys.exit(app.exec())


if __name__ == "__main__":
    main()