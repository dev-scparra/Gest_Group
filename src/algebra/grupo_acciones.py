"""Grupo A de acciones: A = {A_E, A1, A2, A3, A4, A5}, operacion de composicion de efectos.

A se modela, igual que G (ver grupo_gestos.py), como isomorfo a Z/6Z: Ai
corresponde al indice i modulo 6 y la operacion es la suma modular. Esto hace
que A sea abeliano (ALG-FR-007) de forma genuina (no postulada) y que el
homomorfismo phi: G -> A (modulo 002) sea, en la implementacion por defecto,
la biyeccion natural de indices entre dos copias de Z/6Z — un isomorfismo real,
consistente con la Seccion 3.3 del documento de contexto.
"""

from enum import Enum


class Accion(Enum):
    A_E = "ninguna"
    A1 = "subir_volumen"
    A2 = "bajar_volumen"
    A3 = "pausa_play"
    A4 = "siguiente"
    A5 = "anterior"


# Tabla de Cayley de (A, o): misma estructura de Z/6Z que CAYLEY_G, reindexada
# a Accion. Se guarda completa (36 entradas) para lookup O(1) simetrico, aunque
# por conmutatividad solo hay 21 productos unicos.
CAYLEY_A: dict[tuple[Accion, Accion], Accion] = {
    (Accion.A_E, Accion.A_E): Accion.A_E,
    (Accion.A_E, Accion.A1): Accion.A1,
    (Accion.A_E, Accion.A2): Accion.A2,
    (Accion.A_E, Accion.A3): Accion.A3,
    (Accion.A_E, Accion.A4): Accion.A4,
    (Accion.A_E, Accion.A5): Accion.A5,
    (Accion.A1, Accion.A_E): Accion.A1,
    (Accion.A1, Accion.A1): Accion.A2,
    (Accion.A1, Accion.A2): Accion.A3,
    (Accion.A1, Accion.A3): Accion.A4,
    (Accion.A1, Accion.A4): Accion.A5,
    (Accion.A1, Accion.A5): Accion.A_E,
    (Accion.A2, Accion.A_E): Accion.A2,
    (Accion.A2, Accion.A1): Accion.A3,
    (Accion.A2, Accion.A2): Accion.A4,
    (Accion.A2, Accion.A3): Accion.A5,
    (Accion.A2, Accion.A4): Accion.A_E,
    (Accion.A2, Accion.A5): Accion.A1,
    (Accion.A3, Accion.A_E): Accion.A3,
    (Accion.A3, Accion.A1): Accion.A4,
    (Accion.A3, Accion.A2): Accion.A5,
    (Accion.A3, Accion.A3): Accion.A_E,
    (Accion.A3, Accion.A4): Accion.A1,
    (Accion.A3, Accion.A5): Accion.A2,
    (Accion.A4, Accion.A_E): Accion.A4,
    (Accion.A4, Accion.A1): Accion.A5,
    (Accion.A4, Accion.A2): Accion.A_E,
    (Accion.A4, Accion.A3): Accion.A1,
    (Accion.A4, Accion.A4): Accion.A2,
    (Accion.A4, Accion.A5): Accion.A3,
    (Accion.A5, Accion.A_E): Accion.A5,
    (Accion.A5, Accion.A1): Accion.A_E,
    (Accion.A5, Accion.A2): Accion.A1,
    (Accion.A5, Accion.A3): Accion.A2,
    (Accion.A5, Accion.A4): Accion.A3,
    (Accion.A5, Accion.A5): Accion.A4,
}


# El grupo (A, o) como objeto importable (ALG-FR-008, CNF-FR-011), simetrico a
# ELEMENTOS_G/IDENTIDAD_G en grupo_gestos.py.
ELEMENTOS_A: frozenset[Accion] = frozenset(Accion)
IDENTIDAD_A: Accion = Accion.A_E


def operacion_A(a1: Accion, a2: Accion) -> Accion:
    """a1 . a2, lookup O(1) en la tabla de Cayley de A."""
    return CAYLEY_A[(a1, a2)]
