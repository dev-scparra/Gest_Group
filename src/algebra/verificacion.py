"""Verificacion generica de los 4 axiomas de grupo, aplicable a G y a A (ALG-FR-005).

`verificar_axiomas_grupo()` es una utilidad parametrizada por (elementos,
operacion, identidad): la misma funcion verifica G y A sin duplicar logica. No
la invocan `grupo_gestos.py` ni `grupo_acciones.py` — esos modulos solo declaran
sus tablas de Cayley; quien la aplica a ambos grupos es la suite
(`tests/test_verificacion.py`), que es donde la verificacion tiene sentido como
evidencia ejecutable (Demostracion 1, docs/demostraciones.md).
"""

from dataclasses import dataclass, field
from typing import Callable, TypeVar

T = TypeVar("T")


@dataclass
class ReporteAxiomas:
    clausura: bool
    asociatividad: bool
    identidad: bool
    inversos: bool
    fallos_clausura: list = field(default_factory=list)
    fallos_asociatividad: list = field(default_factory=list)
    fallos_identidad: list = field(default_factory=list)
    fallos_inversos: list = field(default_factory=list)

    @property
    def es_grupo(self) -> bool:
        return self.clausura and self.asociatividad and self.identidad and self.inversos


def verificar_axiomas_grupo(
    elementos: set[T], operacion: Callable[[T, T], T], identidad: T
) -> ReporteAxiomas:
    """Recorre la tabla completa y reporta, por separado, cada axioma de grupo."""
    fallos_clausura = []
    for a in elementos:
        for b in elementos:
            resultado = operacion(a, b)
            if resultado not in elementos:
                fallos_clausura.append((a, b, resultado))

    fallos_asociatividad = []
    for a in elementos:
        for b in elementos:
            for c in elementos:
                izquierda = operacion(operacion(a, b), c)
                derecha = operacion(a, operacion(b, c))
                if izquierda != derecha:
                    fallos_asociatividad.append((a, b, c, izquierda, derecha))

    fallos_identidad = []
    for a in elementos:
        if operacion(identidad, a) != a or operacion(a, identidad) != a:
            fallos_identidad.append(a)

    fallos_inversos = []
    for a in elementos:
        if not any(
            operacion(a, b) == identidad and operacion(b, a) == identidad
            for b in elementos
        ):
            fallos_inversos.append(a)

    return ReporteAxiomas(
        clausura=not fallos_clausura,
        asociatividad=not fallos_asociatividad,
        identidad=not fallos_identidad,
        inversos=not fallos_inversos,
        fallos_clausura=fallos_clausura,
        fallos_asociatividad=fallos_asociatividad,
        fallos_identidad=fallos_identidad,
        fallos_inversos=fallos_inversos,
    )
