from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsItem
from PyQt6.QtGui import QPen, QColor
from PyQt6.QtCore import Qt, QPointF, QRectF
from core.modes import Mode
from core.utils import snap_to_5, sync_text_layout
from ui.items.text_item import TextItem

HANDLE_MARGIN = 5
MIN_SIZE = 8

# ── Colores de estado del BoxItem ──────────────────────────────────────────
COLOR_DEFAULT  = QColor(33, 150, 243)       # azul  — sin tocar
COLOR_SELECTED = QColor(253, 158, 46)       # naranja — seleccionado / moviendo
COLOR_EDITING  = QColor(72, 199, 142)       # verde  — editando texto

PEN_DEFAULT  = QPen(COLOR_DEFAULT,  1.0)
PEN_SELECTED = QPen(COLOR_SELECTED, 1.8)
PEN_EDITING  = QPen(COLOR_EDITING,  1.8)

BRUSH_DEFAULT  = QColor(33,  150, 243, 40)
BRUSH_SELECTED = QColor(253, 158,  46, 40)
BRUSH_EDITING  = QColor(72,  199, 142, 40)


def _get_handle(pos, rect, margin=HANDLE_MARGIN):
    x, y = pos.x(), pos.y()
    l, r = rect.left(), rect.right()
    t, b = rect.top(), rect.bottom()

    on_left   = abs(x - l) <= margin
    on_right  = abs(x - r) <= margin
    on_top    = abs(y - t) <= margin
    on_bottom = abs(y - b) <= margin

    if on_left  and on_top:    return "top_left"
    if on_right and on_top:    return "top_right"
    if on_left  and on_bottom: return "bottom_left"
    if on_right and on_bottom: return "bottom_right"

    inside_x = l <= x <= r
    inside_y = t <= y <= b
    if on_top    and inside_x: return "top"
    if on_bottom and inside_x: return "bottom"
    if on_left   and inside_y: return "left"
    if on_right  and inside_y: return "right"

    if inside_x and inside_y:
        return "center"

    return None

def _cursor_for_handle(handle):
    cursors = {
        "top_left":     Qt.CursorShape.SizeFDiagCursor,
        "bottom_right": Qt.CursorShape.SizeFDiagCursor,
        "top_right":    Qt.CursorShape.SizeBDiagCursor,
        "bottom_left":  Qt.CursorShape.SizeBDiagCursor,
        "top":          Qt.CursorShape.SizeVerCursor,
        "bottom":       Qt.CursorShape.SizeVerCursor,
        "left":         Qt.CursorShape.SizeHorCursor,
        "right":        Qt.CursorShape.SizeHorCursor,
        "center":       Qt.CursorShape.SizeAllCursor,
    }
    return cursors.get(handle, Qt.CursorShape.ArrowCursor)


