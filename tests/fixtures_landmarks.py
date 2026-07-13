"""Generadores de landmarks sinteticos para tests de 006-clasificador-gestos.

Solo se rellenan con precision los indices que `dedos_levantados()` realmente
lee (PUNTAS=[4,8,12,16,20], MCPS=[2,5,9,13,17]); el resto se deja en un
placeholder neutro ya que no participa en la clasificacion.
"""

NEUTRO = (0.5, 0.5, 0.0)


def _landmarks_base() -> list:
    return [NEUTRO for _ in range(21)]


def _fijar_dedo(landmarks: list, punta_idx: int, mcp_idx: int, levantado: bool, es_pulgar: bool = False) -> None:
    if es_pulgar:
        # Pulgar: se compara el eje x (CLA-FR-002).
        landmarks[mcp_idx] = (0.5, 0.5, 0.0)
        landmarks[punta_idx] = (0.3, 0.5, 0.0) if levantado else (0.7, 0.5, 0.0)
    else:
        # Resto de dedos: se compara el eje y (CLA-FR-001); y menor = mas arriba.
        landmarks[mcp_idx] = (0.5, 0.6, 0.0)
        landmarks[punta_idx] = (0.5, 0.3, 0.0) if levantado else (0.5, 0.8, 0.0)


def generar_landmarks(pulgar: bool, indice: bool, medio: bool, anular: bool, menique: bool) -> list:
    landmarks = _landmarks_base()
    _fijar_dedo(landmarks, 4, 2, pulgar, es_pulgar=True)
    _fijar_dedo(landmarks, 8, 5, indice)
    _fijar_dedo(landmarks, 12, 9, medio)
    _fijar_dedo(landmarks, 16, 13, anular)
    _fijar_dedo(landmarks, 20, 17, menique)
    return landmarks


def generar_landmark_puno() -> list:
    return generar_landmarks(False, False, False, False, False)


def generar_landmark_un_dedo() -> list:
    return generar_landmarks(False, True, False, False, False)


def generar_landmark_dos_dedos() -> list:
    return generar_landmarks(False, True, True, False, False)


def generar_landmark_mano_abierta() -> list:
    return generar_landmarks(True, True, True, True, True)


def generar_landmark_pulgar() -> list:
    return generar_landmarks(True, False, False, False, False)


def generar_landmark_ambiguo_menique() -> list:
    """Solo el menique levantado: no calza ninguna regla explicita -> debe dar E."""
    return generar_landmarks(False, False, False, False, True)
