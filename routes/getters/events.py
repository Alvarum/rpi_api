from flask import Blueprint, Response, jsonify
from utils.utils import run_cmd, require_token

bp = Blueprint("events", __name__)

@bp.route("/critical")
def critical_events() -> Response:
    """
    Obtiene los eventos criticos del sistema
    """
    require_token()
    return jsonify({
        "log": run_cmd("journalctl -p 3 -xb | head -n 20")
    })
