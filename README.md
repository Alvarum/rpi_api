# Guardian API

Instala y ejecuta automáticamente el servicio de la API Flask para Raspberry Pi.

## Requisitos
- Python 3.11
- `systemd` (presente por defecto en Raspberry Pi OS)
- Conexión a internet

## Instalación
- Clona este repositorio a la ruta de app

    ```bash
    git clone https://github.com/Alvarum/rpi_api.git /home/pi/app/rpi_api

- Crear el archivo .env con las variables de entorno en la carpeta del proyecto

        # Seguridad
        API_TOKEN= token de seguridad
        ALLOWED_IP_RANGE= rango de ips permitidas

        # Rutas
        LOGS_PATH= ruta de los logs
        LOCK_FILE_PATH= ruta del archivo de bloqueo

- Crear el servicio

    ```bash
    chmod +x install_guardian_api.sh
    ./install_guardian_api.sh

- Verificar el servicio

    ```bash
    sudo systemctl status guardian-api


## Mantención o depuración


- Moverse a la carpeta de servicios

    ```bash
    cd /etc/systemd/system/

- Ver los Logs

    ```bash
    journalctl -u guardian-api.service

- Recargar los servicios

    ```bash
    sudo systemctl daemon-reload


- Reiniciar el servicio

    ```bash
    sudo systemctl status guardian-api

- Probar desde consola la API

    ```bash
    sudo -u pi   FLASK_APP=main:app   /home/pi/app/rpi_api-main/.venv/bin/python   -m flask run --host=0.0.0.0 --port=5000