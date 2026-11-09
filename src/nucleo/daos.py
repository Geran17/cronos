from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import fields
import sqlite3
from typing import ClassVar, Iterator

from utilidades.configuraciones import BASE_DATOS_CRONO, LOGGER
from nucleo.dtos import (
    ActividadDTO,
    AsignaturaDTO,
    CalendarioAcademicoDTO,
    CalendarioInstitucionalDTO,
    CarreraDTO,
    EstudianteDTO,
    Facultad,
    HorasSemanalesDTO,
    InscripcionDTO,
    MatriculaDTO,
    MallaCurricularDTO,
    PrerequisitoDTO,
    ProfesorDTO,
    TipoActividadDTO,
)

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
        """Abre la conexión a la base de datos si aún no está abierta."""
        if self._conexion is None:
            if BASE_DATOS_CRONO is None:
                raise sqlite3.OperationalError("La ruta de la base de datos no está configurada")
            try:
                self._conexion = sqlite3.connect(BASE_DATOS_CRONO)
                self._conexion.row_factory = sqlite3.Row
                self._conexion.execute("PRAGMA foreign_keys = ON")
            except sqlite3.Error as error:
                self.cerrar()
                LOGGER.exception("No se pudo establecer la conexión con la base de datos")
                raise sqlite3.OperationalError(
                    "No se pudo establecer la conexión con la base de datos"
                ) from error
        return self._conexion

    @contextmanager
    def _transaccion(self) -> Iterator[sqlite3.Connection]:
        conn = self.conectar()
        try:
            with conn:
                yield conn
        finally:
            self.cerrar()

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
        self.sql_existe_correo = "SELECT count(*) AS cantidad FROM Estudiante WHERE correo=?"
        self.sql_eliminar_id = "DELETE FROM Estudiante WHERE id_estudiante = ?"
        self.sql_eliminar_correo = "DELETE FROM Estudiante WHERE correo = ?"
        self.sql_actualizar = (
            "UPDATE Estudiante SET nombres=?, apellidos=?, correo=? WHERE id_estudiante = ?"
        )

    def insertar(self, dto: EstudianteDTO) -> int | None:
        if not isinstance(dto, EstudianteDTO):
            return None

        data_insert = (dto.nombres, dto.apellidos, dto.correo)

        try:
            with self._transaccion() as conn:
                cursor = conn.execute(self.sql_insert, data_insert)
                return cursor.lastrowid
        except sqlite3.Error as err:
            LOGGER.error("Error al insertar los datos del estudiante: %s", err)
            raise sqlite3.OperationalError(
                "Error al tratar de insertar los datos del estudiante"
            ) from err

    def existe(self, dto: EstudianteDTO) -> bool:
        if not isinstance(dto, EstudianteDTO) or dto.correo is None:
            return False

        try:
            with self._transaccion() as conn:
                datos = conn.execute(self.sql_existe_correo, (dto.correo,)).fetchone()
                return datos is not None and datos["cantidad"] > 0
        except sqlite3.Error as err:
            LOGGER.error("Error al comprobar si el correo existe: %s", err)
            raise sqlite3.OperationalError(
                "Error al comprobar si el correo del estudiante existe"
            ) from err

    def instancie(self, dto: EstudianteDTO) -> bool:
        if not isinstance(dto, EstudianteDTO):
            return False

        if dto.id_estudiante is not None and dto.id_estudiante >= 1:
            sql = self.sql_instancie_id
            parametro = dto.id_estudiante
        elif dto.correo is not None:
            sql = self.sql_instancie_correo
            parametro = dto.correo
        else:
            return False

        try:
            with self._transaccion() as conn:
                datos = conn.execute(sql, (parametro,)).fetchone()
                if datos is None:
                    return False
                dto.id_estudiante = datos["id_estudiante"]
                dto.nombres = datos["nombres"]
                dto.apellidos = datos["apellidos"]
                dto.correo = datos["correo"]
                return True
        except sqlite3.Error as err:
            LOGGER.error("Error al obtener los datos del estudiante: %s", err)
            raise sqlite3.OperationalError(
                "Error al tratar de obtener los datos del estudiante"
            ) from err

    def eliminar(self, dto: EstudianteDTO) -> bool:
        if not isinstance(dto, EstudianteDTO):
            return False

        if dto.id_estudiante is not None and dto.id_estudiante >= 1:
            sql = self.sql_eliminar_id
            parametro = dto.id_estudiante
        elif dto.correo is not None:
            sql = self.sql_eliminar_correo
            parametro = dto.correo
        else:
            return False

        try:
            with self._transaccion() as conn:
                cursor = conn.execute(sql, (parametro,))
                return cursor.rowcount > 0
        except sqlite3.Error as err:
            LOGGER.error("Error al eliminar los datos del estudiante: %s", err)
            raise sqlite3.OperationalError(
                "Error al tratar de eliminar los datos del estudiante"
            ) from err

    def actualizar(self, dto: EstudianteDTO) -> bool:
        if (
            not isinstance(dto, EstudianteDTO)
            or dto.id_estudiante is None
            or dto.id_estudiante < 1
        ):
            return False

        data = (dto.nombres, dto.apellidos, dto.correo, dto.id_estudiante)

        try:
            with self._transaccion() as conn:
                cursor = conn.execute(self.sql_actualizar, data)
                return cursor.rowcount > 0
        except sqlite3.Error as err:
            LOGGER.error("Error al actualizar los datos del estudiante: %s", err)
            raise sqlite3.OperationalError(
                "Error al tratar de actualizar los datos del estudiante"
            ) from err


