import sqlite3
from pathlib import Path

import pytest

from nucleo import daos
from nucleo.dtos import EstudianteDTO


@pytest.fixture
def dao(tmp_path, monkeypatch):
    database_path = tmp_path / "cronos.db"
    schema_path = Path(__file__).resolve().parents[1] / "scripts" / (
        "estructura_db_singleton_estudiante.sql"
    )
    with sqlite3.connect(database_path) as connection:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
    monkeypatch.setattr(daos, "BASE_DATOS_CRONO", database_path)
    return daos.EstudianteDAO()


def estudiante(**datos):
    valores = {
        "nombres": "Ana",
        "apellidos": "Pérez",
        "correo": "ana@example.com",
    }
    valores.update(datos)
    return EstudianteDTO(**valores)


def test_insertar_devuelve_id_y_cierra_conexion(dao):
    assert dao.insertar(estudiante()) == 1
    assert dao._conexion is None


def test_existe_busca_por_correo(dao):
    assert dao.insertar(estudiante()) == 1

    assert dao.existe(estudiante(correo="ana@example.com"))
    assert not dao.existe(estudiante(correo="otro@example.com"))
    assert dao._conexion is None


@pytest.mark.parametrize("criterio", ["id", "correo"])
def test_instancie_carga_todos_los_campos_incluido_id(dao, criterio):
    dao.insertar(estudiante())
    if criterio == "id":
        dto = estudiante(id_estudiante=1)
    else:
        dto = EstudianteDTO(correo="ana@example.com")

    assert dao.instancie(dto)
    assert dto.to_dict == {
        "id_estudiante": 1,
        "nombres": "Ana",
        "apellidos": "Pérez",
        "correo": "ana@example.com",
    }
    assert dao._conexion is None


def test_actualizar_devuelve_false_si_no_hay_registro_y_actualiza_si_existe(dao):
    assert not dao.actualizar(estudiante(id_estudiante=1, nombres="Otro"))
    dao.insertar(estudiante())
    dto = estudiante(id_estudiante=1, nombres="Ana María")

    assert dao.actualizar(dto)
    actualizado = estudiante(id_estudiante=1)
    assert dao.instancie(actualizado)
    assert actualizado.nombres == "Ana María"
    assert dao._conexion is None


def test_eliminar_indica_si_el_registro_existia(dao):
    assert not dao.eliminar(estudiante(id_estudiante=1))
    dao.insertar(estudiante())

    assert dao.eliminar(estudiante(id_estudiante=1))
    assert not dao.eliminar(estudiante(id_estudiante=1))
    assert dao._conexion is None


def test_error_sql_es_propaga_y_cierra_conexion(dao, monkeypatch, tmp_path):
    database_path = tmp_path / "sin_esquema.db"
    monkeypatch.setattr(daos, "BASE_DATOS_CRONO", database_path)

    with pytest.raises(sqlite3.OperationalError):
        dao.existe(estudiante())

    assert dao._conexion is None
