"""
Comandos relacionados con el control de gpio
"""
from pathlib import Path
from flask import Blueprint, jsonify

# Inicializa el blueprint
bp: Blueprint = Blueprint("gpio", __name__)

# Ruta absoluta del archivo actual
BASE_DIR: Path = Path(__file__).resolve().parent

# Sube dos niveles hasta la raíz del proyecto
PROJECT_ROOT: Path = BASE_DIR.parent.parent

# Arma la ruta al archivo gpio.py
GPIO_CONTROL_PATH: Path = (PROJECT_ROOT, "utils", "gpio.py")

@bp.route("/off/<string:gpio>", methods=["POST"])
def gpio_off(gpio: str):
    ...
