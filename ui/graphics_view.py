from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QMessageBox
from PyQt6.QtGui import QWheelEvent, QMouseEvent, QPen, QColor
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer
from ui.items.box_item import BoxItem
from core.modes import Mode
from ui.items.label_item import LabelItem
from core.alignment_manager import AlignmentManager
from core.utils import snap_to_5

class GraphicsView(QGraphicsView):
    def __init__(self, box_manager, label_manager, list_widget, main_window=None, parent=None):
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

        # Auto-panning setup
        self.pan_timer = QTimer()
        self.pan_timer.timeout.connect(self._do_auto_pan)
        self.pan_delta = QPointF(0, 0)
        self.pan_margin = 30
        self.pan_speed = 10
        self.last_mouse_pos = None

    def set_mode(self, mode):
        self.drawing = False
        self.temp_rect = None
        self.mode = mode
        self.setDragMode(QGraphicsView.DragMode.NoDrag)

        for item in self.scene().items():
            if isinstance(item, (BoxItem, LabelItem)):
                # En SELECT o TRANSFORM, permitimos interacción
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, mode == Mode.TRANSFORM)

        if mode == Mode.SELECT:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def wheelEvent(self, event: QWheelEvent):
        delta = 1 if event.angleDelta().y() > 0 else -1
        new_zoom = self._zoom + delta
        if -8 <= new_zoom <= 20:
            self._zoom = new_zoom
            factor = 1.25 if delta > 0 else 1 / 1.25
            self.scale(factor, factor)

    def mousePressEvent(self, event: QMouseEvent):
        pos = self.mapToScene(event.position().toPoint())
        item = self.itemAt(event.position().toPoint())

        while item and not hasattr(item, 'name') and item.parentItem():
            item = item.parentItem()

        if item and hasattr(item, 'name'):
            self.highlight_item(item.name)
            if self.main_window:
                self.main_window.elements_panel.select_item_by_name(item.name)
        else:
            self.highlight_item(None)
            if self.main_window:
                self.main_window.elements_panel.select_item_by_name(None)

        if event.button() == Qt.MouseButton.LeftButton:
            if self.mode == Mode.SELECT:
                super().mousePressEvent(event)
                return

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

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        pos = self.mapToScene(event.position().toPoint())
        
        if self.drawing and event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            if self.temp_rect:
                self.scene().removeItem(self.temp_rect)

            sel_name = self.main_window.header_selector.get_current_name()
            nombre_final = None if sel_name == "AUTO" else sel_name

            self.alignment_manager.update_guides(pos, self.scene().items(), target_type=BoxItem)
            snapped_pos = self.alignment_manager.get_snapped_pos(pos)
            
            final_start = QPointF(snap_to_5(self.start_pos.x()), snap_to_5(self.start_pos.y()))
            final_end = QPointF(snap_to_5(snapped_pos.x()), snap_to_5(snapped_pos.y()))
            
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

        super().mouseMoveEvent(event)
        self._handle_auto_pan(event)

    def _handle_auto_pan(self, event):
        if not self.drawing and self.mode not in [Mode.TRANSFORM]:
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
                self.pan_timer.start(20) # 50 FPS apprx
        else:
            self.pan_timer.stop()

    def _do_auto_pan(self):
        h_bar = self.horizontalScrollBar()
        v_bar = self.verticalScrollBar()
        
        h_bar.setValue(int(h_bar.value() + self.pan_delta.x()))
        v_bar.setValue(int(v_bar.value() + self.pan_delta.y()))

        # Simulamos un mouseMove para actualizar lo que se este dibujando/moviendo
        if self.last_mouse_pos:
            scene_pos = self.mapToScene(self.last_mouse_pos.toPoint())
            self._update_during_movement(scene_pos)

    def _update_during_movement(self, pos):
        # Actualizar guias y rectangulos temporales
        if self.mode == Mode.CREATE:
            self.alignment_manager.update_guides(pos, self.scene().items(), target_type=BoxItem)
            if self.drawing and self.temp_rect:
                snapped_pos = self.alignment_manager.get_snapped_pos(pos)
                grid_start = QPointF(snap_to_5(self.start_pos.x()), snap_to_5(self.start_pos.y()))
                grid_end = QPointF(snap_to_5(snapped_pos.x()), snap_to_5(snapped_pos.y()))
                self.temp_rect.setRect(QRectF(grid_start, grid_end).normalized())
        
        elif self.mode == Mode.CREATE_LABEL:
            self.alignment_manager.update_guides(pos, self.scene().items(), target_type=LabelItem)
        
        elif self.mode == Mode.TRANSFORM:
            moving_items = self.scene().selectedItems()
            if moving_items:
                self.alignment_manager.update_guides(pos, self.scene().items(), moving_items[0], target_type=type(moving_items[0]))

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = self.mapToScene(event.position().toPoint())

        if self.main_window and hasattr(self.main_window, "coord_label"):
            self.main_window.coord_label.setText(f"X: {int(pos.x())}, Y: {int(pos.y())}")

        self._update_during_movement(pos)
        super().mouseMoveEvent(event)
        self._handle_auto_pan(event)
    
    def highlight_item(self, name):
        COLOR_BORDE_SEL = QColor(0, 0, 0) 
        COLOR_BORDE_BOX = QColor(33, 150, 243)  
        COLOR_BORDE_LABEL = QColor(255, 0, 0)  

        for item in self.scene().items():
            if isinstance(item, BoxItem):
                if item.name == name:
                    item.setPen(QPen(COLOR_BORDE_SEL, 1.5))
                    item.setZValue(8) 
                else:
                    item.setPen(QPen(COLOR_BORDE_BOX, 1))
                    item.setZValue(1)
            elif isinstance(item, LabelItem):
                if item.name == name:
                    item.setPen(QPen(COLOR_BORDE_SEL, 1.2)) 
                    item.setZValue(10)
                else:
                    item.setPen(QPen(COLOR_BORDE_LABEL, 0.5))
                    item.setZValue(1)