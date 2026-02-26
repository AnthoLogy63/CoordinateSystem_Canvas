class LabelManager:
    def __init__(self):
        self.labels = {}
        self.counter = 0

    def add_label(self, label_item, name=None):
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
        if name in self.labels:
            del self.labels[name]

    def rename_label(self, old_name, new_name):
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
        self.labels.clear()
        self.counter = 0

    def get_labels_data(self):
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
