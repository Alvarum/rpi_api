"""
Utilidades de la aplicación
"""
# Librerias
import subprocess
from os import environ
#from typing import Optional, List, Union
from flask import request, abort
from dotenv import load_dotenv

# Carga las variables de entorno
load_dotenv()

# Obtiene las variables de entorno requeridas por la API
API_TOKEN = environ.get("API_TOKEN")

# def run_cmd(cmd: Union[List[str], str], timeout: float = 5.0) -> Optional[str]:
#     """
#     Ejecuta un comando del sistema de forma segura (sin shell)
#     y devuelve su salida como string.

#     :param cmd: Lista de argumentos del comando.
#     :param timeout: Tiempo máximo en segundos.
#     :return: Salida del comando sin saltos de línea, o None si falla.
#     """
#     try:
#         output = subprocess.check_output(
#             cmd,
#             stderr=subprocess.DEVNULL,
#             timeout=timeout
#         )
#         return output.decode("utf-8").strip()
#     except (
#         subprocess.CalledProcessError,
#         subprocess.TimeoutExpired,
#         FileNotFoundError
#     ):
#         return "error"


def require_token():
    """
    Función de autenticación.

    lee el header "X-API-TOKEN" del request y compara con la variable
    de entorno, si no son iguales aborta la operación
    """
    if request.headers.get("Authorization") != f"Bearer {API_TOKEN}":
        abort(403)

    # if request.headers.get("X-API-TOKEN") != API_TOKEN:
    #     abort(403)
    # else:
    #     return


def run_cmd(cmd: str) -> str:
    """
    Ejecuta un comando en el sistema y retorna la salida como string.

    :param cmd: Comando a ejecutar.
    :return: Salida del comando o "error" si falla.
    """
    try:
        return subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
    except subprocess.CalledProcessError:
        return "error"

def run_cmd_raiser(cmd: str) -> str:
    """
    Ejecuta un comando en el sistema y retorna la salida como string.

    :param cmd: Comando a ejecutar.
    :return: Salida del comando o "error" si falla.
    """
    # pylint: disable=W0719
    try:
        return subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
    except Exception as e:
        raise Exception from e
