from src.algebra.grupo_acciones import Accion, operacion_A

TODOS = list(Accion)


def test_clausura():
    for a1 in TODOS:
        for a2 in TODOS:
            assert operacion_A(a1, a2) in TODOS


def test_asociatividad():
    for a1 in TODOS:
        for a2 in TODOS:
            for a3 in TODOS:
                izquierda = operacion_A(operacion_A(a1, a2), a3)
                derecha = operacion_A(a1, operacion_A(a2, a3))
                assert izquierda == derecha


def test_identidad():
    for a in TODOS:
        assert operacion_A(Accion.A_E, a) == a
        assert operacion_A(a, Accion.A_E) == a


def test_inversos_existen():
    for a in TODOS:
        assert any(operacion_A(a, b) == Accion.A_E and operacion_A(b, a) == Accion.A_E for b in TODOS)


def test_conmutatividad():
    for a1 in TODOS:
        for a2 in TODOS:
            assert operacion_A(a1, a2) == operacion_A(a2, a1)
