import random

import pytest

from src.preprocesamiento.filtro_ema import FiltroEMA


def test_convergencia_ema():
    """El filtro EMA debe converger al valor constante cuando x_raw es constante."""
    filtro = FiltroEMA(alpha=0.3)
    landmark_constante = [(0.5, 0.5, 0.0)] * 21

    resultado = filtro.aplicar(landmark_constante)
    for _ in range(200):
        resultado = filtro.aplicar(landmark_constante)

    for x, y, z in resultado:
        assert abs(x - 0.5) < 1e-6
        assert abs(y - 0.5) < 1e-6
        assert abs(z - 0.0) < 1e-6


def test_estabilidad_ruido():
    """El filtro EMA debe reducir la varianza del ruido."""
    random.seed(0)
    filtro = FiltroEMA(alpha=0.3)
    señal_ruidosa = [0.5 + random.gauss(0, 0.1) for _ in range(200)]

    señal_suavizada = []
    for x_raw in señal_ruidosa:
        landmark = [(x_raw, x_raw, x_raw)] * 21
        suavizado = filtro.aplicar(landmark)
        señal_suavizada.append(suavizado[0][0])

    var_cruda = sum((x - 0.5) ** 2 for x in señal_ruidosa) / len(señal_ruidosa)
    var_suav = sum((x - 0.5) ** 2 for x in señal_suavizada) / len(señal_suavizada)

    assert var_suav < var_cruda


def test_reset_limpia_historia():
    filtro = FiltroEMA(alpha=0.3)
    filtro.aplicar([(0.1, 0.1, 0.1)] * 21)
    filtro.aplicar([(0.9, 0.9, 0.9)] * 21)

    filtro.reset()
    nuevo_landmark = [(0.3, 0.4, 0.5)] * 21
    resultado = filtro.aplicar(nuevo_landmark)

    assert resultado == nuevo_landmark


def test_alpha_invalido_falla():
    with pytest.raises(ValueError):
        FiltroEMA(alpha=0.0)
    with pytest.raises(ValueError):
        FiltroEMA(alpha=1.0)
    with pytest.raises(ValueError):
        FiltroEMA(alpha=-0.1)
    with pytest.raises(ValueError):
        FiltroEMA(alpha=1.5)


def test_set_alpha_en_caliente_valida():
    filtro = FiltroEMA(alpha=0.3)
    filtro.set_alpha(0.5)
    assert filtro.alpha == 0.5
    with pytest.raises(ValueError):
        filtro.set_alpha(0)
