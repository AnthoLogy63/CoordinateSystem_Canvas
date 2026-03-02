"""
core/label_manager.py

Gestiona la colección de objetos LabelItem, coordinando su registro y exportación.
"""

class LabelManager:
    """
    Gestor lógico de etiquetas (LabelItem).
    
    Se encarga de mantener un registro de todas las etiquetas en la escena,
    garantizar nombres únicos y proporcionar los datos para la exportación.
    """
    
    def __init__(self):
        """
        Inicializa el gestor de etiquetas con un diccionario vacío y un contador.
        """
        self.labels = {}
        self.counter = 0

    def add_label(self, label_item, name=None):
        """
        Registra una nueva etiqueta en el sistema.
        
        Args:
            label_item (LabelItem): El objeto visual de la etiqueta.
            name (str, optional): Nombre sugerido. Si no se da, se genera uno (LabelX).
            
        Returns:
            str: El nombre final asignado a la etiqueta.
        """
        if name is None:
            self.counter += 1
            name = f"Label{self.counter}"
        else:
            base_name = name
            suffix = 1
            while name in self.labels:
                name = f"{base_name}_{suffix}"
                suffix += 1

            try:
                if name.startswith("Label"):
                    number = int(name.replace("Label", ""))
                    self.counter = max(self.counter, number)
            except: pass

        label_item.name = name
        self.labels[name] = label_item
        return name

    def remove_label(self, name):
        """
        Elimina el registro de una etiqueta por su nombre.
        
        Args:
            name (str): Nombre de la etiqueta a eliminar.
        """
        if name in self.labels:
            del self.labels[name]

    def rename_label(self, old_name, new_name):
        """
        Renombra una etiqueta existente validando la disponibilidad del nuevo nombre.
        
        Args:
            old_name (str): Nombre actual.
            new_name (str): Nuevo nombre deseado.
            
        Returns:
            bool: True si el cambio fue exitoso.
        """
        if old_name in self.labels and new_name not in self.labels:
            new_dict = {}
            for key, value in self.labels.items():
                if key == old_name:
                    value.name = new_name
                    new_dict[new_name] = value
                else:
                    new_dict[key] = value
            self.labels = new_dict
            return True
        return False

    def clear(self):
        """
        Limpia todos los registros de etiquetas.
        """
        self.labels.clear()
        self.counter = 0

    def get_labels_data(self):
        """
        Extrae los datos de todas las etiquetas para exportación.
        
        Returns:
            dict: Diccionario mapeando el nombre de la etiqueta a sus atributos (x, y, fuente, texto).
        """
        data = {}
        for name, label in self.labels.items():
            x, y = label.get_center()
            data[name] = {
                "x": int(x), 
                "y": int(y),
                "font_size": label.text_item.font().pointSize(),
                "font_name": label.font_name,
                "text": label.get_text()
            }
            
        return data
