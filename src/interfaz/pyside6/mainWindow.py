from PySide6.QtGui import QCloseEvent

from utilidades.configuraciones import CONFIG_CRONO, LOGGER
from PySide6.QtWidgets import (
    QMainWindow,
    QDockWidget,
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTreeWidgetItem,
    QTreeWidget,
    QGridLayout,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QComboBox,
    QLabel,
    QPushButton,
    QMessageBox,
)
from PySide6.QtSql import QSqlQuery
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QFont
from interfaz.pyside6.facultades import Facultades
from interfaz.pyside6.carreras import Carreras
from interfaz.pyside6.asignaturas import Asignaturas
from interfaz.pyside6.horas_semanales import HorasSemanales
from interfaz.pyside6.prerequisitos import Prerequisitos
from interfaz.pyside6.malla_curricular import MallaCurricular
from interfaz.pyside6.profesores import Profesores
from interfaz.pyside6.estudiante import DialogoEstudiante
from interfaz.pyside6.matriculacion import Matriculacion
from interfaz.pyside6.inscripciones import Inscripciones
from interfaz.pyside6.tipos_actividades import TiposActividades
from interfaz.pyside6.actividades import Actividades
from interfaz.pyside6.calendario_academico import CalendarioAcademico
from interfaz.pyside6.calendario_institucional import CalendarioInstitucional
from interfaz.pyside6.auxiliares import obtener_conexion

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

        self.tab_principal = TabPrincipal()
        self.setCentralWidget(self.tab_principal)

        self.dock_menu = DockMenu(self.tab_principal)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_menu)

        # Configuramos la variable "self.setting"
        # --------------------------------------------------
        self.setting: QSettings | None = None

        if CONFIG_CRONO is not None:
            self.setting = QSettings(str(CONFIG_CRONO), QSettings.Format.IniFormat)
            geo = self.setting.value("MainWindow/geometria")
            if geo is not None:
                self.restoreGeometry(geo)

        self.tab_principal.currentChanged.connect(self._guardar_pestana_actual)
        self._restaurar_ultima_pestana()

    def _guardar_pestana_actual(self, indice: int):
        if self.setting is None:
            return

        titulo = self.tab_principal.tabText(indice) if indice >= 0 else ""
        self.setting.setValue("MainWindow/ultima_pestana", titulo)

    def _restaurar_ultima_pestana(self):
        if self.setting is None:
            return

        titulo = str(self.setting.value("MainWindow/ultima_pestana", ""))
        items = {
            "Facultades": self.dock_menu.item_facultades,
            "Carreras": self.dock_menu.item_carreras,
            "Profesores": self.dock_menu.item_profesores,
            "Asignaturas": self.dock_menu.item_asiganturas,
            "Horas Semanales": self.dock_menu.item_horasemanales,
            "Prerrequisitos": self.dock_menu.item_prerequisitos,
            "Malla Curricular": self.dock_menu.item_malla_curricular,
            "Matriculación": self.dock_menu.item_matriculacion,
            "Inscripciones": self.dock_menu.item_inscripciones,
            "Tipos de actividades": self.dock_menu.item_tipos_actividades,
            "Actividades": self.dock_menu.item_actividades_estudiante,
            "Calendario Académico": self.dock_menu.item_calendario_academico,
            "Calendario Institucional": self.dock_menu.item_calendario_institucional,
        }
        item = items.get(titulo)
        if item is None:
            if titulo:
                LOGGER.warning("No se pudo restaurar la pestaña guardada: %s", titulo)
                self.setting.remove("MainWindow/ultima_pestana")
            return

        self.dock_menu.on_item_clicked(item, 0)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.setting is not None:
            self._guardar_pestana_actual(self.tab_principal.currentIndex())
            self.setting.setValue("MainWindow/geometria", self.saveGeometry())
            self.setting.sync()
        return super().closeEvent(event)


