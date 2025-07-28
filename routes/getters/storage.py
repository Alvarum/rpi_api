"""
Comandos relacionados con almacenamiento.

- /total: Obtiene el espacio total de la memoria
- /used: Obtiene el espacio usado de la memoria
- /free: Obtiene el espacio libre de la memoria
- /get_all: Obtiene el espacio total, usado y libre
"""

# Importaciones
from flask import Blueprint, jsonify
from utils.shell import run_cmd


# Inicializa el blueprint de almacenamiento en la app de flask
bp = Blueprint("storage", __name__)


@bp.route("/total")
def total():
    """
    Obtiene el espacio total de la memoria
    """
    return jsonify({
        "total": run_cmd("df -h / | awk 'NR==2{print $2}'"),
    })


@bp.route("/used")
def used():
    """
    Obtiene el espacio usado de la memoria
    """
    return jsonify({
        "used": run_cmd("df -h / | awk 'NR==2{print $3}'"),
    })


@bp.route("/free")
def free():
    """
    Obtiene el espacio libre de la memoria
    """
    return jsonify({
        "free": run_cmd("df -h / | awk 'NR==2{print $4}'"),
    })


@bp.route("/get_all")
def get_all():
    """
    Obtiene el espacio total, usado y libre
    """
    return jsonify({
        "total": run_cmd("df -h / | awk 'NR==2{print $2}'"),
        "used": run_cmd("df -h / | awk 'NR==2{print $3}'"),
        "free": run_cmd("df -h / | awk 'NR==2{print $4}'"),
    })
