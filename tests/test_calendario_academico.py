import os
import sqlite3
from pathlib import Path
from uuid import uuid4

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QDate
from PySide6.QtSql import QSqlDatabase
from PySide6.QtWidgets import QApplication, QMessageBox

from interfaz.pyside6 import calendario_academico
from interfaz.pyside6.calendario_academico import (
    CalendarioAcademico,
    DialogoCalendarioAcademico,
)


@pytest.fixture
def aplicacion():
    return QApplication.instance() or QApplication([])


def test_crud_calendario_academico(tmp_path, monkeypatch, aplicacion):
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "estructura_db_singleton_estudiante.sql"
    )
    database_path = tmp_path / "calendario_academico.db"
    with sqlite3.connect(database_path) as connection:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        connection.execute(
            "INSERT INTO Facultad (nombre, siglas) VALUES (?, ?)",
            ("Facultad de Ciencias", "FC"),
        )

    connection_name = f"calendario-academico-test-{uuid4()}"
    database = QSqlDatabase.addDatabase("QSQLITE", connection_name)
    database.setDatabaseName(str(database_path))
    assert database.open(), database.lastError().text()
    monkeypatch.setattr(calendario_academico, "obtener_conexion", lambda: database)

    page = CalendarioAcademico()
    assert page.modelo is not None
    dialogo_agregar = DialogoCalendarioAcademico(page.modelo, page.tabla)
    dialogo_agregar.line_periodo.setText("2026-1")
    dialogo_agregar.line_actividad.setText("Inicio de clases")
    dialogo_agregar.date_inicio.setDate(QDate(2026, 3, 2))
    dialogo_agregar.check_fecha_fin.setChecked(True)
    dialogo_agregar.date_fin.setDate(QDate(2026, 3, 6))
    dialogo_agregar.line_hora.setText("09:00")
    dialogo_agregar.text_detalle.setPlainText("Comienzo del período")
    dialogo_agregar.text_original.setPlainText("Fuente institucional")
    dialogo_agregar.on_aplicar()

    assert page.modelo.select()
    assert page.modelo.rowCount() == 1
    registro = page.modelo.record(0)
    assert registro.value("periodo_academico") == "2026-1"
    assert registro.value("actividad") == "Inicio de clases"
    assert registro.value("fecha_inicio") == "2026-03-02"
    assert registro.value("fecha_fin") == "2026-03-06"
    assert registro.value("hora") == "09:00"

    dialogo_editar = DialogoCalendarioAcademico(page.modelo, page.tabla, fila=0)
    assert dialogo_editar.combo_facultad.currentData() == 1
    dialogo_editar.line_actividad.setText("Inicio del período")
    dialogo_editar.on_aplicar()
    assert page.modelo.record(0).value("actividad") == "Inicio del período"

    page.on_buscar("institucional")
    assert page.modelo.rowCount() == 1
    page.on_buscar("sin coincidencias")
    assert page.modelo.rowCount() == 0
    page.on_buscar("")
    page.tabla.selectRow(0)
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )
    page.on_dialogo_eliminar()
    assert page.modelo.rowCount() == 0

    del dialogo_agregar, dialogo_editar
    page.modelo = None
    page.deleteLater()
    aplicacion.processEvents()
    database.close()
    del database
    QSqlDatabase.removeDatabase(connection_name)
