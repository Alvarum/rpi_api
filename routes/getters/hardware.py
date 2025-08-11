"""
Consultas relacionadas con información de hardware.

- /cpu_usage: Uso actual de CPU en porcentaje
- /temp: Temperatura del sistema (°C)
- /ram: RAM usada/total
- /cpu_cores: Número de núcleos
- /cpu_freq: Frecuencia actual de CPU
- /getall: Todos los datos anteriores en una sola respuesta
"""

# Librerias
from flask import Blueprint, jsonify
from utils.utils import run_cmd, require_token

# Inicializa el blueprint
bp = Blueprint("hardware", __name__)

# Mapeo de campos a comandos, mas pythoneano para
# dejar el codigo wonito
_HARDWARE_COMMANDS: dict[str, str] = {
    "cpu_usage":
        "top -bn1 | grep 'Cpu(s)' | awk '{print $2+$4}'",
    "temp":
        "cat /sys/class/thermal/thermal_zone0/temp | awk '{print $1/1000}'",
    "ram":
        "free -h | grep Mem | awk '{print $3\"/\"$2}'",
    "cpu_cores": "nproc",
    "cpu_freq":
        "lscpu | grep 'MHz' | awk '{print $NF}'"
}


def get_info(field: str) -> str:
    """
    Ejecuta el comando asociado a una métrica de hardware.

    :param field: Campo (cpu_usage, temp, etc.)
    :type field: str
    :return: Resultado en string plano
    :rtype: str
    """
    return run_cmd(_HARDWARE_COMMANDS[field])


@bp.route("/cpu_usage")
def cpu_usage():
    """
    Devuelve el uso actual de CPU en porcentaje.
    """
    require_token()
    return jsonify({"cpu_usage": get_info("cpu_usage")})


@bp.route("/temp")
def temperature():
    """
    Devuelve la temperatura actual del sistema en °C.
    """
    require_token()
    return jsonify({"temp": get_info("temp")})


@bp.route("/ram")
def ram():
    """
    Devuelve la memoria RAM usada/total en formato legible.
    """
    require_token()
    return jsonify({"ram": get_info("ram")})


@bp.route("/cpu_cores")
def cpu_cores():
    """
    Devuelve el número total de núcleos del procesador.
    """
    require_token()
    return jsonify({"cpu_cores": get_info("cpu_cores")})


@bp.route("/cpu_freq")
def cpu_freq():
    """
    Devuelve la frecuencia actual del procesador (MHz).
    """
    require_token()
    return jsonify({"cpu_freq": get_info("cpu_freq")})


@bp.route("/getall")
def get_all():
    """
    Devuelve todos los recursos de hardware en una sola respuesta.
    """
    require_token()
    return jsonify({k: get_info(k) for k in _HARDWARE_COMMANDS})
