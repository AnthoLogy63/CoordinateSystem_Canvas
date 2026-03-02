"""
core/alignment_manager.py

Gestiona las guías de alineación y el snapping (ajuste) magnético entre elementos.
"""

from PyQt6.QtWidgets import QGraphicsLineItem
from PyQt6.QtGui import QPen, QColor
from PyQt6.QtCore import Qt, QPointF
from ui.items.label_item import LabelItem
from ui.items.box_item import BoxItem

class AlignmentManager:
    """
    Controlador encargado de calcular y dibujar líneas de guía para alinear elementos.
    
    Permite que los objetos 'salten' a posiciones alineadas con otros objetos 
    cuando están dentro de un umbral de proximidad.
    """
    
    def __init__(self, scene, threshold=6):
        """
        Inicializa el gestor de alineación.
        
        Args:
            scene (QGraphicsScene): La escena donde se añadirán las guías.
            threshold (int): Distancia en píxeles para activar el snapping.
        """
        self.scene = scene
        self.threshold = threshold
        self.guide_items = []
        self._last_snapped_x = None
        self._last_snapped_y = None

    def clear_guides(self):
        """
        Elimina todas las líneas de guía actuales de la escena.
        """
        for item in self.guide_items:
            if item.scene():
                self.scene.removeItem(item)
        self.guide_items.clear()
        self._last_snapped_x = None
        self._last_snapped_y = None

    def get_alignment_points(self, items, active_item=None, target_type=None):
        """
        Recopila los puntos de alineación (bordes y centros) de todos los items visibles.
        
        Args:
            items (list): Lista de items en la escena.
            active_item (QGraphicsItem, optional): El item que se está moviendo (se ignora).
            target_type (type, optional): Filtro por tipo de objeto.
            
        Returns:
            tuple: (x_points, y_points) Listas ordenadas de coordenadas candidatas.
        """
        x_points = set()
        y_points = set()

        for item in items:
            if item == active_item or not item.isVisible():
                continue

            if isinstance(item, LabelItem):
                x, y = item.get_center()
                x_points.add(x)
                y_points.add(y)
            elif isinstance(item, BoxItem):
                rect = item.mapToScene(item.rect()).boundingRect()
                x_points.add(rect.left())
                x_points.add(rect.right())
                y_points.add(rect.top())
                y_points.add(rect.bottom())

        return sorted(list(x_points)), sorted(list(y_points))

    def update_guides(self, pos, items, active_item=None, target_type=None):
        """
        Calcula y dibuja las guías si la posición actual está cerca de un punto de alineación.
        
        Args:
            pos (QPointF): Posición actual del ratón o del objeto.
            items (list): Items candidatos para alinear.
            active_item (QGraphicsItem, optional): Item en movimiento.
            target_type (type, optional): Tipo de objeto con el que alinear.
            
        Returns:
            tuple: (snapped_x, snapped_y) Coordenadas ajustadas o None si no hay ajuste.
        """
        self.clear_guides()
        
        # Determine target_type for filtering
        if target_type is None and active_item is not None:
            target_type = type(active_item)
            
        x_points, y_points = self.get_alignment_points(items, active_item, target_type)
        
        snapped_x = None
        snapped_y = None

        # Find nearest X
        for px in x_points:
            if abs(pos.x() - px) <= self.threshold:
                snapped_x = px
                break

        # Find nearest Y
        for py in y_points:
            if abs(pos.y() - py) <= self.threshold:
                snapped_y = py
                break

        pen = QPen(QColor(0, 0, 0), 0.5, Qt.PenStyle.DashLine)
        
        scene_rect = self.scene.sceneRect()

        if snapped_x is not None:
            line = QGraphicsLineItem(snapped_x, scene_rect.top(), snapped_x, scene_rect.bottom())
            line.setPen(pen)
            line.setZValue(100)
            self.scene.addItem(line)
            self.guide_items.append(line)
            self._last_snapped_x = snapped_x

        if snapped_y is not None:
            line = QGraphicsLineItem(scene_rect.left(), snapped_y, scene_rect.right(), snapped_y)
            line.setPen(pen)
            line.setZValue(100)
            self.scene.addItem(line)
            self.guide_items.append(line)
            self._last_snapped_y = snapped_y

        return snapped_x, snapped_y

    def get_snapped_pos(self, pos):
        """
        Retorna una posición QPointF ajustada a las últimas coordenadas de ajuste detectadas.
        
        Args:
            pos (QPointF): Posición original.
            
        Returns:
            QPointF: Posición (pos.x o snapped_x, pos.y o snapped_y).
        """
        new_x = self._last_snapped_x if self._last_snapped_x is not None else pos.x()
        new_y = self._last_snapped_y if self._last_snapped_y is not None else pos.y()
        return QPointF(new_x, new_y)
