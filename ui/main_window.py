from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QGraphicsPixmapItem, QLabel, QGraphicsTextItem, QMessageBox
from PyQt6.QtGui import QPixmap, QFont, QColor, QPen, QBrush
from PyQt6.QtCore import QRectF, QPointF
from ui.graphics_view import GraphicsView
from core.box_manager import BoxManager
from core.label_manager import LabelManager
from core.modes import Mode
from core.exporter import export_layout
from ui.panels.elements_panel import ElementsPanel
from ui.panels.tools_panel import ToolsPanel
from ui.panels.header_selector import HeaderSelector
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Layout Builder")
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #151f28;
            }
            QStatusBar {
                background-color: #1a2530;
                border-top: 1px solid #24445B;
                min-height: 60px;
            }
            QStatusBar QLabel {
                color: white;
            }
        """)

        self.box_manager = BoxManager()
        self.label_manager = LabelManager()
        self.current_mode = Mode.SELECT
        self.background_path = None  # Ruta de la plantilla activa

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        self.tools_panel = ToolsPanel(self)
        main_layout.addWidget(self.tools_panel)

        self.canvas_container = QWidget()
        canvas_layout = QVBoxLayout()
        self.canvas_container.setLayout(canvas_layout)
        main_layout.addWidget(self.canvas_container, 1)

        self.elements_panel = ElementsPanel(self, self.box_manager, self.label_manager)
        main_layout.addWidget(self.elements_panel)

        self.view = GraphicsView(
            box_manager=self.box_manager,
            label_manager=self.label_manager,
            list_widget=self.elements_panel.list_widget,
            main_window=self
        )
        self.view.set_mode(self.current_mode)
        canvas_layout.addWidget(self.view)

        # BARRA DE ESTADO
        self.coord_label = QLabel("X: 0, Y: 0")
        self.coord_label.setFont(QFont("Segoe UI", 12))
        self.coord_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 150);
                padding: 4px 15px;
                border-radius: 4px;
                margin-left: 5px;
            }
        """)
        self.statusBar().addWidget(self.coord_label)

        # Agregamos el selector directamente a la barra de estado
        self.header_selector = HeaderSelector()
        self.statusBar().addWidget(self.header_selector)

        # Conectar cambio de fuente para actualizar items seleccionados
        self.header_selector.combo_font.currentTextChanged.connect(self._on_font_changed)

        # Siempre arrancar con el placeholder; el usuario carga la plantilla manualmente
        self._show_placeholder()

    def _on_font_changed(self, font_name):
        """Actualiza la fuente de los elementos seleccionados en el canvas"""
        selected_items = self.view.scene().selectedItems()
        for item in selected_items:
            if hasattr(item, "text_item"):
                item.font_name = font_name
                item.text_item.update_font_family(font_name)
        
        # Opcional: actualizar la lista si los nombres cambian (no es el caso aquí)
        # self.elements_panel.update_list()

    def _show_placeholder(self):
        """Muestra un mensaje en el canvas cuando no hay plantilla cargada"""
        scene = self.view.scene()
        scene.setSceneRect(0, 0, 1200, 700)

        # Fondo oscuro
        bg = scene.addRect(
            0, 0, 1200, 700,
            QPen(QColor("#1a2530")),
            QBrush(QColor("#1a2530"))
        )
        bg.setZValue(-2)
        self._placeholder_items = [bg]

        # Texto principal
        title = QGraphicsTextItem()
        title.setDefaultTextColor(QColor("#9AC7C8"))
        f1 = QFont("Segoe UI", 20)
        f1.setBold(True)
        title.setFont(f1)
        title.setPlainText("🖼️  Carga una plantilla de fondo")
        title.setTextWidth(800)
        title.setZValue(-1)
        title.setPos(200, 290)
        scene.addItem(title)
        self._placeholder_items.append(title)

        # Subtexto
        sub = QGraphicsTextItem()
        sub.setDefaultTextColor(QColor("#4a6880"))
        sub.setFont(QFont("Segoe UI", 13))
        sub.setPlainText("Usa el botón \"Importar Plantilla de Fondo\" en el panel izquierdo para empezar.")
        sub.setTextWidth(800)
        sub.setZValue(-1)
        sub.setPos(200, 345)
        scene.addItem(sub)
        self._placeholder_items.append(sub)

    def load_background(self, path):
        """Carga la imagen de fondo y guarda su ruta para el exportador"""
        # Quitar el placeholder si existe
        if hasattr(self, '_placeholder_items'):
            for item in self._placeholder_items:
                if item.scene():
                    self.view.scene().removeItem(item)
            del self._placeholder_items
        self.background_path = path
        self.load_image(path)
        # Mostrar el nombre de la plantilla en el título de la ventana
        basename = os.path.basename(path)
        self.setWindowTitle(f"Layout Builder  |  {basename}")

    def load_image(self, path):
        pixmap = QPixmap(path)
        if hasattr(self, "background_item") and getattr(self, "background_item"):
            self.background_item.setPixmap(pixmap)
        else:
            self.background_item = QGraphicsPixmapItem(pixmap)
            self.background_item.setZValue(-1)
            self.view.scene().addItem(self.background_item)

        rect = pixmap.rect()
        self.view.scene().setSceneRect(QRectF(rect))

    def change_mode(self, mode):
        self.current_mode = mode
        self.view.set_mode(mode)
        self.tools_panel.change_mode(mode)

    def export_elements(self, export_dir=None):
        py_path, txt_path = export_layout(self.box_manager, self.label_manager, self.background_path, export_dir)
        print(f"Configuración exportada en: {py_path}")
        return py_path, txt_path

    def create_box(self, x, y, w, h, name=None, font_name="Arial"):
        from ui.items.box_item import BoxItem
        rect = QRectF(x, y, w, h)
        box_item = BoxItem(rect, name, font_name=font_name)
        self.view.scene().addItem(box_item)
        return box_item

    def create_label(self, x, y, name=None, font_name="Arial"):
        from ui.items.label_item import LabelItem
        label_item = LabelItem(QPointF(x, y), name, font_name=font_name)
        self.view.scene().addItem(label_item)
        return label_item

    def add_box_to_list(self, box):
        self.elements_panel.add_box(box)

    def add_label_to_list(self, label):
        self.elements_panel.add_label(label)

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Confirmar Salida", "¿Seguro que deseas salir?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()