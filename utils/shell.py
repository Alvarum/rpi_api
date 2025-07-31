import subprocess
from typing import Optional, List


def run_cmd(cmd: List[str], timeout: float = 5.0) -> Optional[str]:
    """
    Ejecuta un comando del sistema de forma segura (sin shell)
    y devuelve su salida como string.

    :param cmd: Lista de argumentos del comando.
    :param timeout: Tiempo máximo en segundos.
    :return: Salida del comando sin saltos de línea, o None si falla.
    """
    try:
        output = subprocess.check_output(
            cmd,
            stderr=subprocess.DEVNULL,
            timeout=timeout
        )
        return output.decode("utf-8").strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return "error"


# def run_cmd(cmd: str) -> str:
#     """
#     Ejecuta un comando en el sistema y retorna la salida como string.

#     :param cmd: Comando a ejecutar.
#     :return: Salida del comando sin saltos de línea.
#     """
#     try:
#         return subprocess.check_output(
#             cmd, shell=True, stderr=subprocess.DEVNULL
#         ).decode("utf-8").strip()
#     except subprocess.CalledProcessError:
#         return "error"
