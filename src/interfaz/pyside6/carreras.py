from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QTableView,
    QAbstractItemView,
    QGridLayout,
    QTextEdit,
    QMessageBox,
    QComboBox,
)
from PySide6.QtSql import QSqlTableModel, QSqlQuery
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from interfaz.pyside6.estilos import (
    ESTILO_PUSH_BUTTON_AGREGAR,
    ESTILO_PUSH_BUTTON_EDITAR,
    ESTILO_PUSH_BUTTON_ELIMINAR,
)
from utilidades.configuraciones import LOGGER
from interfaz.pyside6.auxiliares import conectar_modelo


class Carreras(QWidget):
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

        label_titulo = QLabel(" 🏫 Carreras")
        layout_titulo.addWidget(label_titulo)
        font = QFont()
        font.setPointSize(14)
        label_titulo.setFont(font)
        frame_linea = QFrame()
        frame_linea.setFrameShape(QFrame.Shape.HLine)
        layout_titulo.addWidget(frame_linea)

        self.line_buscar = QLineEdit()
        self.line_buscar.setPlaceholderText("Busca por codigo, nombre, modalidad o titulacion")
        self.line_buscar.textChanged.connect(self.on_buscar)
        layout_operaciones.addWidget(self.line_buscar)

        self.push_agregar = QPushButton("Agregar")
        self.push_agregar.clicked.connect(self.on_dialogo_agregar)
        self.push_agregar.setToolTip("Agrega una nueva carrera")
        self.push_agregar.setStyleSheet(ESTILO_PUSH_BUTTON_AGREGAR)
        layout_operaciones.addWidget(self.push_agregar)

        self.push_editar = QPushButton("Editar")
        self.push_editar.clicked.connect(self.on_dialogo_editar)
        self.push_editar.setToolTip("Edita la carrera seleccionada en la tabla")
        self.push_editar.setStyleSheet(ESTILO_PUSH_BUTTON_EDITAR)
        layout_operaciones.addWidget(self.push_editar)

        self.push_eliminar = QPushButton("Eliminar")
        self.push_eliminar.clicked.connect(self.on_dialogo_eliminar)
        self.push_eliminar.setToolTip("Elimina la carrera seleccionada en la tabla")
        self.push_eliminar.setStyleSheet(ESTILO_PUSH_BUTTON_ELIMINAR)
        layout_operaciones.addWidget(self.push_eliminar)

        self.tabla = QTableView()
        layout_tabla.addWidget(self.tabla)
        self.setLayout(layout_main)

    def configurar_tabla(self):
        if self.modelo is None:
            LOGGER.warning("El modelo de la tabla no se pudo cargar: %s", self.modelo)
            return

        self.modelo.setTable("Carrera")
        self.modelo.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)
        if not self.modelo.select():
            LOGGER.error("Error al cargar las carreras: %s", self.modelo.lastError().text())

        encabezados = (
            "Id",
            "Facultad",
            "Codigo",
            "Nombre",
            "Descripcion",
            "Modalidad",
            "Duracion",
            "Titulacion",
            "Plan Curricular",
        )
        for columna, encabezado in enumerate(encabezados):
            self.modelo.setHeaderData(columna, Qt.Orientation.Horizontal, encabezado)

        self.tabla.setModel(self.modelo)
        self.tabla.resizeColumnsToContents()
        self.tabla.setColumnHidden(0, True)
        self.tabla.setColumnHidden(1, True)
        self.tabla.setColumnHidden(4, True)
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
                f"codigo LIKE {patron} OR nombre LIKE {patron} "
                f"OR modalidad LIKE {patron} OR titulacion LIKE {patron}"
            )
        else:
            self.modelo.setFilter("")

        if not self.modelo.select():
            LOGGER.error("Error al buscar carreras: %s", self.modelo.lastError().text())

    def on_dialogo_agregar(self):
        if self.modelo is None:
            return
        self.dialog = DialogoCarrera(self.modelo, self.tabla)
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()

    def on_dialogo_editar(self):
        index = self.tabla.currentIndex()
        if not index.isValid():
            QMessageBox.information(self, "Seleccione", "Seleccione una carrera para editar")
            return
        if self.modelo is None:
            return

        self.dialog = DialogoCarrera(self.modelo, self.tabla, fila=index.row())
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()

    def on_dialogo_eliminar(self):
        index = self.tabla.currentIndex()
        if not index.isValid():
            QMessageBox.information(self, "Seleccione", "Seleccione una carrera para eliminar")
            return
        if self.modelo is None:
            return

        respuesta = QMessageBox.question(
            self,
            "Eliminar carrera",
            "Esta seguro que quiere eliminar la carrera seleccionada?",
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return

        if not self.modelo.removeRow(index.row()) or not self.modelo.submitAll():
            error = self.modelo.lastError().text()
            LOGGER.error("Error al eliminar la carrera: %s", error)
            self.modelo.revertAll()
            QMessageBox.warning(self, "Error", f"No se pudo eliminar la carrera: {error}")
            return

        if not self.modelo.select():
            LOGGER.error("Error al actualizar las carreras: %s", self.modelo.lastError().text())
        self.tabla.clearSelection()


class DialogoCarrera(QWidget):
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
        self.setWindowTitle(
            "Edita la carrera seleccionada" if fila is not None else "Agrega una nueva carrera"
        )
        # self.resize(550, 500)

        self._crear_formulario()
        self._cargar_facultades()
        if self.fila is not None:
            self._cargar_campos()

    def _crear_formulario(self):
        layout_main = QVBoxLayout()
        layout_grid = QGridLayout()
        layout_main.addLayout(layout_grid)
        layout_buttons = QHBoxLayout()
        layout_main.addLayout(layout_buttons)

        label_codigo = QLabel("Codigo *")
        layout_grid.addWidget(label_codigo, 0, 0)
        self.line_codigo = QLineEdit()
        self.line_codigo.setPlaceholderText("Codigo de la carrera")
        layout_grid.addWidget(self.line_codigo, 1, 0)

        label_plan_curricular = QLabel("Plan Curricular")
        layout_grid.addWidget(label_plan_curricular, 0, 2)
        self.line_plan_curricular = QLineEdit()
        self.line_plan_curricular.setPlaceholderText("Ano")
        layout_grid.addWidget(self.line_plan_curricular, 1, 2)

        label_duracion = QLabel("Duracion")
        layout_grid.addWidget(label_duracion, 0, 3)
        self.line_duracion = QLineEdit()
        self.line_duracion.setPlaceholderText("Anos")
        layout_grid.addWidget(self.line_duracion, 1, 3)

        label_nombre = QLabel("Carrera *")
        layout_grid.addWidget(label_nombre, 2, 0, 1, 3)
        self.line_nombre = QLineEdit()
        self.line_nombre.setPlaceholderText("Nombre de la carrera")
        layout_grid.addWidget(self.line_nombre, 3, 0, 1, 3)

        label_facultad = QLabel("Facultad")
        layout_grid.addWidget(label_facultad, 2, 3)
        self.combo_facultad = QComboBox()
        layout_grid.addWidget(self.combo_facultad, 3, 3)

        label_titulacion = QLabel("Titulacion")
        layout_grid.addWidget(label_titulacion, 4, 0, 1, 3)
        self.line_titulacion = QLineEdit()
        self.line_titulacion.setPlaceholderText("Titulo que se obtiene")
        layout_grid.addWidget(self.line_titulacion, 5, 0, 1, 3)

        label_modalidad = QLabel("Modalidad")
        layout_grid.addWidget(label_modalidad, 4, 3)
        self.line_modalidad = QLineEdit()
        self.line_modalidad.setPlaceholderText("Presencial, semi-presencial, virtual")
        layout_grid.addWidget(self.line_modalidad, 5, 3)

        label_descripcion = QLabel("Descripcion")
        layout_grid.addWidget(label_descripcion, 6, 0, 1, 4)
        self.text_descripcion = QTextEdit()
        self.text_descripcion.setPlaceholderText("Descripcion de la carrera")
        layout_grid.addWidget(self.text_descripcion, 7, 0, 1, 4)

        layout_buttons.addStretch()
        self.button_aplicar = QPushButton("Aplicar")
        self.button_aplicar.clicked.connect(self.on_aplicar)
        layout_buttons.addWidget(self.button_aplicar)

        self.button_cancelar = QPushButton("Cancelar")
        self.button_cancelar.clicked.connect(self.close)
        layout_buttons.addWidget(self.button_cancelar)

        self.setLayout(layout_main)

    def _cargar_facultades(self):
        self.combo_facultad.addItem("(Sin facultad)", userData=None)
        query = QSqlQuery(db=self.modelo.database())
        if not query.exec("SELECT id_facultad, siglas, nombre FROM Facultad ORDER BY siglas"):
            error = query.lastError().text()
            LOGGER.error("Error al cargar las facultades: %s", error)
            QMessageBox.warning(self, "Error", f"No se pudieron cargar las facultades: {error}")
            return

        while query.next():
            facultad_id = query.value("id_facultad")
            siglas = query.value("siglas")
            nombre = query.value("nombre")
            self.combo_facultad.addItem(f"{siglas} - {nombre}", userData=facultad_id)

    def _cargar_campos(self):
        if self.fila is None:
            return

        registro = self.modelo.record(self.fila)
        self.line_codigo.setText(str(registro.value("codigo") or ""))
        self.line_nombre.setText(str(registro.value("nombre") or ""))
        self.line_modalidad.setText(str(registro.value("modalidad") or ""))
        self.line_duracion.setText(str(registro.value("duracion") or ""))
        self.line_titulacion.setText(str(registro.value("titulacion") or ""))
        self.line_plan_curricular.setText(str(registro.value("plan_curricular") or ""))
        self.text_descripcion.setPlainText(str(registro.value("descripcion") or ""))

        facultad_id = registro.value("id_facultad")
        indice = self.combo_facultad.findData(facultad_id)
        if indice >= 0:
            self.combo_facultad.setCurrentIndex(indice)

    def on_aplicar(self):
        codigo = self.line_codigo.text().strip()
        nombre = self.line_nombre.text().strip()
        if not codigo or not nombre:
            QMessageBox.warning(self, "Advertencia", "El codigo y el nombre son obligatorios")
            return

        duracion_texto = self.line_duracion.text().strip()
        plan_texto = self.line_plan_curricular.text().strip()
        try:
            duracion = int(duracion_texto) if duracion_texto else None
            plan_curricular = int(plan_texto) if plan_texto else None
        except ValueError:
            QMessageBox.warning(
                self,
                "Advertencia",
                "La duracion y el plan curricular deben ser numeros enteros",
            )
            return

        if duracion is not None and duracion <= 0:
            QMessageBox.warning(self, "Advertencia", "La duracion debe ser mayor que cero")
            return

        if self.fila is None:
            self.fila = self.modelo.rowCount()
            if not self.modelo.insertRow(self.fila):
                self._mostrar_error("No se pudo agregar la carrera")
                return

        valores = {
            "id_facultad": self.combo_facultad.currentData(),
            "codigo": codigo,
            "nombre": nombre,
            "descripcion": self.text_descripcion.toPlainText().strip() or None,
            "modalidad": self.line_modalidad.text().strip() or None,
            "duracion": duracion,
            "titulacion": self.line_titulacion.text().strip() or None,
            "plan_curricular": plan_curricular,
        }
        for columna, valor in valores.items():
            if not self.modelo.setData(
                self.modelo.index(self.fila, self.modelo.fieldIndex(columna)), valor
            ):
                self.modelo.revertAll()
                self._mostrar_error(f"No se pudo actualizar el campo {columna}")
                return

        if not self.modelo.submitAll():
            self.modelo.revertAll()
            self._mostrar_error("No se pudo guardar la carrera")
            return

        if not self.modelo.select():
            LOGGER.error("Error al actualizar las carreras: %s", self.modelo.lastError().text())
        self.tabla.clearSelection()
        self.close()

    def _mostrar_error(self, mensaje: str):
        error = self.modelo.lastError().text()
        LOGGER.error("%s: %s", mensaje, error)
        QMessageBox.warning(self, "Error", f"{mensaje}: {error}")
