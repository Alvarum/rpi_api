from flask import Blueprint, Response, jsonify
from utils.utils import run_cmd

bp = Blueprint("gpio", __name__)

@bp.route("/status")
def gpio_status() -> Response:
    """
    Obtiene el estado de los pines GPIO
    """
    return jsonify({
        "values": run_cmd("gpio readall"),
        "bcm_board": run_cmd("gpio readall | head -n 1")
    })
