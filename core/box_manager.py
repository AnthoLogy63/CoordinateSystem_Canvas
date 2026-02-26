class BoxManager:
    def __init__(self):
        self.boxes = {}
        self.counter = 0

    def add_box(self, box_item, name=None):
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
        if name in self.boxes:
            del self.boxes[name]

    def rename_box(self, old_name, new_name):
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
        self.boxes.clear()
        self.counter = 0

    def get_boxes_data(self):
        data = {}
        for name, box in self.boxes.items():
            rect = box.sceneBoundingRect()

            x1 = int(rect.left())
            y1 = int(rect.top())
            x2 = int(rect.right())
            y2 = int(rect.bottom())

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
