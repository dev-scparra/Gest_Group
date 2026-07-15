"""Captura guiada de combos por votacion de mayoria (spec 015).

Reemplaza el disparo por ventana-de-tiempo de la spec 014 (`CombinadorGestos`) por
una maquina de estados guiada, orientada a que la composicion o de G se lea bien:

- El combo se arma con DOS gestos. Cada uno se captura durante una ventana fija de
  `frames_captura` frames y se resuelve por VOTACION DE MAYORIA sobre esa ventana. Asi,
  los frames de transicion entre un gesto y el siguiente (donde el clasificador titubea)
  quedan en minoria y no corrompen la lectura — que es justo lo que se buscaba.
- Entre el gesto 1 y el 2 hay una fase de ESPERA ("preparate") de `frames_espera` frames,
  para que el usuario cambie de gesto sin que esa transicion contamine la votacion del 2.
- Al cerrar el gesto 2 se calcula g1 o g2 (operacion_G, 001) y se emite `disparar` en UN
  solo frame (borde), para que 009 aplique phi y ejecute exactamente una vez.
- Tras mostrar el resultado `frames_resultado` frames, vuelve a INACTIVO y exige ver
  reposo (E) antes de armar un combo nuevo — evita encadenar combos sin querer.

Es frame-driven y puro: recibe UN gesto clasificado por frame (no lee reloj ni camara),
lo que lo hace determinista y testeable sin hardware. La ventana de la camara (008) usa
`EstadoCombo` para asistir al usuario: fase, gesto lider, conteo de votos, cuenta
regresiva y el resultado de la composicion.
"""

from collections import Counter
from dataclasses import dataclass, field
from enum import Enum

from src.algebra.grupo_gestos import Gesto, operacion_G


class FaseCombo(Enum):
    INACTIVO = "inactivo"          # esperando que aparezca un gesto (armado tras ver E)
    CAPTURANDO_G1 = "capturando_g1"
    ESPERA = "espera"              # "preparate para el gesto 2"
    CAPTURANDO_G2 = "capturando_g2"
    RESULTADO = "resultado"        # mostrando g1 o g2 = compuesto


@dataclass
class EstadoCombo:
    """Instantanea de la captura para que 008 dibuje el HUD y 009 sepa cuando disparar.

    `disparar` es != None SOLO en el frame en que se cierra el gesto 2 (borde): contiene
    el gesto compuesto g1 o g2 al que 009 debe aplicar phi y ejecutar una unica vez.
    """

    fase: FaseCombo
    frames_restantes: int = 0
    frames_total_fase: int = 0
    lider: Gesto | None = None                 # gesto que va ganando la votacion en curso
    conteo: list = field(default_factory=list)  # most_common(3): [(Gesto, votos), ...]
    g1: Gesto | None = None
    g2: Gesto | None = None
    compuesto: Gesto | None = None
    disparar: Gesto | None = None


