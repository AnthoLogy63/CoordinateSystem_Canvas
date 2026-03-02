"""
ui/items/text_item.py

Componente de texto editable basado en QGraphicsTextItem.
Gestiona la carga de fuentes personalizadas y la interacción con el usuario.
"""

import os
from PyQt6.QtWidgets import QGraphicsTextItem
from PyQt6.QtGui import QTextOption, QPen, QColor, QFont, QFontDatabase
from PyQt6.QtCore import Qt, QRectF

class TextItem(QGraphicsTextItem):
    """
    Subclase de QGraphicsTextItem optimizada para el sistema.
    
    Permite el renderizado de texto multilinea, carga dinámica de fuentes
    TTF/OTF y modo de edición activable por el padre.
    """
    
    _loaded_fonts = {}  # Cache de {path: family_name} para evitar recargas constantes

    def __init__(self, text_mode="short", parent=None):
        """
        Inicializa el item de texto.
        
        Args:
            text_mode (str): "short" para labels, "long" para bloques de texto.
            parent (QGraphicsItem): Item contenedor (BoxItem o LabelItem).
        """
        content = "Lorem" if text_mode == "short" else "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
        super().__init__(content, parent)
        
        self.setDefaultTextColor(QColor("#3e87ab"))
        # Edición desactivada por defecto — se activa solo con doble clic
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.document().setDocumentMargin(0)
        
        # Conectar cambio de texto para notificar al padre si es necesario
        self.document().contentsChanged.connect(self._on_content_changed)
        
        # Fuente por defecto suave
        font = QFont("Segoe UI", 10)
        self.setFont(font)
        
        self._show_border = True
        self._max_height = 1000
        self._editing = False

    def start_editing(self):
        """
        Activa el modo de edición de texto y otorga el foco al item.
        """
        if self._editing:
            return
        self._editing = True
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setAcceptedMouseButtons(Qt.MouseButton.AllButtons)
        self.setFocus(Qt.FocusReason.MouseFocusReason)

    def stop_editing(self):
        """
        Finaliza el modo de edición, limpia la selección y pierde el foco.
        """
        if not self._editing:
            return
        self._editing = False
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        self.clearFocus()
        # Notificar al padre (BoxItem) para que restaure su color
        parent = self.parentItem()
        if parent and hasattr(parent, 'on_text_editing_stopped'):
            parent.on_text_editing_stopped()

    def update_font_family(self, font_name):
        """
        Carga una fuente desde la carpeta /fonts y la aplica al item.
        
        Args:
            font_name (str): Nombre del archivo de fuente (ej: 'Arial.ttf').
            
        Returns:
            bool: True si la fuente se cargó o ya existía.
        """
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
            
            # Intentar detectar si es negrita por el nombre del archivo
            is_bold = "bold" in font_name.lower()
            font.setBold(is_bold)
            
            self.setFont(font)
            return True
        
        # Fallback a Arial
        font = self.font()
        font.setFamily("Arial")
        font.setBold(False)
        self.setFont(font)
        return False

    def boundingRect(self):
        """
        Define el área rectangular del item, limitando la altura al contenedor padre.
        
        Esto evita que el texto 'robe' eventos de mouse fuera de su contenedor.
        """
        br = super().boundingRect()
        w = br.width() if br.width() > 0 else (self.textWidth() if self.textWidth() > 0 else 200)
        constrained_h = min(br.height(), self._max_height)
        return QRectF(br.x(), br.y(), w, constrained_h)

    def paint(self, painter, option, widget):
        """
        Dibuja el texto y opcionalmente un borde punteado de guía.
        
        Implementa recorte (clipping) para asegurar que el texto no se salga del box.
        """
        clip_w = self.textWidth() if self.textWidth() > 0 else 2000
        clip_rect = QRectF(0, 0, clip_w, self._max_height)

        if self._show_border:
            painter.setPen(QPen(QColor(154, 199, 200, 60), 0.8, Qt.PenStyle.DashLine))
            painter.drawRect(clip_rect)

        painter.save()
        painter.setClipRect(clip_rect)

        if self.document().size().height() > self._max_height:
            super().paint(painter, option, widget)
            painter.setPen(self.defaultTextColor())
            painter.drawText(int(clip_w - 16), int(self._max_height - 3), "...")
        else:
            super().paint(painter, option, widget)

        painter.restore()

    def set_simple(self):
        """
        Configura el item para texto simple (alineado a la izquierda, sin ancho fijo).
        """
        self.setTextWidth(-1)
        option = QTextOption()
        option.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.document().setDefaultTextOption(option)

    def set_justified(self, width, height=None):
        """
        Configura el item para texto justificado con un ancho específico.
        
        Args:
            width (float): Ancho del bloque de texto.
            height (float, optional): Altura máxima para limitar el recorte visual.
        """
        self.setTextWidth(width)
        if height:
            self._max_height = height
        option = QTextOption()
        option.setAlignment(Qt.AlignmentFlag.AlignJustify)
        option.setWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.document().setDefaultTextOption(option)

    def _on_content_changed(self):
        """
        Notifica al item padre cuando el texto interno ha sido modificado.
        """
        parent = self.parentItem()
        if parent and hasattr(parent, "update_text_layout"):
            parent.update_text_layout()

    def focusOutEvent(self, event):
        """
        Finaliza automáticamente la edición cuando el item pierde el foco.
        """
        super().focusOutEvent(event)
        self.stop_editing()

    def update_font_size(self, delta):
        """
        Aumenta o disminuye el tamaño de la fuente.
        
        Args:
            delta (int): Cambio en el tamaño (ej: +1 o -1).
            
        Returns:
            int: El nuevo tamaño de fuente resultante.
        """
        self.prepareGeometryChange()
        font = self.font()
        new_size = max(4, font.pointSize() + delta)
        font.setPointSize(new_size)
        self.setFont(font)
        return new_size
