from flask import Blueprint, Response, jsonify
from guardian_rpi_api.utils.utils import run_cmd, require_token

bp = Blueprint("gpio", __name__)

@bp.route("/status")
def gpio_status() -> Response:
    """
    Obtiene el estado de los pines GPIO
    """
    require_token()
    return jsonify({
        "values": run_cmd("gpio readall"),
        "bcm_board": run_cmd("gpio readall | head -n 1")
    })
