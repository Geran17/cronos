import os
import sqlite3
from pathlib import Path
from uuid import uuid4

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QSettings
from PySide6.QtGui import QColor
from PySide6.QtSql import QSqlDatabase
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QMessageBox,
    QStyleOptionViewItem,
)

from interfaz.pyside6 import actividades
from interfaz.pyside6.actividades import (
    INDICES_COLUMNAS,
    Actividades,
    DelegadoColorActividad,
    DialogoActividad,
    DialogoSeleccionInscripcion,
)
from interfaz.pyside6.tipos_actividades import CLAVE_COLORES


@pytest.fixture
def aplicacion():
    return QApplication.instance() or QApplication([])


def test_crud_actividad(tmp_path, monkeypatch, aplicacion):
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "estructura_db_singleton_estudiante.sql"
    )
    database_path = tmp_path / "actividades.db"
    with sqlite3.connect(database_path) as connection:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        connection.execute(
            "INSERT INTO Asignatura (codigo, nombre, credito) VALUES (?, ?, ?)",
            ("MAT101", "Matemática", 4),
        )
        connection.execute(
            "INSERT INTO Inscripcion "
            "(id_asignatura, fecha_inscripcion, semestre, periodo, seccion, estado) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (1, "2025-03-01", "1er Semestre", "1er Periodo", "Seccion B", "Aprobado"),
        )
        connection.execute(
            "INSERT INTO Inscripcion "
            "(id_asignatura, fecha_inscripcion, semestre, periodo, seccion, estado) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (1, "2026-03-01", "2do Semestre", "2do. Periodo", "Seccion C", "Cursando"),
        )
        connection.execute(
            "INSERT INTO TipoActividad (nombre, siglas, prioridad) "
            "VALUES (?, ?, ?)",
            ("Examen", "EX", "alta"),
        )
        connection.execute(
            "INSERT INTO TipoActividad (nombre, siglas, prioridad) "
            "VALUES (?, ?, ?)",
            ("Tarea", "TA", "media"),
        )

    connection_name = f"actividades-test-{uuid4()}"
    database = QSqlDatabase.addDatabase("QSQLITE", connection_name)
    database.setDatabaseName(str(database_path))
    assert database.open(), database.lastError().text()
    monkeypatch.setattr(actividades, "obtener_conexion", lambda: database)
    config_path = tmp_path / "crono.ini"
    monkeypatch.setattr(actividades, "CONFIG_CRONO", config_path)
    settings = QSettings(str(config_path), QSettings.Format.IniFormat)
    settings.setValue(f"{CLAVE_COLORES}/1", "#336699")
    settings.sync()

    page = Actividades()
    assert page.modelo is not None

    add_dialog = DialogoActividad(page.modelo, page.tabla)
    assert add_dialog.line_inscripcion.isReadOnly()
    picker = DialogoSeleccionInscripcion(page.modelo.database())
    assert picker.carga_valida
    assert picker.tabla_inscripciones.rowCount() == 2
    assert picker.combo_anio.count() == 3
    assert picker.combo_periodo.count() == 3
    assert picker.combo_estado.count() == 3

    def seleccionar_inscripcion(dialogo):
        fila_2025 = next(
            fila
            for fila in range(dialogo.tabla_inscripciones.rowCount())
            if dialogo.tabla_inscripciones.item(fila, 1).text() == "2025"
        )
        fila_2026 = next(
            fila
            for fila in range(dialogo.tabla_inscripciones.rowCount())
            if dialogo.tabla_inscripciones.item(fila, 1).text() == "2026"
        )
        dialogo.combo_estado.setCurrentIndex(
            dialogo.combo_estado.findData("Cursando")
        )
        assert dialogo.tabla_inscripciones.isRowHidden(fila_2025)
        assert not dialogo.tabla_inscripciones.isRowHidden(fila_2026)
        dialogo.combo_estado.setCurrentIndex(
            dialogo.combo_estado.findData("Aprobado")
        )
        dialogo.combo_periodo.setCurrentIndex(
            dialogo.combo_periodo.findData("1er Periodo")
        )
        assert not dialogo.tabla_inscripciones.isRowHidden(fila_2025)
        assert dialogo.tabla_inscripciones.isRowHidden(fila_2026)
        dialogo.combo_anio.setCurrentIndex(dialogo.combo_anio.findData("2025"))
        assert not dialogo.tabla_inscripciones.isRowHidden(fila_2025)
        assert dialogo.tabla_inscripciones.isRowHidden(fila_2026)
        dialogo.tabla_inscripciones.selectRow(fila_2025)
        dialogo._aceptar()
        return QDialog.DialogCode.Accepted

    monkeypatch.setattr(DialogoSeleccionInscripcion, "exec", seleccionar_inscripcion)
    add_dialog.on_seleccionar_inscripcion()
    assert add_dialog.inscripcion_id == 1
    assert add_dialog.line_inscripcion.text() == (
        "MAT101 - Matemática - Año 2025 - 1er Periodo - Seccion B - Aprobado"
    )
    assert "1er Semestre" not in add_dialog.line_inscripcion.text()
    add_dialog.line_titulo.setText("Examen parcial")
    add_dialog.line_dias.setText("7")
    add_dialog.line_puntaje.setText("20")
    add_dialog.combo_estado.setCurrentIndex(
        add_dialog.combo_estado.findText("Pendiente")
    )
    add_dialog.on_aplicar()

    assert page.modelo.select()
    assert page.modelo.rowCount() == 1
    assert str(page.modelo.record(0).value("titulo")) == "Examen parcial"
    delegado = page.tabla.itemDelegateForColumn(
        INDICES_COLUMNAS["id_tipoactividad"]
    )
    assert isinstance(delegado, DelegadoColorActividad)
    opcion = QStyleOptionViewItem()
    delegado.initStyleOption(
        opcion,
        page.modelo.index(0, INDICES_COLUMNAS["id_tipoactividad"]),
    )
    assert opcion.backgroundBrush.color() == QColor("#336699")

    second_dialog = DialogoActividad(page.modelo, page.tabla)
    second_dialog.inscripcion_id = 2
    second_dialog.line_inscripcion.setText("MAT101 - Matemática - Año 2026")
    second_dialog.combo_tipo.setCurrentIndex(second_dialog.combo_tipo.findData(2))
    second_dialog.line_titulo.setText("Tarea 2026")
    second_dialog.combo_estado.setCurrentIndex(
        second_dialog.combo_estado.findText("Entregada")
    )
    second_dialog.on_aplicar()
    assert page.modelo.rowCount() == 2

    page.combo_filtro_anio.setCurrentIndex(
        page.combo_filtro_anio.findData("2026")
    )
    assert page.modelo.rowCount() == 1
    page.combo_filtro_tipo.setCurrentIndex(
        page.combo_filtro_tipo.findData(1)
    )
    assert page.modelo.rowCount() == 0
    page.combo_filtro_tipo.setCurrentIndex(
        page.combo_filtro_tipo.findData(2)
    )
    page.combo_filtro_estado.setCurrentIndex(
        page.combo_filtro_estado.findData("Pendiente")
    )
    assert page.modelo.rowCount() == 0
    page.combo_filtro_estado.setCurrentIndex(
        page.combo_filtro_estado.findData("Entregada")
    )
    assert page.modelo.rowCount() == 1

    page.combo_filtro_anio.setCurrentIndex(0)
    page.combo_filtro_tipo.setCurrentIndex(0)
    page.combo_filtro_estado.setCurrentIndex(0)
    fila_tarea = next(
        fila
        for fila in range(page.modelo.rowCount())
        if page.modelo.record(fila).value("titulo") == "Tarea 2026"
    )
    page.tabla.selectRow(fila_tarea)
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )
    page.on_dialogo_eliminar()
    assert page.modelo.rowCount() == 1

    edit_dialog = DialogoActividad(page.modelo, page.tabla, fila=0)
    assert edit_dialog.line_inscripcion.text() == (
        "MAT101 - Matemática - Año 2025 - 1er Periodo - Seccion B - Aprobado"
    )
    edit_dialog.line_titulo.setText("Examen final")
    edit_dialog.on_aplicar()
    assert str(page.modelo.record(0).value("titulo")) == "Examen final"

    page.tabla.selectRow(0)
    page.on_dialogo_eliminar()
    assert page.modelo.rowCount() == 0

    del add_dialog, edit_dialog, picker, second_dialog, settings
    page.modelo = None
    page.deleteLater()
    aplicacion.processEvents()
    database.close()
    del database
    QSqlDatabase.removeDatabase(connection_name)
