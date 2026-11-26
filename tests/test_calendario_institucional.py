import os
import sqlite3
from pathlib import Path
from uuid import uuid4

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QDate
from PySide6.QtSql import QSqlDatabase
from PySide6.QtWidgets import QApplication, QMessageBox

from interfaz.pyside6 import calendario_institucional
from interfaz.pyside6.calendario_institucional import (
    CalendarioInstitucional,
    DialogoCalendarioInstitucional,
)


@pytest.fixture
def aplicacion():
    return QApplication.instance() or QApplication([])


def test_crud_calendario_institucional(tmp_path, monkeypatch, aplicacion):
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "estructura_db_singleton_estudiante.sql"
    )
    database_path = tmp_path / "calendario_institucional.db"
    with sqlite3.connect(database_path) as connection:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        connection.execute(
            "INSERT INTO Facultad (nombre, siglas) VALUES (?, ?)",
            ("Facultad de Ciencias", "FC"),
        )

    connection_name = f"calendario-institucional-test-{uuid4()}"
    database = QSqlDatabase.addDatabase("QSQLITE", connection_name)
    database.setDatabaseName(str(database_path))
    assert database.open(), database.lastError().text()
    monkeypatch.setattr(calendario_institucional, "obtener_conexion", lambda: database)

    page = CalendarioInstitucional()
    assert page.modelo is not None
    dialogo_agregar = DialogoCalendarioInstitucional(page.modelo, page.tabla)
    dialogo_agregar.text_descripcion.setPlainText("Aniversario de la institución")
    dialogo_agregar.line_tipo_evento.setText("Aniversario")
    dialogo_agregar.date_inicio.setDate(QDate(2026, 8, 15))
    dialogo_agregar.check_fecha_fin.setChecked(True)
    dialogo_agregar.date_fin.setDate(QDate(2026, 8, 15))
    dialogo_agregar.check_es_fijo.setChecked(True)
    dialogo_agregar.line_estado.setText("Activo")
    dialogo_agregar.check_fecha_registro.setChecked(True)
    dialogo_agregar.date_registro.setDate(QDate(2026, 1, 10))
    dialogo_agregar.text_observaciones.setPlainText("Se repite cada año")
    dialogo_agregar.on_aplicar()

    assert page.modelo.select()
    assert page.modelo.rowCount() == 1
    registro = page.modelo.record(0)
    assert registro.value("fecha_inicio") == "2026-08-15"
    assert registro.value("fecha_fin") == "2026-08-15"
    assert registro.value("descripcion") == "Aniversario de la institución"
    assert registro.value("tipo_evento") == "Aniversario"
    assert registro.value("es_fijo") == 1
    assert registro.value("estado") == "Activo"
    assert registro.value("fecha_registro") == "2026-01-10"

    dialogo_editar = DialogoCalendarioInstitucional(page.modelo, page.tabla, fila=0)
    assert dialogo_editar.combo_facultad.currentData() == 1
    assert dialogo_editar.check_es_fijo.isChecked()
    dialogo_editar.line_estado.setText("Suspendido")
    dialogo_editar.on_aplicar()
    assert page.modelo.record(0).value("estado") == "Suspendido"

    page.on_buscar("Facultad de Ciencias")
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
