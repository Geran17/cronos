from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtSql import QSqlQuery, QSqlTableModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QColorDialog,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from interfaz.pyside6.auxiliares import conectar_modelo
from interfaz.pyside6.estilos import (
    ESTILO_PUSH_BUTTON_AGREGAR,
    ESTILO_PUSH_BUTTON_EDITAR,
    ESTILO_PUSH_BUTTON_ELIMINAR,
)
from utilidades.configuraciones import CONFIG_CRONO, LOGGER

INDICES_COLUMNAS = {
    "id_tipoactividad": 0,
    "nombre": 1,
    "siglas": 2,
    "descripcion": 3,
    "prioridad": 4,
}
PRIORIDADES = ("alta", "media", "baja")
CLAVE_COLORES = "TiposActividad/colores"


class TiposActividades(QWidget):
    def __init__(self):
        super().__init__()

        self.modelo: QSqlTableModel | None = conectar_modelo()
        self._crear()
        self.configurar_tabla()

    def _crear(self):
        layout_main = QVBoxLayout()
        layout_titulo = QVBoxLayout()
        layout_main.addLayout(layout_titulo)
        layout_operaciones = QHBoxLayout()
        layout_main.addLayout(layout_operaciones)
        layout_tabla = QVBoxLayout()
        layout_main.addLayout(layout_tabla)

        label_titulo = QLabel(" 🗂️ Tipos de actividades")
        layout_titulo.addWidget(label_titulo)
        font = QFont()
        font.setPointSize(14)
        label_titulo.setFont(font)
        frame_linea = QFrame()
        frame_linea.setFrameShape(QFrame.Shape.HLine)
        layout_titulo.addWidget(frame_linea)

        self.line_buscar = QLineEdit()
        self.line_buscar.setPlaceholderText("Busca por nombre, sigla o prioridad")
        self.line_buscar.textChanged.connect(self.on_buscar)
        layout_operaciones.addWidget(self.line_buscar)

        self.push_agregar = QPushButton("Agregar")
        self.push_agregar.clicked.connect(self.on_dialogo_agregar)
        self.push_agregar.setToolTip("Agrega un nuevo tipo de actividad")
        self.push_agregar.setStyleSheet(ESTILO_PUSH_BUTTON_AGREGAR)
        layout_operaciones.addWidget(self.push_agregar)

        self.push_editar = QPushButton("Editar")
        self.push_editar.clicked.connect(self.on_dialogo_editar)
        self.push_editar.setToolTip("Edita el tipo de actividad seleccionado")
        self.push_editar.setStyleSheet(ESTILO_PUSH_BUTTON_EDITAR)
        layout_operaciones.addWidget(self.push_editar)

        self.push_eliminar = QPushButton("Eliminar")
        self.push_eliminar.clicked.connect(self.on_dialogo_eliminar)
        self.push_eliminar.setToolTip("Elimina el tipo de actividad seleccionado")
        self.push_eliminar.setStyleSheet(ESTILO_PUSH_BUTTON_ELIMINAR)
        layout_operaciones.addWidget(self.push_eliminar)

        self.tabla = QTableView()
        layout_tabla.addWidget(self.tabla)
        self.setLayout(layout_main)

    def configurar_tabla(self):
        if self.modelo is None:
            LOGGER.warning("El modelo de la tabla no se pudo cargar: %s", self.modelo)
            return

        self.modelo.setTable("TipoActividad")
        self.modelo.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)
        if not self.modelo.select():
            LOGGER.error("Error al cargar los tipos de actividades: %s", self.modelo.lastError().text())

        encabezados = ("Id", "Nombre", "Siglas", "Descripción", "Prioridad")
        for columna, encabezado in enumerate(encabezados):
            self.modelo.setHeaderData(columna, Qt.Orientation.Horizontal, encabezado)

        self.tabla.setModel(self.modelo)
        self.tabla.resizeColumnsToContents()
        self.tabla.setColumnHidden(INDICES_COLUMNAS["id_tipoactividad"], True)
        self.tabla.setColumnHidden(INDICES_COLUMNAS["descripcion"], True)
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

    def on_buscar(self, texto: str):
        if self.modelo is None:
            return

        patron = texto.replace("'", "''")
        if patron:
            patron = f"'%{patron}%'"
            self.modelo.setFilter(
                f"nombre LIKE {patron} OR siglas LIKE {patron} OR prioridad LIKE {patron}"
            )
        else:
            self.modelo.setFilter("")

        if not self.modelo.select():
            LOGGER.error(
                "Error al buscar tipos de actividades: %s",
                self.modelo.lastError().text(),
            )

    def on_dialogo_agregar(self):
        if self.modelo is None:
            return
        self.dialog = DialogoTipoActividad(self.modelo, self.tabla)
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()

    def on_dialogo_editar(self):
        index = self.tabla.currentIndex()
        if not index.isValid():
            QMessageBox.information(
                self,
                "Seleccione",
                "Seleccione un tipo de actividad para editar",
            )
            return
        if self.modelo is None:
            return

        self.dialog = DialogoTipoActividad(self.modelo, self.tabla, fila=index.row())
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()

    def on_dialogo_eliminar(self):
        index = self.tabla.currentIndex()
        if not index.isValid():
            QMessageBox.information(
                self,
                "Seleccione",
                "Seleccione un tipo de actividad para eliminar",
            )
            return
        if self.modelo is None:
            return

        tipo_id = self.modelo.record(index.row()).value("id_tipoactividad")
        respuesta = QMessageBox.question(
            self,
            "Eliminar tipo de actividad",
            "¿Está seguro de eliminar el tipo seleccionado? "
            "También se eliminarán las actividades asociadas.",
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return

        if not self.modelo.removeRow(index.row()) or not self.modelo.submitAll():
            error = self.modelo.lastError().text()
            LOGGER.error("Error al eliminar el tipo de actividad: %s", error)
            self.modelo.revertAll()
            QMessageBox.warning(self, "Error", f"No se pudo eliminar el tipo: {error}")
            return

        error_configuracion = self._eliminar_color(tipo_id)
        if not self.modelo.select():
            LOGGER.error(
                "Error al actualizar los tipos de actividades: %s",
                self.modelo.lastError().text(),
            )
        self.tabla.clearSelection()
        if error_configuracion is not None:
            QMessageBox.warning(self, "Error", error_configuracion)

    @staticmethod
    def _crear_configuracion() -> QSettings | None:
        if CONFIG_CRONO is None:
            LOGGER.error("No se pudo acceder al archivo de configuraciones")
            return None
        return QSettings(str(CONFIG_CRONO), QSettings.Format.IniFormat)

    @classmethod
    def _eliminar_color(cls, tipo_id) -> str | None:
        configuracion = cls._crear_configuracion()
        if configuracion is None:
            return "Se eliminó el tipo, pero no se pudo actualizar su color en configuraciones."

        configuracion.remove(f"{CLAVE_COLORES}/{tipo_id}")
        configuracion.sync()
        if configuracion.status() != QSettings.Status.NoError:
            error = configuracion.status().name
            LOGGER.error("No se pudo eliminar el color del tipo %s: %s", tipo_id, error)
            return f"Se eliminó el tipo, pero no se pudo quitar su color: {error}"
        return None


class DialogoTipoActividad(QWidget):
    def __init__(
        self,
        modelo: QSqlTableModel,
        tabla: QTableView,
        fila: int | None = None,
    ):
        super().__init__()
        self.modelo = modelo
        self.tabla = tabla
        self.fila = fila
        self.tipo_id = None
        self.color = QColor()
        self.setWindowTitle(
            "Editar tipo de actividad" if fila is not None else "Agregar tipo de actividad"
        )

        if self.fila is not None:
            self.tipo_id = self.modelo.record(self.fila).value("id_tipoactividad")
            self.color = self._cargar_color(self.tipo_id)

        self._crear_formulario()
        if self.color.isValid():
            self._actualizar_vista_color()
        if self.fila is not None:
            self._cargar_campos()

    def _crear_formulario(self):
        layout_main = QVBoxLayout()
        layout_grid = QGridLayout()
        layout_main.addLayout(layout_grid)
        layout_buttons = QHBoxLayout()
        layout_main.addLayout(layout_buttons)

        layout_grid.addWidget(QLabel("Nombre *"), 0, 0)
        self.line_nombre = QLineEdit()
        self.line_nombre.setPlaceholderText("Nombre del tipo de actividad")
        layout_grid.addWidget(self.line_nombre, 0, 1)

        layout_grid.addWidget(QLabel("Siglas"), 1, 0)
        self.line_siglas = QLineEdit()
        self.line_siglas.setPlaceholderText("Siglas (opcional)")
        layout_grid.addWidget(self.line_siglas, 1, 1)

        layout_grid.addWidget(QLabel("Prioridad"), 2, 0)
        self.combo_prioridad = QComboBox()
        self.combo_prioridad.addItem("(Sin prioridad)", userData=None)
        for prioridad in PRIORIDADES:
            self.combo_prioridad.addItem(prioridad.capitalize(), userData=prioridad)
        layout_grid.addWidget(self.combo_prioridad, 2, 1)

        layout_grid.addWidget(QLabel("Color *"), 3, 0)
        self.button_color = QPushButton("Seleccionar color")
        self.button_color.clicked.connect(self.on_seleccionar_color)
        layout_grid.addWidget(self.button_color, 3, 1)

        layout_grid.addWidget(QLabel("Descripción"), 4, 0)
        self.text_descripcion = QTextEdit()
        self.text_descripcion.setPlaceholderText("Descripción del tipo de actividad")
        layout_grid.addWidget(self.text_descripcion, 4, 1)

        layout_buttons.addStretch()
        self.button_aplicar = QPushButton("Aplicar")
        self.button_aplicar.clicked.connect(self.on_aplicar)
        layout_buttons.addWidget(self.button_aplicar)

        self.button_cancelar = QPushButton("Cancelar")
        self.button_cancelar.clicked.connect(self.close)
        layout_buttons.addWidget(self.button_cancelar)

        self.setLayout(layout_main)

    def _cargar_color(self, tipo_id) -> QColor:
        configuracion = TiposActividades._crear_configuracion()
        if configuracion is None:
            return QColor()

        valor = configuracion.value(f"{CLAVE_COLORES}/{tipo_id}")
        if valor is None:
            return QColor()

        color = QColor(str(valor))
        if not color.isValid():
            LOGGER.warning("El color guardado para el tipo %s no es válido: %s", tipo_id, valor)
            return QColor()
        return color

    def _actualizar_vista_color(self):
        self.button_color.setText(self.color.name(QColor.NameFormat.HexRgb))
        self.button_color.setStyleSheet(f"background-color: {self.color.name()};")

    def on_seleccionar_color(self):
        color_inicial = self.color if self.color.isValid() else QColor(Qt.GlobalColor.white)
        color = QColorDialog.getColor(
            color_inicial,
            self,
            "Seleccionar color del tipo de actividad",
        )
        if not color.isValid():
            return
        self.color = color
        self._actualizar_vista_color()

    def _cargar_campos(self):
        if self.fila is None:
            return

        registro = self.modelo.record(self.fila)
        self.line_nombre.setText(str(registro.value("nombre") or ""))
        self.line_siglas.setText(str(registro.value("siglas") or ""))
        self.text_descripcion.setPlainText(str(registro.value("descripcion") or ""))
        prioridad = registro.value("prioridad")
        indice = self.combo_prioridad.findData(prioridad)
        if indice >= 0:
            self.combo_prioridad.setCurrentIndex(indice)

    def on_aplicar(self):
        nombre = self.line_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Advertencia", "El nombre del tipo es obligatorio.")
            return
        if not self.color.isValid():
            QMessageBox.warning(self, "Advertencia", "Selecciona un color para el tipo.")
            return

        if self.fila is None:
            self.fila = self.modelo.rowCount()
            if not self.modelo.insertRow(self.fila):
                self._mostrar_error("No se pudo agregar el tipo de actividad")
                return

        valores = {
            "nombre": nombre,
            "siglas": self.line_siglas.text().strip() or None,
            "descripcion": self.text_descripcion.toPlainText().strip() or None,
            "prioridad": self.combo_prioridad.currentData(),
        }
        for campo, valor in valores.items():
            columna = INDICES_COLUMNAS[campo]
            if not self.modelo.setData(self.modelo.index(self.fila, columna), valor):
                self.modelo.revertAll()
                self._mostrar_error(f"No se pudo actualizar el campo {campo}")
                return

        if not self.modelo.submitAll():
            self.modelo.revertAll()
            self._mostrar_error("No se pudo guardar el tipo de actividad")
            return

        if self.tipo_id is None:
            self.tipo_id = self._ultimo_id_insertado()
            if self.tipo_id is None:
                if not self.modelo.select():
                    LOGGER.error(
                        "Error al actualizar los tipos de actividades: %s",
                        self.modelo.lastError().text(),
                    )
                QMessageBox.warning(
                    self,
                    "Error",
                    "El tipo se guardó, pero no se pudo identificar para guardar su color.",
                )
                self.close()
                return

        error_configuracion = self._guardar_color()
        if not self.modelo.select():
            LOGGER.error(
                "Error al actualizar los tipos de actividades: %s",
                self.modelo.lastError().text(),
            )
        self.tabla.clearSelection()
        if error_configuracion is not None:
            QMessageBox.warning(self, "Error", error_configuracion)
        self.close()

    def _ultimo_id_insertado(self) -> int | None:
        consulta = QSqlQuery(db=self.modelo.database())
        if not consulta.exec("SELECT last_insert_rowid()"):
            LOGGER.error(
                "No se pudo obtener el id del tipo de actividad: %s",
                consulta.lastError().text(),
            )
            return None
        if not consulta.next():
            LOGGER.error("No se obtuvo el id del tipo de actividad recién agregado")
            return None
        return int(consulta.value(0))

    def _guardar_color(self) -> str | None:
        configuracion = TiposActividades._crear_configuracion()
        if configuracion is None:
            return "El tipo se guardó, pero no se pudo guardar su color en configuraciones."

        configuracion.setValue(
            f"{CLAVE_COLORES}/{self.tipo_id}",
            self.color.name(QColor.NameFormat.HexRgb),
        )
        configuracion.sync()
        if configuracion.status() != QSettings.Status.NoError:
            error = configuracion.status().name
            LOGGER.error("No se pudo guardar el color del tipo %s: %s", self.tipo_id, error)
            return f"El tipo se guardó, pero no se pudo guardar su color: {error}"
        return None

    def _mostrar_error(self, mensaje: str, error: str | None = None):
        if error is None:
            error = self.modelo.lastError().text()
        LOGGER.error("%s: %s", mensaje, error)
        QMessageBox.warning(self, "Error", f"{mensaje}: {error}")
