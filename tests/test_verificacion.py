from src.algebra.grupo_acciones import Accion, operacion_A
from src.algebra.grupo_gestos import Gesto, operacion_G
from src.algebra.verificacion import verificar_axiomas_grupo


def test_verificacion_sobre_G():
    reporte = verificar_axiomas_grupo(set(Gesto), operacion_G, Gesto.E)
    assert reporte.clausura
    assert reporte.asociatividad
    assert reporte.identidad
    assert reporte.inversos
    assert reporte.es_grupo


def test_verificacion_sobre_A():
    reporte = verificar_axiomas_grupo(set(Accion), operacion_A, Accion.A_E)
    assert reporte.es_grupo


def test_tabla_rota_sin_inverso_se_detecta():
    elementos = {"e", "x", "y"}

    # Tabla rota a proposito: "x" no tiene inverso.
    tabla = {
        ("e", "e"): "e", ("e", "x"): "x", ("e", "y"): "y",
        ("x", "e"): "x", ("x", "x"): "x", ("x", "y"): "y",
        ("y", "e"): "y", ("y", "x"): "y", ("y", "y"): "e",
    }

    def operacion(a, b):
        return tabla[(a, b)]

    reporte = verificar_axiomas_grupo(elementos, operacion, "e")
    assert not reporte.es_grupo
    assert not reporte.inversos
    assert "x" in reporte.fallos_inversos
    # Los demas axiomas no deben reportarse rotos solo porque el de inversos lo esta.
    assert reporte.clausura
    assert reporte.identidad
