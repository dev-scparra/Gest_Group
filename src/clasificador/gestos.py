"""Clasificador geometrico: 21 landmarks suavizados -> elemento g in G.

Ver spec 006-clasificador-gestos. Heuristica de "dedo levantado" por
comparacion punta-vs-MCP; el pulgar usa el eje x por su movimiento lateral
(CLA-FR-002).
"""

from src.algebra.grupo_gestos import Gesto

PUNTAS = [4, 8, 12, 16, 20]
MCPS = [2, 5, 9, 13, 17]


def dedos_levantados(coords: list[tuple[float, float, float]]) -> list[bool]:
    """[pulgar, indice, medio, anular, menique]."""
    levantados = []
    for punta, mcp in zip(PUNTAS, MCPS):
        if punta == 4:
            levantado = coords[punta][0] < coords[mcp][0]
        else:
            levantado = coords[punta][1] < coords[mcp][1]
        levantados.append(levantado)
    return levantados


def clasificar_gesto(coords: list[tuple[float, float, float]]) -> Gesto:
    pulgar, indice, medio, anular, menique = dedos_levantados(coords)

    # G5 (solo pulgar) se comprueba antes que G3: ambos comparten
    # "indice/medio/anular/menique abajo", y solo el estado del pulgar los
    # distingue. Revisar G3 primero (como en el esbozo original del
    # documento de contexto) vuelve G5 inalcanzable.
    if pulgar and not any([indice, medio, anular, menique]):
        return Gesto.G5  # pulgar
    elif not any([indice, medio, anular, menique]):
        return Gesto.G3  # puno
    elif indice and not medio and not anular and not menique:
        return Gesto.G1  # 1 dedo
    elif indice and medio and not anular and not menique:
        return Gesto.G2  # 2 dedos
    elif all([pulgar, indice, medio, anular, menique]):
        return Gesto.G4  # mano abierta
    else:
        return Gesto.E  # reposo / gesto no reconocido (CLA-FR-004)
