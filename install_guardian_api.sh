#!/bin/bash

#############################################################
# Crea automaticamente el servicio para el api de guardian  #
# Se valida luego con: sudo systemctl status guardian-api    #
#############################################################

# Nombre del servicio
SERVICE_NAME="guardian-api"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# Detecta automáticamente la ruta del proyecto (donde está este script)
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv"
PYTHON_BIN="${VENV_DIR}/bin/python"
APP_FILE="${PROJECT_DIR}/app.py"

# Crea el entorno virtual si no existe
if [ ! -d "$VENV_DIR" ]; then
    echo "[+] Creando entorno virtual en ${VENV_DIR}..."
    python -m venv "$VENV_DIR"
fi

# Instala dependencias si hay requirements.txt
if [ -f "${PROJECT_DIR}/requirements.txt" ]; then
    echo "[+] Instalando dependencias desde requirements.txt..."
    "${PYTHON_BIN}" -m pip install --upgrade pip
    "${PYTHON_BIN}" -m pip install -r "${PROJECT_DIR}/requirements.txt"
fi

# Crea archivo de servicio con la configuración exacta que pediste
echo "[+] Creando archivo de servicio en ${SERVICE_FILE}..."
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Flask API para control y obtencion de datos del raspberry
After=network.target

[Service]
WorkingDirectory=${PROJECT_DIR}
ExecStart=${PYTHON_BIN} -m flask run --host=0.0.0.0 --port=5000
Environment="FLASK_APP=${APP_FILE}"
Environment="FLASK_END=production"
Environment="PYTHONUNBUFFERED=1"
Restart=on-failure
StandardOutput=journal
StandardError=journal
User=pi

[Install]
WantedBy=multi-user.target
EOF

# Recarga systemd, habilita y arranca el servicio
echo "[+] Recargando systemd y habilitando servicio..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}.service"
sudo systemctl restart "${SERVICE_NAME}.service"

echo "Instalación completada."
echo "Verifica con: sudo systemctl status ${SERVICE_NAME}"