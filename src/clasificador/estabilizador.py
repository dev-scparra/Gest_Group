"""Debounce de gestos: exige `frames_estables` frames consecutivos antes de confirmar.

Ver spec 006-clasificador-gestos, Sección de estabilización. Disparo único
por sostenimiento (CLA-FR-006); se reinicia al cambiar de gesto (CLA-FR-007).
"""

from src.algebra.grupo_gestos import Gesto


class EstabilizadorGesto:
    def __init__(self, frames_estables: int = 10):
        self.frames_estables = frames_estables
        self.gesto_actual = Gesto.E
        self.contador = 0
        self.gesto_ejecutado = False

    def actualizar(self, gesto_nuevo: Gesto) -> Gesto | None:
        """None si aun no se confirma; Gesto si se acaba de confirmar (edge, no nivel)."""
        if gesto_nuevo == self.gesto_actual:
            self.contador += 1
        else:
            self.gesto_actual = gesto_nuevo
            self.contador = 1
            self.gesto_ejecutado = False

        if self.contador >= self.frames_estables and not self.gesto_ejecutado:
            self.gesto_ejecutado = True
            return self.gesto_actual

        return None

    def reset(self) -> None:
        """Reinicia el estado (p. ej. al perder y recuperar la mano)."""
        self.gesto_actual = Gesto.E
        self.contador = 0
        self.gesto_ejecutado = False
