import os
import pandas as pd
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QCompleter
from PyQt6.QtCore import Qt


class HeaderSelector(QWidget):
    def __init__(self, parent=None):
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
        left_layout.addWidget(self.label)

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

        self.load_excel_headers()
        self.load_fonts()

    def load_fonts(self):
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
        return self.combo_font.currentText()

    def _update_variable_label(self, text):
        self.lbl_variable.setText(text if text else "—")

    def load_excel_headers(self):
        self.combo.clear()
        items = ["AUTO"]

        try:
            excel_path = os.path.join(os.path.dirname(__file__), "..", "..", "import", "plantilla.xlsx")
            if os.path.exists(excel_path):
                df = pd.read_excel(excel_path, nrows=0)
                headers = [str(h).strip().lower().replace(" ", "_") for h in df.columns]
                items.extend(headers)

                self.combo.addItems(items)
                self.combo.completer().setModel(self.combo.model())
            else:
                print(f"No se encontró el archivo: {excel_path}")
        except Exception as e:
            print(f"Error cargando headers: {e}")

        self._update_variable_label(self.combo.currentText())

    def get_current_name(self):
        return self.combo.currentText()