class CapturadorCombo:
    def __init__(
        self,
        frames_captura: int = 20,
        frames_espera: int = 12,
        frames_resultado: int = 25,
    ):
        self.frames_captura = frames_captura
        self.frames_espera = frames_espera
        self.frames_resultado = frames_resultado

        self.fase = FaseCombo.INACTIVO
        self._votos: Counter = Counter()
        self._frames_en_fase = 0
        self._armado = True  # el primer gesto de la sesion puede arrancar un combo
        self.g1: Gesto | None = None
        self.g2: Gesto | None = None
        self.compuesto: Gesto | None = None

    def actualizar(self, gesto: Gesto) -> EstadoCombo:
        """Avanza un frame con el gesto clasificado y devuelve el estado del combo."""
        if self.fase == FaseCombo.INACTIVO:
            return self._paso_inactivo(gesto)
        if self.fase == FaseCombo.CAPTURANDO_G1:
            return self._paso_captura(gesto, slot=1)
        if self.fase == FaseCombo.ESPERA:
            return self._paso_espera()
        if self.fase == FaseCombo.CAPTURANDO_G2:
            return self._paso_captura(gesto, slot=2)
        return self._paso_resultado()  # RESULTADO

    def reset(self) -> None:
        """Vuelve a INACTIVO y DESARMA: exige ver reposo (E) antes de un combo nuevo."""
        self.fase = FaseCombo.INACTIVO
        self._votos = Counter()
        self._frames_en_fase = 0
        self._armado = False
        self.g1 = self.g2 = self.compuesto = None

    # --- pasos por fase ---

    def _paso_inactivo(self, gesto: Gesto) -> EstadoCombo:
        if gesto == Gesto.E:
            self._armado = True  # ver reposo re-arma
            return self._snapshot(FaseCombo.INACTIVO)
        if not self._armado:
            # Un gesto no-E pero aun sin re-armar (p. ej. justo tras un combo): se ignora
            # hasta que el usuario baje la mano. Evita encadenar combos sin querer.
            return self._snapshot(FaseCombo.INACTIVO)
        # Armado + gesto real: arranca la captura del gesto 1, contando este frame.
        self._armado = False
        self.fase = FaseCombo.CAPTURANDO_G1
        self._votos = Counter()
        self._frames_en_fase = 0
        self.g1 = self.g2 = self.compuesto = None
        return self._paso_captura(gesto, slot=1)

    def _paso_captura(self, gesto: Gesto, slot: int) -> EstadoCombo:
        self._votos[gesto] += 1
        self._frames_en_fase += 1

        if self._frames_en_fase < self.frames_captura:
            return self._snapshot(self.fase)

        ganador = self._votos.most_common(1)[0][0]
        if ganador == Gesto.E:
            # La mayoria fue reposo: el usuario no sostuvo un gesto -> cancela el combo.
            self.reset()
            return self._snapshot(FaseCombo.INACTIVO)

        if slot == 1:
            self.g1 = ganador
            self.fase = FaseCombo.ESPERA
            self._frames_en_fase = 0
            return self._snapshot(FaseCombo.ESPERA)

        self.g2 = ganador
        self.compuesto = operacion_G(self.g1, self.g2)  # o en vivo (001)
        self.fase = FaseCombo.RESULTADO
        self._frames_en_fase = 0
        return self._snapshot(FaseCombo.RESULTADO, disparar=self.compuesto)

    def _paso_espera(self) -> EstadoCombo:
        self._frames_en_fase += 1
        if self._frames_en_fase >= self.frames_espera:
            self.fase = FaseCombo.CAPTURANDO_G2
            self._votos = Counter()
            self._frames_en_fase = 0
            return self._snapshot(FaseCombo.CAPTURANDO_G2)
        return self._snapshot(FaseCombo.ESPERA)

    def _paso_resultado(self) -> EstadoCombo:
        self._frames_en_fase += 1
        if self._frames_en_fase >= self.frames_resultado:
            self.reset()  # desarma: hay que ver E para el proximo combo
            return self._snapshot(FaseCombo.INACTIVO)
        return self._snapshot(FaseCombo.RESULTADO)  # disparar=None: solo dispara una vez

    # --- construccion del snapshot ---

    def _snapshot(self, fase: FaseCombo, disparar: Gesto | None = None) -> EstadoCombo:
        if fase in (FaseCombo.CAPTURANDO_G1, FaseCombo.CAPTURANDO_G2):
            total = self.frames_captura
            conteo = self._votos.most_common(3)
            lider = conteo[0][0] if conteo else None
        elif fase == FaseCombo.ESPERA:
            total, conteo, lider = self.frames_espera, [], None
        elif fase == FaseCombo.RESULTADO:
            total, conteo, lider = self.frames_resultado, [], None
        else:  # INACTIVO
            total, conteo, lider = 0, [], None

        return EstadoCombo(
            fase=fase,
            frames_restantes=max(0, total - self._frames_en_fase),
            frames_total_fase=total,
            lider=lider,
            conteo=conteo,
            g1=self.g1,
            g2=self.g2,
            compuesto=self.compuesto,
            disparar=disparar,
        )
