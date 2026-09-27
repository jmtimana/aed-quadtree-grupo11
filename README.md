# Quadtree — animación sin voz ni subtítulos

Código del proyecto original con siete escenas de Manim. Conserva los tiempos, diagramas, títulos, etiquetas, explicaciones y pseudocódigo de la animación. No carga audio ni genera o incrusta subtítulos de narración.

## Ejecutar

Requisitos del proyecto original: Python 3.12, Manim Community, FFmpeg en PATH y fuente DejaVu Sans. No requiere LaTeX.

Desde esta carpeta:

```bash
python -m venv .venv
```

En Windows:

```bat
.venv\\Scripts\\activate
python -m pip install -r requirements.txt
python -m unittest -v
python renderizar.py
```

En Linux/macOS, activar con `source .venv/bin/activate` y ejecutar los mismos comandos de instalación y renderizado.

El video completo se guarda en `../video/quadtree.mp4`, y las siete escenas en `../escenas/`. La duración prevista conserva la original: aproximadamente 4 minutos y 47 segundos, a 1080p y 30 fps.

Para una vista previa de menor resolución:

```bash
python renderizar.py --preview
```

Para renderizar una escena:

```bash
python renderizar.py --scene S02Insercion
```

Para unir las siete escenas ya renderizadas:

```bash
python renderizar.py --solo-unir
```

## Contenido

* `main.py`: siete escenas de la animación original; carga de audio eliminada.
* `quadtree.py`: implementación real del PR quadtree y eventos de las operaciones.
* `renderizar.py`: renderizado y unión; la unión excluye pistas de audio y subtítulos.
* `tiempos.json`: duraciones originales para conservar la sincronización visual.
* `integrantes.json`: créditos editables.
* `test\_quadtree.py`: pruebas originales del modelo.
* `ANALISIS.md`: análisis de complejidad original.
* `requirements.txt`: dependencia de Manim.

Subir el contenido de esta carpeta al repositorio. No se incluyen voz, guion de narración, archivos SRT ni videos renderizados.

Implementación y animación en Python, elaboradas con asistencia de ChatGPT. Revisar y declarar las contribuciones reales según las reglas del curso.

