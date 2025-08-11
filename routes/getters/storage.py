"""
Comandos relacionados con almacenamiento.

- /total: Obtiene el espacio total de la memoria
- /used: Obtiene el espacio usado de la memoria
- /free: Obtiene el espacio libre de la memoria
- /get_all: Obtiene el espacio total, usado y libre
"""

from flask import Blueprint, jsonify
from utils.utils import run_cmd

# Inicializa el blueprint
bp = Blueprint("storage", __name__)


def get_storage_value(field: int) -> str:
    """
    Ejecuta `df -h /` y extrae una columna específica.

    :param field: Número de columna (2=total, 3=used, 4=free)
    :type field: int
    :return: Valor como string (ej: '3.5G')
    :rtype: str
    """
    return run_cmd(f"df -h / | awk 'NR==2{{print ${field}}}'")


@bp.route("/total")
def total():
    """
    Obtiene el espacio total de la memoria
    """
    return jsonify({"total": get_storage_value(2)})


@bp.route("/used")
def used():
    """
    Obtiene el espacio usado de la memoria
    """
    return jsonify({"used": get_storage_value(3)})


@bp.route("/free")
def free():
    """
    Obtiene el espacio libre de la memoria
    """
    return jsonify({"free": get_storage_value(4)})


@bp.route("/get_all")
def get_all():
    """
    Obtiene el espacio total, usado y libre de la memoria
    """
    return jsonify({
        "total": get_storage_value(2),
        "used": get_storage_value(3),
        "free": get_storage_value(4),
    })
