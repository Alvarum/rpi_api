"""
Comandos relacionados con validaciones de archivos.

- /directory/<path:dir_path>: Verifica si un directorio existe
- /file/<path:file_path>: Verifica si un archivo existe
"""

import os
from typing import Literal, Union
from flask import Blueprint, Response, jsonify
from utils.utils import require_token

bp: Blueprint = Blueprint("validations", __name__)

# Rutas no autorizadas
NOT_AUTHORIZED_PATHS: list[str] = [
    "/",
]

# region aux
def is_safe_path(path: str) -> bool:
    """
    Verifica que la ruta no esté explícitamente bloqueada ni escape del cwd.
    """
    resolved = os.path.abspath(path)
    if resolved in NOT_AUTHORIZED_PATHS:
        return False
    return True


@bp.route("/directory/<path:dir_path>")
def directory_exists(dir_path: str) -> Union[Response, tuple[Response, Literal[400]]]:
    """
    Verifica si un directorio existe.

    :param dir_path: Ruta del directorio relativa a CWD del servidor.
    :return: True si existe, False si no.
    """

    # Verifica el token
    require_token()

    # Verifica si la ruta es válida
    if not dir_path or len(dir_path) > 1024 or "\x00" in dir_path:
        return jsonify({
            "error": "Ruta inválida"
        }), 400

    # Verifica si la ruta es segura
    if not is_safe_path(dir_path):
        return jsonify({
            "exists": False,
            "error": "Ruta no autorizada"
        })

    # Hace que el path sea absoluto
    safe_path: str = os.path.abspath(dir_path)

    # Verifica si el directorio existe
    exists: bool = os.path.isdir(safe_path)

    # Devuelve la respuesta
    return jsonify({"exists": exists})


@bp.route("/file/<path:file_path>")
def file_exists(file_path: str) -> Union[Response, tuple[Response, Literal[400]]]:
    """
    Verifica si un archivo existe.

    :param file_path: Ruta del archivo relativa o absoluta.
    :return: True si existe, False si no.
    """
    # Verifica el token
    require_token()

    # Verifica si la ruta es válida
    if not file_path or len(file_path) > 1024 or "\x00" in file_path:
        return jsonify({"error": "Ruta inválida"}), 400

    # Verifica si la ruta es segura
    if not is_safe_path(file_path):
        return jsonify({
            "exists": False,
            "error": "Ruta no autorizada"
        })

    # Hace que el path sea absoluto
    safe_path: str = os.path.abspath(file_path)

    # Verifica si el archivo existe
    exists: bool = os.path.isfile(safe_path)

    # Devuelve la respuesta
    return jsonify({"exists": exists})
