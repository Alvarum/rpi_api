import subprocess

def run_cmd(cmd: str) -> str:
    """
    Ejecuta un comando en el sistema y retorna la salida como string.

    :param cmd: Comando a ejecutar.
    :return: Salida del comando sin saltos de línea.
    """
    try:
        return subprocess.check_output(
            cmd, shell=True, stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
    except subprocess.CalledProcessError:
        return "error"
