"""
ui/panels/header_selector.py

Widget de cabecera que permite seleccionar el nombre de la variable activa (desde un Excel)
y el tipo de fuente global que se aplicará a los nuevos items o a los seleccionados.
"""

import os
import pandas as pd
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QCompleter, QPushButton, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt


class HeaderSelector(QWidget):
    """
    Componente de la barra de estado para la configuración rápida de nombres y fuentes.
    """
    
    def __init__(self, parent=None):
        """
        Inicializa el selector y carga los datos iniciales (headers y fuentes).
        
        Args:
            parent (QWidget, optional): Widget padre.
        """
        super().__init__(parent)

        # Layout principal horizontal: [label+combo] | [variable activa]
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 4, 10, 4)
        main_layout.setSpacing(12)
        self.setLayout(main_layout)

        # --- Bloque izquierdo: etiqueta + combo ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(2)

        self.label = QLabel("HEADER ACTIVO:")
        self.label.setStyleSheet("font-weight: bold; font-size: 11px; color: #9AC7C8;")
        
        # Botón de Importación al lado del label
        header_top_layout = QHBoxLayout()
        header_top_layout.setContentsMargins(0, 0, 0, 0)
        header_top_layout.addWidget(self.label)
        
        self.btn_import = QPushButton("Importar Excel")
        self.btn_import.setFixedWidth(100)
        self.btn_import.setStyleSheet("""
            QPushButton {
                background-color: #24445B;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
                padding: 2px 5px;
            }
            QPushButton:hover {
                background-color: #FD9E2E;
                color: #1a2530;
            }
        """)
        self.btn_import.clicked.connect(self._on_import_clicked)
        header_top_layout.addWidget(self.btn_import)
        header_top_layout.addStretch()
        
        left_layout.addLayout(header_top_layout)

        self.combo = QComboBox()
        self.combo.setMinimumHeight(36)
        self.combo.setMinimumWidth(280)

        # Buscador integrado
        self.combo.setEditable(True)
        self.combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        completer = QCompleter(self.combo.model(), self)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.combo.setCompleter(completer)

        self.combo.setStyleSheet("""
            QComboBox {
                padding: 5px 8px;
                font-size: 14px;
                color: white;
                border: 1px solid #24445B;
                border-radius: 4px;
                background-color: #1a2530;
                padding-right: 26px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 26px;
                border-left: 1px solid #24445B;
                background-color: #24445B;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            QComboBox::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid #ffffff;
            }
            QComboBox QLineEdit {
                color: white;
                background-color: #1a2530;
                border: none;
                font-size: 14px;
            }
            QComboBox QAbstractItemView {
                background-color: #1a2530;
                color: #d0e0e8;
                selection-background-color: #24445B;
                selection-color: #FD9E2E;
                border: 1px solid #24445B;
                font-size: 13px;
                padding: 2px;
            }
            QComboBox QAbstractItemView::item {
                min-height: 26px;
                padding: 3px 6px;
            }
        """)

        left_layout.addWidget(self.combo)
        main_layout.addWidget(left_widget)

        # --- Separador vertical ---
        sep = QLabel("|")
        sep.setStyleSheet("color: #24445B; font-size: 20px; padding: 0 4px;")
        main_layout.addWidget(sep)

        # --- Bloque derecho: variable seleccionada ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(2)

        lbl_var_title = QLabel("Variable Seleccionada")
        lbl_var_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #9AC7C8; letter-spacing: 0.5px;")
        right_layout.addWidget(lbl_var_title)

        self.lbl_variable = QLabel("AUTO")
        self.lbl_variable.setStyleSheet("""
            font-size: 21px;
            font-weight: bold;
            color: #FD9E2E;
            padding: 4px 12px;
            background-color: #1a2530;
            border: 2px solid #FD9E2E;
            border-radius: 5px;
            min-width: 200px;
        """)
        right_layout.addWidget(self.lbl_variable)

        main_layout.addWidget(right_widget)

        # --- Bloque fuentes: selector de fuente ---
        font_widget = QWidget()
        font_layout = QVBoxLayout(font_widget)
        font_layout.setContentsMargins(0, 0, 0, 0)
        font_layout.setSpacing(2)

        lbl_font_title = QLabel("Tipo de Fuente")
        lbl_font_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #9AC7C8; letter-spacing: 0.5px;")
        font_layout.addWidget(lbl_font_title)

        self.combo_font = QComboBox()
        self.combo_font.setMinimumHeight(36)
        self.combo_font.setMinimumWidth(350)
        self.combo_font.setStyleSheet("""
            QComboBox {
                padding: 5px 8px;
                font-size: 14px;
                color: #FD9E2E;
                border: 1px solid #24445B;
                border-radius: 4px;
                background-color: #1a2530;
                font-weight: bold;
            }
            QComboBox QAbstractItemView {
                background-color: #1a2530;
                color: #d0e0e8;
                selection-background-color: #24445B;
                selection-color: #FD9E2E;
            }
        """)
        font_layout.addWidget(self.combo_font)
        main_layout.addWidget(font_widget)

        main_layout.addStretch()

        # Conectar cambio del combo para actualizar la etiqueta de variable
        self.combo.currentTextChanged.connect(self._update_variable_label)

        # Inicializar combo con solo AUTO
        self.combo.clear()
        self.combo.addItem("AUTO")
        self.load_fonts()

    def load_fonts(self):
        """Busca archivos TTF/OTF en la carpeta /fonts y los lista en el combo."""
        self.combo_font.clear()
        fonts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "fonts")
        font_files = []
        if os.path.exists(fonts_dir):
            for f in os.listdir(fonts_dir):
                if f.lower().endswith(('.ttf', '.otf')):
                    font_files.append(f)
        
        if not font_files:
            font_files = ["Arial"]
        
        self.combo_font.addItems(font_files)

    def get_current_font(self):
        """Devuelve el nombre del archivo de fuente seleccionado actualmente."""
        return self.combo_font.currentText()

    def _update_variable_label(self, text):
        """Actualiza el texto del indicador visual de variable activa."""
        self.lbl_variable.setText(text if text else "—")

    def _on_import_clicked(self):
        """Abre un diálogo para seleccionar el archivo Excel."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Excel de Datos", "", 
            "Archivos Excel (*.xlsx *.xls)"
        )
        if file_path:
            self.load_excel_headers(file_path)

    def load_excel_headers(self, excel_path=None):
        """Carga las cabeceras desde el archivo Excel de importación."""
        if not excel_path:
            return

        items = ["AUTO"]
        try:
            if os.path.exists(excel_path):
                # Usar pandas para leer solo las cabeceras
                df = pd.read_excel(excel_path, nrows=0)
                headers = [str(h).strip().lower().replace(" ", "_") for h in df.columns]
                
                if not headers:
                    QMessageBox.warning(self, "Excel Vacío", "El archivo seleccionado no tiene columnas.")
                    return

                items.extend(headers)
                self.combo.clear()
                self.combo.addItems(items)
                self.combo.completer().setModel(self.combo.model())
                
                # Feedback visual de éxito
                self.btn_import.setText("Excel Cargado ✔")
                self.btn_import.setStyleSheet(self.btn_import.styleSheet().replace("#24445B", "#2e7d32"))
            else:
                QMessageBox.critical(self, "Error", f"No se encontró el archivo:\n{excel_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error de Carga", f"No se pudo leer el Excel:\n{str(e)}")

        self._update_variable_label(self.combo.currentText())

    def get_current_name(self):
        """Devuelve el nombre seleccionado en el combo de headers."""
        return self.combo.currentText()
