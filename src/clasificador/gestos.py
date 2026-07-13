"""Clasificador geometrico: 21 landmarks suavizados -> elemento g in G.

Ver spec 006-clasificador-gestos y spec 012 (Decision D2). Heuristica de "dedo
levantado" por comparacion punta-vs-MCP en el eje y para indice/medio/anular/
menique; el pulgar, cuyo movimiento es lateral, se resuelve proyectando sobre el
eje de la palma en vez de comparar la x cruda (ver `_pulgar_levantado`).
"""

import math

from src.algebra.grupo_gestos import Gesto

PUNTAS = [4, 8, 12, 16, 20]
MCPS = [2, 5, 9, 13, 17]

PULGAR_PUNTA, PULGAR_MCP = 4, 2
INDICE_MCP, MENIQUE_MCP = 5, 17

# Fraccion del ancho de la palma que la punta del pulgar debe apartarse de su MCP,
# hacia el lado del pulgar, para contar como levantado. Da histeresis a la frontera
# G3 (puno) / G5 (pulgar), que sin margen queda a un pixel de distancia: en un puno
# natural el pulgar se pliega sobre los dedos y la proyeccion ronda el cero
# (PUL-FR-005). Es relativo al ancho de la palma, asi que no depende de la distancia
# de la mano a la camara.
UMBRAL_PULGAR = 0.15


def _pulgar_levantado(coords: list[tuple[float, float, float]]) -> bool:
    """True si la punta del pulgar se aparta de su MCP hacia el lado del pulgar.

    La comparacion cruda `x_punta < x_mcp` del documento de contexto solo es valida
    para UNA de las dos manos: el pulgar de una mano se extiende hacia +x y el de la
    otra hacia -x, asi que con la mano contraria el signo se invierte y G3/G5 se
    intercambian silenciosamente (spec 012, Seccion 1).

    En vez de condicionar el signo a la lateralidad reportada por MediaPipe, se
    deriva de la geometria de la propia mano: el vector del MCP del menique (17) al
    MCP del indice (5) recorre los nudillos y apunta, por anatomia, hacia el lado del
    pulgar. Proyectar (punta - MCP) del pulgar sobre ese eje da un signo que no
    depende de que mano sea, de si el frame esta espejado (CAP-FR-002), ni de la
    rotacion de la mano en el plano. Normalizar por el ancho de la palma lo vuelve
    ademas independiente de la escala.
    """
    eje_x = coords[INDICE_MCP][0] - coords[MENIQUE_MCP][0]
    eje_y = coords[INDICE_MCP][1] - coords[MENIQUE_MCP][1]
    ancho_palma = math.hypot(eje_x, eje_y)
    if ancho_palma < 1e-9:
        # Palma degenerada (landmarks corruptos): no adivinar, degradar a "abajo",
        # que lleva a la familia {G3, G1, G2} en vez de a un G4/G5 espurio.
        return False

    dx = coords[PULGAR_PUNTA][0] - coords[PULGAR_MCP][0]
    dy = coords[PULGAR_PUNTA][1] - coords[PULGAR_MCP][1]
    proyeccion = (dx * eje_x + dy * eje_y) / ancho_palma  # sobre el eje unitario

    return proyeccion / ancho_palma > UMBRAL_PULGAR  # relativa al ancho de la palma


def dedos_levantados(coords: list[tuple[float, float, float]]) -> list[bool]:
    """[pulgar, indice, medio, anular, menique]."""
    levantados = [_pulgar_levantado(coords)]
    for punta, mcp in zip(PUNTAS[1:], MCPS[1:]):
        # y crece hacia abajo en la imagen: punta mas arriba que el MCP = levantado.
        levantados.append(coords[punta][1] < coords[mcp][1])
    return levantados


def clasificar_gesto(coords: list[tuple[float, float, float]]) -> Gesto:
    """Tabla desambiguada de spec 012, Seccion 4. Se evalua en orden: gana la primera.

    | Pulgar | Ind | Med | Anu | Men | Gesto              |
    |--------|-----|-----|-----|-----|--------------------|
    |   T    |  F  |  F  |  F  |  F  | G5 (pulgar)        |
    |   F    |  F  |  F  |  F  |  F  | G3 (puno)          |
    |   -    |  T  |  F  |  F  |  F  | G1 (1 dedo)        |
    |   -    |  T  |  T  |  F  |  F  | G2 (2 dedos)       |
    |   T    |  T  |  T  |  T  |  T  | G4 (mano abierta)  |
    | cualquier otra combinacion     | E  (reposo)        |

    La tabla de la Seccion 4.5 del documento de contexto declara el pulgar como
    indiferente en la fila de G3, lo que hace de G5 un caso particular de G3 y deja
    a G5 inalcanzable (PUL-FR-004). Aqui G5 se comprueba primero y G3 exige pulgar
    abajo de forma explicita.
    """
    pulgar, indice, medio, anular, menique = dedos_levantados(coords)
    otros_abajo = not any([indice, medio, anular, menique])

    if pulgar and otros_abajo:
        return Gesto.G5  # pulgar
    if otros_abajo:
        return Gesto.G3  # puno
    if indice and not medio and not anular and not menique:
        return Gesto.G1  # 1 dedo
    if indice and medio and not anular and not menique:
        return Gesto.G2  # 2 dedos
    if all([pulgar, indice, medio, anular, menique]):
        return Gesto.G4  # mano abierta
    return Gesto.E  # reposo / gesto no reconocido (CLA-FR-004)
