# Guardian API

Instala y ejecuta automáticamente el servicio de la API Flask para Raspberry Pi.

## Requisitos
- Python 3.11
- `systemd` (presente por defecto en Raspberry Pi OS)
- Conexión a internet

## Instalación
- Crear el archivo .env con las variables de entorno en la carpeta del proyecto

        # Seguridad
        API_TOKEN= token de seguridad
        ALLOWED_IP_RANGE= rango de ips permitidas

        # Rutas
        LOGS_PATH= ruta de los logs
        LOCK_FILE_PATH= ruta del archivo de bloqueo

- Modificar el instalador con la siguiente información

        PROJECT_DIR= ruta actual donde está el codigo


- Crear el servicio

    ```bash
    chmod +x install_guardian_api.sh
    ./install_guardian_api.sh

- Verificar el servicio

    ```bash
    sudo systemctl status guardian-api