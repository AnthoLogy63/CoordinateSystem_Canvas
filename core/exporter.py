import os
from datetime import datetime

def export_layout(box_manager, label_manager, template_path=None, export_dir=None):
    if export_dir:
        os.makedirs(export_dir, exist_ok=True)
    else:
        export_dir = os.path.join(os.path.dirname(__file__), "..", "export")
        os.makedirs(export_dir, exist_ok=True)

    if template_path:
        base_name = os.path.splitext(os.path.basename(template_path))[0]
        filename = f"{base_name}_Coordenadas"
    else:
        timestamp = datetime.now().strftime("Layout-%Y-%m-%d_%H-%M-%S")
        filename = f"layout_config---{timestamp}"

    base_path = os.path.join(export_dir, filename)
    py_path = f"{base_path}.py"
    txt_path = f"{base_path}.txt"

    boxes_data = box_manager.get_boxes_data()
    labels_data = label_manager.get_labels_data()

    # Recolectar combinaciones únicas de fuentes
    unique_fonts = {}
    all_pairs = set()

    for data in boxes_data.values():
        all_pairs.add((data["font_name"], data["font_size"]))

    for data in labels_data.values():
        all_pairs.add((data["font_name"], data["font_size"]))

    def build_font_var(name, size):
        clean = name.split('.')[0].replace('-', '_').replace(' ', '_').lower()
        return f"font_{clean}_{size}"

    for fname, fsize in all_pairs:
        unique_fonts[(fname, fsize)] = build_font_var(fname, fsize)

    # Preparar bloque de fuentes
    font_setup_lines = []
    font_setup_lines.append("from PIL import ImageFont")
    font_setup_lines.append("")
    font_setup_lines.append("# Configuración de fuentes")
    font_setup_lines.append("")

    unique_font_names = sorted({fname for fname, _ in all_pairs})

    for fname in unique_font_names:
        clean = fname.split('.')[0].replace('-', '_').replace(' ', '_').lower()
        path_var = f"path_{clean}"
        font_setup_lines.append(f"{path_var} = r'fonts\\{fname}'")

    font_setup_lines.append("")
    font_setup_lines.append("# Carga de fuentes")

    for fname, fsize in sorted(all_pairs):
        clean = fname.split('.')[0].replace('-', '_').replace(' ', '_').lower()
        path_var = f"path_{clean}"
        var_name = unique_fonts[(fname, fsize)]
        font_setup_lines.append(f"{var_name} = ImageFont.truetype({path_var}, {fsize})")

    # Exportar .py
    with open(py_path, "w", encoding="utf-8") as py_file:
        for line in font_setup_lines:
            py_file.write(line)

        py_file.write("\nLAYOUT_CONFIG = {\n")

        py_file.write("    'boxes': {\n")
        for name, data in boxes_data.items():
            font_var = unique_fonts.get(
                (data["font_name"], data["font_size"]),
                "custom_font"
            )

            py_file.write(f"        '{name}': {{\n")
            py_file.write(f"            'x1': {data['x1']},\n")
            py_file.write(f"            'y1': {data['y1']},\n")
            py_file.write(f"            'x2': {data['x2']},\n")
            py_file.write(f"            'y2': {data['y2']},\n")
            py_file.write(f"            'font': {font_var}\n")
            py_file.write("        },\n")
        py_file.write("    },\n")

        py_file.write("    'labels': {\n")
        for name, data in labels_data.items():
            font_var = unique_fonts.get(
                (data["font_name"], data["font_size"]),
                "custom_font"
            )

            py_file.write(f"        '{name}': {{\n")
            py_file.write(f"            'x': {data['x']},\n")
            py_file.write(f"            'y': {data['y']},\n")
            py_file.write(f"            'font': {font_var},\n")
            py_file.write(f"            'fill': {data.get('fill', (0,0,0))}\n")
            py_file.write("        },\n")
        py_file.write("    }\n")

        py_file.write("}\n")

    # Exportar .txt
    with open(txt_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(f"# --- {filename} ---\n\n")

        for line in font_setup_lines:
            if line.strip() == "":
                txt_file.write("#\n")
            elif line.startswith("#"):
                txt_file.write(f"{line}\n")
            else:
                txt_file.write(f"# {line}\n")

        txt_file.write("\n# LABELS\n")
        for name, data in labels_data.items():
            f_var = unique_fonts.get(
                (data["font_name"], data["font_size"]),
                "custom_font"
            )
            txt_file.write(
                f"# draw.text(({data['x']}, {data['y']}), {name}, font={f_var}, fill=(0,0,0))\n"
            )

        txt_file.write("\n# BOXES\n")
        for name, data in boxes_data.items():
            x1, y1, x2, y2 = data['x1'], data['y1'], data['x2'], data['y2']
            f_var = unique_fonts.get(
                (data["font_name"], data["font_size"]),
                "semi_bold_font"
            )
            txt_file.write(f"# draw.rectangle([({x1}, {y1}), ({x2}, {y2})], fill=None, outline=None)\n")
            txt_file.write(f"# text_box = ({x1}, {y1}, {x2}, {y2})\n")
            txt_file.write(
                f"# draw_wrapped_text_justified(draw, {name}, {f_var}, text_box, 17, (0, 0, 0))\n\n"
            )

    return py_path, txt_path
