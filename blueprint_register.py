"""
Registra los blueprints en la app
"""
from flask import Flask
from routes.getters import (
    storage,
    system,
    network,
    hardware,
    gpio,
    events,
    guardian_scroll
)
from routes.validations import services, files, binaries



def register_getters_blueprints(app: Flask) -> None:
    """
    Registra los blueprints en la app de flask para que puedan ser
    accedidos y usados.

    :param Flask app: App de flask
    """
    # GETTERS
    app.register_blueprint(guardian_scroll.bp, url_prefix="/guardian")
    app.register_blueprint(storage.bp, url_prefix="/storage")
    app.register_blueprint(system.bp, url_prefix="/system")
    app.register_blueprint(network.bp, url_prefix="/network")
    app.register_blueprint(hardware.bp, url_prefix="/hardware")
    app.register_blueprint(gpio.bp, url_prefix="/gpio")
    app.register_blueprint(events.bp, url_prefix="/events")

    # VALIDADORES
    app.register_blueprint(files.bp, url_prefix="/files")
    app.register_blueprint(binaries.bp, url_prefix="/binaries")
    app.register_blueprint(services.bp, url_prefix="/services")
