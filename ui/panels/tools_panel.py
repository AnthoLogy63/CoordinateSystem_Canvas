from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QGraphicsPixmapItem
from PyQt6.QtCore import Qt, QRectF
from core.modes import Mode
import importlib.util

NORMAL_BTN_STYLE = """
    QPushButton {
        font-size: 13px;
        padding: 8px 10px;
        border-radius: 6px;
        background-color: #1e2a35;
        color: #d0e0e8;
        border: 1px solid #24445B;
        text-align: left;
    }
    QPushButton:hover {
        background-color: #24445B;
        color: #9AC7C8;
        border: 1px solid #9AC7C8;
    }
    QPushButton:pressed {
        background-color: #1a3348;
    }
"""

ACTIVE_BTN_STYLE = """
    QPushButton {
        font-size: 13px;
        font-weight: bold;
        padding: 8px 10px;
        border-radius: 6px;
        background-color: #24445B;
        color: #FD9E2E;
        border: 1px solid #FD9E2E;
        text-align: left;
    }
    QPushButton:hover {
        background-color: #2e5370;
        border: 1px solid #FD9E2E;
    }
"""

ACTION_BTN_STYLE = """
    QPushButton {
        font-size: 13px;
        padding: 8px 10px;
        border-radius: 6px;
        background-color: #162030;
        color: #9AC7C8;
        border: 1px solid #24445B;
        text-align: left;
    }
    QPushButton:hover {
        background-color: #1e3348;
        color: #FD9E2E;
        border: 1px solid #9AC7C8;
    }
    QPushButton:pressed {
        background-color: #0f1820;
    }
"""

