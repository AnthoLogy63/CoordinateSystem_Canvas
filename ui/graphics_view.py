"""
ui/graphics_view.py

Vista principal del lienzo (Canvas) basada en QGraphicsView.
Maneja la interacción del ratón para crear, seleccionar y transformar items,
así como el scroll automático (auto-panning) y el zoom.
"""

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QMessageBox
from PyQt6.QtGui import QWheelEvent, QMouseEvent, QPen, QColor
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer
from ui.items.box_item import BoxItem
from core.modes import Mode
from ui.items.label_item import LabelItem
from core.alignment_manager import AlignmentManager
from core.utils import snap_to_5

class GraphicsView(QGraphicsView):
    """
    Componente que visualiza y gestiona la interacción con la escena de dibujo.
    
    Proporciona herramientas para:
    - Zoom con la rueda del ratón.
    - Paneo manual (arrastrar con el mouse en modo SELECT).
    - Creación de cajas y etiquetas.
    - Alineación automática mediante AlignmentManager.
    - Auto-panning cuando se arrastra cerca de los bordes.
    """
    
    def __init__(self, box_manager, label_manager, list_widget, main_window=None, parent=None):
        """
        Inicializa la vista y sus gestores.
        
        Args:
            box_manager (BoxManager): Referencia al gestor de cajas.
            label_manager (LabelManager): Referencia al gestor de etiquetas.
            list_widget (QListWidget): Widget de la lista de elementos (histórico).
            main_window (MainWindow, optional): Referencia a la ventana principal.
            parent (QWidget, optional): Widget padre.
        """
        super().__init__(parent)
        self.setScene(QGraphicsScene())
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setMouseTracking(True)
        self._zoom = 0

        self.box_manager = box_manager
        self.label_manager = label_manager
        self.list_widget = list_widget
        self.main_window = main_window

        self.drawing = False
        self.start_pos = None
        self.temp_rect = None
        self.mode = Mode.SELECT
        self.alignment_manager = AlignmentManager(self.scene())

        # Auto-panning
        self.pan_timer = QTimer()
        self.pan_timer.timeout.connect(self._do_auto_pan)
        self.pan_delta = QPointF(0, 0)
        self.pan_margin = 30
        self.pan_speed = 10
        self.last_mouse_pos = None

        # Paneo manual en modo SELECT
        self._panning = False
        self._pan_start_pos = None

    def set_mode(self, mode):
        """
        Cambia el modo de operación actual y actualiza el cursor y estado de los items.
        
        Args:
            mode (Mode): Nuevo modo (Select, Transform, Create, etc.).
        """
        self.drawing = False
        self.temp_rect = None
        self.mode = mode
        self.setDragMode(QGraphicsView.DragMode.NoDrag)

        for item in self.scene().items():
            if isinstance(item, BoxItem):
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
            elif isinstance(item, LabelItem):
                item.setFlag(
                    QGraphicsItem.GraphicsItemFlag.ItemIsMovable,
                    mode in (Mode.SELECT, Mode.TRANSFORM)
                )

        if mode in (Mode.SELECT, Mode.TRANSFORM):
            self.viewport().setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.viewport().setCursor(Qt.CursorShape.CrossCursor)

    def wheelEvent(self, event: QWheelEvent):
        """
        Gestiona el zoom mediante la rueda del ratón, limitando el rango.
        """
        delta = 1 if event.angleDelta().y() > 0 else -1
        new_zoom = self._zoom + delta
        if -8 <= new_zoom <= 20:
            self._zoom = new_zoom
            factor = 1.25 if delta > 0 else 1 / 1.25
            self.scale(factor, factor)

    def _item_at(self, viewport_pos):
        """
        Busca un item del sistema (Box o Label) en una posición del viewport.
        
        Args:
            viewport_pos (QPoint): Posición del ratón en píxeles de pantalla.
        """
        item = self.itemAt(viewport_pos)
        while item and not hasattr(item, 'name') and item.parentItem():
            item = item.parentItem()
        if item and hasattr(item, 'name') and isinstance(item, (BoxItem, LabelItem)):
            return item
        return None

    def mousePressEvent(self, event: QMouseEvent):
        """
        Inicia acciones de creación o selección basándose en el modo actual.
        """
        pos = self.mapToScene(event.position().toPoint())
        item = self._item_at(event.position().toPoint())

        if item:
            self.highlight_item(item.name)
            if self.main_window:
                self.main_window.elements_panel.select_item_by_name(item.name)
        else:
            self.highlight_item(None)
            if self.main_window:
                self.main_window.elements_panel.select_item_by_name(None)

        if event.button() == Qt.MouseButton.LeftButton:

            if self.mode in [Mode.CREATE, Mode.CREATE_LABEL]:
                t_type = BoxItem if self.mode == Mode.CREATE else LabelItem
                self.alignment_manager.update_guides(pos, self.scene().items(), target_type=t_type)
                snapped_pos = self.alignment_manager.get_snapped_pos(pos)
                grid_snapped_pos = QPointF(snap_to_5(snapped_pos.x()), snap_to_5(snapped_pos.y()))

                if self.mode == Mode.CREATE:
                    self.start_pos = grid_snapped_pos
                    self.drawing = True
                    self.temp_rect = self.scene().addRect(
                        QRectF(self.start_pos, self.start_pos),
                        pen=QPen(QColor(33, 150, 243), 1)
                    )
                    return

                elif self.mode == Mode.CREATE_LABEL:
                    sel_name = self.main_window.header_selector.get_current_name()
                    nombre_final = None if sel_name == "AUTO" else sel_name

                    if nombre_final is not None:
                        if nombre_final in self.main_window.box_manager.boxes or \
                           nombre_final in self.main_window.label_manager.labels:
                            resp = QMessageBox.question(
                                self.main_window, "Nombre duplicado",
                                f"Ya existe un objeto con el nombre '{nombre_final}'.\n¿Deseas continuar?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                            )
                            if resp == QMessageBox.StandardButton.No:
                                return

                    sel_font = self.main_window.header_selector.get_current_font()
                    label_item = LabelItem(grid_snapped_pos, "", font_name=sel_font)
                    actual_name = self.main_window.label_manager.add_label(label_item, name=nombre_final)
                    label_item.name = actual_name
                    self.scene().addItem(label_item)
                    if self.main_window:
                        self.main_window.elements_panel.update_list()
                    self.alignment_manager.clear_guides()
                    return

            if self.mode in (Mode.SELECT, Mode.TRANSFORM):
                if item:
                    self.setDragMode(QGraphicsView.DragMode.NoDrag)
                    super().mousePressEvent(event)
                    return
                else:
                    self._panning = True
                    self._pan_start_pos = event.position()
                    self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
                    event.accept()
                    return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Gestiona el feedback visual durante el arrastre (guías, creación de rectángulos).
        """
        pos = self.mapToScene(event.position().toPoint())

        if self.main_window and hasattr(self.main_window, "coord_label"):
            self.main_window.coord_label.setText(f"X: {int(pos.x())}, Y: {int(pos.y())}")

        if self._panning and self.mode in (Mode.SELECT, Mode.TRANSFORM):
            delta = event.position() - self._pan_start_pos
            self._pan_start_pos = event.position()
            self.horizontalScrollBar().setValue(
                int(self.horizontalScrollBar().value() - delta.x())
            )
            self.verticalScrollBar().setValue(
                int(self.verticalScrollBar().value() - delta.y())
            )
            event.accept()
            return

        self._update_during_movement(pos)
        super().mouseMoveEvent(event)
        self._handle_auto_pan(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Finaliza la creación de items o el paneo de cámara.
        """
        pos = self.mapToScene(event.position().toPoint())

        if self._panning:
            self._panning = False
            self.viewport().setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
            super().mouseReleaseEvent(event)
            self.alignment_manager.clear_guides()
            self.pan_timer.stop()
            self.last_mouse_pos = None
            return

        if self.drawing and event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            if self.temp_rect:
                self.scene().removeItem(self.temp_rect)

            sel_name = self.main_window.header_selector.get_current_name()
            nombre_final = None if sel_name == "AUTO" else sel_name

            self.alignment_manager.update_guides(pos, self.scene().items(), target_type=BoxItem)
            snapped_pos = self.alignment_manager.get_snapped_pos(pos)

            final_start = QPointF(snap_to_5(self.start_pos.x()), snap_to_5(self.start_pos.y()))
            final_end   = QPointF(snap_to_5(snapped_pos.x()),    snap_to_5(snapped_pos.y()))

            sel_font = self.main_window.header_selector.get_current_font()
            rect = QRectF(final_start, final_end).normalized()
            box_item = BoxItem(rect, "", font_name=sel_font)
            actual_name = self.box_manager.add_box(box_item, name=nombre_final)
            box_item.name = actual_name
            self.scene().addItem(box_item)

            if self.main_window:
                self.main_window.elements_panel.update_list()
            self.temp_rect = None

        super().mouseReleaseEvent(event)
        self.alignment_manager.clear_guides()
        self.pan_timer.stop()
        self.last_mouse_pos = None

    def _handle_auto_pan(self, event):
        """
        Detecta si el mouse está en los márgenes para activar el auto-panning.
        Solo funciona si se está dibujando (creando item) o si se está arrastrando un elemento seleccionado.
        """
        is_moving_item = (len(self.scene().selectedItems()) > 0 and 
                          event.buttons() & Qt.MouseButton.LeftButton)
        
        if not self.drawing and not is_moving_item:
            self.pan_timer.stop()
            return

        pos = event.position()
        delta_x = 0
        delta_y = 0

        if pos.x() < self.pan_margin:
            delta_x = -self.pan_speed
        elif pos.x() > self.width() - self.pan_margin:
            delta_x = self.pan_speed

        if pos.y() < self.pan_margin:
            delta_y = -self.pan_speed
        elif pos.y() > self.height() - self.pan_margin:
            delta_y = self.pan_speed

        if delta_x != 0 or delta_y != 0:
            self.pan_delta = QPointF(delta_x, delta_y)
            self.last_mouse_pos = event.position()
            if not self.pan_timer.isActive():
                self.pan_timer.start(20)
        else:
            self.pan_timer.stop()

    def _do_auto_pan(self):
        """
        Ejecuta el desplazamiento de la vista y actualiza guías si es necesario.
        """
        h_bar = self.horizontalScrollBar()
        v_bar = self.verticalScrollBar()
        h_bar.setValue(int(h_bar.value() + self.pan_delta.x()))
        v_bar.setValue(int(v_bar.value() + self.pan_delta.y()))
        if self.last_mouse_pos:
            scene_pos = self.mapToScene(self.last_mouse_pos.toPoint())
            self._update_during_movement(scene_pos)

    def _update_during_movement(self, pos):
        """
        Lógica interna para actualizar guías y rectángulos temporales según el movimiento.
        """
        if self.mode == Mode.CREATE:
            self.alignment_manager.update_guides(pos, self.scene().items(), target_type=BoxItem)
            if self.drawing and self.temp_rect:
                snapped_pos = self.alignment_manager.get_snapped_pos(pos)
                grid_start = QPointF(snap_to_5(self.start_pos.x()), snap_to_5(self.start_pos.y()))
                grid_end = QPointF(snap_to_5(snapped_pos.x()), snap_to_5(snapped_pos.y()))
                self.temp_rect.setRect(QRectF(grid_start, grid_end).normalized())

        elif self.mode == Mode.CREATE_LABEL:
            self.alignment_manager.update_guides(pos, self.scene().items(), target_type=LabelItem)

        elif self.mode in (Mode.TRANSFORM, Mode.SELECT):
            moving_items = self.scene().selectedItems()
            if moving_items:
                self.alignment_manager.update_guides(
                    pos, self.scene().items(), moving_items[0],
                    target_type=type(moving_items[0])
                )

    def highlight_item(self, name):
        """
        Aplica colores de estado a todos los items para resaltar la selección.
        
        Args:
            name (str): Nombre del item a seleccionar (None para deseleccionar todo).
        """
        COLOR_BORDE_SEL_LABEL   = QColor(0, 0, 0)
        COLOR_BORDE_LABEL       = QColor(255, 0, 0)

        for item in self.scene().items():
            if isinstance(item, BoxItem):
                if item.name == name:
                    # Solo cambiar a 'selected' si no está en edición
                    if item._vis_state != "editing":
                        item.set_state("selected")
                    item.setZValue(8)
                else:
                    # Respetar el estado 'editing' si está activo
                    if item._vis_state not in ("editing",):
                        item.set_state("default")
                    item.setZValue(1)

            elif isinstance(item, LabelItem):
                if item.name == name:
                    item.setPen(QPen(COLOR_BORDE_SEL_LABEL, 1.2))
                    item.setZValue(10)
                else:
                    item.setPen(QPen(COLOR_BORDE_LABEL, 0.5))
                    item.setZValue(1)