class BoxItem(QGraphicsRectItem):
    def __init__(self, rect, name, font_name="Arial"):
        super().__init__(rect)
        self.name = name
        self.font_name = font_name

        self.setFlags(
            QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self._apply_state("default")

        self.text_item = TextItem(text_mode="long", parent=self)
        self.text_item.update_font_family(self.font_name)
        self.update_text_layout()

        self._handle = None
        self._drag_start = None
        self._rect_start = None
        self._pos_start = None
        self.setAcceptHoverEvents(True)

    # ── Estado visual ──────────────────────────────────────────────────────
    def _apply_state(self, state: str):
        """Aplica el color de borde/fondo según el estado: 'default', 'selected', 'editing'."""
        self._vis_state = state
        if state == "selected":
            self.setPen(PEN_SELECTED)
            self.setBrush(BRUSH_SELECTED)
        elif state == "editing":
            self.setPen(PEN_EDITING)
            self.setBrush(BRUSH_EDITING)
        else:
            self.setPen(PEN_DEFAULT)
            self.setBrush(BRUSH_DEFAULT)

    def set_state(self, state: str):
        self._apply_state(state)

    # ── Layout de texto ────────────────────────────────────────────────────
    def update_text_layout(self):
        self._sync_layout()

    def _sync_layout(self):
        sync_text_layout(self.rect(), self.text_item)

    # ── Helpers ───────────────────────────────────────────────────────────
    def _view(self):
        if self.scene() and self.scene().views():
            return self.scene().views()[0]
        return None

    def _in_interactive_mode(self):
        v = self._view()
        return v and v.mode in (Mode.TRANSFORM, Mode.SELECT)

    def _in_transform_mode(self):
        return self._in_interactive_mode()

    def get_text(self):
        return self.text_item.toPlainText()

    def set_name(self, new_name):
        self.name = new_name

    def get_resize_corner(self, pos):
        return _get_handle(pos, self.rect())

    # ── Eventos de ratón ──────────────────────────────────────────────────
    def mouseDoubleClickEvent(self, event):
        if self._in_interactive_mode():
            self._apply_state("editing")
            self.text_item.start_editing()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def on_text_editing_stopped(self):
        """Llamado por TextItem al salir de la edición."""
        self._apply_state("default")

    def mousePressEvent(self, event):
        if not self._in_interactive_mode():
            super().mousePressEvent(event)
            return

        if self.text_item._editing:
            super().mousePressEvent(event)
            return

        handle = _get_handle(event.pos(), self.rect())
        if handle is None:
            super().mousePressEvent(event)
            return

        self._handle = handle
        self._drag_start = event.scenePos()
        self._rect_start = QRectF(self.rect())
        self._pos_start  = QPointF(self.pos())
        self.setCursor(_cursor_for_handle(handle))
        event.accept()

    def mouseMoveEvent(self, event):
        if not self._in_interactive_mode() or self._handle is None:
            super().mouseMoveEvent(event)
            return

        v = self._view()
        if not (v and v.main_window and v.alignment_manager):
            return super().mouseMoveEvent(event)

        delta = event.scenePos() - self._drag_start
        r = QRectF(self._rect_start)
        h = self._handle

        if h == "center":
            new_pos = self._pos_start + delta
            self.setPos(snap_to_5(new_pos.x()), snap_to_5(new_pos.y()))
        else:
            ref_point = event.scenePos()
            v.alignment_manager.update_guides(ref_point, self.scene().items(), self, target_type=BoxItem)
            snapped_pos = v.alignment_manager.get_snapped_pos(ref_point)

            sdx = snapped_pos.x() - self._drag_start.x()
            sdy = snapped_pos.y() - self._drag_start.y()

            if "left"   in h: r.setLeft  (snap_to_5(self._rect_start.left()   + sdx))
            if "right"  in h: r.setRight (snap_to_5(self._rect_start.right()  + sdx))
            if "top"    in h: r.setTop   (snap_to_5(self._rect_start.top()    + sdy))
            if "bottom" in h: r.setBottom(snap_to_5(self._rect_start.bottom() + sdy))

            r = r.normalized()
            if r.width() >= MIN_SIZE and r.height() >= MIN_SIZE:
                self.setRect(r)
                self.update_text_layout()

        if v.main_window:
            v.main_window.elements_panel.update_list()
        event.accept()

    def mouseReleaseEvent(self, event):
        self._handle = None
        v = self._view()
        if v and v.alignment_manager:
            v.alignment_manager.clear_guides()
        super().mouseReleaseEvent(event)

    def hoverMoveEvent(self, event):
        if self._in_interactive_mode() and not self.text_item._editing:
            handle = _get_handle(event.pos(), self.rect())
            self.setCursor(_cursor_for_handle(handle) if handle else Qt.CursorShape.SizeAllCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverLeaveEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            return QPointF(snap_to_5(value.x()), snap_to_5(value.y()))

        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.update_text_layout()
            v = self._view()
            if v and v.main_window:
                v.main_window.elements_panel.update_list()
        return super().itemChange(change, value)