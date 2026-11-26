import os
import sqlite3
from pathlib import Path
from uuid import uuid4

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtGui import QColor
from PySide6.QtCore import QSettings
from PySide6.QtSql import QSqlDatabase, QSqlTableModel
from PySide6.QtWidgets import QApplication, QColorDialog, QMessageBox

from interfaz.pyside6 import tipos_actividades
from interfaz.pyside6.tipos_actividades import (
    CLAVE_COLORES,
    DialogoTipoActividad,
    TiposActividades,
)


@pytest.fixture
def aplicacion():
    return QApplication.instance() or QApplication([])


def test_crud_persistiendo_color_en_configuraciones(
    tmp_path,
    monkeypatch,
    aplicacion,
):
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "estructura_db_singleton_estudiante.sql"
    )
    database_path = tmp_path / "tipos_actividades.db"
    with sqlite3.connect(database_path) as connection:
        connection.executescript(schema_path.read_text(encoding="utf-8"))

    connection_name = f"tipos-actividades-test-{uuid4()}"
    database = QSqlDatabase.addDatabase("QSQLITE", connection_name)
    database.setDatabaseName(str(database_path))
    assert database.open(), database.lastError().text()

    config_path = tmp_path / "crono.ini"
    monkeypatch.setattr(tipos_actividades, "CONFIG_CRONO", config_path)
    monkeypatch.setattr(
        tipos_actividades,
        "conectar_modelo",
        lambda: QSqlTableModel(db=database),
    )
    colores = iter((QColor("#336699"), QColor("#FF8800")))
    monkeypatch.setattr(QColorDialog, "getColor", lambda *args, **kwargs: next(colores))

    page = TiposActividades()
    assert page.modelo is not None
    add_dialog = DialogoTipoActividad(page.modelo, page.tabla)
    add_dialog.line_nombre.setText("Examen")
    add_dialog.line_siglas.setText("EX")
    add_dialog.combo_prioridad.setCurrentIndex(
        add_dialog.combo_prioridad.findData("alta")
    )
    add_dialog.on_seleccionar_color()
    add_dialog.on_aplicar()
    assert page.modelo.select()
    assert page.modelo.rowCount() == 1

    tipo_id = page.modelo.record(0).value("id_tipoactividad")
    settings = QSettings(str(config_path), QSettings.Format.IniFormat)
    clave_color = f"{CLAVE_COLORES}/{tipo_id}"
    assert settings.value(clave_color) == "#336699"

    edit_dialog = DialogoTipoActividad(page.modelo, page.tabla, fila=0)
    assert edit_dialog.color == QColor("#336699")
    edit_dialog.on_seleccionar_color()
    edit_dialog.line_nombre.setText("Examen final")
    edit_dialog.on_aplicar()
    settings.sync()
    assert settings.value(clave_color) == "#ff8800"
    page.on_buscar("Examen final")
    assert page.modelo.rowCount() == 1

    page.on_buscar("")
    page.tabla.selectRow(0)
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )
    page.on_dialogo_eliminar()
    assert page.modelo.rowCount() == 0
    assert settings.value(clave_color) is None

    del add_dialog, edit_dialog, settings
    page.modelo = None
    page.deleteLater()
    aplicacion.processEvents()
    database.close()
    del database
    QSqlDatabase.removeDatabase(connection_name)
