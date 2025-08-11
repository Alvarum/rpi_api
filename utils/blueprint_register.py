from __future__ import annotations

from flask import Flask

from routes.getters import (
    storage, system, network, hardware, gpio, events, guardian_scroll,
)
from routes.actions import gpiocontrol, power
from routes.validations import services, files, binaries


def register_getters_blueprints(app: Flask) -> None:
    """
    Registra blueprints (GETTERS/VALIDATIONS/ACTIONS).
    """
    # GETTERS
    app.register_blueprint(guardian_scroll.bp, url_prefix="/guardian")
    app.register_blueprint(storage.bp, url_prefix="/storage")
    app.register_blueprint(system.bp, url_prefix="/system")
    app.register_blueprint(network.bp, url_prefix="/network")
    app.register_blueprint(hardware.bp, url_prefix="/hardware")
    app.register_blueprint(gpio.bp, url_prefix="/gpio")
    app.register_blueprint(events.bp, url_prefix="/events")

    # VALIDATIONS
    app.register_blueprint(files.bp, url_prefix="/files")
    app.register_blueprint(binaries.bp, url_prefix="/binaries")
    app.register_blueprint(services.bp, url_prefix="/services")

    # ACTIONS
    app.register_blueprint(gpiocontrol.bp, url_prefix="/gpiocontrol")
    app.register_blueprint(power.bp, url_prefix="/power")
