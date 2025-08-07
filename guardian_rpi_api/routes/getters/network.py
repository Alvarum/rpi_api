"""
Comandos relacionados con red y seguridad.

- /ip: Obtiene la IP local principal
- /gateway: Obtiene la IP del gateway
- /open_ports: Lista los puertos TCP/UDP abiertos
- /failed_logins: Muestra los últimos intentos de login fallidos
- /getall: Devuelve todos los datos anteriores
"""

# Librerias
from flask import Blueprint, jsonify
from guardian_rpi_api.utils.utils import run_cmd, require_token

# Inicializa el blueprint
bp = Blueprint("network", __name__)

# Mapeo de campos a comandos, mas pythoneano para
# dejar el codigo wonito
_NETWORK_COMMANDS: dict[str, str] = {
    "ip": "hostname -I | cut -d' ' -f1",
    "gateway": "ip route | grep default | awk '{print $3}'",
    "open_ports": "ss -tuln | awk 'NR>1 {print $5}'",
    "failed_logins": "lastb -n 5"
}


def get_info(field: str) -> str:
    """
    Ejecuta el comando de red asociado a un campo.

    :param field: Campo solicitado (ip, gateway, etc.)
    :type field: str
    :return: Resultado del comando como string
    :rtype: str
    """
    return run_cmd(_NETWORK_COMMANDS[field])


@bp.route("/ip")
def get_ip():
    """
    Devuelve la dirección IP local del sistema.
    """
    require_token()
    return jsonify({"ip": get_info("ip")})


@bp.route("/gateway")
def get_gateway():
    """
    Devuelve la dirección IP del gateway predeterminado.
    """
    require_token()
    return jsonify({"gateway": get_info("gateway")})


@bp.route("/open_ports")
def get_open_ports():
    """
    Devuelve una lista de puertos TCP/UDP abiertos.
    """
    require_token()
    return jsonify({"open_ports": get_info("open_ports")})


@bp.route("/failed_logins")
def get_failed_logins():
    """
    Devuelve los últimos intentos fallidos de login del sistema.
    """
    require_token()
    return jsonify({"failed_logins": get_info("failed_logins")})


@bp.route("/getall")
def get_all_network_info():
    """
    Devuelve toda la información de red en una sola respuesta.
    """
    require_token()
    return jsonify({key: get_info(key) for key in _NETWORK_COMMANDS})
