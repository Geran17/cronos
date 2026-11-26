import os
import sqlite3
from pathlib import Path
from uuid import uuid4

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtSql import QSqlDatabase
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QDate

from interfaz.pyside6 import inscripciones
from interfaz.pyside6.inscripciones import DialogoInscripcion, Inscripciones


@pytest.fixture
def aplicacion():
    return QApplication.instance() or QApplication([])


def test_crud_y_busqueda_de_inscripciones(tmp_path, monkeypatch, aplicacion):
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "estructura_db_singleton_estudiante.sql"
    )
    database_path = tmp_path / "inscripciones.db"
    with sqlite3.connect(database_path) as connection:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        connection.execute(
            "INSERT INTO Asignatura (codigo, nombre, credito) "
            "VALUES ('INF101', 'Programación', 4)"
        )
        connection.execute(
            "INSERT INTO Profesor (nombre, apellido) VALUES ('Ana', 'Pérez')"
        )

    connection_name = f"inscripciones-test-{uuid4()}"
    database = QSqlDatabase.addDatabase("QSQLITE", connection_name)
    database.setDatabaseName(str(database_path))
    assert database.open(), database.lastError().text()
    monkeypatch.setattr(inscripciones, "obtener_conexion", lambda: database)

    page = Inscripciones()
    assert page.modelo is not None
    add_dialog = DialogoInscripcion(page.modelo, page.tabla)
    assert add_dialog.date_fecha.calendarPopup()
    add_dialog.combo_profesor.setCurrentIndex(1)
    add_dialog.combo_semestre.setCurrentIndex(
        add_dialog.combo_semestre.findData("1er Semestre")
    )
    add_dialog.combo_periodo.setCurrentIndex(
        add_dialog.combo_periodo.findData("2do. Periodo")
    )
    add_dialog.check_fecha.setChecked(True)
    add_dialog.date_fecha.setDate(QDate(2025, 3, 1))
    add_dialog.line_seccion.setText("A1")
    add_dialog.line_puntaje.setText("30")
    add_dialog.line_nota.setText("88")
    add_dialog.combo_estado.setCurrentText("Aprobado")
    add_dialog.on_aplicar()
    assert page.modelo.select()
    assert page.modelo.rowCount() == 1

    edit_dialog = DialogoInscripcion(page.modelo, page.tabla, fila=0)
    assert edit_dialog.combo_semestre.currentData() == "1er Semestre"
    assert edit_dialog.combo_periodo.currentData() == "2do. Periodo"
    assert edit_dialog.check_fecha.isChecked()
    assert edit_dialog.date_fecha.date() == QDate(2025, 3, 1)
    assert edit_dialog.line_nota.text() == "88.0"
    edit_dialog.line_nota.setText("91")
    edit_dialog.on_aplicar()
    assert page.modelo.select()
    assert page.modelo.record(0).value("nota") == 91

    optional_professor_dialog = DialogoInscripcion(page.modelo, page.tabla)
    assert not optional_professor_dialog.check_fecha.isChecked()
    optional_professor_dialog.combo_semestre.setCurrentIndex(
        optional_professor_dialog.combo_semestre.findData("2do Semestre")
    )
    optional_professor_dialog.line_seccion.setText("B1")
    optional_professor_dialog.on_aplicar()
    assert page.modelo.select()
    assert page.modelo.rowCount() == 2

    page.on_buscar("Pérez")
    assert page.modelo.rowCount() == 1
    page.on_buscar("sin coincidencia")
    assert page.modelo.rowCount() == 0
    page.on_buscar("")

    page.tabla.selectRow(0)
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )
    page.on_dialogo_eliminar()
    assert page.modelo.rowCount() == 1
    assert page.modelo.record(0).value("nombre") in ("", None)

    del add_dialog, edit_dialog, optional_professor_dialog
    page.modelo = None
    page.deleteLater()
    aplicacion.processEvents()
    database.close()
    del database
    QSqlDatabase.removeDatabase(connection_name)
