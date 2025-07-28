from flask import Blueprint, jsonify
from utils.shell import run_cmd

bp = Blueprint("security", __name__)

@bp.route("/users")
def users_groups():
    return jsonify({
        "users": run_cmd("cut -d: -f1 /etc/passwd"),
        "groups": run_cmd("cut -d: -f1 /etc/group")
    })

@bp.route("/ssh_keys")
def ssh_keys():
    return jsonify({
        "keys": run_cmd("cat ~/.ssh/authorized_keys")
    })