class ToolsPanel(QFrame):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setFixedWidth(220)

        self.setStyleSheet("""
            QFrame {
                background-color: #1e2a35;
                border-right: 1px solid #24445B;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(10, 20, 10, 20)
        self.setLayout(layout)

        label = QLabel("HERRAMIENTAS")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            letter-spacing: 2px;
            color: #9AC7C8;
            padding-bottom: 8px;
            border-bottom: 1px solid #24445B;
        """)
        layout.addWidget(label)

        layout.addSpacing(6)

        # --- Sección: Plantilla de Fondo ---
        lbl_bg = QLabel("PLANTILLA")
        lbl_bg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_bg.setStyleSheet("""
            font-size: 10px;
            font-weight: bold;
            color: #9AC7C8;
            letter-spacing: 1px;
        """)
        layout.addWidget(lbl_bg)

        self.btn_plantilla = QPushButton("🖼️  Importar Plantilla de Fondo")
        self.btn_plantilla.setMinimumHeight(42)
        self.btn_plantilla.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_plantilla.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                padding: 8px 10px;
                border-radius: 6px;
                background-color: #1a2e3a;
                color: #9AC7C8;
                border: 1px solid #9AC7C8;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1e3d50;
                color: #FD9E2E;
                border: 1px solid #FD9E2E;
            }
            QPushButton:pressed {
                background-color: #152430;
            }
        """)
        layout.addWidget(self.btn_plantilla)

        layout.addSpacing(6)

        sep0 = QLabel("───────────────")
        sep0.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sep0.setStyleSheet("color: #24445B; font-size: 10px;")
        layout.addWidget(sep0)

        layout.addSpacing(4)

        # --- Sección: Herramientas de modo ---
        lbl_tools = QLabel("MODO")
        lbl_tools.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_tools.setStyleSheet("""
            font-size: 10px;
            font-weight: bold;
            color: #9AC7C8;
            letter-spacing: 1px;
        """)
        layout.addWidget(lbl_tools)

        layout.addSpacing(4)

        self.btn_moverse = QPushButton("🖱  Moverse en la Plantilla")
        self.btn_crear_box = QPushButton("⬛   Crear Box")
        self.btn_crear_label = QPushButton("⚪   Crear Label")
        self.btn_transformar = QPushButton("📐   Transformar Objeto")
        self.btn_exportar = QPushButton("📤   Exportar Coordenadas")
        self.btn_importar = QPushButton("📥   Importar Coordenadas")

        mode_buttons = [
            self.btn_moverse, self.btn_crear_box, self.btn_crear_label,
            self.btn_transformar,
        ]
        action_buttons = [self.btn_exportar, self.btn_importar]

        for btn in mode_buttons:
            btn.setMinimumHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(NORMAL_BTN_STYLE)
            layout.addWidget(btn)

        layout.addSpacing(10)

        sep = QLabel("───────────────")
        sep.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sep.setStyleSheet("color: #24445B; font-size: 10px;")
        layout.addWidget(sep)

        layout.addSpacing(4)

        for btn in action_buttons:
            btn.setMinimumHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(ACTION_BTN_STYLE)
            layout.addWidget(btn)

        layout.addStretch()

        # Conexiones
        self.btn_plantilla.clicked.connect(self.import_background_action)
        self.btn_moverse.clicked.connect(lambda: self.change_mode(Mode.SELECT))
        self.btn_crear_box.clicked.connect(lambda: self.change_mode(Mode.CREATE))
        self.btn_crear_label.clicked.connect(lambda: self.change_mode(Mode.CREATE_LABEL))
        self.btn_transformar.clicked.connect(lambda: self.change_mode(Mode.TRANSFORM))
        self.btn_exportar.clicked.connect(self.export_action)
        self.btn_importar.clicked.connect(self.import_action)

        self.set_default_mode()

    def set_default_mode(self):
        self.change_mode(Mode.SELECT)

    def change_mode(self, mode):
        self.main_window.current_mode = mode
        if hasattr(self.main_window, "view"):
            self.main_window.view.set_mode(mode)

        btn_map = {
            Mode.SELECT: self.btn_moverse,
            Mode.CREATE: self.btn_crear_box,
            Mode.CREATE_LABEL: self.btn_crear_label,
            Mode.TRANSFORM: self.btn_transformar,
        }

        for m, btn in btn_map.items():
            btn.setStyleSheet(ACTIVE_BTN_STYLE if m == mode else NORMAL_BTN_STYLE)

    def import_background_action(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Plantilla de Fondo", "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)"
        )
        if not file_path:
            return
        self.main_window.load_background(file_path)
        QMessageBox.information(
            self, "Plantilla cargada",
            f"Plantilla cargada:\n{file_path}\n\nEl archivo exportado usará este nombre como base."
        )

    def export_action(self):
        export_dir = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta para exportar", ""
        )
        if not export_dir:
            return  # El usuario canceló
        py_path, txt_path = self.main_window.export_elements(export_dir)
        QMessageBox.information(
            self, "Exportar",
            f"Archivos guardados en:\n{export_dir}\n\n"
            f"📄 {py_path.split(chr(92))[-1]}\n"
            f"📄 {txt_path.split(chr(92))[-1]}"
        )

    def import_action(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importar Layout (.py)", "", "Python Files (*.py)"
        )
        if not file_path:
            return

        try:
            spec = importlib.util.spec_from_file_location("imported_layout", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if not hasattr(module, "LAYOUT_CONFIG"):
                raise Exception("El archivo no contiene LAYOUT_CONFIG")
            
            config = module.LAYOUT_CONFIG
            boxes_data = config.get('boxes', {})
            labels_data = config.get('labels', {})

            for item in list(self.main_window.view.scene().items()):
                if not isinstance(item, QGraphicsPixmapItem):
                    self.main_window.view.scene().removeItem(item)

            self.main_window.box_manager.clear()
            self.main_window.label_manager.clear()

            for name, c in boxes_data.items():
                box = self.main_window.create_box(c['x1'], c['y1'], c['x2']-c['x1'], c['y2']-c['y1'], name)
                self.main_window.box_manager.add_box(box, name)

            for name, c in labels_data.items():
                label = self.main_window.create_label(c['x'], c['y'], name)
                self.main_window.label_manager.add_label(label, name)

            self.main_window.elements_panel.update_list()
            QMessageBox.information(self, "Éxito", "Layout cargado correctamente.")

        except Exception as e:
            QMessageBox.critical(self, "Error de Importación", f"No se pudo cargar el archivo:\n{str(e)}")