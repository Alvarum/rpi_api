# -*- coding: utf-8 -*-
"""
Contiene la consulta unica que entregará todos los datos que necesita 
Grid Guardian, es más que nada para poder obtener todo lo que necesita
solo con una consulta.
"""

from __future__ import annotations
import os
import platform
import shutil
import time
from pathlib import Path
from typing import Final
from flask import Blueprint, Response, jsonify
from utils.utils import run_cmd

# pylint: disable=W0718

# Inicializa el blueprint
bp: Blueprint = Blueprint("guardian", __name__)

# Comandos de interes
_OS_RELEASE: Final[Path] = Path("/etc/os-release")
_DT_MODEL: Final[Path] = Path("/proc/device-tree/model")
_UPTIME: Final[Path] = Path("/proc/uptime")
_CPU_STAT: Final[Path] = Path("/proc/stat")

_TEMP0: Final[Path] = Path(
    "/sys/class/thermal/thermal_zone0/temp"
)
_CPUFREQ_CUR: Final[Path] = Path(
    "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"
)
_CPUFREQ_MAX: Final[Path] = Path(
    "/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq"
)
_MEMINFO: Final[Path] = Path("/proc/meminfo")

# region Helpers
def _clean(s: str) -> str:
    """Colapsa espacios, quita NUL y recorta."""
    return " ".join(s.replace("\x00", " ").split()).strip()


def _human_bytes(n: int) -> str:
    """
    Transforma bytes en string humano con base de 1024.

    :param n: bytes
    :return: string
    """
    # Unidades de medida
    units = ("B", "KiB", "MiB", "GiB", "TiB")

    # Busca la unidad de medida adecuada y convierte
    i = 0
    x = float(n)
    while x >= 1024.0 and i < len(units) - 1:
        x /= 1024.0
        i += 1
    if i == 0:
        return f"{int(x)} {units[i]}"
    return f"{x:.1f} {units[i]}"


def _fmt_unit_es(n: int, s: str, p: str) -> str:
    """
    Formatea unidades en español.
    """
    return f"{n} {s if n == 1 else p}"


