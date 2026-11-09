import sqlite3
from pathlib import Path

import pytest

from nucleo.daos import (
    ActividadDAO,
    AsignaturaDAO,
    CalendarioAcademicoDAO,
    CalendarioInstitucionalDAO,
    CarreraDAO,
    FacultadDAO,
    HorasSemanalesDAO,
    InscripcionDAO,
    MatriculaDAO,
    MallaCurricularDAO,
    PrerequisitoDAO,
    ProfesorDAO,
    TipoActividadDAO,
)
from nucleo.dtos import (
    ActividadDTO,
    AsignaturaDTO,
    CalendarioAcademicoDTO,
    CalendarioInstitucionalDTO,
    CarreraDTO,
    Facultad,
    HorasSemanalesDTO,
    InscripcionDTO,
    MatriculaDTO,
    MallaCurricularDTO,
    PrerequisitoDTO,
    ProfesorDTO,
    TipoActividadDTO,
)


DAO_CASES = [
    (FacultadDAO, Facultad, {"nombre": "Ciencias", "siglas": "CIE"}, "nombre", "Ciencias actualizada"),
    (ProfesorDAO, ProfesorDTO, {"nombre": "Luis", "apellido": "Pérez", "correo": "luis@example.com"}, "nombre", "Luis actualizado"),
    (AsignaturaDAO, AsignaturaDTO, {"codigo": "TEST300", "nombre": "Prueba", "credito": 3.0}, "nombre", "Prueba actualizada"),
    (TipoActividadDAO, TipoActividadDTO, {"nombre": "Examen"}, "nombre", "Examen actualizado"),
    (CarreraDAO, CarreraDTO, {"id_facultad": 1, "codigo": "TESTC", "nombre": "Prueba"}, "nombre", "Carrera actualizada"),
    (HorasSemanalesDAO, HorasSemanalesDTO, {"id_asignatura": 1, "teoricas": 3.0}, "teoricas", 4.0),
    (InscripcionDAO, InscripcionDTO, {"id_asignatura": 1}, "estado", "Aprobado"),
    (ActividadDAO, ActividadDTO, {"id_inscripcion": 1, "id_tipoactividad": 1, "titulo": "Prueba"}, "titulo", "Prueba actualizada"),
    (MatriculaDAO, MatriculaDTO, {"id_carrera": 1}, "plan", "Plan actualizado"),
    (
        CalendarioAcademicoDAO,
        CalendarioAcademicoDTO,
        {
            "id_facultad": 1,
            "periodo_academico": "2025-1",
            "actividad": "Inicio de clases",
            "fecha_inicio": "2025-01-10",
        },
        "actividad",
        "Clases iniciadas",
    ),
    (
        CalendarioInstitucionalDAO,
        CalendarioInstitucionalDTO,
        {
            "id_facultad": 1,
            "fecha_inicio": "2025-01-01",
            "descripcion": "Feriado",
            "tipo_evento": "Institucional",
        },
        "descripcion",
        "Feriado actualizado",
    ),
    (MallaCurricularDAO, MallaCurricularDTO, {"id_carrera": 1, "id_asignatura": 2}, None, None),
    (PrerequisitoDAO, PrerequisitoDTO, {"id_asignatura": 2, "id_prerequisito": 1}, None, None),
]


@pytest.fixture
def database_path(tmp_path):
    database_path = tmp_path / "cronos.db"
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "estructura_db_singleton_estudiante.sql"
    )
    with sqlite3.connect(database_path) as connection:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        connection.executescript(
            """
            INSERT INTO Facultad (nombre, siglas) VALUES ('Ingeniería', 'ING');
            INSERT INTO Profesor (nombre, apellido) VALUES ('Ana', 'García');
            INSERT INTO Asignatura (codigo, nombre, credito)
                VALUES ('BASE100', 'Fundamentos', 3), ('BASE200', 'Avanzado', 4);
            INSERT INTO TipoActividad (nombre) VALUES ('Tarea');
            INSERT INTO Carrera (id_facultad, codigo, nombre)
                VALUES (1, 'BASEC', 'Carrera base');
            INSERT INTO Inscripcion (id_asignatura) VALUES (2);
            """
        )
    return database_path


@pytest.mark.parametrize(
    ("dao_type", "dto_type", "datos", "columna_actualizable", "valor_actualizado"),
    DAO_CASES,
)
def test_dao_crud_para_cada_tabla(
    dao_type,
    dto_type,
    datos,
    columna_actualizable,
    valor_actualizado,
    database_path,
    monkeypatch,
):
    monkeypatch.setattr("nucleo.daos.BASE_DATOS_CRONO", database_path)
    dao = dao_type()
    dto = dto_type(**datos)

    nuevo_id = dao.insertar(dto)
    if dao.id_generado:
        assert nuevo_id is not None
    else:
        assert nuevo_id is None

    if dao.id_generado:
        setattr(dto, dao.clave_primaria[0], nuevo_id)
    assert dao.existe(dto)

    consultado = dto_type(**datos)
    for columna in dao.clave_primaria:
        setattr(consultado, columna, getattr(dto, columna))
    assert dao.instancie(consultado)
    assert all(
        getattr(consultado, columna) == getattr(dto, columna)
        for columna in dao.columnas
    )

    if columna_actualizable is not None:
        setattr(consultado, columna_actualizable, valor_actualizado)
        assert dao.actualizar(consultado)
        verificado = dto_type(**{columna: getattr(consultado, columna) for columna in dao.clave_primaria})
        assert dao.instancie(verificado)
        assert getattr(verificado, columna_actualizable) == valor_actualizado
    else:
        assert not dao.actualizar(consultado)

    assert dao.eliminar(consultado)
    assert not dao.existe(consultado)
    assert dao._conexion is None
