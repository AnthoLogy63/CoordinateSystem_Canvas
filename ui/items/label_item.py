from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsItem
from PyQt6.QtGui import QPen, QBrush, QColor
from PyQt6.QtCore import Qt, QPointF
from core.utils import snap_to_5
from ui.items.text_item import TextItem

class LabelItem(QGraphicsEllipseItem):
    def __init__(self, position, name, font_name="Arial"):
        size = 5
        super().__init__(-size/2, -size/2, size, size)
        self.name = name
        self.font_name = font_name
        self.setPos(position.x(), position.y())

        self.setBrush(QBrush(QColor(255, 0, 0, 150)))
        self.setPen(QPen(QColor(255, 0, 0), 0.5))

        self.text_item = TextItem(text_mode="short", parent=self)
        self.text_item.update_font_family(self.font_name)
        self.text_item.set_simple()
        self.text_item.setPos(0, 0)

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            snapped_x = snap_to_5(value.x())
            snapped_y = snap_to_5(value.y())
            return QPointF(snapped_x, snapped_y)

        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if self.scene() and self.scene().views():
                view = self.scene().views()[0]
                if hasattr(view, "main_window") and view.main_window:
                    view.main_window.elements_panel.update_list()
                    
        return super().itemChange(change, value)

    def get_text(self):
        """Devuelve el texto actual del item"""
        return self.text_item.toPlainText()

    def update_text_layout(self):
        """Alias para mantener compatibilidad con la señal de TextItem"""
        pass

    def get_center(self):
        return self.pos().x(), self.pos().y()