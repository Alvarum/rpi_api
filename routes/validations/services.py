"""
Comandos para obtener e interactuar con servicios.

- /<service_name>/status: Obtiene el estado del servicio
- /<service_name>/restart: Reinicia el servicio
- /<service_name>/start: Inicia el servicio
- /<service_name>/stop: Detiene el servicio
"""

from typing import Literal, Union
from flask import Blueprint, jsonify
from flask.wrappers import Response
from utils.shell import run_cmd

# Inicializa el blueprint
bp = Blueprint(
    name="services",
    import_name=__name__
)


# test  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
AUTHORIZED_SERVICES = {
    "nodered",
    "ssh"
}

def is_authorized_service(service: str) -> bool:
    """Verifica si el servicio está autorizado."""
    return service in AUTHORIZED_SERVICES
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -




# region Getters
@bp.route("/<string:service_name>", methods=["GET"])
def get_service_status(service_name: str) -> Response:
    """
    Consulta el estado de un servicio del sistema usando systemctl.

    :param service_name: Nombre del servicio (ej: ssh, nodered)
    :return type: Response
    """
    status: str = run_cmd(f"systemctl is-active {service_name}")
    return jsonify({
        "service": service_name,
        "status": status
    })


# region Post
@bp.route("/<string:service_name>/restart", methods=["POST"])
def restart_service(service_name: str) -> Union[Response, tuple[Response, Literal[404]]]:
    """
    Reinicia un servicio usando systemctl.

    :param service_name: Nombre del servicio
    :return type: Response
    """
    exists: str = run_cmd(
        f"systemctl list-unit-files | grep -w '{service_name}.service'"
    )
    if not exists:
        return jsonify({
            "error": f"Servicio '{service_name}' no encontrado"
        }), 404

    result: str = run_cmd(f"sudo systemctl restart {service_name}")
    return jsonify({
        "service": service_name,
        "action": "restart",
        "result": "ok" if result == "" else result
    })


@bp.route("/<string:service_name>/start", methods=["POST"])
def start_service(service_name: str) -> Union[Response, tuple[Response, Literal[404]]]:
    """
    Inicia un servicio usando systemctl.

    :param service_name: Nombre del servicio
    :return type: Response
    """
    exists: str = run_cmd(
        f"systemctl list-unit-files | grep -w '{service_name}.service'"
    )
    if not exists:
        return jsonify({
            "error": f"Servicio '{service_name}' no encontrado"
        }), 404

    result: str = run_cmd(f"sudo systemctl start {service_name}")
    return jsonify({
        "service": service_name,
        "action": "start",
        "result": "ok" if result == "" else result
    })


@bp.route("/<string:service_name>/stop", methods=["POST"])
def stop_service(service_name: str) -> Union[Response, tuple[Response, Literal[404]]]:
    """
    Detiene un servicio usando systemctl.

    :param service_name: Nombre del servicio
    :return type: Response
    """
    # Verifica si el servicio existe
    exists: str = run_cmd(
        f"systemctl list-unit-files | grep -w '{service_name}.service'"
    )

    # Si no existe, devuelve un error
    if not exists:
        return jsonify({
            "error": f"Servicio '{service_name}' no encontrado"
        }), 404

    # Detiene el servicio
    result: str = run_cmd(f"sudo systemctl stop {service_name}")

    # Devuelve la respuesta
    return jsonify({
        "service": service_name,
        "action": "stop",
        "result": "ok" if result == "" else result
    })


@bp.route("/<string:service_name>/enable", methods=["POST"])
def enable_service(service_name: str) -> Union[Response, tuple[Response, Literal[404]]]:
    """
    Habilita un servicio para que se inicie al arrancar el sistema.

    :param service_name: Nombre del servicio
    :return type: Response
    """
    # Verifica si el servicio existe
    exists: str = run_cmd(
        f"systemctl list-unit-files | grep -w '{service_name}.service'"
    )

    # Si no existe, devuelve un error
    if not exists:
        return jsonify(
            {"error": f"Servicio '{service_name}' no encontrado"}
        ), 404

    # Habilita el servicio
    result: str = run_cmd(f"sudo systemctl enable {service_name}")

    # Devuelve la respuesta
    return jsonify({
        "service": service_name,
        "action": "enable",
        "result": result or "ok"
    })


@bp.route("/<string:service_name>/disable", methods=["POST"])
def disable_service(service_name: str) -> Union[Response, tuple[Response, Literal[404]]]:
    """
    Deshabilita un servicio para que no se inicie al arrancar el sistema.
    
    :param service_name: Nombre del servicio
    :return type: Response
    """
    # Verifica si el servicio existe
    exists: str = run_cmd(
        f"systemctl list-unit-files | grep -w '{service_name}.service'"
    )

    # Si no existe, devuelve un error
    if not exists:
        return jsonify(
            {"error": f"Servicio '{service_name}' no encontrado"}
        ), 404

    # Deshabilita el servicio
    result: str = run_cmd(f"sudo systemctl disable {service_name}")

    # Devuelve la respuesta
    return jsonify({
        "service": service_name,
        "action": "disable",
        "result": result or "ok"
    })



# region dog shit
# @bp.route("/nodered")
# def nodered_status():
#     """
#     Obtiene el estado del servicio nodered
#     """
#     return jsonify({
#         "nodered": run_cmd("systemctl is-active nodered")
#     })

# @bp.route("/ssh")
# def ssh_status():
#     """
#     Obtiene el estado del servicio ssh
#     """
#     return jsonify({
#         "ssh": run_cmd("systemctl is-active ssh")
#     })


@bp.route("/processes")
def processes():
    return jsonify({
        "processes": run_cmd("ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head -n 10")
    })
