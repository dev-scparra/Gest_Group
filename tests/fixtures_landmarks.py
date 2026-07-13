"""Generadores de landmarks sinteticos para tests de 006-clasificador-gestos.

Los fixtures previos colapsaban todos los MCP en el mismo punto (0.5, 0.6): bastaba
para la heuristica cruda `x_punta < x_mcp`, pero deja indefinido el eje de la palma
(menique -> indice) del que ahora depende la deteccion del pulgar (spec 012, D2). Se
construye una mano geometricamente plausible, con los nudillos separados.

Convencion base: mano "Right" en el frame ya espejado (CAP-FR-002), palma hacia la
camara, dedos hacia arriba. Con `lateralidad="Left"` se espeja el eje x (`x -> 1-x`),
que es exactamente lo que cambia entre una mano y la otra — y es la sonda con la que
se descubrio que el clasificador anterior intercambiaba G3 y G5 (PUL-FR-007).
"""

# (indice del MCP, x, y) para indice / medio / anular / menique.
# Los MCP de un dedo i son: MCP=i, PIP=i+1, DIP=i+2, PUNTA=i+3.
_DEDOS = [
    (5, 0.60, 0.60),   # indice (adyacente al pulgar: es el extremo "pulgar" de la palma)
    (9, 0.53, 0.58),   # medio
    (13, 0.46, 0.59),  # anular
    (17, 0.40, 0.62),  # menique (extremo opuesto al pulgar)
]

_MUNECA = (0.50, 0.90, 0.0)
_PULGAR_CMC = (0.60, 0.85, 0.0)
_PULGAR_MCP = (0.66, 0.78, 0.0)
_PULGAR_IP = (0.72, 0.72, 0.0)
_PULGAR_PUNTA_EXTENDIDA = (0.80, 0.66, 0.0)  # se aparta hacia el lado del pulgar
_PULGAR_PUNTA_PLEGADA = (0.56, 0.74, 0.0)    # cruza hacia la palma

_ALTURA_LEVANTADO = -0.25  # la punta sube (y decrece) respecto al MCP
_ALTURA_PLEGADO = 0.10     # la punta baja respecto al MCP


def generar_landmarks(
    pulgar: bool,
    indice: bool,
    medio: bool,
    anular: bool,
    menique: bool,
    lateralidad: str = "Right",
) -> list[tuple[float, float, float]]:
    landmarks: list[tuple[float, float, float]] = [(0.5, 0.5, 0.0)] * 21

    landmarks[0] = _MUNECA
    landmarks[1] = _PULGAR_CMC
    landmarks[2] = _PULGAR_MCP
    landmarks[3] = _PULGAR_IP
    landmarks[4] = _PULGAR_PUNTA_EXTENDIDA if pulgar else _PULGAR_PUNTA_PLEGADA

    for (mcp, x, y), levantado in zip(_DEDOS, [indice, medio, anular, menique]):
        desplazamiento = _ALTURA_LEVANTADO if levantado else _ALTURA_PLEGADO
        y_punta = y + desplazamiento
        landmarks[mcp] = (x, y, 0.0)
        landmarks[mcp + 1] = (x, y + desplazamiento * 0.4, 0.0)  # PIP
        landmarks[mcp + 2] = (x, y + desplazamiento * 0.7, 0.0)  # DIP
        landmarks[mcp + 3] = (x, y_punta, 0.0)                   # PUNTA

    if lateralidad == "Left":
        landmarks = [(1.0 - x, y, z) for (x, y, z) in landmarks]
    return landmarks


def generar_landmark_puno(lateralidad: str = "Right") -> list:
    return generar_landmarks(False, False, False, False, False, lateralidad)


def generar_landmark_un_dedo(lateralidad: str = "Right") -> list:
    return generar_landmarks(False, True, False, False, False, lateralidad)


def generar_landmark_dos_dedos(lateralidad: str = "Right") -> list:
    return generar_landmarks(False, True, True, False, False, lateralidad)


def generar_landmark_mano_abierta(lateralidad: str = "Right") -> list:
    return generar_landmarks(True, True, True, True, True, lateralidad)


def generar_landmark_pulgar(lateralidad: str = "Right") -> list:
    return generar_landmarks(True, False, False, False, False, lateralidad)


def generar_landmark_ambiguo_menique(lateralidad: str = "Right") -> list:
    """Solo el menique levantado: no calza ninguna regla explicita -> debe dar E."""
    return generar_landmarks(False, False, False, False, True, lateralidad)
