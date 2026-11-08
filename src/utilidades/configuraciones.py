# configuraciones.py
# ------------------
# Aqui vamos a tener las configuraciones importantes del sistema

import platform
from datetime import datetime
from pathlib import Path
from getpass import getuser
import sqlite3

from utilidades.logger import LOGGER, configurar_logger

# Constantes
# -----------
# 'Windows' / 'Linux' / 'Darwin'
SYSTEM_NAME = platform.system()
USER_NAME = getuser()
USER_PATH = Path.home()
CONFIG_DIR_APP = None
CONFIG_CRONO = None
CONFIG_APP = None
BASE_DATOS_CRONO = None


def path_script() -> Path:
    return Path(__file__).parent.parent.parent.joinpath(
        "scripts", "estructura_db_singleton_estudiante.sql"
    )


def obtener_directorio_configuracion(sistema: str) -> Path:
    if sistema == "Windows":
        return USER_PATH.joinpath("AppData", "Roaming", "cronos")
    if sistema == "Linux":
        return USER_PATH.joinpath(".config", "cronos")
    if sistema == "Darwin":
        return USER_PATH.joinpath("Library", "Application Support", "cronos")
    raise ValueError(f"Sistema operativo no soportado: {sistema}")


def inicializar_configuracion(sistema: str = SYSTEM_NAME) -> Path:
    global CONFIG_DIR_APP, CONFIG_APP, CONFIG_CRONO, BASE_DATOS_CRONO

    CONFIG_DIR_APP = obtener_directorio_configuracion(sistema)
    CONFIG_APP = CONFIG_DIR_APP

    try:
        CONFIG_DIR_APP.mkdir(parents=True, exist_ok=True)
        LOGGER.info("Directorio de configuracion: %s", CONFIG_DIR_APP)
        CONFIG_CRONO = CONFIG_DIR_APP.joinpath("crono.conf")
        if not CONFIG_CRONO.exists():
            CONFIG_CRONO.write_text(
                f"# se creo: {datetime.now()}",
                encoding="utf-8",
            )
        # Cambiamos a el nombre de la base de datos "cronos.db" a "test_cronos.db"
        BASE_DATOS_CRONO = CONFIG_DIR_APP.joinpath("test_cronos.db")
        if not BASE_DATOS_CRONO.exists():
            script_sql = path_script()
            if not script_sql.is_file():
                raise ValueError(f"No se encontro el script SQL: {script_sql}")

            sql = script_sql.read_text(encoding="utf-8")
            if sql.strip():
                with sqlite3.connect(BASE_DATOS_CRONO) as db:
                    db.executescript(sql)
                LOGGER.info("Base de datos creada: %s", BASE_DATOS_CRONO)
    except OSError as error:
        LOGGER.error("No se pudo inicializar la configuracion: %s", error)
        raise ValueError(
            f"No se pudo inicializar el directorio de configuracion: " f"{CONFIG_DIR_APP}"
        ) from error
    except sqlite3.Error as error:
        LOGGER.error("No se pudo crear la base de datos: %s", error)
        raise ValueError(f"No se pudo crear la base de datos: {BASE_DATOS_CRONO}") from error

    return CONFIG_CRONO


CONFIG_CRONO = inicializar_configuracion()
if CONFIG_DIR_APP is not None:
    configurar_logger(directorio=CONFIG_DIR_APP)
