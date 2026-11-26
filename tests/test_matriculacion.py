import os
import sqlite3
from pathlib import Path
from uuid import uuid4

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtSql import QSqlDatabase
from PySide6.QtWidgets import QApplication

from interfaz.pyside6 import matriculacion
from interfaz.pyside6.matriculacion import DialogoMatriculacion, Matriculacion


@pytest.fixture
def aplicacion():
    return QApplication.instance() or QApplication([])


def test_crud_y_busqueda_de_matriculacion(tmp_path, monkeypatch, aplicacion):
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "estructura_db_singleton_estudiante.sql"
    )
    database_path = tmp_path / "matriculacion.db"
    with sqlite3.connect(database_path) as connection:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        connection.execute("INSERT INTO Facultad (nombre, siglas) VALUES ('Ingeniería', 'ING')")
        connection.execute(
            "INSERT INTO Carrera (id_facultad, codigo, nombre) "
            "VALUES (1, 'INF', 'Informática')"
        )

    connection_name = f"matriculacion-test-{uuid4()}"
    database = QSqlDatabase.addDatabase("QSQLITE", connection_name)
    database.setDatabaseName(str(database_path))
    assert database.open(), database.lastError().text()
    monkeypatch.setattr(matriculacion, "obtener_conexion", lambda: database)

    page = Matriculacion()
    assert page.modelo is not None
    add_dialog = DialogoMatriculacion(page.modelo, page.tabla)
    add_dialog.line_ano.setText("2025")
    add_dialog.line_plan.setText("Plan 2025")
    add_dialog.on_aplicar()
    assert page.modelo.select()
    assert page.modelo.rowCount() == 1

    edit_dialog = DialogoMatriculacion(page.modelo, page.tabla, fila=0)
    assert edit_dialog.line_ano.text() == "2025"
    assert edit_dialog.line_plan.text() == "Plan 2025"
    edit_dialog.line_ano.setText("2026")
    edit_dialog.on_aplicar()
    assert page.modelo.select()
    assert page.modelo.record(0).value("ano_matriculacion") == 2026

    page.on_buscar("INF")
    assert page.modelo.rowCount() == 1
    page.on_buscar("sin coincidencia")
    assert page.modelo.rowCount() == 0

    del add_dialog, edit_dialog
    page.modelo = None
    page.deleteLater()
    aplicacion.processEvents()
    database.close()
    del database
    QSqlDatabase.removeDatabase(connection_name)
