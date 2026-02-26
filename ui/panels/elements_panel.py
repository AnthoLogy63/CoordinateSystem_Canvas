from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
                             QListWidgetItem, QInputDialog, QFileDialog, QWidget,
                             QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from ui.items.label_item import LabelItem
from ui.items.box_item import BoxItem

MAX_NAME_CHARS = 28 

class ElementsPanel(QFrame):
    def __init__(self, main_window, box_manager, label_manager):
        super().__init__()
        self.main_window = main_window
        self.box_manager = box_manager
        self.label_manager = label_manager
        self.setFixedWidth(300)

        self.setStyleSheet("""
            QFrame {
                background-color: #1e2a35;
                border-right: 1px solid #24445B;
            }
        """)

        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("ELEMENTOS")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 5px;
            color: #9AC7C8;
            letter-spacing: 1px;
        """)
        layout.addWidget(label)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #1a2530;
                border: 1px solid #24445B;
                border-radius: 4px;
                color: #d0e0e8;
            }
            QListWidget::item {
                border-bottom: 1px solid #24445B;
            }
            QListWidget::item:selected {
                background-color: #24445B;
                color: #FD9E2E;
            }
        """)
        layout.addWidget(self.list_widget)

        self.list_widget.itemDoubleClicked.connect(self.rename_box_or_label)
        self.list_widget.itemClicked.connect(self.on_item_clicked)

    def _truncate(self, text, max_chars=MAX_NAME_CHARS):
        return text if len(text) <= max_chars else text[:max_chars - 3] + "..."

    def _create_item_layout(self, element, text):
        item = QListWidgetItem(self.list_widget)
        item.setData(Qt.ItemDataRole.UserRole, element)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        row_layout = QHBoxLayout(container)
        row_layout.setContentsMargins(5, 6, 5, 6)
        row_layout.setSpacing(6)

        lines = text.split("\n")
        truncated_lines = [self._truncate(lines[0])] + lines[1:]
        truncated_text = "\n".join(truncated_lines)

        lbl = QLabel(truncated_text)
        lbl.setToolTip(text)  
        lbl.setStyleSheet("font-size: 13px; color: #d0e0e8; background: transparent; font-weight: 500;")
        row_layout.addWidget(lbl, 1) 

        if isinstance(element, (LabelItem, BoxItem)):
            btn_style = """
                QPushButton {
                    background-color: #24445B;
                    color: #9AC7C8;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #355f7d;
                }
            """
            current_sz = element.text_item.font().pointSize()
            size_label = QLabel(str(current_sz))
            size_label.setStyleSheet("color: #FD9E2E; font-weight: bold; min-width: 24px; font-size: 13px;")
            size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            def update_ui(delta, el=element, sl=size_label):
                new_size = el.text_item.update_font_size(delta)
                sl.setText(str(new_size))
                if isinstance(el, BoxItem):
                    el.update_text_layout()

            btn_min = QPushButton("-")
            btn_min.setFixedSize(24, 24)
            btn_min.setStyleSheet(btn_style)
            btn_min.clicked.connect(lambda: update_ui(-1))
            
            btn_max = QPushButton("+")
            btn_max.setFixedSize(24, 24)
            btn_max.setStyleSheet(btn_style)
            btn_max.clicked.connect(lambda: update_ui(1))

            row_layout.addWidget(btn_min)
            row_layout.addWidget(size_label) 
            row_layout.addWidget(btn_max)

        btn_del = QPushButton("🗑")
        btn_del.setFixedSize(28, 28)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setToolTip("Eliminar este elemento")
        btn_del.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #e05050;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #4a2020;
                border-radius: 4px;
            }
        """)
        btn_del.clicked.connect(lambda: self.delete_element(element))
        row_layout.addWidget(btn_del)

        item.setSizeHint(container.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, container)

    def add_box(self, box):
        rect = box.sceneBoundingRect()
        x1, y1 = round(rect.left()), round(rect.top())
        x2, y2 = round(rect.right()), round(rect.bottom())
        item_text = f"Box: {box.name}\n({x1}, {y1}) -> ({x2}, {y2})"
        self._create_item_layout(box, item_text)

    def add_label(self, label: LabelItem):
        x, y = label.get_center()
        item_text = f"Label: {label.name}\nPos: ({round(x)}, {round(y)})"
        self._create_item_layout(label, item_text)

    def delete_element(self, element):
        confirm = QMessageBox.question(
            self, "Confirmar borrado", 
            f"¿Estás seguro de eliminar '{element.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            if element.scene():
                element.scene().removeItem(element)
            
            if isinstance(element, LabelItem):
                self.label_manager.remove_label(element.name)
            else:
                self.box_manager.remove_box(element.name)
            
            self.update_list()

    def update_list(self):
        self.list_widget.clear()
        for box in self.box_manager.boxes.values():
            self.add_box(box)
        for label in self.label_manager.labels.values():
            self.add_label(label)

    def rename_box_or_label(self, item: QListWidgetItem):
        element = item.data(Qt.ItemDataRole.UserRole)
        old_name = element.name
        new_name, ok = QInputDialog.getText(
            self, f"Renombrar {type(element).__name__}", 
            "Nuevo nombre:", text=old_name
        )
        
        if ok and new_name.strip():
            new_name = new_name.strip()
            if isinstance(element, LabelItem):
                self.main_window.label_manager.rename_label(old_name, new_name)
            else:
                self.main_window.box_manager.rename_box(old_name, new_name)
            
            self.update_list()

    def on_item_clicked(self, item):
        element = item.data(Qt.ItemDataRole.UserRole)
        if element:
            self.main_window.view.highlight_item(element.name)

    def select_item_by_name(self, name):
        self.list_widget.blockSignals(True)
        self.list_widget.clearSelection()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            element = item.data(Qt.ItemDataRole.UserRole)
            widget = self.list_widget.itemWidget(item)
            if name and element and element.name == name:
                item.setSelected(True)
                self.list_widget.scrollToItem(item)
                if widget:
                    widget.setStyleSheet("background-color: #24445B; border-radius: 3px;")
            else:
                if widget:
                    widget.setStyleSheet("background: transparent;")
        self.list_widget.blockSignals(False)