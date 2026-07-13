from src.algebra.grupo_gestos import Gesto, operacion_G

TODOS = list(Gesto)

# Inversos genuinos (ALG-FR-004 revisado, ver docs/demostraciones.md Decision D1):
# no todos los elementos son autoinversos (imposible para |G|=6), solo E y G3.
INVERSOS = {
    Gesto.E: Gesto.E,
    Gesto.G1: Gesto.G5,
    Gesto.G2: Gesto.G4,
    Gesto.G3: Gesto.G3,
    Gesto.G4: Gesto.G2,
    Gesto.G5: Gesto.G1,
}


def test_clausura():
    for g1 in TODOS:
        for g2 in TODOS:
            assert operacion_G(g1, g2) in TODOS


def test_asociatividad():
    for g1 in TODOS:
        for g2 in TODOS:
            for g3 in TODOS:
                izquierda = operacion_G(operacion_G(g1, g2), g3)
                derecha = operacion_G(g1, operacion_G(g2, g3))
                assert izquierda == derecha


def test_identidad():
    for g in TODOS:
        assert operacion_G(Gesto.E, g) == g
        assert operacion_G(g, Gesto.E) == g


def test_inversos_genuinos():
    for g, inverso_esperado in INVERSOS.items():
        assert operacion_G(g, inverso_esperado) == Gesto.E
        assert operacion_G(inverso_esperado, g) == Gesto.E


def test_operar_con_clave_invalida_falla():
    import pytest

    with pytest.raises(KeyError):
        operacion_G(Gesto.E, None)
