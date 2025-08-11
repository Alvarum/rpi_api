"""
Comandos relacionados con el sistema.

- /os: Obtiene la versión del sistema operativo
- /uptime: Obtiene el tiempo de uso del sistema
- /kernel: Obtiene la versión del kernel
- /model: Obtiene el modelo del dispositivo
- /getall: Devuelve todos los anteriores
"""

# Librerias
from flask import Blueprint, jsonify
from utils.utils import run_cmd

# Inicializa el blueprint
bp = Blueprint("system", __name__)

# Mapeo de campos a comandos, mas pythoneano para
# dejar el codigo bonito
_SYSTEM_COMMANDS: dict[str, str] = {
    "os": "lsb_release -d | cut -f2",
    "uptime": "uptime -p",
    "kernel": "uname -r",
    "model": "cat /proc/device-tree/model"
}


def get_info(field: str) -> str:
    """
    Ejecuta el comando asociado a un campo del sistema.

    :param field: Campo solicitado (os, uptime, kernel, model)
    :type field: str
    :return: Resultado del comando como string
    :rtype: str
    """
    return run_cmd(_SYSTEM_COMMANDS[field])


@bp.route("/os")
def get_os():
    """
    Devuelve la descripción del sistema operativo.
    """
    return jsonify({"os": get_info("os")})


@bp.route("/uptime")
def get_uptime():
    """
    Devuelve el tiempo de uso desde el último reinicio.
    """
    return jsonify({"uptime": get_info("uptime")})


@bp.route("/kernel")
def get_kernel():
    """
    Devuelve la versión del kernel Linux.
    """
    return jsonify({"kernel": get_info("kernel")})


@bp.route("/model")
def get_model():
    """
    Devuelve el modelo del dispositivo (ej. Raspberry Pi).
    """
    return jsonify({"model": get_info("model")})


@bp.route("/getall")
def get_all():
    """
    Devuelve toda la información del sistema en un solo JSON.
    """
    return jsonify({k: get_info(k) for k in _SYSTEM_COMMANDS})
