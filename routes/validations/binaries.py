"""
Comandos relacionados con binarios.

- /version/<string:bin_name>: Obtiene la versión de un binario
- /exists/<string:bin_name>: Verifica si un binario existe
- /install/<string:package_name>: Instala un paquete del sistema

ejemplos:
- /version/python3
- /exists/ffmpeg
- /install/nmap
"""

# Librerias
import shlex
import re
from typing import Literal, Union
from flask import Blueprint, jsonify
from flask.wrappers import Response
from utils.utils import run_cmd, require_token

# Inicializa el blueprint
bp = Blueprint("binaries", __name__)


@bp.route("/version/<string:bin_name>")
def binary_version(
    bin_name: str
) -> Union[Response, tuple[Response, Union[Literal[400], Literal[404]]]]:
    """
    Obtiene la versión de un binario del sistema usando '--version'.

    :param bin_name: Nombre del comando (ej: git, python2, ffmpeg)
    :return type: Response
    """
    # Verifica el token
    require_token()

    # Verifica si los parametros son validos
    if not re.match(r"^[\w.-]+$", bin_name):
        return jsonify({
            "binary": bin_name,
            "error": "Nombre inválido"
        }), 400

    # Modifica el parametro para que sea seguro
    safe_bin: str = shlex.quote(bin_name)

    # Verifica si el binario existe
    exists: str = run_cmd(f"which {safe_bin}")

    # Si no existe, devuelve un error
    if exists == "error" or not exists:
        return jsonify({
            "binary": bin_name,
            "error": "El binario no está instalado o no está en $PATH"
        }), 404

    # Obtiene la versión
    version_output = run_cmd(f"{bin_name} --version 2>&1 | head -n 1")

    # Devuelve la respuesta
    return jsonify({
        "binary": bin_name,
        "version": version_output
    })


# @bp.route("/exists/<string:bin_name>")
# def binary_exists(bin_name: str) -> Response:
#     """
#     Verifica si un binario está disponible en el sistema ($PATH).

#     :param bin_name: Nombre del binario (ej: git, curl, ffmpeg)
#     :return type: Response
#     """
#     # Verifica si el binario existe
#     exists: str = run_cmd(f"command -v {bin_name}")

#     # Devuelve la respuesta
#     return jsonify({
#         "binary": bin_name,
#         "exists": bool(exists and exists != "error")
#     })


@bp.route("/exists/<string:bin_name>")
def binary_exists(bin_name: str) -> Union[Response, tuple[Response, Literal[400]]]:
    """
    Verifica si un binario está disponible en el sistema ($PATH).
    """
    # Verifica el token
    require_token()

    # Verifica si los parametros son validos
    if not re.match(r"^[\w.-]+$", bin_name):
        return jsonify({"error": "Nombre inválido"}), 400

    # Modifica el parametro para que sea seguro
    safe_bin = shlex.quote(bin_name)

    # Verifica si el binario existe
    result = run_cmd(f"command -v {safe_bin}")

    # Devuelve la respuesta
    return jsonify({
        "binary": bin_name,
        "exists": bool(result and result != "error")
    })


# @bp.route("/install/<string:package_name>", methods=["POST"])
# def install_package(package_name: str) -> Response:
#     """
#     Instala un paquete del sistema con apt.

#     :param package_name: Nombre del paquete (ej: nmap, curl, git)
#     :return type: Response
#     """
#     # Verifica si ya está instalado
#     installed: str = run_cmd(f"dpkg -s {package_name} | grep Status")

#     # Si ya estaba instalado, retorna notificando
#     if "installed" in installed:
#         return jsonify({
#             "package": package_name,
#             "status": "already installed"
#         })

#     # Instala el paquete
#     output: str = run_cmd(
#         f"sudo apt-get update && sudo apt-get install -y {package_name}"
#     )

#     # Devuelve la respuesta
#     return jsonify({
#         "package": package_name,
#         "status": "installed",
#         # las ultimas 10 lineas solamente
#         "output": output.splitlines()[-10:]
#     })


# @bp.route("/python2")
# def python2():
#     """
#     Obtiene la version de python2
#     """
#     return jsonify({
#         "python2": run_cmd("python2 --version 2>&1")
#     })

# @bp.route("/python3")
# def python3():
#     """
#     Obtiene la version de python3
#     """
#     return jsonify({
#         "python3": run_cmd("python3 --version 2>&1")
#     })
