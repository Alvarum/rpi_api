# -*- coding: utf-8 -*-
"""
API para obtener datos y manipular la Raspberry Pi.
"""

from __future__ import annotations

import logging
from typing import Final, Optional

from flask import Flask, Response, jsonify

from config import NetworkConfig, load_settings
from utils.blueprint_register import register_getters_blueprints
from utils.utils import require_token

from __init__ import __version__

# Formato de los logs
LOG_FMT: Final[str] = "%(asctime)s %(levelname)s %(name)s %(message)s"


def create_app() -> Flask:
    """
    Crea la app Flask leyendo config validada.

    :returns: Instancia de Flask con blueprints registrados.
    :rtype: Flask
    """
    # carga las configuraciones
    cfg: NetworkConfig = load_settings()

    # Crea la app
    app: Flask = Flask(__name__)

    # Define la autenticación global para cualquier request
    @app.before_request
    def _auth_guard() -> Optional[Response]:
        """Hook global de autenticación (Bearer obligatorio)."""
        require_token()
        return None

    # Agrega los blueprints
    register_getters_blueprints(app)

    # Endpoints primigemios
    @app.get("/health")
    def _health() -> str:
        """Verifica la salud de la API."""
        return "ok"

    @app.get("/version")
    def _version() -> Response:
        """Devuelve la version de la API."""
        return jsonify({"version": __version__})

    # Configura el host y el port al que se va a escuchar
    app.config["HOST"] = cfg.host
    app.config["PORT"] = cfg.port

    return app


def main() -> None:
    """
    Entrypoint: `guardian-rpi-api` o `python -m app`.
    """
    # Configura el logging
    logging.basicConfig(level=logging.INFO, format=LOG_FMT)

    # Crea la app de flask
    app = create_app()

    # Configura la app
    host: str = app.config["HOST"]
    port: int = app.config["PORT"]

    # Arranca la app
    logging.info(
        "Levantando servicio guardian-rpi-api %s on %s:%s",
        __version__,
        host,
        port
    )

    app.run(
        host=host,
        port=port
    )


if __name__ == "__main__":
    main()