class EntidadDAO(BaseDatosSQLite):
    """Implementa las operaciones CRUD comunes para un DTO y su tabla."""

    tabla: ClassVar[str]
    tipo_dto: ClassVar[type]
    clave_primaria: ClassVar[tuple[str, ...]]
    claves_unicas: ClassVar[tuple[tuple[str, ...], ...]] = ()
    id_generado: ClassVar[bool] = True

    def __init__(self) -> None:
        super().__init__()
        self.columnas = tuple(campo.name for campo in fields(self.tipo_dto))

    def _es_clave_valida(self, dto: object, columnas: tuple[str, ...]) -> bool:
        for columna in columnas:
            valor = getattr(dto, columna)
            if valor is None:
                return False
            if isinstance(valor, (int, float)) and valor <= 0:
                return False
            if isinstance(valor, str) and not valor:
                return False
        return True

    def _criterio_busqueda(self, dto: object) -> tuple[str, tuple] | None:
        criterios = (self.clave_primaria, *self.claves_unicas)
        for columnas in criterios:
            if self._es_clave_valida(dto, columnas):
                clausula = " AND ".join(f"{columna} = ?" for columna in columnas)
                valores = tuple(getattr(dto, columna) for columna in columnas)
                return clausula, valores
        return None

    def insertar(self, dto: object) -> int | None:
        if not isinstance(dto, self.tipo_dto):
            return None

        columnas = tuple(
            columna
            for columna in self.columnas
            if not (self.id_generado and columna in self.clave_primaria)
        )
        placeholders = ", ".join("?" for _ in columnas)
        columnas_sql = ", ".join(columnas)
        valores = tuple(getattr(dto, columna) for columna in columnas)
        sql = f"INSERT INTO {self.tabla} ({columnas_sql}) VALUES ({placeholders})"

        try:
            with self._transaccion() as conn:
                cursor = conn.execute(sql, valores)
                return cursor.lastrowid if self.id_generado else None
        except sqlite3.Error as err:
            LOGGER.error("Error al insertar datos en %s: %s", self.tabla, err)
            raise sqlite3.OperationalError(
                f"Error al tratar de insertar datos en {self.tabla}"
            ) from err

    def existe(self, dto: object) -> bool:
        if not isinstance(dto, self.tipo_dto):
            return False
        criterio = self._criterio_busqueda(dto)
        if criterio is None:
            return False
        clausula, valores = criterio

        try:
            with self._transaccion() as conn:
                fila = conn.execute(
                    f"SELECT 1 FROM {self.tabla} WHERE {clausula} LIMIT 1",
                    valores,
                ).fetchone()
                return fila is not None
        except sqlite3.Error as err:
            LOGGER.error("Error al comprobar existencia en %s: %s", self.tabla, err)
            raise sqlite3.OperationalError(
                f"Error al comprobar existencia en {self.tabla}"
            ) from err

    def instancie(self, dto: object) -> bool:
        if not isinstance(dto, self.tipo_dto):
            return False
        criterio = self._criterio_busqueda(dto)
        if criterio is None:
            return False
        clausula, valores = criterio

        try:
            with self._transaccion() as conn:
                fila = conn.execute(
                    f"SELECT {', '.join(self.columnas)} FROM {self.tabla} "
                    f"WHERE {clausula} LIMIT 1",
                    valores,
                ).fetchone()
                if fila is None:
                    return False
                for columna in self.columnas:
                    setattr(dto, columna, fila[columna])
                return True
        except sqlite3.Error as err:
            LOGGER.error("Error al obtener datos de %s: %s", self.tabla, err)
            raise sqlite3.OperationalError(
                f"Error al tratar de obtener datos de {self.tabla}"
            ) from err

    def eliminar(self, dto: object) -> bool:
        if not isinstance(dto, self.tipo_dto):
            return False
        criterio = self._criterio_busqueda(dto)
        if criterio is None:
            return False
        clausula, valores = criterio

        try:
            with self._transaccion() as conn:
                cursor = conn.execute(
                    f"DELETE FROM {self.tabla} WHERE {clausula}",
                    valores,
                )
                return cursor.rowcount > 0
        except sqlite3.Error as err:
            LOGGER.error("Error al eliminar datos de %s: %s", self.tabla, err)
            raise sqlite3.OperationalError(
                f"Error al tratar de eliminar datos de {self.tabla}"
            ) from err

    def actualizar(self, dto: object) -> bool:
        if not isinstance(dto, self.tipo_dto):
            return False
        if not self._es_clave_valida(dto, self.clave_primaria):
            return False

        columnas_actualizables = tuple(
            columna for columna in self.columnas if columna not in self.clave_primaria
        )
        if not columnas_actualizables:
            return False
        asignaciones = ", ".join(f"{columna} = ?" for columna in columnas_actualizables)
        clausula = " AND ".join(f"{columna} = ?" for columna in self.clave_primaria)
        valores = tuple(getattr(dto, columna) for columna in columnas_actualizables)
        valores += tuple(getattr(dto, columna) for columna in self.clave_primaria)

        try:
            with self._transaccion() as conn:
                cursor = conn.execute(
                    f"UPDATE {self.tabla} SET {asignaciones} WHERE {clausula}",
                    valores,
                )
                return cursor.rowcount > 0
        except sqlite3.Error as err:
            LOGGER.error("Error al actualizar datos de %s: %s", self.tabla, err)
            raise sqlite3.OperationalError(
                f"Error al tratar de actualizar datos de {self.tabla}"
            ) from err


