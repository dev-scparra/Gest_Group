"""NFR-G03 / HOM-FR-010: la capa algebraica es pura (sin cv2, sin mediapipe, sin subprocess).

Ambos son requerimientos MUST con ID propio, y hasta ahora se cumplian por suerte:
nada impedia que un `import cv2` se colara manana en src/algebra/ y la suite siguiera
en verde. Es la capa que el curso evalua, y era la unica cuyo requerimiento de pureza
no tenia respaldo ejecutable (CNF-FR-010).

Se inspecciona el AST en vez de importar los modulos: importarlos ejecutaria su codigo
y, peor, no revelaria un import que estuviera dentro de una funcion.
"""

import ast
from pathlib import Path

RAIZ_ALGEBRA = Path(__file__).resolve().parent.parent / "src" / "algebra"
PROHIBIDOS = {"cv2", "mediapipe", "subprocess"}


def _modulos_importados(arbol: ast.AST) -> set[str]:
    modulos: set[str] = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            modulos.update(alias.name.split(".")[0] for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            modulos.add(nodo.module.split(".")[0])
    return modulos


def test_capa_algebraica_no_importa_io_ni_vision():
    archivos = sorted(RAIZ_ALGEBRA.glob("*.py"))
    assert archivos, f"no se encontraron modulos en {RAIZ_ALGEBRA}"

    for archivo in archivos:
        arbol = ast.parse(archivo.read_text(encoding="utf-8"), filename=str(archivo))
        prohibidos_usados = _modulos_importados(arbol) & PROHIBIDOS
        assert not prohibidos_usados, (
            f"{archivo.name} importa {sorted(prohibidos_usados)}: la capa algebraica "
            "debe poder probarse sin camara ni SO (NFR-G03, HOM-FR-010)"
        )
