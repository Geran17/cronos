from PySide6.QtGui import QCloseEvent

from utilidades.configuraciones import CONFIG_CRONO
from PySide6.QtWidgets import (
    QMainWindow,
    QDockWidget,
    QWidget,
    QLabel,
    QVBoxLayout,
    QTreeWidgetItem,
    QTreeWidget,
)
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QFont

# ==================================================================================================
# Ventana Principal de la Aplicacion: Cronos
# ==================================================================================================
"""
Descripción del módulo o sección principal

Author: Geran
Date: 2026-11-09
Version: 1.0

"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cronos -- Organiza tus actividades de la Facu !!!!")
        self.resize(900, 600)

        self.dock_menu = DockMenu()
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_menu)

        # Configuramos la variable "self.setting"
        # --------------------------------------------------
        self.setting = None

        if CONFIG_CRONO is not None:
            self.setting = QSettings(str(CONFIG_CRONO), QSettings.Format.IniFormat)
            geo = self.setting.value("mainWindow/geometria")
            if geo is not None:
                self.restoreGeometry(geo)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.setting is not None:
            self.setting.setValue("MainWindow/geometria", self.saveGeometry())
            self.setting.sync()
        return super().closeEvent(event)


class DockMenu(QDockWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Menu Principal")
        self.setObjectName("DockMenu")
        # widget que contendra el menu
        self.widget_principal = QWidget()

        self._cargar_menu()

    def _cargar_menu(self):

        layout_v = QVBoxLayout()
        self.widget_principal.setLayout(layout_v)

        self.tree_menu = QTreeWidget()
        self.tree_menu.setColumnCount(2)
        self.tree_menu.setHeaderLabels([" Panel de Acciones ", ""])
        layout_v.addWidget(self.tree_menu)

        self.item_academicos = QTreeWidgetItem()
        self.item_academicos.setText(0, " 🎓 Académicos")
        self.item_academicos.setToolTip(0, "Accede a las funciones academicas")
        self.tree_menu.addTopLevelItem(self.item_academicos)

        # Item falsatantes: Facultades, Carreras, Asignaturas, PreRequisitos, Malla Curricular
        self.item_facultades = QTreeWidgetItem()
        self.item_facultades.setText(0, " 🏛️ Facultades")
        self.item_facultades.setToolTip(0, " Organiza las Facultades a las que vas !!!")
        self.item_academicos.addChild(self.item_facultades)

        self.item_carreras = QTreeWidgetItem()
        self.item_carreras.setText(0, " 🏫 Carreras")
        self.item_carreras.setToolTip(0, "Carga y administra las carreras que llevas")
        self.item_academicos.addChild(self.item_carreras)

        self.item_asiganturas = QTreeWidgetItem()
        self.item_asiganturas.setText(0, " 📚 Asignaturas")
        self.item_asiganturas.setToolTip(
            0, "Carga y administra las asignaturas de las carreras que llevas"
        )
        self.item_academicos.addChild(self.item_asiganturas)

        # items: Dime quien eres, Inscripciones, Actividades
        self.item_alumno = QTreeWidgetItem()
        self.item_alumno.setText(0, " 🧑‍🎓 Alumno")
        self.tree_menu.addTopLevelItem(self.item_alumno)

        font_tree_menu = QFont()
        font_tree_menu.setPointSize(10)
        self.tree_menu.setFont(font_tree_menu)
        self.tree_menu.resizeColumnToContents(0)

        self.setWidget(self.widget_principal)
