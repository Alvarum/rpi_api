from flask import Blueprint, jsonify
from utils.utils import run_cmd, require_token

bp = Blueprint("gpio", __name__)

@bp.route("/status")
def gpio_status():
    require_token()
    return jsonify({
        "values": run_cmd("gpio readall"),
        "bcm_board": run_cmd("gpio readall | head -n 1")
    })
