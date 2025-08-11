import hmac
import shlex
import subprocess
from os import environ
from typing import Final, Literal, Union
from flask import request, abort

# Validacion del token
API_TOKEN: Final[str] = environ.get("API_TOKEN", "").strip()
if not API_TOKEN:
    # Si no lo pilla, falla de una
    raise RuntimeError("API_TOKEN no definido en el entorno.")


def require_token() -> None:
    """
    Exige *Bearer token* en el header ``Authorization``.

    Formato requerido:
        ``Authorization: Bearer <token>``

    :raises werkzeug.exceptions.Forbidden:
        Si falta el header/esquema, o el token no coincide.
    """
    # Obtiene el header (puede venir vacío si no lo enviaron)
    auth_header: str = request.headers.get("Authorization", "")

    # Divide en esquema y token. ``split(None, 1)`` usa cualquier
    # whitespace, robusto ante "Bearer    <token>".
    parts = auth_header.split(None, 1)

    # Valida formato mínimo: "Bearer <token>"
    if len(parts) != 2 or parts[0].lower() != "bearer":
        abort(403)

    presented: str = parts[1].strip()
    if not presented:
        abort(403)

    # Comparación en tiempo constante
    # Evita timing attacks
    if not hmac.compare_digest(presented, API_TOKEN):
        abort(403)

    # Si pasa, no retornamos nada (HTTP continúa)
    return None


def run_cmd(cmd: str, timeout: float = 5.0) -> Union[str, Literal["error"]]:
    """
    Ejecuta un comando de forma segura (sin shell).

    :param cmd: Comando completo en una cadena (se separa con shlex).
    :param timeout: Tiempo máximo (s).
    :returns: Salida o "error".
    """
    try:
        out = subprocess.check_output(
            shlex.split(cmd),
            stderr=subprocess.DEVNULL,
            timeout=timeout,
        )
        return out.decode("utf-8").strip()
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError
    ):
        return "error"


def run_cmd_raiser(cmd: str, timeout: float = 5.0) -> str:
    """
    Igual que `run_cmd`, pero deja propagar la excepción para manejo upstream.
    """
    out = subprocess.check_output(
        shlex.split(cmd),
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    return out.decode("utf-8").strip()
