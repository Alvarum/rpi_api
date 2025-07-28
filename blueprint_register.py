"""
Registra los blueprints en la app
"""
from flask import Flask
from routes.getters import (
    storage,
    system,
    network,
    hardware,
    security,
    gpio,
    events
)
from routes.validations import services

def register_getters_blueprints(app: Flask) -> None:
    """
    Registra los blueprints en la app de flask para que puedan ser
    accedidos y usados.

    :param Flask app: App de flask
    """
    # Comandos relacionados con almacenamiento
    app.register_blueprint(storage.bp, url_prefix="/storage")

    # Comandos relacionados con el sistema
    app.register_blueprint(system.bp, url_prefix="/system")

    # Comandos relacionados con los servicios
    app.register_blueprint(services.bp, url_prefix="/services")

    # Comandos relacionados con la red
    app.register_blueprint(network.bp, url_prefix="/network")

    # Comandos relacionados con el hardware
    app.register_blueprint(hardware.bp, url_prefix="/hardware")

    # Comandos relacionados con la seguridad
    app.register_blueprint(security.bp, url_prefix="/security")

    # Comandos relacionados con el gpio
    app.register_blueprint(gpio.bp, url_prefix="/gpio")

    # Comandos relacionados con los eventos
    app.register_blueprint(events.bp, url_prefix="/events")
