def snap_to_5(value: float) -> int:
    """
    Redondea un valor al múltiplo de 5 más cercano.

    Args:
        value (float): El valor a redondear.

    Returns:
        int: Valor redondeado al múltiplo de 5 más cercano.
    
    Ejemplo:
        >>> snap_to_5(12)
        10
        >>> snap_to_5(13)
        15
    """
    return round(value / 5) * 5


def sync_text_layout(container_rect, text_item):
    """
    Sincroniza la posición y tamaño de un item de texto dentro de un rectángulo contenedor.
    
    Centra el texto verticalmente dentro del contenedor y ajusta su ancho.  
    Si el item tiene el método `set_justified`, lo usará para aplicar justificación horizontal
    considerando un ancho y, opcionalmente, una altura máxima para limitar el recorte visual.

    Args:
        container_rect (QRectF): Rectángulo contenedor donde se debe alinear el texto.
        text_item: Item de texto
    """
    width = container_rect.width()
    height = container_rect.height()
    
    # Ajustar ancho y justificación horizontal si existe set_justified
    if hasattr(text_item, 'set_justified'): 
        text_item.set_justified(width, height)
    else:
        text_item.setTextWidth(width)
        
    # Calcular altura del documento para centrar verticalmente
    doc_height = text_item.document().size().height()
    y_offset = max(0, (height - doc_height) / 2)
    
    # Posicionar el texto dentro del contenedor
    text_item.setPos(container_rect.left(), container_rect.top() + y_offset)