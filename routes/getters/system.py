"""
Comandos relacionados con el sistema.

- /os: Obtiene la version de la OS
- /uptime: Obtiene el tiempo de uso del sistema
- /kernel: Obtiene la version del kernel
- /model: Obtiene el modelo del dispositivo
"""

from flask import Blueprint, jsonify
from utils.utils import run_cmd, require_token

bp = Blueprint("system", __name__)

@bp.route("/os")
def get_os():
    """
    Obtiene la version de la OS
    """
    require_token()
    return jsonify({
        "os": run_cmd("lsb_release -d | cut -f2"),
    })

@bp.route("/uptime")
def get_uptime():
    """
    Obtiene el tiempo de uso del sistema
    """
    require_token()
    return jsonify({
        "uptime": run_cmd("uptime -p")
    })

@bp.route("/kernel")
def get_kernel():
    """
    Obtiene la version del kernel
    """
    require_token()
    return jsonify({
        "kernel": run_cmd("uname -r")
    })

@bp.route("/model")
def get_model():
    """
    Obtiene el modelo del dispositivo
    """
    require_token()
    return jsonify({
        "model": run_cmd("cat /proc/device-tree/model")
    })

@bp.route("/getall")
def get_all():
    require_token()
    return jsonify({
        "os": run_cmd("lsb_release -d | cut -f2"),
        "uptime": run_cmd("uptime -p"),
        "kernel": run_cmd("uname -r"),
        "model": run_cmd("cat /proc/device-tree/model")
    })