def _uptime_human(secs: float) -> str:
    """Segs -> 'X días Y horas Z minutos'."""
    minutes = int(secs // 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    parts: list[str] = []
    if days:
        parts.append(_fmt_unit_es(days, "día", "días"))
    if hours:
        parts.append(_fmt_unit_es(hours, "hora", "horas"))
    if minutes or not parts:
        parts.append(_fmt_unit_es(max(1, minutes), "minuto", "minutos"))
    return " ".join(parts)


def _os_description() -> str:
    try:
        if _OS_RELEASE.exists():
            data = _OS_RELEASE.read_text(encoding="utf-8", errors="ignore")
            for line in data.splitlines():
                if line.startswith("PRETTY_NAME="):
                    return _clean(line.split("=", 1)[1].strip().strip('"'))
        return _clean(os.uname().sysname)
    except Exception:
        out = run_cmd("lsb_release -d")
        if out != "error" and ":" in out:
            return _clean(out.split(":", 1)[1])
        return "unknown"
# endregion

# region Getters
def _kernel() -> str:
    try:
        u = os.uname()
        return _clean(f"{u.release} {u.machine}")
    except Exception:
        out = run_cmd("uname -r")
        return _clean(out) if out != "error" else "unknown"


def _model() -> str:
    try:
        if _DT_MODEL.exists():
            return _clean(
                _DT_MODEL.read_text(encoding="utf-8", errors="ignore")
            )
        return "unknown"
    except Exception:
        return "unknown"


def _uptime() -> str:
    try:
        if _UPTIME.exists():
            raw = _UPTIME.read_text(encoding="utf-8", errors="ignore")
            secs = float(raw.split()[0])
            return _uptime_human(secs)
    except Exception:
        pass
    out = run_cmd("uptime -p")
    if out != "error":
        return _clean(
            out.replace("up ", "")
               .replace("hours", "horas")
               .replace("hour", "hora")
               .replace("minutes", "minutos")
               .replace("minute", "minuto")
               .replace(",", "")
        )
    return _uptime_human(time.monotonic())


def _disk_root() -> dict[str, str]:
    """
    Usa shutil.disk_usage('/') (bytes) y formatea humano.
    """
    total, used, free = shutil.disk_usage("/")
    return {
        "total": _human_bytes(total),
        "used": _human_bytes(used),
        "free": _human_bytes(free),
    }


def _ram_info() -> dict[str, str]:
    """
    Lee /proc/meminfo; calcula used = total - available.
    """
    total = 0
    avail = 0
    try:
        for line in _MEMINFO.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("MemTotal:"):
                total = int(line.split()[1]) * 1024
            elif line.startswith("MemAvailable:"):
                avail = int(line.split()[1]) * 1024
        used = max(0, total - avail)
        return {
            "used": _human_bytes(used),
            "total": _human_bytes(total),
        }
    except Exception:
        out = run_cmd("free -b")
        if out != "error":
            try:
                for line in out.splitlines():
                    if line.startswith("Mem:") or line.lower().startswith("mem:"):
                        parts = [p for p in line.split() if p]
                        total_b = int(parts[1])
                        used_b = int(parts[2]) if len(parts) > 2 else 0
                        return {
                            "used": _human_bytes(used_b),
                            "total": _human_bytes(total_b),
                        }
            except Exception:
                pass
        return {"used_total": "unknown"}



def _cpu_usage_pct(sample_sec: float = 0.2) -> str:
    """
    Estima % de uso con delta en /proc/stat (sample corto).
    """
    try:
        def _read() -> tuple[int, int]:
            parts = _CPU_STAT.read_text(encoding="utf-8").splitlines()[0].split()
            vals = list(map(int, parts[1:]))
            idle = vals[3] + vals[4]
            total = sum(vals)
            return idle, total

        idle1, total1 = _read()
        time.sleep(sample_sec)
        idle2, total2 = _read()
        didle = idle2 - idle1
        dtotal = total2 - total1
        usage = 0.0 if dtotal <= 0 else (1.0 - didle / dtotal) * 100.0
        return f"{usage:.0f}%"
    except Exception:
        out = run_cmd("top -bn1")
        if out != "error":
            try:
                for ln in out.splitlines():
                    if "Cpu(s)" in ln or "CPU:" in ln:
                        txt = ln.replace(",", " ")
                        fields = txt.split()
                        idle = None
                        for i, tok in enumerate(fields):
                            if tok.endswith("%id"):
                                val = fields[i - 1].strip("%")
                                idle = float(val)
                                break
                        if idle is not None:
                            usage = 100.0 - idle
                            return f"{usage:.0f}%"
            except Exception:
                pass
        return "error"


def _cpu_freq() -> str:
    """
    Frecuencia actual (y máx si está disponible), en MHz.
    """
    try:
        cur = None
        mx = None
        if _CPUFREQ_CUR.exists():
            cur = int(_CPUFREQ_CUR.read_text(encoding="utf-8").strip()) / 1000.0
        if _CPUFREQ_MAX.exists():
            mx = int(_CPUFREQ_MAX.read_text(encoding="utf-8").strip()) / 1000.0
        if cur and mx:
            return f"{cur:.0f}/{mx:.0f} MHz"
        if cur:
            return f"{cur:.0f} MHz"
    except Exception:
        pass
    out = run_cmd("lscpu")
    if out != "error":
        try:
            cur = None
            mx = None
            for ln in out.splitlines():
                if "CPU max MHz" in ln:
                    mx = float(ln.split(":", 1)[1].strip())
                elif "CPU MHz" in ln:
                    cur = float(ln.split(":", 1)[1].strip())
            if cur and mx:
                return f"{cur:.0f}/{mx:.0f} MHz"
            if cur:
                return f"{cur:.0f} MHz"
        except Exception:
            pass
    return "unknown"


def _cpu_cores() -> int:
    return os.cpu_count() or 1


def _temp_c() -> str:
    try:
        if _TEMP0.exists():
            milli = int(_TEMP0.read_text(encoding="utf-8").strip())
            return f"{milli / 1000.0:.1f} °C"
    except Exception:
        pass
    out = run_cmd("cat /sys/class/thermal/thermal_zone0/temp")
    if out != "error":
        try:
            return f"{int(out) / 1000.0:.1f} °C"
        except Exception:
            return _clean(out)
    return "unknown"


def _py3_version() -> str:
    return f"Python {platform.python_version()}"


def _py2_version() -> str:
    out = run_cmd("python2 --version 2>&1")
    return _clean(out) if out != "error" else "error"



@bp.get("/data")
def get_data() -> Response:
    """
    Devuelve datos agregados con salida **humana y limpia**.
    """
    disk = _disk_root()
    ram = _ram_info()
    return jsonify(
        {
            # Sistema
            "os": _os_description(),
            "uptime": _uptime(),
            "kernel": _kernel(),
            "model": _model(),

            # SD
            "total_memory": disk["total"],
            "used_memory": disk["used"],
            "free_memory": disk["free"],

            # RAM
            "ram": f"{ram.get('used','?')} / {ram.get('total','?')}",

            # CPU
            "cpu_cores": _cpu_cores(),
            "cpu_freq": _cpu_freq(),
            "cpu_usage": _cpu_usage_pct(),

            # Temp
            "temp": _temp_c(),

            # Python
            "python3_version": _py3_version(),
            "python2_version": _py2_version(),
        }
    )


# """
# Contiene la consulta unica que entregará todos los datos que necesita 
# Grid Guardian, es más que nada para poder obtener todo lo que necesita
# solo con una consulta.
# """

# from flask import Blueprint, Response, jsonify
# from utils.utils import run_cmd, require_token

# bp = Blueprint("guardian", __name__)

# @bp.route("/data")
# def get_data() -> Response:
#     """
#     Obtiene todos los datos que requiere Grid Guardian de la Raspberry Pi.
#     """
#     require_token()
#     return jsonify({
#         "os": run_cmd("lsb_release -d | cut -f2"),
#         "uptime": run_cmd("uptime -p"),
#         "kernel": run_cmd("uname -r"),
#         "model": run_cmd("cat /proc/device-tree/model"),
#         "total_memory": run_cmd("df -h / | awk 'NR==2{print $2}'"),
#         "used_memory": run_cmd("df -h / | awk 'NR==2{print $3}'"),
#         "free_memory": run_cmd("df -h / | awk 'NR==2{print $4}'"),
#         "cpu_usage": run_cmd("top -bn1 | grep 'Cpu(s)' | awk '{print $2+$4}'"),
#         "temp": run_cmd("cat /sys/class/thermal/thermal_zone0/temp | awk '{print $1/1000}'"),
#         "ram": run_cmd("free -h | grep Mem | awk '{print $3\"/\"$2}'"),
#         "cpu_cores": run_cmd("nproc"),
#         "cpu_freq": run_cmd("lscpu | grep 'MHz' | awk '{print $NF}'"),
#         "python3_version": run_cmd("python3 --version 2>&1"),
#         "python2_version": run_cmd("python2 --version 2>&1")
#     })
