"""
Controlar reinicio de la Raspberry Pi vía API HTTP.

Este endpoint ejecuta comandos de reinicio en la Raspberry
y verifica si alguno tiene éxito.

POST /reboot
Requiere: Header con X-API-TOKEN
"""

from time import sleep
from typing import Literal, Union
from flask import Blueprint, jsonify
from flask.wrappers import Response
from guardian_rpi_api.utils.utils import require_token, run_cmd_raiser

# Inicializa el blueprint
bp: Blueprint = Blueprint("power", __name__)

# Lista de comandos de reinicio a intentar
REBOOT_COMMANDS: list[str] = [
    "sudo shutdown -r now",
    "sudo reboot",
    "sudo init 6",
    # OJO no abusar de este comando, mata tarjetas SD
    "sudo systemctl --force --force reboot",
]


@bp.route("/reboot", methods=["GET"])
def reboot() -> Union[Response, tuple[Response, Literal[500]]]:
    """
    Reinicia la Raspberry localmente.

    Intenta varios comandos hasta que uno tenga éxito.

    :return: JSON con resultado de la operación
    :rtype: Union[Response, tuple[Response, Literal[500]]]
    """
    require_token()

    for command in REBOOT_COMMANDS:
        try:
            run_cmd_raiser(command)
            sleep(0.5)
            return jsonify({"status": "rebooting", "command": command})
        # Si lanza una excepción intentará con el siguiente comando
        except Exception as e: # pylint: disable=broad-except
            # Imprime el error
            print(e)
            # Intenta siguiente comando
            continue

    # Si llegó hasta aquí, todos fallaron
    return jsonify({"error": "Todos los métodos de reinicio fallaron."}), 500
