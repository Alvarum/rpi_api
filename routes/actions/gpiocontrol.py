"""
Rutas para controlar pines GPIO
"""

# Librerias
from typing import List, Optional, Union
from flask import Blueprint, jsonify, request
from utils.gpio import GPIOController

# Inicializa el blueprint
bp: Blueprint = Blueprint("gpiocontrol", __name__)

@bp.route("/<action>", methods=["POST"])
def control_gpio(action: str):
    """
    Controla pines GPIO mediante HTTP.

    Requiere JSON en el body con `pins: List[int]`
    """

    # Obtiene los datos
    data = request.get_json(force=True)

    # Obtiene los pines del JSON
    pins: Optional[Union[List[int], int]] = data.get("pins", [])

    # Verifica el formato
    if not isinstance(pins, list):
        return jsonify(
            {"error": "Formato inválido. Se requiere 'pins': List[int]"}
        ), 400

    try:
        # Realiza la operación
        with GPIOController(pins) as gpio:
            if action == "off":
                success = gpio.change_state("off")
            elif action == "on":
                success = gpio.change_state("on")
            elif action == "reboot":
                success = gpio.reboot()
            elif action == "test":
                if len(pins) != 1:
                    return jsonify(
                        {"error": "Test requiere exactamente un pin."}
                    ), 400
                success = gpio.test(pins[0])
            # Acción no reconocida
            else:
                return jsonify({"error": f"Acción '{action}' no válida"}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 423  # 423 Locked

    # Si no registra el exito, devuelve un error
    if not success:
        return jsonify({"error": "Fallo la operación"}), 500

    # Si llega hasta aca, todo va bien
    return jsonify({"status": "ok", "action": action, "pins": pins}), 200
