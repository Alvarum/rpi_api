from flask import Blueprint, jsonify
from utils.shell import run_cmd

bp = Blueprint("gpio", __name__)

@bp.route("/status")
def gpio_status():
    return jsonify({
        "values": run_cmd("gpio readall"),
        "bcm_board": run_cmd("gpio readall | head -n 1")
    })