class FacultadDAO(EntidadDAO):
    tabla = "Facultad"
    tipo_dto = Facultad
    clave_primaria = ("id_facultad",)
    claves_unicas = (("siglas",),)


class ProfesorDAO(EntidadDAO):
    tabla = "Profesor"
    tipo_dto = ProfesorDTO
    clave_primaria = ("id_profesor",)
    claves_unicas = (("correo",),)


class AsignaturaDAO(EntidadDAO):
    tabla = "Asignatura"
    tipo_dto = AsignaturaDTO
    clave_primaria = ("id_asignatura",)
    claves_unicas = (("codigo",),)


class TipoActividadDAO(EntidadDAO):
    tabla = "TipoActividad"
    tipo_dto = TipoActividadDTO
    clave_primaria = ("id_tipoactividad",)


class CarreraDAO(EntidadDAO):
    tabla = "Carrera"
    tipo_dto = CarreraDTO
    clave_primaria = ("id_carrera",)
    claves_unicas = (("codigo",),)


class HorasSemanalesDAO(EntidadDAO):
    tabla = "HorasSemanales"
    tipo_dto = HorasSemanalesDTO
    clave_primaria = ("id_horassemanales",)
    claves_unicas = (("id_asignatura",),)


class InscripcionDAO(EntidadDAO):
    tabla = "Inscripcion"
    tipo_dto = InscripcionDTO
    clave_primaria = ("id_inscripcion",)


class ActividadDAO(EntidadDAO):
    tabla = "Actividad"
    tipo_dto = ActividadDTO
    clave_primaria = ("id_actividad",)


class MatriculaDAO(EntidadDAO):
    tabla = "Matricula"
    tipo_dto = MatriculaDTO
    clave_primaria = ("id_matricula",)


class CalendarioAcademicoDAO(EntidadDAO):
    tabla = "Calendario_Academico"
    tipo_dto = CalendarioAcademicoDTO
    clave_primaria = ("id_calendario",)


class CalendarioInstitucionalDAO(EntidadDAO):
    tabla = "Calendario_Institucional"
    tipo_dto = CalendarioInstitucionalDTO
    clave_primaria = ("id_evento",)


class MallaCurricularDAO(EntidadDAO):
    tabla = "Malla_Curricular"
    tipo_dto = MallaCurricularDTO
    clave_primaria = ("id_carrera", "id_asignatura")
    id_generado = False


class PrerequisitoDAO(EntidadDAO):
    tabla = "Prerequisito"
    tipo_dto = PrerequisitoDTO
    clave_primaria = ("id_asignatura", "id_prerequisito")
    id_generado = False
