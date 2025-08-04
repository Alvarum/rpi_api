"""
API para obtener información de un Raspberry Pi con Raspberry OS.
"""

from flask import Flask
from utils.blueprint_register import register_getters_blueprints

app = Flask(__name__)
register_getters_blueprints(app)

# Inicia el servidor
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
