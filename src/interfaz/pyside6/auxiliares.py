from utilidades.configuraciones import BASE_DATOS_CRONO, LOGGER
from PySide6.QtSql import QSqlDatabase, QSqlTableModel


NOMBRE_CONEXION = "cronos"


def obtener_conexion() -> QSqlDatabase | None:
    """Devuelve la conexión compartida de Cronos, creándola solo una vez."""
    if not BASE_DATOS_CRONO.exists():
        LOGGER.warning("No existe la base de datos: %s", str(BASE_DATOS_CRONO))
        return None

    if QSqlDatabase.contains(NOMBRE_CONEXION):
        conexion = QSqlDatabase.database(NOMBRE_CONEXION)
    else:
        conexion = QSqlDatabase.addDatabase("QSQLITE", NOMBRE_CONEXION)
        conexion.setDatabaseName(str(BASE_DATOS_CRONO))

    if not conexion.isOpen() and not conexion.open():
        LOGGER.error("No se pudo abrir la base de datos: %s", conexion.lastError().text())
        return None

    return conexion


def conectar_modelo() -> QSqlTableModel | None:

    conexion = obtener_conexion()
    if conexion is None:
        return None

    # Ahora conectamos el modelo
    modelo = QSqlTableModel(db=conexion)

    return modelo
