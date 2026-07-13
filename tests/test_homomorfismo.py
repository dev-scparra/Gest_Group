import pytest

from src.algebra.grupo_acciones import Accion
from src.algebra.grupo_gestos import Gesto
from src.algebra.homomorfismo import Homomorfismo


def test_phi_mapea_identidad_a_identidad():
    phi = Homomorfismo()
    assert phi.aplicar(Gesto.E) == Accion.A_E


def test_kernel_contiene_solo_identidad():
    phi = Homomorfismo()
    assert phi.kernel() == {Gesto.E}


def test_phi_es_inyectiva():
    phi = Homomorfismo()
    assert phi.es_inyectiva()


def test_imagen_es_A_completo():
    phi = Homomorfismo()
    assert phi.imagen() == set(Accion)


def test_primer_teorema_isomorfismo():
    phi = Homomorfismo()
    clases = phi.clases_laterales_kernel()
    assert len(clases) == len(phi.imagen())


def test_verificar_homomorfismo_sobre_cayley():
    phi = Homomorfismo()
    reporte = phi.verificar_homomorfismo()
    assert reporte.cumple
    assert reporte.pares_fallidos == []


def test_tabla_custom_con_kernel_no_trivial():
    tabla = {
        Gesto.E: Accion.A_E,
        Gesto.G1: Accion.A1,
        Gesto.G2: Accion.A2,
        Gesto.G3: Accion.A1,  # G3 tambien mapea a A1 -> mismo tipo de clase que G1
        Gesto.G4: Accion.A4,
        Gesto.G5: Accion.A5,
    }
    phi = Homomorfismo(tabla)
    assert phi.kernel() == {Gesto.E}
    clases = phi.clases_laterales_kernel()
    assert len(clases[Accion.A1]) == 2
    assert set(clases[Accion.A1]) == {Gesto.G1, Gesto.G3}


def test_tabla_constante_a_identidad():
    tabla = {g: Accion.A_E for g in Gesto}
    phi = Homomorfismo(tabla)
    assert phi.kernel() == set(Gesto)
    assert not phi.es_sobreyectiva()
    assert not phi.es_inyectiva()


def test_tabla_incompleta_falla_en_constructor():
    tabla_incompleta = {Gesto.E: Accion.A_E, Gesto.G1: Accion.A1}
    with pytest.raises(ValueError):
        Homomorfismo(tabla_incompleta)


def test_tabla_con_clave_espuria_falla_en_constructor():
    """HOM-FR-001 exige EXACTAMENTE las 6 claves de Gesto. Comprobar solo las
    faltantes dejaba construir una tabla con basura, e imagen() devolvia entonces
    acciones que ningun gesto produce (CNF-FR-001)."""
    tabla = {g: Accion.A1 for g in Gesto}
    tabla["no_soy_un_gesto"] = Accion.A5

    with pytest.raises(ValueError, match="sobran"):
        Homomorfismo(tabla)
