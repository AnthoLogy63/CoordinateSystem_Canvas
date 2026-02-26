# Layout Builder

Una herramienta intuitiva para diseñar y exportar layouts de objetos (cajas y etiquetas) sobre plantillas de imagen, construida con Python y PyQt6.

## Características Principales

- **Gestión de Objetos**: Creación y edición de cajas (Boxes) y puntos de referencia (Labels/Círculos).
- **Reglas de Alineación**: Guías visuales automáticas que facilitan la alineación entre objetos.
- **Ajuste Magnético (Snapping)**: Los objetos se "imantan" a las guías de alineación para una precisión perfecta.
- **Importación de Plantillas**: Carga imágenes de fondo para usarlas como guía de diseño.
- **Exportación de Datos**: Genera archivos de configuración en Python y texto con las coordenadas de los elementos.
- **Sincronización en Vivo**: Las coordenadas de los elementos se actualizan en tiempo real en el panel lateral al mover o redimensionar.
- **Alineación Vertical Automática**: El texto dentro de los Boxes se justifica y se centra verticalmente de forma automática.
- **Confirmación de Salida**: Previene el cierre accidental mediante un diálogo de confirmación.

## Estructura del Proyecto

```text
4ta Version Programa/
│
├── main.py                 # Punto de entrada de la aplicación.
├── README.md               # Documentación general.
│
├── core/                   # Lógica de negocio y motores.
│   ├── alignment_manager.py# Motor central de reglas y snapping.
│   ├── box_manager.py      # Control de almacenamiento de cajas.
│   ├── label_manager.py    # Control de almacenamiento de etiquetas.
│   ├── exporter.py         # Lógica para exportar el diseño.
│   └── modes.py            # Modos de interacción (Select, Create, etc.).
│
├── ui/                     # Interfaz de usuario y visualización.
│   ├── main_window.py      # Ventana principal y eventos globales.
│   ├── graphics_view.py    # Lienzo interactivo (Canvas).
│   ├── items/              # Clases de objetos gráficos individuales.
│   │   ├── box_item.py     # Representación visual de las cajas.
│   │   └── label_item.py   # Representación visual de las etiquetas.
│   └── panels/             # Paneles laterales de herramientas y listas.
│
├── export/                 # Destino de archivos exportados (.py, .txt).
└── import/                 # Recursos y plantillas de fondo.
```

## ¿Cómo funciona el Proyecto?

El **Layout Builder** está diseñado para ser un flujo de trabajo lineal y eficiente para definir coordenadas en plantillas de diseño:

1.  **Carga de Plantilla**: Se inicia importando una imagen de fondo (plantilla) que sirve como base visual.
2.  **Definición de Elementos**:
    -   **Boxes**: Áreas rectangulares (para bloques de texto).
    -   **Labels**: Puntos específicos (coordenadas X, Y individuales).
3.  **Alineación Inteligente**: Al mover o redimensionar, el `AlignmentManager` detecta automáticamente otros elementos cercanos y dibuja guías para asegurar que todo esté perfectamente alineado.
4.  **Exportación**: Una vez finalizado, se genera:
    -   Un archivo `.py` con un diccionario de configuración listo para ser usado en otros scripts.
    -   Un archivo `.txt` con fragmentos de código de ejemplo (usando PIL/Pillow) para dibujar sobre la plantilla.

## Flujo de Alineación y Snapping

El sistema sigue un flujo reactivo:
1.  **Interacción**: El usuario interactúa con un objeto en el `GraphicsView`.
2.  **Cálculo**: Se solicita al `AlignmentManager` (en `core/`) que verifique puntos de referencia cercanos.
3.  **Snapping**: Si hay coincidencia (dentro de un umbral de 8px), se devuelve una coordenada ajustada y se muestran guías visuales.
4.  **Actualización**: El objeto se posiciona exactamente en la línea de alineación.

## 🏛️ Responsabilidades de los Componentes

| Componente | Responsabilidad |
| :--- | :--- |
| `main.py` | Punto de entrada y configuración de estilos. |
| `MainWindow` | Coordinación de paneles, barra de estado y orquestación general. |
| `GraphicsView` | Gestión del zoom, dibujo temporal y control de ratón sobre el canvas. |
| `AlignmentManager` | Lógica matemática de alineación (independiente de la UI). |
| `Items (Package)` | Representación visual individual, estilos y eventos específicos de cada objeto. |
| `Managers (Core)` | Gestión de datos pura: IDs únicos, búsqueda por nombre y persistencia. |
