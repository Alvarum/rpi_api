"""
Este archivo está hecho para ser llamado con argumentos por la consola.

Debe ejecutarse con los argumentos gpio_number y state_wanted.

Dependencias:
Raspberry py 4+
Python 3.5+
RPi.GPIO
"""

# Version del archivo
__version__ = "1.2.1"

# Librerias
from os import mkdir, path, remove, environ
import time
import sys
import logging
import subprocess
from typing import Callable, Dict, List, Optional
from dotenv import load_dotenv

# region Configs

# Configs del lint
# pylint: disable=broad-except

# Carga las variables de entorno
load_dotenv()

# Rutas
LOGS_PATH = environ.get("LOGS_PATH")
LOCK_FILE_PATH = environ.get("LOCK_FILE_PATH")

# Carga las variables entregadas al script
try:

    # Convierte el string que se recibe (cada valor separado por espacios)
    # y lo transforma en una lista para poder trabajar con esta.
    gpio_number: List[int] = list(map(int, sys.argv[1].split()))

    # Obtiene el estado al que se quiere cambiar los Gpios.
    state_wanted: Optional[str] = sys.argv[2].lower()

except Exception as e:

    # Si no se pudo obtener los argumentos, informa del error
    logging.error("Error al obtener los argumentos: %s", e)

    # Explica el uso del script
    logging.info(
        "Uso: gpio_control.py"
        + "'<pines separados por espacio>' <on|off|reboot|test>"
    )

    # Termina la ejecución
    sys.exit(1)


# Configura logging para archivo y consola
logging.basicConfig(
    # Nivel de logging
    level=logging.INFO,

    # Formato del log
    format='%(asctime)s - %(levelname)s - %(message)s',

    # ruta del log
    filename=LOGS_PATH + "/gpio_control.log",

    # "a" agrega el log al final del archivo en vez de sobre escribir
    filemode='a'
)


try:
    # Verifica si la carpeta logs existe
    if not path.exists(LOGS_PATH):
        logging.info("La carpeta logs no existe. Creando...")

        # Crea la carpeta
        mkdir(LOGS_PATH)
except Exception as e:
    logging.error(
        "Error al crear la carpeta logs: %s", e
    )


# Verifica si el archivo de bloqueo ya existe
# Con este se valida que no haya otra instancia del script en ejecución
# ya que esto genera problemas.
if path.exists(LOCK_FILE_PATH):
    logging.error(
        "Ya está tomado el control de GPIOs en este momento, abortando..."
    )
    sys.exit(1)

# Crea el archivo de bloqueo para indicar que el script se esta
# ejecutando
try:
    with open(LOCK_FILE_PATH, 'w', encoding="utf-8") as lock_file:
        # Escribe en el archivo
        lock_file.write("Lock file to indicate script is running.")
    logging.info("Archivo de bloqueo creado.")
except Exception as e:
    logging.error("No se pudo crear el archivo de bloqueo: %s", e)
    sys.exit(1)


# Si el raspberry no viene con el paquete RPi, lo instala.
# Es el paquete que contiene el módulo RPi.GPIO, el cual se encarga de
# controlar los pines GPIO.
try:
    # intenta importar el módulo
    from RPi import GPIO  # type: ignore

# Si el módulo no se encuentra, lo instala
except ModuleNotFoundError:
    logging.info("El módulo RPi.GPIO no está instalado, instalando...")

    # Instala el módulo
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "RPi.GPIO"]
    )

# Desactiva los warnings de RPi.GPIO, ya que ensucia la consola
GPIO.setwarnings(False)



# region Functions
def setup_gpio(pines: List[int]) -> bool:
    """
    Configuración inicial de los pines GPIO, necesario para poder
    manipularlos.

    :param List[int] pines: Lista de pines a configurar
    :return: bool
    """
    try:
        # Se trabaja con el modo BOARD
        GPIO.setmode(GPIO.BOARD)

        # Se configuran los pines entregados en la lista en modo
        # de salida
        for pin in pines:
            GPIO.setup(pin, GPIO.OUT)

        # Notifica que los pines fueron configurados
        logging.info("Pines configurados correctamente: %s", pines)

        # retorna verdadero
        return True
    except (ValueError, RuntimeError) as e:
        logging.error("Error al configurar los pines %s: %s", pines, e)

    # si llega aquí es porque algo fallo, por lo que retorna falso
    return False


def change_pin_state(pines: List[int], state: bool) -> bool:
    """
    Cambia el estado de uno o más pines, estos deben estar previamente
    inicializados y configurados.

    :param List[int] pines: Lista de pines a cambiar
    :param bool state: Estado a cambiar
    :return: bool
    """
    try:
        for pin in pines:
            # Cambia el estado del pin al estado deseado
            GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)

            # Notifica el cambio
            logging.info(
                "Pin %s cambiado a %s",
                pin,
                'ENCENDIDO' if state else 'APAGADO'
            )

            # Espera un segundo antes de continuar con el siguiente
            time.sleep(1)

        # si llega aqui es porque todo salio bien
        return True
    except Exception as e:
        logging.error("Error al cambiar estado de los pines %s: %s", pines, e)

    # si llega aqui es porque algo fallo
    return False


def gpio_reboot(pines: List[int]) -> bool:
    """
    Reinicia los GPIOs especificados en la lista.
    
    :param List[int] pines: Lista de pines a reiniciar
    :return: bool
    """
    try:
        logging.info("Reiniciando pines %s", pines)

        # Cambia el estado de los pines a false (apagado)
        change_pin_state(pines, False)

        # Espera 3 segundos para que se apague el dispositivo
        time.sleep(3)

        # Cambia el estado de los pines a true (encendido)
        change_pin_state(pines, True)

        logging.info("Pines %s reiniciados", pines)

        # si llega aqui es porque todo salio bien
        return True
    except Exception as e:
        logging.error("Error al reiniciar los pines %s: %s",pines, e)

    # si llega aqui es porque algo fallo
    return False


def test(pin: int) -> bool:
    """
    Testea un pin GPIO especifico:
        - Apaga el pin
        - Espera 15 segundos
        - Enciende el pin
        - Devuelve True si todo salio bien

    :param int pin: Pin a testear
    :return: bool
    """
    # Apaga el pin y guarda el resultado
    result = change_pin_state([pin], False)

    # Espera 15 segundos
    time.sleep(15)

    # Enciende el pin y si el encendido y el apagado salieron bien
    # retorna verdadero, de lo contrario retorna falso
    return result and change_pin_state([pin], True)


# Crea un diccionario con las acciones que se pueden realizar
actions: Dict[str, Callable] = {
    "on": lambda: change_pin_state(gpio_number, True),
    "off": lambda: change_pin_state(gpio_number, False),
    "reboot": lambda: gpio_reboot(gpio_number),
    "test": lambda: test(gpio_number[0])
}


# region Main
if __name__ == "__main__":
    try:

        # Configura los pines, si falla se sale del script
        if not setup_gpio(gpio_number):
            sys.exit(1)

        # Si la acción está disponible, la ejecuta
        if state_wanted in actions:
            actions[state_wanted]()

        # Si la acción no estaba disponible, se sale
        else:
            logging.error("Estado no reconocido: %s", state_wanted)
            sys.exit(1)

    except Exception as e:
        logging.error("Error al ejecutar el script: %s", e)

    finally:

        # Elimina el archivo de bloqueo para que se pueda volver a
        # controlar los GPIOs
        if path.exists(LOCK_FILE_PATH):
            remove(LOCK_FILE_PATH)
            logging.info("Archivo de bloqueo eliminado.")
