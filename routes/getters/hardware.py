"""
Consultas relacionadas con información de hardware
"""
# Librerias
from flask import Blueprint, jsonify
from utils.utils import require_token, run_cmd

# Inicializa el blueprint
bp = Blueprint("hardware", __name__)

@bp.route("/resources")
def resources():
    """
    Obtiene recursos del hardware.
    """
    require_token()

    return jsonify({
        "cpu_usage": run_cmd("top -bn1 | grep 'Cpu(s)' | awk '{print $2+$4}'"),
        "temp": run_cmd("cat /sys/class/thermal/thermal_zone0/temp | awk '{print $1/1000}'"),
        "ram": run_cmd("free -h | grep Mem | awk '{print $3\"/\"$2}'"),
        "cpu_cores": run_cmd("nproc"),
        "cpu_freq": run_cmd("lscpu | grep 'MHz' | awk '{print $NF}'")
    })
