#!/bin/bash

#############################################################
# Crea automaticamente el servicio para el api de guardian  #
# se puede validar luego de la instalacion con el comando   #
# sudo systemctl status guardian-api                        #
#############################################################

# Nombre del servicio
SERVICE_NAME="guardian-api"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# Ruta del proyecto (Configurar con la ruta donde se deje el codigo)
PROJECT_DIR="/home/pi/app/api/v2"
VENV_DIR="${PROJECT_DIR}/.venv"
PYTHON_BIN="${VENV_DIR}/bin/python"
FLASK_APP="main:app"

# Crea el entorno virtual si no existe
if [ ! -d "$VENV_DIR" ]; then
    echo "[+] Creando entorno virtual en ${VENV_DIR}..."
    python -m venv "$VENV_DIR"
fi

# Instala las dependencias desde el archivo requirements.txt
echo "[+] Instalando dependencias desde requirements.txt..."
"${PYTHON_BIN}" -m pip install --upgrade pip
"${PYTHON_BIN}" -m pip install -r "${PROJECT_DIR}/requirements.txt"

# Crea archivo del servicio
echo "[+] Creando archivo de servicio en ${SERVICE_FILE}..."
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Flask API para control y obtencion de datos del raspberry
After=network.target

[Service]
WorkingDirectory=${PROJECT_DIR}
ExecStart=${PYTHON_BIN} -m flask run --host=0.0.0.0 --port=5000
Environment="FLASK_APP=${FLASK_APP}"
Environment="PYTHONUNBUFFERED=1"
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOF

# Recarga systemd, habilitaa y arranca el servicio
echo "[+] Recargando systemd y habilitando servicio..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}.service"
sudo systemctl restart "${SERVICE_NAME}.service"

echo "Instalación completada."
echo "Verifica con: sudo systemctl status ${SERVICE_NAME}"
echo "Atte: Equipo de desarrollo Everseek"
