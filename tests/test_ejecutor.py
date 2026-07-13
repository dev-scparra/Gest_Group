import subprocess
from unittest.mock import MagicMock, patch

from src.acciones.ejecutor import (
    TIMEOUT_SUBPROCESS_S,
    VK_MEDIA_NEXT_TRACK,
    VK_MEDIA_PLAY_PAUSE,
    VK_MEDIA_PREV_TRACK,
    VK_VOLUME_DOWN,
    VK_VOLUME_UP,
    ejecutar_accion,
)
from src.algebra.grupo_acciones import Accion


@patch("src.acciones.ejecutor.subprocess.run")
def test_accion_identidad_no_invoca_subprocess(mock_run):
    resultado = ejecutar_accion(Accion.A_E)
    mock_run.assert_not_called()
    assert resultado.exito is True


@patch("src.acciones.ejecutor.platform.system", return_value="Darwin")
@patch("src.acciones.ejecutor.subprocess.run")
def test_macos_subir_volumen(mock_run, mock_system):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    resultado = ejecutar_accion(Accion.A1)
    assert resultado.exito is True
    comando = mock_run.call_args[0][0]
    assert comando[0] == "osascript"
    assert "output volume" in comando[2] and "+ 10" in comando[2]


@patch("src.acciones.ejecutor.platform.system", return_value="Darwin")
@patch("src.acciones.ejecutor.subprocess.run")
def test_macos_bajar_volumen(mock_run, mock_system):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    ejecutar_accion(Accion.A2)
    comando = mock_run.call_args[0][0]
    assert comando[0] == "osascript"
    assert "output volume" in comando[2] and "- 10" in comando[2]


@patch("src.acciones.ejecutor.platform.system", return_value="Darwin")
@patch("src.acciones.ejecutor.subprocess.run")
def test_macos_pausa_play(mock_run, mock_system):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    ejecutar_accion(Accion.A3)
    comando = mock_run.call_args[0][0]
    assert comando[0] == "osascript"
    assert "key code 49" in comando[2]


@patch("src.acciones.ejecutor.platform.system", return_value="Darwin")
@patch("src.acciones.ejecutor.subprocess.run")
def test_macos_siguiente_pista(mock_run, mock_system):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    ejecutar_accion(Accion.A4)
    comando = mock_run.call_args[0][0]
    assert "key code 124 using command down" in comando[2]


@patch("src.acciones.ejecutor.platform.system", return_value="Darwin")
@patch("src.acciones.ejecutor.subprocess.run")
def test_macos_pista_anterior(mock_run, mock_system):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    ejecutar_accion(Accion.A5)
    comando = mock_run.call_args[0][0]
    assert "key code 123 using command down" in comando[2]


@patch("src.acciones.ejecutor.platform.system", return_value="Darwin")
@patch("src.acciones.ejecutor.subprocess.run")
def test_macos_fallo_subprocess_reporta_no_exito(mock_run, mock_system):
    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error simulado")
    resultado = ejecutar_accion(Accion.A1)
    assert resultado.exito is False
    assert resultado.mensaje == "error simulado"


@patch("src.acciones.ejecutor.platform.system", return_value="Linux")
@patch("src.acciones.ejecutor.subprocess.run")
def test_linux_volumen(mock_run, mock_system):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    resultado = ejecutar_accion(Accion.A1)
    assert resultado.exito is True
    comando = mock_run.call_args[0][0]
    assert comando[0] == "amixer"


@patch("src.acciones.ejecutor.platform.system", return_value="Linux")
@patch("src.acciones.ejecutor.subprocess.run")
def test_linux_accion_no_soportada_no_invoca_subprocess(mock_run, mock_system):
    resultado = ejecutar_accion(Accion.A3)
    mock_run.assert_not_called()
    assert resultado.exito is False


# --- Spec 010: fallos del binario de SO (ROB-FR-001..003, ROB-FR-005) ---
#
# Estos tests parchean subprocess.run con `side_effect` (una excepcion), no con
# `return_value` (un objeto con returncode). Un mock que solo devuelve returncode
# no puede alcanzar el camino de "el binario no existe", que es precisamente el
# caso borde que 007/spec.md Seccion 5 declara obligatorio.


@patch("src.acciones.ejecutor.platform.system", return_value="Linux")
@patch("src.acciones.ejecutor.subprocess.run", side_effect=FileNotFoundError("amixer"))
def test_binario_ausente_reporta_fallo_sin_excepcion(mock_run, mock_system):
    resultado = ejecutar_accion(Accion.A1)
    assert resultado.exito is False
    assert "amixer" in resultado.mensaje
    assert "alsa-utils" in resultado.mensaje


@patch("src.acciones.ejecutor.platform.system", return_value="Darwin")
@patch(
    "src.acciones.ejecutor.subprocess.run",
    side_effect=subprocess.TimeoutExpired(cmd="osascript", timeout=TIMEOUT_SUBPROCESS_S),
)
def test_timeout_reporta_fallo(mock_run, mock_system):
    resultado = ejecutar_accion(Accion.A3)
    assert resultado.exito is False
    assert "timeout" in resultado.mensaje


@patch("src.acciones.ejecutor.platform.system", return_value="Darwin")
@patch("src.acciones.ejecutor.subprocess.run", side_effect=PermissionError("denegado"))
def test_permission_error_reporta_fallo(mock_run, mock_system):
    resultado = ejecutar_accion(Accion.A1)
    assert resultado.exito is False
    assert "osascript" in resultado.mensaje


@patch("src.acciones.ejecutor.platform.system", return_value="Darwin")
@patch("src.acciones.ejecutor.subprocess.run")
def test_run_pasa_timeout_a_subprocess(mock_run, mock_system):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    ejecutar_accion(Accion.A1)
    assert mock_run.call_args.kwargs["timeout"] == TIMEOUT_SUBPROCESS_S


@patch("src.acciones.ejecutor._enviar_tecla_virtual")
@patch("src.acciones.ejecutor.platform.system", return_value="Windows")
def test_windows_paridad_completa_vk_codes(mock_system, mock_enviar):
    mapeo = {
        Accion.A1: VK_VOLUME_UP,
        Accion.A2: VK_VOLUME_DOWN,
        Accion.A3: VK_MEDIA_PLAY_PAUSE,
        Accion.A4: VK_MEDIA_NEXT_TRACK,
        Accion.A5: VK_MEDIA_PREV_TRACK,
    }
    for accion, vk_esperado in mapeo.items():
        mock_enviar.reset_mock()
        resultado = ejecutar_accion(accion)
        mock_enviar.assert_called_once_with(vk_esperado)
        assert resultado.exito is True
