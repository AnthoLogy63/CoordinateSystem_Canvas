import os
from PyQt6.QtWidgets import QGraphicsTextItem
from PyQt6.QtGui import QTextOption, QPen, QColor, QFont, QFontDatabase
from PyQt6.QtCore import Qt, QRectF

class TextItem(QGraphicsTextItem):
    _loaded_fonts = {}  # Cache de {path: family_name}

    def __init__(self, text_mode="short", parent=None):
        content = "Lorem" if text_mode == "short" else "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
        super().__init__(content, parent)
        
        self.setDefaultTextColor(QColor("#3e87ab"))
        # Habilitar edición de texto
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        self.document().setDocumentMargin(0)
        
        # Conectar cambio de texto para notificar al padre si es necesario
        self.document().contentsChanged.connect(self._on_content_changed)
        
        # Fuente por defecto suave, sin forzar negrita aquí
        font = QFont("Segoe UI", 10)
        self.setFont(font)
        
        self._show_border = True
        self._max_height = 1000

    def update_font_family(self, font_name):
        """Carga y aplica una fuente desde la carpeta fonts/"""
        if not font_name or font_name.lower() == "arial":
            font = self.font()
            font.setFamily("Arial")
            font.setBold(False)
            self.setFont(font)
            return True

        fonts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "fonts")
        font_path = os.path.normpath(os.path.join(fonts_dir, font_name))

        family = None
        if font_path in TextItem._loaded_fonts:
            family = TextItem._loaded_fonts[font_path]
        else:
            if os.path.exists(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        family = families[0]
                        TextItem._loaded_fonts[font_path] = family

        if family:
            font = self.font()
            font.setFamily(family)
            
            # Intentar detectar si es negrita por el nombre del archivo si la familia es la misma
            # Esto ayuda cuando varias fuentes comparten la misma familia (Ej: Tw Cen MT)
            is_bold = "bold" in font_name.lower()
            font.setBold(is_bold)
            
            self.setFont(font)
            return True
        
        # Fallback
        font = self.font()
        font.setFamily("Arial")
        font.setBold(False)
        self.setFont(font)
        return False

    def paint(self, painter, option, widget):
        if self._show_border:
            painter.setPen(QPen(QColor(154, 199, 200, 120), 1, Qt.PenStyle.DashLine))
            painter.drawRect(self.boundingRect())
        
        painter.save()
        painter.setClipRect(QRectF(0, 0, self.textWidth() if self.textWidth() > 0 else 2000, self._max_height))
        
        if self.document().size().height() > self._max_height:
            super().paint(painter, option, widget)
            painter.setPen(self.defaultTextColor())
            painter.drawText(int(self.textWidth() - 12), int(self._max_height - 2), "...")
        else:
            super().paint(painter, option, widget)
            
        painter.restore()

    def set_simple(self):
        self.setTextWidth(-1)
        option = QTextOption()
        option.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.document().setDefaultTextOption(option)

    def set_justified(self, width, height=None):
        self.setTextWidth(width)
        if height:
            self._max_height = height
        option = QTextOption()
        option.setAlignment(Qt.AlignmentFlag.AlignJustify)
        option.setWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.document().setDefaultTextOption(option)

    def _on_content_changed(self):
        """Notifica al padre que el contenido ha cambiado"""
        parent = self.parentItem()
        if parent and hasattr(parent, "update_text_layout"):
            parent.update_text_layout()

    def focusOutEvent(self, event):
        """Sale del modo edición al perder el foco"""
        super().focusOutEvent(event)
        # Opcional: mover el cursor al inicio
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)

    def update_font_size(self, delta):
        self.prepareGeometryChange()
        font = self.font()
        new_size = max(4, font.pointSize() + delta)
        font.setPointSize(new_size)
        self.setFont(font)
        return new_size