import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOGGER_NAME = "cronos"
FORMATO_LOG = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
NOMBRE_ARCHIVO_LOG = "cronos.log"


def configurar_logger(
    nombre: str = LOGGER_NAME,
    directorio: Path | None = None,
    nivel: int = logging.INFO,
) -> logging.Logger:
    if directorio is None:
        directorio = Path.home().joinpath(".cronos")

    logger = logging.getLogger(nombre)
    logger.setLevel(nivel)

    if logger.handlers:
        archivo_log = directorio.joinpath(NOMBRE_ARCHIVO_LOG)
        tiene_directorio = any(
            isinstance(handler, RotatingFileHandler)
            and Path(handler.baseFilename).resolve() == archivo_log.resolve()
            for handler in logger.handlers
        )
        if not tiene_directorio:
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
        else:
            return logger

    directorio.mkdir(parents=True, exist_ok=True)
    archivo_log = directorio.joinpath(NOMBRE_ARCHIVO_LOG)
    formato = logging.Formatter(FORMATO_LOG)

    archivo_handler = RotatingFileHandler(
        archivo_log,
        maxBytes=1_048_576,
        backupCount=3,
        encoding="utf-8",
    )
    archivo_handler.setLevel(nivel)
    archivo_handler.setFormatter(formato)

    consola_handler = logging.StreamHandler()
    consola_handler.setLevel(logging.WARNING)
    consola_handler.setFormatter(formato)

    logger.addHandler(archivo_handler)
    logger.addHandler(consola_handler)
    logger.propagate = False
    return logger


LOGGER = configurar_logger()
