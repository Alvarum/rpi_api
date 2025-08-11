import hmac
import shlex
import subprocess
from os import environ
from typing import Literal, Union
from flask import request, abort

API_TOKEN = environ.get("API_TOKEN")

def require_token() -> None:
    """
    Autenticación por Bearer token en Authorization.

    - Formato esperado: "Authorization: Bearer <token>"
    - Comparación en tiempo constante para evitar timing attacks.
    """
    auth = request.headers.get("Authorization", "")
    parts = auth.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not API_TOKEN:
        abort(403)
    if not hmac.compare_digest(parts[1], API_TOKEN):
        abort(403)


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
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
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
