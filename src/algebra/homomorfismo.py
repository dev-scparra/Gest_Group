"""Homomorfismo phi: G -> A y sus propiedades derivadas (kernel, imagen, clases laterales).

No importa cv2/mediapipe/subprocess (NFR-G03, HOM-FR-010): esta capa es pura
y se prueba sin camara.
"""

from dataclasses import dataclass, field

from src.algebra.grupo_acciones import Accion, operacion_A
from src.algebra.grupo_gestos import Gesto, operacion_G

TABLA_PHI_DEFECTO: dict[Gesto, Accion] = {
    Gesto.E: Accion.A_E,
    Gesto.G1: Accion.A1,
    Gesto.G2: Accion.A2,
    Gesto.G3: Accion.A3,
    Gesto.G4: Accion.A4,
    Gesto.G5: Accion.A5,
}


@dataclass
class ReporteHomomorfismo:
    cumple: bool
    pares_fallidos: list = field(default_factory=list)


class Homomorfismo:
    """Implementa phi: G -> A como funcion total explicita sobre G."""

    def __init__(self, tabla_phi: dict[Gesto, Accion] | None = None):
        if tabla_phi is None:
            tabla_phi = dict(TABLA_PHI_DEFECTO)
        # HOM-FR-001 exige EXACTAMENTE las 6 claves de Gesto. Comprobar solo las
        # faltantes dejaba pasar claves espurias, que despues contaminaban imagen()
        # y kernel() con acciones que ningun gesto produce (CNF-FR-001).
        if set(tabla_phi) != set(Gesto):
            faltantes = set(Gesto) - set(tabla_phi)
            sobrantes = set(tabla_phi) - set(Gesto)
            raise ValueError(
                "tabla_phi debe tener exactamente las 6 claves de Gesto "
                f"(faltan: {faltantes or 'ninguna'}; sobran: {sobrantes or 'ninguna'})"
            )
        self.tabla_phi = tabla_phi

    def aplicar(self, gesto: Gesto) -> Accion:
        """phi(g)."""
        return self.tabla_phi[gesto]

    def kernel(self) -> set[Gesto]:
        """ker(phi) = {g in G : phi(g) = A_E}."""
        return {g for g, a in self.tabla_phi.items() if a == Accion.A_E}

    def imagen(self) -> set[Accion]:
        """Im(phi) = {phi(g) : g in G}."""
        return set(self.tabla_phi.values())

    def es_inyectiva(self) -> bool:
        """phi es inyectiva sii |ker(phi)| = 1."""
        return len(self.kernel()) == 1

    def es_sobreyectiva(self) -> bool:
        """phi es sobreyectiva sii Im(phi) = A."""
        return self.imagen() == set(Accion)

    def clases_laterales_kernel(self) -> dict[Accion, list[Gesto]]:
        """G/ker(phi): agrupa los gestos de G por la accion que producen."""
        clases: dict[Accion, list[Gesto]] = {}
        for g in Gesto:
            a = self.aplicar(g)
            clases.setdefault(a, []).append(g)
        return clases

    def verificar_homomorfismo(self) -> ReporteHomomorfismo:
        """Comprueba phi(g1 o g2) = phi(g1) o phi(g2) para los 36 pares de G x G."""
        pares_fallidos = []
        for g1 in Gesto:
            for g2 in Gesto:
                izquierda = self.aplicar(operacion_G(g1, g2))
                derecha = operacion_A(self.aplicar(g1), self.aplicar(g2))
                if izquierda != derecha:
                    pares_fallidos.append((g1, g2))
        return ReporteHomomorfismo(cumple=not pares_fallidos, pares_fallidos=pares_fallidos)
