"""
Comandos relacionados con validaciones de archivos.

- /directory/<path:dir_path>: Verifica si un directorio existe
- /file/<path:file_path>: Verifica si un archivo existe
"""

from flask import Blueprint, Response, jsonify
from utils.shell import run_cmd

bp = Blueprint("validations", __name__)

@bp.route("/directory/<path:dir_path>")
def directory_exists(dir_path: str) -> Response:
    """
    Verifica si un directorio existe.

    :param dir_path: Ruta del directorio.
    :return: True si existe, False si no.
    """
    return jsonify({
        "exists": run_cmd(f"test -d '{dir_path}' && echo yes || echo no")
    })

@bp.route("/file/<path:file_path>")
def file_exists(file_path: str) -> Response:
    """
    Verifica si un archivo existe.

    :param file_path: Ruta del archivo.
    :return: True si existe, False si no.
    """
    return jsonify({
        "exists": run_cmd(f"test -f '{file_path}' && echo yes || echo no")
    })
