"""
Controlador GPIO para Raspberry Pi.

Este módulo permite el control de pines GPIO mediante encendido,
apagado, reinicio y test. 
Incluye mecanismos de bloqueo para evitar ejecuciones simultáneas.
Está hecho para ser usado como contexto.
"""

# Deshabilita excepciones generales
# pylint: disable= W0719, W0718


# Librerias
from os import environ
import time
import logging
import subprocess
import types
from typing import List, Literal, Optional
from pathlib import Path
from dotenv import load_dotenv

# Carga las variables de entorno
load_dotenv()


# Revisa si el módulo RPi.GPIO esta instalado, caso contrario lo
# instala
try:
    from RPi import GPIO  # type: ignore
except ModuleNotFoundError:
    logging.info("Instalando RPi.GPIO...")
    subprocess.check_call(["python3", "-m", "pip", "install", "RPi.GPIO"])
    from RPi import GPIO  # type: ignore


# Configura el módulo GPIO, desactiva los warnings que ensuciam la
# consola y establece el modo de numeración de pines a BOARD que es
# el que se usa en Raspberry Pi.
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)


class GPIOController:
    """
    Controlador de pines GPIO de Raspberry Pi.

    Este controlador permite operaciones sobre GPIOs como encendido,
    apagado, reinicio y testeo. Utiliza archivos de lock para evitar
    colisiones en tiempo de ejecución.
    """

    def __init__(self, pins: List[int]) -> None:
        """
        Inicializa el controlador y configura los GPIOs.

        :param pins: Lista de pines a controlar
        :type pins: List[int]
        """
        # Obtiene los pines con los que se va a trabajar
        self.pins: List[int] = pins

        # Paths
        self.logs_path: Path = Path(
            environ.get("LOGS_PATH", "./logs")
        )
        self.lock_path: Path = Path(
            environ.get("LOCK_FILE_PATH", "./gpio.lock")
        )

        # Configuraciones
        self._configure_logging()
        self._check_and_create_log_dir()
        self._acquire_lock()
        self._setup_gpio()

    def __enter__(self) -> "GPIOController":
        """
        Permite el uso del controlador como contexto.

        :return: Instancia del controlador
        :rtype: GPIOController
        """
        return self


    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[types.TracebackType]
    ) -> None:
        """
        Libera recursos al salir del contexto.

        :param exc_type: Tipo de excepción (si existe)
        :param exc_val: Valor de excepción
        :param exc_tb: Traceback
        """
        self.cleanup()


    def _configure_logging(self) -> None:
        """Configura logging solo si no hay handlers existentes."""
        if not logging.getLogger().hasHandlers():
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(message)s",
                filename=str(self.logs_path / "gpio_control.log"),
                filemode="a"
            )


    def _check_and_create_log_dir(self) -> None:
        """Crea el directorio de logs si no existe."""
        if not self.logs_path.exists():
            self.logs_path.mkdir(parents=True)
            logging.info("Carpeta de logs creada: %s", self.logs_path)


    def _acquire_lock(self) -> None:
        """Crea archivo de lock para ejecución exclusiva."""
        if self.lock_path.exists():
            raise RuntimeError("GPIO en uso por otro proceso.")
        self.lock_path.write_text("Lock activo", encoding="utf-8")
        logging.info("Lock creado: %s", self.lock_path)


    def _release_lock(self) -> None:
        """Elimina el archivo de lock si existe."""
        if self.lock_path.exists():
            self.lock_path.unlink()
            logging.info("Lock liberado.")


    def _setup_gpio(self) -> Optional[bool]:
        """
        Configura los pines en modo salida.

        :raises Exception: Si no se pueden configurar los pines
        """
        try:
            for pin in self.pins:
                GPIO.setup(pin, GPIO.OUT)
            logging.info("Pines configurados: %s", self.pins)
        except Exception as e:
            logging.error("Error al configurar GPIOs: %s", e)
            return False

    def change_state(
        self,
        state: Literal["on", "off"],
        delay: float = 1.0
    ) -> bool:
        """
        Cambia el estado lógico de los GPIOs.

        :param state: Estado deseado ("on" o "off")
        :type state: Literal["on", "off"]
        :return: True si fue exitoso, False si falló
        :rtype: bool
        """
        value = GPIO.HIGH if state == "on" else GPIO.LOW
        try:
            for pin in self.pins:
                GPIO.output(pin, value)
                logging.info("Pin %d => %s", pin, state.upper())
                time.sleep(delay)
            return True
        except Exception as e:
            logging.error("Fallo cambio de estado: %s", e)
            return False


    def reboot(self) -> bool:
        """
        Reinicia los GPIOs apagándolos y encendiéndolos luego.

        :return: True si fue exitoso, False si falló
        :rtype: bool
        """
        try:
            logging.info("Reiniciando pines: %s", self.pins)
            self.change_state("off")
            time.sleep(3)
            self.change_state("on")
            logging.info("Reinicio completo.")
            return True
        except Exception as e:
            logging.error("Error reiniciando GPIOs: %s", e)
            return False


    def test(self, pin: int) -> bool:
        """
        Testea un pin: apaga, espera, enciende.

        :param pin: Pin a testear
        :type pin: int
        :return: True si ambas acciones fueron exitosas
        :rtype: bool
        """
        try:
            logging.info("Testeando pin: %d", pin)
            self.change_state("off")
            time.sleep(15)
            return self.change_state("on")
        except Exception as e:
            logging.error("Fallo test de pin %d: %s", pin, e)
            return False


    def cleanup(self) -> None:
        """
        Libera el lock y limpia la configuración de GPIO.

        Siempre debe llamarse al terminar el uso del controlador.
        """
        self._release_lock()
        GPIO.cleanup()
