"""
ui/items/label_item.py

Item visual de tipo etiqueta (círculo pequeño con texto).
Utiliza sync_text_layout para posicionar el texto relativo al punto.
"""

from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsItem
from PyQt6.QtGui import QPen, QBrush, QColor
from PyQt6.QtCore import Qt, QPointF
from core.utils import snap_to_5, sync_text_layout
from ui.items.text_item import TextItem

class LabelItem(QGraphicsEllipseItem):
    """
    Representa un punto de control con una etiqueta de texto asociada.
    
    Es útil para marcar coordenadas específicas en el layout con un nombre descriptivo.
    """
    
    def __init__(self, position, name, font_name="Arial"):
        """
        Inicializa la etiqueta.
        
        Args:
            position (QPointF): Posición inicial en la escena.
            name (str): Nombre identificador de la etiqueta.
            font_name (str): Nombre del archivo de fuente a utilizar.
        """
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
        self.setAcceptHoverEvents(True)

    def mouseDoubleClickEvent(self, event):
        """
        Activa el modo de edición del texto asociado al hacer doble clic.
        """
        self.text_item.start_editing()
        event.accept()

    def hoverEnterEvent(self, event):
        """Cambia el cursor al entrar al área del item."""
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Restaura el cursor al salir del área del item."""
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverLeaveEvent(event)

    def itemChange(self, change, value):
        """
        Gestiona cambios en el item, aplicando snapping a la rejilla de 5px.
        """
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
        """
        Devuelve el contenido textual de la etiqueta.
        
        Returns:
            str: Texto plano contenido en el TextItem.
        """
        return self.text_item.toPlainText()

    def update_text_layout(self):
        """
        Sincroniza la posición del texto según el bounding box del item.
        """
        sync_text_layout(self.rect(), self.text_item)

    def get_center(self):
        """
        Devuelve las coordenadas (x, y) de la etiqueta.
        
        Returns:
            tuple: (x, y) en coordenadas de la escena.
        """
        return self.pos().x(), self.pos().y()
