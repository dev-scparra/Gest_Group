"""Grupo G de gestos: G = {E, G1, G2, G3, G4, G5}, operacion de composicion secuencial.

G se realiza como el subgrupo ciclico de S5 generado por sigma = (1 2 3)(4 5),
que tiene orden 6 (lcm(3,2)). Gi := sigma^i para i=1..5, E := sigma^0. La tabla
de Cayley completa (36 entradas) se deriva por composicion real de permutaciones
en `scripts/derivar_cayley.py` (no se transcribe a mano) y se fija aqui como
constante offline, tal como exige NFR-G03 (esta capa no puede depender de
geometria/landmarks en tiempo de ejecucion).

Ver docs/demostraciones.md (Decision D1) para la justificacion completa de por
que esta realizacion reemplaza la version del documento de contexto original
("cada gesto es su propio inverso"), que es matematicamente inconsistente con
|G|=6 (un grupo donde todo elemento es autoinverso es abeliano y de orden
2^n, y 6 no es potencia de 2).
"""

from enum import Enum


class Gesto(Enum):
    E = "reposo"
    G1 = "1_dedo"
    G2 = "2_dedos"
    G3 = "puno"
    G4 = "mano_abierta"
    G5 = "pulgar"


# Tabla de Cayley de (G, o), derivada de sigma^i . sigma^j = sigma^((i+j) mod 6)
# via scripts/derivar_cayley.py. G es isomorfo a Z/6Z.
CAYLEY_G: dict[tuple[Gesto, Gesto], Gesto] = {
    (Gesto.E, Gesto.E): Gesto.E,
    (Gesto.E, Gesto.G1): Gesto.G1,
    (Gesto.E, Gesto.G2): Gesto.G2,
    (Gesto.E, Gesto.G3): Gesto.G3,
    (Gesto.E, Gesto.G4): Gesto.G4,
    (Gesto.E, Gesto.G5): Gesto.G5,
    (Gesto.G1, Gesto.E): Gesto.G1,
    (Gesto.G1, Gesto.G1): Gesto.G2,
    (Gesto.G1, Gesto.G2): Gesto.G3,
    (Gesto.G1, Gesto.G3): Gesto.G4,
    (Gesto.G1, Gesto.G4): Gesto.G5,
    (Gesto.G1, Gesto.G5): Gesto.E,
    (Gesto.G2, Gesto.E): Gesto.G2,
    (Gesto.G2, Gesto.G1): Gesto.G3,
    (Gesto.G2, Gesto.G2): Gesto.G4,
    (Gesto.G2, Gesto.G3): Gesto.G5,
    (Gesto.G2, Gesto.G4): Gesto.E,
    (Gesto.G2, Gesto.G5): Gesto.G1,
    (Gesto.G3, Gesto.E): Gesto.G3,
    (Gesto.G3, Gesto.G1): Gesto.G4,
    (Gesto.G3, Gesto.G2): Gesto.G5,
    (Gesto.G3, Gesto.G3): Gesto.E,
    (Gesto.G3, Gesto.G4): Gesto.G1,
    (Gesto.G3, Gesto.G5): Gesto.G2,
    (Gesto.G4, Gesto.E): Gesto.G4,
    (Gesto.G4, Gesto.G1): Gesto.G5,
    (Gesto.G4, Gesto.G2): Gesto.E,
    (Gesto.G4, Gesto.G3): Gesto.G1,
    (Gesto.G4, Gesto.G4): Gesto.G2,
    (Gesto.G4, Gesto.G5): Gesto.G3,
    (Gesto.G5, Gesto.E): Gesto.G5,
    (Gesto.G5, Gesto.G1): Gesto.E,
    (Gesto.G5, Gesto.G2): Gesto.G1,
    (Gesto.G5, Gesto.G3): Gesto.G2,
    (Gesto.G5, Gesto.G4): Gesto.G3,
    (Gesto.G5, Gesto.G5): Gesto.G4,
}


def operacion_G(g1: Gesto, g2: Gesto) -> Gesto:
    """g1 . g2, lookup O(1) en la tabla de Cayley de G."""
    return CAYLEY_G[(g1, g2)]
