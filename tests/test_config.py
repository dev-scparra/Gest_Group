from src.main import CONFIG_PATH, cargar_config


def test_carga_config_real_tiene_claves_y_tipos_esperados():
    config = cargar_config(CONFIG_PATH)

    assert isinstance(config["camara"]["id"], int)
    assert isinstance(config["camara"]["ancho"], int)
    assert isinstance(config["camara"]["alto"], int)
    assert isinstance(config["filtro_ema"]["alpha"], float)
    assert 0 < config["filtro_ema"]["alpha"] < 1
    assert isinstance(config["estabilizador"]["frames_estables"], int)
    assert isinstance(config["deteccion"]["min_detection_confidence"], float)
    assert isinstance(config["deteccion"]["min_tracking_confidence"], float)
    for clave in ("frames_captura", "frames_espera", "frames_resultado"):
        assert isinstance(config["combinador"][clave], int)
        assert config["combinador"][clave] > 0


def test_config_ausente_falla_explicito(tmp_path):
    import pytest

    ruta_falsa = tmp_path / "no_existe.yaml"
    with pytest.raises(FileNotFoundError):
        cargar_config(ruta_falsa)


def test_config_mal_formado_falla_explicito(tmp_path):
    import pytest

    ruta = tmp_path / "config_incompleta.yaml"
    ruta.write_text("camara:\n  id: 0\n")
    with pytest.raises(ValueError):
        cargar_config(ruta)


def test_config_sin_clave_combinador_falla_explicito(tmp_path):
    """INT-FR-010 / spec 015: la clave combinador es requerida (frames de captura de
    combos). Sin ella, cargar_config debe fallar al arrancar, no a mitad de sesion."""
    import pytest

    ruta = tmp_path / "config_sin_combinador.yaml"
    ruta.write_text(
        "camara:\n  id: 0\n  ancho: 640\n  alto: 480\n"
        "filtro_ema:\n  alpha: 0.3\n"
        "estabilizador:\n  frames_estables: 10\n"
        "deteccion:\n  min_detection_confidence: 0.7\n  min_tracking_confidence: 0.5\n"
    )
    with pytest.raises(ValueError):
        cargar_config(ruta)
