"""Filtro EMA: x[n] = alpha*x_raw[n] + (1-alpha)*x[n-1], aplicado a los 21 landmarks.

Ver spec 005-filtro-ema. Estabilidad asintotica para alpha en (0,1): la
solucion homogenea x_h[n] = C*(1-alpha)^n converge a 0 (Demostracion 4,
docs/demostraciones.md).
"""


class FiltroEMA:
    def __init__(self, alpha: float = 0.3, num_landmarks: int = 21):
        self._validar_alpha(alpha)
        self.alpha = alpha
        self.num_landmarks = num_landmarks
        self.x_prev: list[tuple[float, float, float]] | None = None

    @staticmethod
    def _validar_alpha(alpha: float) -> None:
        if not (0 < alpha < 1):
            raise ValueError(f"alpha debe estar en (0,1), se recibio: {alpha}")

    def set_alpha(self, alpha: float) -> None:
        """Permite ajustar alpha en caliente (EMA-FR-005, US-4)."""
        self._validar_alpha(alpha)
        self.alpha = alpha

    def aplicar(
        self, landmarks_raw: list[tuple[float, float, float]]
    ) -> list[tuple[float, float, float]]:
        if self.x_prev is None:
            self.x_prev = list(landmarks_raw)
            return self.x_prev

        coords_suav = []
        for (x_raw, y_raw, z_raw), (x_prev, y_prev, z_prev) in zip(
            landmarks_raw, self.x_prev
        ):
            x_s = self.alpha * x_raw + (1 - self.alpha) * x_prev
            y_s = self.alpha * y_raw + (1 - self.alpha) * y_prev
            z_s = self.alpha * z_raw + (1 - self.alpha) * z_prev
            coords_suav.append((x_s, y_s, z_s))

        self.x_prev = coords_suav
        return coords_suav

    def reset(self) -> None:
        """Limpia la historia. Debe llamarse cuando 004 devuelve None (EMA-FR-003)."""
        self.x_prev = None
