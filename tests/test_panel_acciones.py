import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget

from interfaz.pyside6 import mainWindow
from interfaz.pyside6.mainWindow import DockMenu, TabPrincipal


@pytest.fixture
def aplicacion():
    return QApplication.instance() or QApplication([])


def test_menu_calendarios_contiene_subitems(aplicacion):
    menu = DockMenu(TabPrincipal())

    assert menu.item_calendarios.text(0).strip() == "🗓️ Calendarios"
    assert menu.item_calendarios.childCount() == 2
    assert menu.item_calendario_academico.text(0).strip() == "📚 Calendario Académico"
    assert menu.item_calendario_institucional.text(0).strip() == "🏛️ Calendario Institucional"
    assert menu.item_calendario_academico.data(
        0,
        Qt.ItemDataRole.UserRole,
    ) == {"name": "calendario_academico"}
    assert menu.item_calendario_institucional.data(
        0,
        Qt.ItemDataRole.UserRole,
    ) == {"name": "calendario_institucional"}


def test_subitem_calendario_academico_abre_una_pestana(aplicacion, monkeypatch):
    class VistaCalendario(QWidget):
        pass

    monkeypatch.setattr(mainWindow, "CalendarioAcademico", VistaCalendario)
    tabs = TabPrincipal()
    menu = DockMenu(tabs)

    menu.on_item_clicked(menu.item_calendario_academico, 0)
    menu.on_item_clicked(menu.item_calendario_academico, 0)

    assert tabs.count() == 1
    assert tabs.tabText(0) == "Calendario Académico"


def test_subitem_calendario_institucional_abre_una_pestana(aplicacion, monkeypatch):
    class VistaCalendario(QWidget):
        pass

    monkeypatch.setattr(mainWindow, "CalendarioInstitucional", VistaCalendario)
    tabs = TabPrincipal()
    menu = DockMenu(tabs)

    menu.on_item_clicked(menu.item_calendario_institucional, 0)
    menu.on_item_clicked(menu.item_calendario_institucional, 0)

    assert tabs.count() == 1
    assert tabs.tabText(0) == "Calendario Institucional"
