from flask import Blueprint, jsonify
from utils.shell import run_cmd

bp = Blueprint("events", __name__)

@bp.route("/critical")
def critical_events():
    return jsonify({
        "log": run_cmd("journalctl -p 3 -xb | head -n 20")
    })
