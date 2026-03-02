"""
core/box_manager.py

Gestiona la colección de objetos BoxItem, su creación, eliminación y recuperación de datos.
"""

from core.utils import snap_to_5

class BoxManager:
    """
    Gestor lógico de cajas (BoxItem).
    
    Se encarga de mantener un registro de todas las cajas en la escena,
    gestionar sus nombres únicos y facilitar la exportación de sus datos geométricos.
    """
    
    def __init__(self):
        """
        Inicializa el gestor de cajas con un diccionario vacío y un contador interno.
        """
        self.boxes = {}
        self.counter = 0

    def add_box(self, box_item, name=None):
        """
        Registra una nueva caja en el sistema.
        
        Si no se proporciona un nombre, genera uno automáticamente (Box1, Box2, etc.).
        Si el nombre ya existe, añade un sufijo numérico para garantizar unicidad.
        
        Args:
            box_item (BoxItem): El objeto visual de la caja.
            name (str, optional): Nombre sugerido para la caja.
            
        Returns:
            str: El nombre final asignado a la caja.
        """
        if name is None:
            self.counter += 1
            name = f"Box{self.counter}"
        else:
            base_name = name
            suffix = 1
            while name in self.boxes:
                name = f"{base_name}_{suffix}"
                suffix += 1
            try:
                if name.startswith("Box"):
                    number = int(name.replace("Box", ""))
                    self.counter = max(self.counter, number)
            except:
                pass

        box_item.name = name
        self.boxes[name] = box_item
        return name

    def remove_box(self, name):
        """
        Elimina una caja del registro interno por su nombre.
        
        Args:
            name (str): Nombre de la caja a eliminar.
        """
        if name in self.boxes:
            del self.boxes[name]

    def rename_box(self, old_name, new_name):
        """
        Renombra una caja existente, validando que el nuevo nombre no esté ocupado.
        
        Args:
            old_name (str): Nombre actual de la caja.
            new_name (str): Nuevo nombre deseado.
            
        Returns:
            bool: True si el renombrado fue exitoso, False en caso contrario.
        """
        if old_name in self.boxes and new_name not in self.boxes:
            new_dict = {}
            for key, value in self.boxes.items():
                if key == old_name:
                    value.name = new_name
                    new_dict[new_name] = value
                else:
                    new_dict[key] = value
            self.boxes = new_dict
            return True
        return False

    def clear(self):
        """
        Limpia todos los registros de cajas y reinicia el contador.
        """
        self.boxes.clear()
        self.counter = 0

    def get_boxes_data(self):
        """
        Extrae la información geométrica y de contenido de todas las cajas.
        
        Asegura que todas las coordenadas de exportación estén ajustadas a múltiplos 
        de 5 píxeles mediante la utilidad snap_to_5.
        
        Returns:
            dict: Diccionario con los datos de todas las cajas (coordenadas, fuente, texto).
        """
        data = {}
        for name, box in self.boxes.items():
            rect = box.sceneBoundingRect()

            x1 = snap_to_5(rect.left())
            y1 = snap_to_5(rect.top())
            x2 = snap_to_5(rect.right())
            y2 = snap_to_5(rect.bottom())

            data[name] = {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "font_size": box.text_item.font().pointSize(),
                "font_name": box.font_name,
                "text": box.get_text()
            }

        return data
