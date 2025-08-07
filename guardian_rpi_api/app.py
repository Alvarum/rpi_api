# -*- coding: utf-8 -*-
"""
API para obtener datos y manipular la Raspberry Pi.
"""

from __future__ import annotations

import logging
from typing import Final

from flask import Flask, Response, jsonify

from guardian_rpi_api import __version__
from guardian_rpi_api.config import NetworkConfig, load_settings
from guardian_rpi_api.utils.blueprint_register import register_getters_blueprints

# Formato de los logs
LOG_FMT: Final[str] = "%(asctime)s %(levelname)s %(name)s %(message)s"


def create_app() -> Flask:
    """
    Crea la app Flask leyendo config validada.

    :returns: Instancia de Flask con blueprints registrados.
    :rtype: Flask
    """
    cfg: NetworkConfig = load_settings()
    app: Flask = Flask(__name__)
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

    # Configuraciones
    app.config["HOST"] = cfg.host
    app.config["PORT"] = cfg.port

    return app


def main() -> None:
    """
    Entrypoint: `guardian-rpi-api` o `python -m guardian_rpi_api.app`.
    """
    # Configura el logging
    logging.basicConfig(level=logging.INFO, format=LOG_FMT)

    # Crea la app de flask
    app = create_app()

    # Configura la app
    host: str = app.config["HOST"]
    port: int = app.config["PORT"]

    # Arranca la app
    logging.info("Starting guardian-rpi-api %s on %s:%s", __version__, host, port)
    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
