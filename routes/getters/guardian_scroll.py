"""
Contiene la consulta unica que entregará todos los datos que necesita 
Grid Guardian, es más que nada para poder obtener todo lo que necesita
solo con una consulta.
"""

from flask import Blueprint, Response, jsonify
from utils.utils import run_cmd, require_token

bp = Blueprint("guardian", __name__)

@bp.route("/dataslow")
def get_data():
    """
    Obtiene todos los datos que requiere Grid Guardian de la Raspberry Pi.
    """
    require_token()
    return jsonify({
        "os": run_cmd("lsb_release -d | cut -f2"),
        "uptime": run_cmd("uptime -p"),
        "kernel": run_cmd("uname -r"),
        "model": run_cmd("cat /proc/device-tree/model"),
        "total_memory": run_cmd("df -h / | awk 'NR==2{print $2}'"),
        "used_memory": run_cmd("df -h / | awk 'NR==2{print $3}'"),
        "free_memory": run_cmd("df -h / | awk 'NR==2{print $4}'"),
        "cpu_usage": run_cmd("top -bn1 | grep 'Cpu(s)' | awk '{print $2+$4}'"),
        "temp": run_cmd("cat /sys/class/thermal/thermal_zone0/temp | awk '{print $1/1000}'"),
        "ram": run_cmd("free -h | grep Mem | awk '{print $3\"/\"$2}'"),
        "cpu_cores": run_cmd("nproc"),
        "cpu_freq": run_cmd("lscpu | grep 'MHz' | awk '{print $NF}'"),
        "python3_version": run_cmd("python3 --version 2>&1"),
        "python2_version": run_cmd("python2 --version 2>&1")
    })

@bp.route("/data")
def get_data_onsteroid() -> Response:
    """
    Obtiene todos los datos que requiere Grid Guardian de la Raspberry Pi.
    
    Realiza menos comandos que la versión anterior para hacer la función mas rapida
    """

    require_token()

    # Información del sistema
    sysinfo = run_cmd(
        "lsb_release -d; uname -r; cat /proc/device-tree/model; uptime -p"
    ).splitlines()

    # Almacenamiento
    disk_info = run_cmd("df -h / | awk 'NR==2{print $2, $3, $4}'").split()
    total_memory, used_memory, free_memory = disk_info

    # CPU info y RAM
    cpuinfo = run_cmd(
        "top -bn1 | grep 'Cpu(s)'; "
        "nproc; "
        "lscpu | grep 'MHz' | awk '{print $NF}'; "
        "free -h | grep Mem"
    ).splitlines()

    user_cpu = float(cpuinfo[0].split()[1])
    system_cpu = float(cpuinfo[0].split()[3])
    cpu_usage = str(round(user_cpu + system_cpu, 2))

    cpu_cores = cpuinfo[1]
    cpu_freq = cpuinfo[2]
    ram_parts = cpuinfo[3].split()
    ram = f"{ram_parts[2]}/{ram_parts[1]}"

    # Temperatura
    temp_raw = run_cmd("cat /sys/class/thermal/thermal_zone0/temp")
    temp = str(float(temp_raw) / 1000)

    # Versiones de Python
    python_versions = run_cmd("python2 --version 2>&1; python3 --version 2>&1").splitlines()
    python2_version = python_versions[0]
    python3_version = python_versions[1]

    # Construye el JSON final
    return jsonify({
        "os": sysinfo[0].split(":", 1)[1].strip(),
        "kernel": sysinfo[1],
        "model": sysinfo[2],
        "uptime": sysinfo[3],

        "total_memory": total_memory,
        "used_memory": used_memory,
        "free_memory": free_memory,

        "cpu_usage": cpu_usage,
        "temp": temp,
        "ram": ram,
        "cpu_cores": cpu_cores,
        "cpu_freq": cpu_freq,

        "python2_version": python2_version,
        "python3_version": python3_version,
    })
