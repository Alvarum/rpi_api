from flask import Blueprint, jsonify
from utils.utils import run_cmd, require_token

bp = Blueprint("network", __name__)

@bp.route("/info")
def info():
    require_token()
    return jsonify({
        "ip": run_cmd("hostname -I | cut -d' ' -f1"),
        "gateway": run_cmd("ip route | grep default | awk '{print $3}'"),
        "open_ports": run_cmd("ss -tuln | awk 'NR>1 {print $5}'"),
        "failed_logins": run_cmd("lastb -n 5")
    })
