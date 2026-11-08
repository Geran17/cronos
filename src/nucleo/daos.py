from abc import ABC, abstractmethod
import sqlite3
from utilidades.configuraciones import BASE_DATOS_CRONO, LOGGER
from nucleo.dtos import *

# --------------- BaseDatosSQLite -----------------------
# Esta clase es una clase abstracta para conectar a la
# base de datos SQLite, con al funciones principales de
# insertar, instanciar, existencia, actualizar, eliminar
# -------------------------------------------------------


class BaseDatosSQLite(ABC):
    def __init__(self) -> None:
        super().__init__()
        self._conexion: sqlite3.Connection | None = None

    def conectar(self) -> sqlite3.Connection:
        """Abre l aconexion a la base de datos"""
        if self._conexion is None:
            try:
                self._conexion = sqlite3.connect(BASE_DATOS_CRONO)
                self._conexion.row_factory = sqlite3.Row
                self._conexion.execute("PRAGMA foreign_keys = ON")
                LOGGER.info("Conexion a la base de datos exitosa!!!")
            except sqlite3.Error as error:
                LOGGER.debug("Error al conectar la base de datos %s", error)
                raise sqlite3.OperationalError("No se pudo establecer la conexión")
        return self._conexion

    def cerrar(self) -> None:
        """Cierra la conexión si está abierta."""
        if self._conexion is not None:
            self._conexion.close()
            self._conexion = None

    # ------------- Metodos abstractos --------------------------

    @abstractmethod
    def insertar(self, dto: object) -> int | None:
        """Inserta un registro y devuelve el id generado."""
        ...

    @abstractmethod
    def existe(self, dto: object) -> bool:
        """Verifica si un registro existe, por medio de uno de sus campos unicos"""
        ...

    @abstractmethod
    def instancie(self, dto: object) -> bool:
        """Instancia un objeto mediante un de sus campos unicos"""
        ...

    @abstractmethod
    def eliminar(self, dto: object) -> bool:
        """Elimna un objeto mediante un de sus campos unicos"""
        ...

    @abstractmethod
    def actualizar(self, dto: object) -> bool:
        """Actualiza un objeto mediante su campo de registro unico ID"""
        ...


class EstudianteDAO(BaseDatosSQLite):
    def __init__(self) -> None:
        super().__init__()
        self.sql_insert = "INSERT INTO Estudiante (nombres, apellidos, correo) VALUES (?, ?, ?)"
        self.sql_instancie_id = "SELECT * FROM Estudiante WHERE id_estudiante=?"
        self.sql_instancie_correo = "SELECT * FROM Estudiante WHERE correo=?"
        self.sql_existe_correo = "SELECT count(*) AS correo FROM Estudiante WHERE correo=?"
        self.sql_eliminar_id = "DELETE FROM Estudiante WHERE id_estudiante = ?"
        self.sql_eliminar_correo = "DELETE FROM Estudiante WHERE correo = ?"
        self.sql_actualizar = (
            "UPDATE Estudiante SET nombres=?, apellidos=?, correo=? WHERE id_estudiante = ?"
        )

    def insertar(self, dto: EstudianteDTO) -> int | None:
        if not isinstance(dto, EstudianteDTO):
            return None

        data_insert = (dto.nombres, dto.apellidos, dto.correo)

        # establecemos la conexion a la base de datos y verificamos que no  se None
        conn = self.conectar()
        if conn is None:
            return None
        # Intentamos ejecutar la setencia SQL
        try:
            with conn:
                cursor = conn.execute(self.sql_insert, data_insert)
                return cursor.lastrowid
        except sqlite3.Error as err:
            LOGGER.error("Error al insertar los datos del estudiante: %s", err)
            raise sqlite3.OperationalError("Error al tratar de insertar los datos") from err

    def existe(self, dto: EstudianteDTO) -> bool:
        if not isinstance(dto, EstudianteDTO) or dto.correo is None:
            return False

        data_insert = (dto.correo,)
        # establecemos la conexion a la base de datos y verificamos que no  se None
        conn = self.conectar()
        if conn is None:
            return False
        # Intentamos ejecutar la setencia SQL
        try:
            with conn:
                cur = conn.execute(self.sql_existe_correo, data_insert)
                datos = cur.fetchone()
                if datos is None:
                    return False
                return int(datos['correo']) >= 1
        except sqlite3.Error as err:
            LOGGER.error("Error al comprobar si el correo existe: %s", err)
            return False

    def instancie(self, dto: EstudianteDTO) -> bool:
        if not isinstance(dto, EstudianteDTO):
            return False

        if dto.id_estudiante is not None and dto.id_estudiante >= 1:
            conn = self.conectar()
            if conn is None:
                return False
            try:
                with conn:
                    cur = conn.execute(self.sql_instancie_id, (dto.id_estudiante,))
                    datos = cur.fetchone()
                    if datos is None:
                        return False
                    dto.nombres = str(datos['nombres'])
                    dto.apellidos = str(datos['apellidos'])
                    dto.correo = str(datos['correo'])
                    return True
            except sqlite3.Error as err:
                LOGGER.error("Error al tratar de obtener los datos del estudiante: %s", err)
                sqlite3.OperationalError("Error al tratar de obtener los datos del estudiante")

        if dto.correo is not None and dto.correo.find('@') != -1:
            conn = self.conectar()
            if conn is None:
                return False
            try:
                with conn:
                    cur = conn.execute(self.sql_instancie_correo, (dto.correo,))
                    datos = cur.fetchone()
                    if datos is None:
                        return False
                    dto.nombres = str(datos['nombres'])
                    dto.apellidos = str(datos['apellidos'])
                    dto.correo = str(datos['correo'])
                    return True
            except sqlite3.Error as err:
                LOGGER.error("Error al tratar de obtener los datos del estudiante: %s", err)
                sqlite3.OperationalError("Error al tratar de obtener los datos del estudiante")

        return False

    def eliminar(self, dto: EstudianteDTO) -> bool:
        if not isinstance(dto, EstudianteDTO):
            return False

        if dto.id_estudiante is not None and dto.id_estudiante >= 1:
            conn = self.conectar()
            if conn is None:
                return False
            try:
                with conn:
                    conn.execute(self.sql_eliminar_id, (dto.id_estudiante,))
                    return True
            except sqlite3.Error as err:
                LOGGER.error("Error al tratar de eliminar los datos del estudiante: %s", err)
                sqlite3.OperationalError("Error al tratar de eliminar los datos del estudiante")

        if dto.correo is not None and dto.correo.find('@') != -1:
            conn = self.conectar()
            if conn is None:
                return False
            try:
                with conn:
                    conn.execute(self.sql_eliminar_correo, (dto.correo,))
                    return True
            except sqlite3.Error as err:
                LOGGER.error("Error al tratar de obtener los datos del estudiante: %s", err)
                sqlite3.OperationalError("Error al tratar de obtener los datos del estudiante")

        return False

    def actualizar(self, dto: EstudianteDTO) -> bool:
        if not isinstance(dto, EstudianteDTO):
            return False

        data = (dto.nombres, dto.apellidos, dto.correo, dto.id_estudiante)

        conn = self.conectar()
        if conn is None:
            return False

        try:
            with conn:
                conn.execute(self.sql_actualizar, data)
                return True
        except sqlite3.Error as err:
            LOGGER.error("Error al tratar de obtener los datos del estudiante: %s", err)
            sqlite3.OperationalError("Error al tratar de obtener los datos del estudiante")

        return False