class TabPrincipal(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setTabsClosable(True)
        self.setTabPosition(QTabWidget.TabPosition.South)
        self.setMovable(True)
        self.tabCloseRequested.connect(self._cerrar_pestana)

    def _cerrar_pestana(self, indice: int):
        pagina = self.widget(indice)
        self.removeTab(indice)
        if pagina is not None:
            pagina.deleteLater()


class DockMenu(QDockWidget):
    def __init__(self, tab_principal: TabPrincipal):
        super().__init__()

        self.tab_principal = tab_principal
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

        # Incio
        # --------------------------------------------------
        self.item_inicio = QTreeWidgetItem()
        self.item_inicio.setText(0, " 🏠 Inicio")
        self.tree_menu.addTopLevelItem(self.item_inicio)

        # Academicos
        # --------------------------------------------------

        self.item_academicos = QTreeWidgetItem()
        self.item_academicos.setText(0, " 🎓 Académicos")
        self.item_academicos.setToolTip(0, "Accede a las funciones academicas")
        self.tree_menu.addTopLevelItem(self.item_academicos)

        # Item falsatantes: Facultades, Carreras, Asignaturas, PreRequisitos, Malla Curricular
        self.item_facultades = QTreeWidgetItem()
        self.item_facultades.setText(0, " 🏛️ Facultades")
        self.item_facultades.setToolTip(0, " Organiza las Facultades a las que vas !!!")
        self.item_facultades.setData(0, Qt.ItemDataRole.UserRole, {"name": "facultades"})
        self.item_academicos.addChild(self.item_facultades)

        self.item_carreras = QTreeWidgetItem()
        self.item_carreras.setText(0, " 🏫 Carreras")
        self.item_carreras.setToolTip(0, "Carga y administra las carreras que llevas")
        self.item_carreras.setData(0, Qt.ItemDataRole.UserRole, {"name": "carreras"})
        self.item_academicos.addChild(self.item_carreras)

        self.item_profesores = QTreeWidgetItem()
        self.item_profesores.setText(0, " 👨‍🏫 Profesores")
        self.item_profesores.setToolTip(0, "Carga y administra los profesores")
        self.item_profesores.setData(0, Qt.ItemDataRole.UserRole, {"name": "profesores"})
        self.item_academicos.addChild(self.item_profesores)

        self.item_asiganturas = QTreeWidgetItem()
        self.item_asiganturas.setText(0, " 📚 Asignaturas")
        self.item_asiganturas.setToolTip(
            0, "Carga y administra las asignaturas de las carreras que llevas"
        )
        self.item_asiganturas.setData(0, Qt.ItemDataRole.UserRole, {"name": "asignaturas"})
        self.item_academicos.addChild(self.item_asiganturas)

        self.item_horasemanales = QTreeWidgetItem()
        self.item_horasemanales.setText(0, " ⌛ Horas Semanales")
        self.item_horasemanales.setToolTip(
            0, "Carga y administra las Horas Semanales de asignaturas"
        )
        self.item_horasemanales.setData(0, Qt.ItemDataRole.UserRole, {"name": "horasemanales"})
        self.item_academicos.addChild(self.item_horasemanales)

        self.item_prerequisitos = QTreeWidgetItem()
        self.item_prerequisitos.setText(0, " ⛓️ Prerequisitos")
        self.item_prerequisitos.setToolTip(
            0, "Carga y administra los prerequisitos de las asiganturas"
        )
        self.item_prerequisitos.setData(0, Qt.ItemDataRole.UserRole, {"name": "prerequisitos"})
        self.item_academicos.addChild(self.item_prerequisitos)

        self.item_malla_curricular = QTreeWidgetItem()
        self.item_malla_curricular.setText(0, " 🪜 Malla Curricular")
        self.item_malla_curricular.setToolTip(0, "Explora las mallas curriculares de las carreras")
        self.item_malla_curricular.setData(
            0,
            Qt.ItemDataRole.UserRole,
            {"name": "malla_curricular"},
        )
        self.item_academicos.addChild(self.item_malla_curricular)

        # Calendarios
        # --------------------------------------------------

        self.item_calendarios = QTreeWidgetItem()
        self.item_calendarios.setText(0, " 🗓️ Calendarios")
        self.item_calendarios.setToolTip(0, "Consulta los calendarios académicos e institucionales")
        self.tree_menu.addTopLevelItem(self.item_calendarios)

        self.item_calendario_academico = QTreeWidgetItem()
        self.item_calendario_academico.setText(0, " 📚 Calendario Académico")
        self.item_calendario_academico.setData(
            0,
            Qt.ItemDataRole.UserRole,
            {"name": "calendario_academico"},
        )
        self.item_calendarios.addChild(self.item_calendario_academico)

        self.item_calendario_institucional = QTreeWidgetItem()
        self.item_calendario_institucional.setText(0, " 🏛️ Calendario Institucional")
        self.item_calendario_institucional.setData(
            0,
            Qt.ItemDataRole.UserRole,
            {"name": "calendario_institucional"},
        )
        self.item_calendarios.addChild(self.item_calendario_institucional)
        self.item_calendarios.setExpanded(True)

        # Estudiante
        # --------------------------------------------------

        self.item_estudiante = QTreeWidgetItem()
        self.item_estudiante.setText(0, " 🧑‍🎓 Estudiante")
        self.tree_menu.addTopLevelItem(self.item_estudiante)

        self.item_quien_eres = QTreeWidgetItem()
        self.item_quien_eres.setText(0, " 🙋 Dime quién eres")
        self.item_quien_eres.setToolTip(0, "Selecciona el estudiante que usara la aplicacion")
        self.item_quien_eres.setData(0, Qt.ItemDataRole.UserRole, {"name": "quien_eres"})
        self.item_estudiante.addChild(self.item_quien_eres)

        self.item_matriculacion = QTreeWidgetItem()
        self.item_matriculacion.setText(0, " 📝 Matriculación")
        self.item_matriculacion.setToolTip(0, "Registra la matricula del estudiante en una carrera")
        self.item_matriculacion.setData(0, Qt.ItemDataRole.UserRole, {"name": "matriculacion"})
        self.item_estudiante.addChild(self.item_matriculacion)

        self.item_inscripciones = QTreeWidgetItem()
        self.item_inscripciones.setText(0, " 📋 Inscripciones")
        self.item_inscripciones.setToolTip(0, "Administra las inscripciones del estudiante")
        self.item_inscripciones.setData(0, Qt.ItemDataRole.UserRole, {"name": "inscripciones"})
        self.item_estudiante.addChild(self.item_inscripciones)

        self.item_tipos_actividades = QTreeWidgetItem()
        self.item_tipos_actividades.setText(0, " 🗂️ Tipos de actividades")
        self.item_tipos_actividades.setToolTip(0, "Administra los tipos de actividades academicas")
        self.item_tipos_actividades.setData(
            0,
            Qt.ItemDataRole.UserRole,
            {"name": "tipos_actividades"},
        )
        self.item_estudiante.addChild(self.item_tipos_actividades)

        self.item_actividades_estudiante = QTreeWidgetItem()
        self.item_actividades_estudiante.setText(0, " 📅 Actividades")
        self.item_actividades_estudiante.setToolTip(
            0,
            "Administra las actividades asociadas al estudiante",
        )
        self.item_actividades_estudiante.setData(
            0,
            Qt.ItemDataRole.UserRole,
            {"name": "actividades_estudiante"},
        )
        self.item_estudiante.addChild(self.item_actividades_estudiante)
        self.item_estudiante.setExpanded(True)

        # Configuraciones
        # --------------------------------------------------
        self.item_configuraciones = QTreeWidgetItem()
        self.item_configuraciones.setText(0, " ⚙️ Configuraciones")
        self.tree_menu.addTopLevelItem(self.item_configuraciones)

        self.item_webs = QTreeWidgetItem()
        self.item_webs.setText(0, " 🌎 Sitios Webs")
        self.item_webs.setData(0, Qt.ItemDataRole.UserRole, {"name": "webs"})
        self.item_webs.setToolTip(0, "Agregar sitios webs que quieras mostrar de la facultad")
        self.item_configuraciones.addChild(self.item_webs)

        font_tree_menu = QFont()
        font_tree_menu.setPointSize(10)
        self.tree_menu.setFont(font_tree_menu)
        self.tree_menu.resizeColumnToContents(0)

        # ┌────────────────────────────────────────────────────────────┐
        # │ Conexion con los eventos
        # └────────────────────────────────────────────────────────────┘

        self.tree_menu.itemClicked.connect(self.on_item_clicked)

        self.setWidget(self.widget_principal)

    # ┌────────────────────────────────────────────────────────────┐
    # │ Eventos
    # └────────────────────────────────────────────────────────────┘

    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        datos = item.data(0, Qt.ItemDataRole.UserRole)  # datos esta en forma de diccionario
        # print(f"Clic en '{item.text(0)}' col={column} datos={datos}")

        if datos is None:
            return

        if datos['name'] == "facultades":
            if not self._existe_tab(widget=self.tab_principal, titulo="Facultades"):
                tab_facultad = Facultades()
                self._agregar_tab(tab_facultad, "Facultades")
        elif datos['name'] == "carreras":
            if not self._existe_tab(widget=self.tab_principal, titulo="Carreras"):
                tab_facultad = Carreras()
                self._agregar_tab(tab_facultad, "Carreras")
        elif datos['name'] == "profesores":
            if not self._existe_tab(widget=self.tab_principal, titulo="Profesores"):
                tab_profesores = Profesores()
                self._agregar_tab(tab_profesores, "Profesores")
        elif datos['name'] == "asignaturas":
            if not self._existe_tab(widget=self.tab_principal, titulo="Asignaturas"):
                tab_asignaturas = Asignaturas()
                self._agregar_tab(tab_asignaturas, "Asignaturas")
        elif datos['name'] == "horasemanales":
            if not self._existe_tab(widget=self.tab_principal, titulo="Horas Semanales"):
                tab_horas = HorasSemanales()
                self._agregar_tab(tab_horas, "Horas Semanales")
        elif datos['name'] == "prerequisitos":
            if not self._existe_tab(widget=self.tab_principal, titulo="Prerrequisitos"):
                tab_prerequisitos = Prerequisitos()
                self._agregar_tab(tab_prerequisitos, "Prerrequisitos")
        elif datos['name'] == "malla_curricular":
            if not self._existe_tab(widget=self.tab_principal, titulo="Malla Curricular"):
                tab_malla = MallaCurricular()
                self._agregar_tab(tab_malla, "Malla Curricular")
        elif datos['name'] == "matriculacion":
            if not self._existe_tab(widget=self.tab_principal, titulo="Matriculación"):
                tab_matriculacion = Matriculacion()
                self._agregar_tab(tab_matriculacion, "Matriculación")
        elif datos['name'] == "inscripciones":
            if not self._existe_tab(widget=self.tab_principal, titulo="Inscripciones"):
                tab_inscripciones = Inscripciones()
                self._agregar_tab(tab_inscripciones, "Inscripciones")
        elif datos['name'] == "tipos_actividades":
            if not self._existe_tab(widget=self.tab_principal, titulo="Tipos de actividades"):
                tab_tipos_actividades = TiposActividades()
                self._agregar_tab(tab_tipos_actividades, "Tipos de actividades")
        elif datos['name'] == "actividades_estudiante":
            if not self._existe_tab(widget=self.tab_principal, titulo="Actividades"):
                tab_actividades = Actividades()
                self._agregar_tab(tab_actividades, "Actividades")
        elif datos['name'] == "calendario_academico":
            if not self._existe_tab(
                widget=self.tab_principal,
                titulo="Calendario Académico",
            ):
                tab_calendario = CalendarioAcademico()
                self._agregar_tab(tab_calendario, "Calendario Académico")
        elif datos['name'] == "calendario_institucional":
            if not self._existe_tab(
                widget=self.tab_principal,
                titulo="Calendario Institucional",
            ):
                tab_calendario = CalendarioInstitucional()
                self._agregar_tab(tab_calendario, "Calendario Institucional")
        elif datos['name'] == "quien_eres":
            conexion = obtener_conexion()
            if conexion is None:
                QMessageBox.warning(
                    self,
                    "Error",
                    "No se pudo acceder a la base de datos del estudiante.",
                )
                return

            self.dialogo_estudiante = DialogoEstudiante(conexion, self)
            if self.dialogo_estudiante.carga_valida:
                self.dialogo_estudiante.exec()
        elif datos['name'] == "webs":
            self.dialogo_webs = SitiosWebs()
            self.dialogo_webs.setWindowModality(Qt.WindowModality.ApplicationModal)
            self.dialogo_webs.show()

    # ┌──────────────────────────────────────────────────┐
    # │ Metodos Privados
    # └──────────────────────────────────────────────────┘

    def _agregar_tab(self, widget: QWidget, titulo: str):
        indice = self.tab_principal.addTab(widget, titulo)
        self.tab_principal.setCurrentIndex(indice)

    def _existe_tab(self, widget: QTabWidget, titulo: str) -> bool:
        for i in range(widget.count()):
            if widget.tabText(i) == titulo:
                widget.setCurrentIndex(i)
                return True
        return False


# ┌──────────────────────────────────────────────────┐
# │ Dialogos
# └──────────────────────────────────────────────────┘


class SitiosWebs(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sitios Webs")

        # cargamos el formulario
        self._crear_formulario()
        # cargamos en el combobox las facultades
        self._cargar_facultades()

    # ┌──────────────────────────────────────────────────┐
    # │ Eventos
    # └──────────────────────────────────────────────────┘

    def on_agregar(self):
        # cargamos el archivo de configuraciones
        setting: QSettings = QSettings(str(CONFIG_CRONO), QSettings.Format.IniFormat)
        # obtenemos los valores a agregar
        nombre_sitio = self.line_nombre_sitio.text()
        url_sitio = self.line_url_sitio.text()
        sigla = self.combo_facultades.currentData()['sigla']
        # verificamos
        if len(nombre_sitio) > 0 and len(url_sitio) > 0 and len(sigla) > 0:
            setting.setValue(f"{sigla}/{nombre_sitio}", url_sitio)
            # mostrar en la lista
            self._cargar_lista()

    def change_combox(self, facultad):
        if len(facultad) > 0:
            self._cargar_lista()

    def double_click_lista(self, item: QListWidgetItem):
        if item is None:
            return
        # cargamos el archivo de configuraciones
        setting: QSettings = QSettings(str(CONFIG_CRONO), QSettings.Format.IniFormat)
        sigla = self.combo_facultades.currentData()['sigla']
        # obtenemos la url del sitio
        if len(sigla) > 0:
            url = setting.value(f"{sigla}/{item.text()}")
            # mostramos
            self.line_nombre_sitio.setText(item.text())
            self.line_url_sitio.setText(url)

    def click_remover(self):
        nombre = self.line_nombre_sitio.text()
        if len(nombre) == 0:
            return
        setting: QSettings = QSettings(str(CONFIG_CRONO), QSettings.Format.IniFormat)
        sigla = self.combo_facultades.currentData()['sigla']
        setting.remove(f"{sigla}/{nombre}")
        # limpiamos la lista
        self._cargar_lista()
        # limpiamos los campos
        self.line_nombre_sitio.setText("")
        self.line_url_sitio.setText("")

    def click_nuevo(self):
        # limpiamos los campos
        self.line_nombre_sitio.setText("")
        self.line_url_sitio.setText("")

    # ┌──────────────────────────────────────────────────┐
    # │ Metodos
    # └──────────────────────────────────────────────────┘
    def _cargar_lista(self):
        # limpiamos la lista
        self.lista_sitios.clear()
        # cargamos el archivo de configuraciones
        setting: QSettings = QSettings(str(CONFIG_CRONO), QSettings.Format.IniFormat)
        # obtenemos la sigla de la facultad
        sigla = self.combo_facultades.currentData()['sigla']
        # le pasamos como seccion del archivo ini
        setting.beginGroup(sigla)
        # obtenemos la claves de la seccion
        claves: list = setting.childKeys()
        if claves is None:
            return
        for clave in claves:
            self.lista_sitios.addItem(clave)

    def _cargar_facultades(self):
        conexion = obtener_conexion()
        if conexion is None:
            return

        query = QSqlQuery(db=conexion)
        if query.exec("SELECT nombre, siglas FROM Facultad ORDER BY siglas"):
            while query.next():
                sigla = query.value("siglas")
                nombre = query.value("nombre")
                self.combo_facultades.addItem(f"{sigla} - {nombre}", userData={"sigla": sigla})
        else:
            LOGGER.error("Error al realizar la consulta: %s", query.lastError().text())
            return

    # ┌──────────────────────────────────────────────────┐
    # │ Formulario
    # └──────────────────────────────────────────────────┘

    def _crear_formulario(self):
        # Layouts
        # --------------------------------------------------
        layout_main = QVBoxLayout()
        layout_grid = QGridLayout()
        layout_main.addLayout(layout_grid)
        layout_operaciones = QHBoxLayout()
        layout_main.addLayout(layout_operaciones)

        # Widgets
        # --------------------------------------------------
        label_facultades = QLabel("Facultades: ")
        layout_grid.addWidget(label_facultades, 0, 0)

        self.combo_facultades = QComboBox()
        self.combo_facultades.currentTextChanged.connect(self.change_combox)
        layout_grid.addWidget(self.combo_facultades, 1, 0)

        label_nombre_sitio = QLabel("Nombre del Sitio: ")
        layout_grid.addWidget(label_nombre_sitio, 2, 0)

        self.line_nombre_sitio = QLineEdit()
        self.line_nombre_sitio.setPlaceholderText(
            "Escribe el nombre del sitio: evento, notocias, ect"
        )
        layout_grid.addWidget(self.line_nombre_sitio, 3, 0)

        label_url = QLabel("URL del Sitio: ")
        layout_grid.addWidget(label_url, 4, 0)

        self.line_url_sitio = QLineEdit()
        self.line_url_sitio.setPlaceholderText("https://www.facen.una.py/evento/")
        layout_grid.addWidget(self.line_url_sitio, 5, 0)

        label_lista_sitios = QLabel("Lista Sitios: ")
        layout_grid.addWidget(label_lista_sitios, 6, 0)

        self.lista_sitios = QListWidget()
        self.lista_sitios.setToolTip("Doble click para cargar los datos")
        self.lista_sitios.itemDoubleClicked.connect(self.double_click_lista)
        layout_grid.addWidget(self.lista_sitios, 7, 0)

        layout_operaciones.addStretch()

        self.button_agregar = QPushButton("Agregar")
        self.button_agregar.clicked.connect(self.on_agregar)
        layout_operaciones.addWidget(self.button_agregar)

        self.button_remover = QPushButton("Remover")
        self.button_remover.clicked.connect(self.click_remover)
        layout_operaciones.addWidget(self.button_remover)

        self.button_nuevo = QPushButton("Nuevo")
        self.button_nuevo.clicked.connect(self.click_nuevo)
        layout_operaciones.addWidget(self.button_nuevo)

        # Agregmos el layout principal
        self.setLayout(layout_main)
