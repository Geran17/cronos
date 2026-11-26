from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont
from PySide6.QtSql import QSqlQuery, QSqlRelation, QSqlRelationalTableModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDateEdit,
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

from interfaz.pyside6.auxiliares import obtener_conexion
from interfaz.pyside6.estilos import (
    ESTILO_PUSH_BUTTON_AGREGAR,
    ESTILO_PUSH_BUTTON_EDITAR,
    ESTILO_PUSH_BUTTON_ELIMINAR,
)
from utilidades.configuraciones import LOGGER

INDICES_COLUMNAS = {
    "id_evento": 0,
    "id_facultad": 1,
    "fecha_inicio": 2,
    "fecha_fin": 3,
    "descripcion": 4,
    "tipo_evento": 5,
    "es_fijo": 6,
    "estado": 7,
    "observaciones": 8,
    "fecha_registro": 9,
}


class CalendarioInstitucional(QWidget):
    def __init__(self):
        super().__init__()

        conexion = obtener_conexion()
        self.modelo: QSqlRelationalTableModel | None = None
        if conexion is not None:
            self.modelo = QSqlRelationalTableModel(db=conexion)

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

        label_titulo = QLabel(" 🏛️ Calendario Institucional")
        layout_titulo.addWidget(label_titulo)
        font = QFont()
        font.setPointSize(14)
        label_titulo.setFont(font)
        frame_linea = QFrame()
        frame_linea.setFrameShape(QFrame.Shape.HLine)
        layout_titulo.addWidget(frame_linea)

        self.line_buscar = QLineEdit()
        self.line_buscar.setPlaceholderText(
            "Busca por facultad, descripción, tipo, estado o fecha"
        )
        self.line_buscar.textChanged.connect(self.on_buscar)
        layout_operaciones.addWidget(self.line_buscar)

        self.push_agregar = QPushButton("Agregar")
        self.push_agregar.clicked.connect(self.on_dialogo_agregar)
        self.push_agregar.setToolTip("Agrega un evento al calendario institucional")
        self.push_agregar.setStyleSheet(ESTILO_PUSH_BUTTON_AGREGAR)
        layout_operaciones.addWidget(self.push_agregar)

        self.push_editar = QPushButton("Editar")
        self.push_editar.clicked.connect(self.on_dialogo_editar)
        self.push_editar.setToolTip("Edita el evento seleccionado")
        self.push_editar.setStyleSheet(ESTILO_PUSH_BUTTON_EDITAR)
        layout_operaciones.addWidget(self.push_editar)

        self.push_eliminar = QPushButton("Eliminar")
        self.push_eliminar.clicked.connect(self.on_dialogo_eliminar)
        self.push_eliminar.setToolTip("Elimina el evento seleccionado")
        self.push_eliminar.setStyleSheet(ESTILO_PUSH_BUTTON_ELIMINAR)
        layout_operaciones.addWidget(self.push_eliminar)

        self.tabla = QTableView()
        layout_tabla.addWidget(self.tabla)
        self.setLayout(layout_main)

    def configurar_tabla(self):
        if self.modelo is None:
            LOGGER.warning("El modelo del calendario institucional no se pudo cargar")
            return

        self.modelo.setTable("Calendario_Institucional")
        self.modelo.setRelation(
            INDICES_COLUMNAS["id_facultad"],
            QSqlRelation("Facultad", "id_facultad", "nombre"),
        )
        self.modelo.setJoinMode(QSqlRelationalTableModel.JoinMode.LeftJoin)
        self.modelo.setEditStrategy(QSqlRelationalTableModel.EditStrategy.OnManualSubmit)
        if not self.modelo.select():
            LOGGER.error(
                "Error al cargar el calendario institucional: %s",
                self.modelo.lastError().text(),
            )

        encabezados = (
            "Id",
            "Facultad",
            "Fecha inicio",
            "Fecha fin",
            "Descripción",
            "Tipo de evento",
            "Fijo",
            "Estado",
            "Observaciones",
            "Fecha de registro",
        )
        for columna, encabezado in enumerate(encabezados):
            self.modelo.setHeaderData(columna, Qt.Orientation.Horizontal, encabezado)

        self.tabla.setModel(self.modelo)
        self.tabla.resizeColumnsToContents()
        self.tabla.setColumnHidden(INDICES_COLUMNAS["id_evento"], True)
        self.tabla.setColumnHidden(INDICES_COLUMNAS["observaciones"], True)
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
                "Calendario_Institucional.id_facultad IN ("
                "SELECT id_facultad FROM Facultad "
                f"WHERE nombre LIKE {patron} OR siglas LIKE {patron}) "
                f"OR Calendario_Institucional.fecha_inicio LIKE {patron} "
                f"OR Calendario_Institucional.fecha_fin LIKE {patron} "
                f"OR Calendario_Institucional.descripcion LIKE {patron} "
                f"OR Calendario_Institucional.tipo_evento LIKE {patron} "
                f"OR Calendario_Institucional.estado LIKE {patron} "
                f"OR Calendario_Institucional.observaciones LIKE {patron} "
                f"OR Calendario_Institucional.fecha_registro LIKE {patron}"
            )
        else:
            self.modelo.setFilter("")

        if not self.modelo.select():
            LOGGER.error(
                "Error al buscar en el calendario institucional: %s",
                self.modelo.lastError().text(),
            )
        else:
            self.tabla.resizeColumnsToContents()

    def on_dialogo_agregar(self):
        if self.modelo is None:
            return
        self.dialog = DialogoCalendarioInstitucional(self.modelo, self.tabla)
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()

    def on_dialogo_editar(self):
        index = self.tabla.currentIndex()
        if not index.isValid():
            QMessageBox.information(
                self,
                "Seleccione",
                "Seleccione un evento para editar",
            )
            return
        if self.modelo is None:
            return

        self.dialog = DialogoCalendarioInstitucional(
            self.modelo,
            self.tabla,
            fila=index.row(),
        )
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()

    def on_dialogo_eliminar(self):
        index = self.tabla.currentIndex()
        if not index.isValid():
            QMessageBox.information(
                self,
                "Seleccione",
                "Seleccione un evento para eliminar",
            )
            return
        if self.modelo is None:
            return

        respuesta = QMessageBox.question(
            self,
            "Eliminar evento institucional",
            "¿Está seguro de eliminar el evento seleccionado?",
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return

        if not self.modelo.removeRow(index.row()) or not self.modelo.submitAll():
            error = self.modelo.lastError().text()
            LOGGER.error("Error al eliminar evento institucional: %s", error)
            self.modelo.revertAll()
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudo eliminar el evento institucional: {error}",
            )
            return

        if not self.modelo.select():
            LOGGER.error(
                "Error al actualizar el calendario institucional: %s",
                self.modelo.lastError().text(),
            )
        else:
            self.tabla.resizeColumnsToContents()
        self.tabla.clearSelection()


class DialogoCalendarioInstitucional(QWidget):
    def __init__(
        self,
        modelo: QSqlRelationalTableModel,
        tabla: QTableView,
        fila: int | None = None,
    ):
        super().__init__()
        self.modelo = modelo
        self.tabla = tabla
        self.fila = fila
        self.setWindowTitle(
            "Editar evento institucional" if fila is not None else "Agregar evento institucional"
        )

        self._crear_formulario()
        if not self._cargar_facultades():
            self.button_aplicar.setEnabled(False)
            return
        if self.fila is not None and not self._cargar_campos():
            self.button_aplicar.setEnabled(False)

    def _crear_formulario(self):
        layout_main = QVBoxLayout()
        layout_grid = QGridLayout()
        layout_main.addLayout(layout_grid)
        layout_buttons = QHBoxLayout()
        layout_main.addLayout(layout_buttons)

        layout_grid.addWidget(QLabel("Facultad *"), 0, 0)
        self.combo_facultad = QComboBox()
        layout_grid.addWidget(self.combo_facultad, 0, 1)

        layout_grid.addWidget(QLabel("Descripción *"), 1, 0)
        self.text_descripcion = QTextEdit()
        self.text_descripcion.setPlaceholderText("Descripción del evento institucional")
        layout_grid.addWidget(self.text_descripcion, 1, 1)

        layout_grid.addWidget(QLabel("Tipo de evento *"), 2, 0)
        self.line_tipo_evento = QLineEdit()
        self.line_tipo_evento.setPlaceholderText("Ej. Feriado, ceremonia, cierre")
        layout_grid.addWidget(self.line_tipo_evento, 2, 1)

        layout_grid.addWidget(QLabel("Fecha de inicio *"), 3, 0)
        self.date_inicio = QDateEdit()
        self._configurar_fecha(self.date_inicio)
        layout_grid.addWidget(self.date_inicio, 3, 1)

        layout_grid.addWidget(QLabel("Fecha de fin"), 4, 0)
        self.check_fecha_fin = QCheckBox("Indicar fecha")
        self.date_fin = QDateEdit()
        self._configurar_fecha(self.date_fin)
        self.date_fin.setEnabled(False)
        self.check_fecha_fin.toggled.connect(self.date_fin.setEnabled)
        layout_fecha_fin = QHBoxLayout()
        layout_fecha_fin.addWidget(self.check_fecha_fin)
        layout_fecha_fin.addWidget(self.date_fin)
        layout_grid.addLayout(layout_fecha_fin, 4, 1)

        layout_grid.addWidget(QLabel("Estado *"), 5, 0)
        self.line_estado = QLineEdit("Activo")
        self.line_estado.setPlaceholderText("Estado del evento")
        layout_grid.addWidget(self.line_estado, 5, 1)

        layout_grid.addWidget(QLabel("Fecha de registro"), 6, 0)
        self.check_fecha_registro = QCheckBox("Indicar fecha")
        self.date_registro = QDateEdit()
        self._configurar_fecha(self.date_registro)
        self.date_registro.setEnabled(False)
        self.check_fecha_registro.toggled.connect(self.date_registro.setEnabled)
        layout_fecha_registro = QHBoxLayout()
        layout_fecha_registro.addWidget(self.check_fecha_registro)
        layout_fecha_registro.addWidget(self.date_registro)
        layout_grid.addLayout(layout_fecha_registro, 6, 1)

        layout_grid.addWidget(QLabel("Evento fijo"), 7, 0)
        self.check_es_fijo = QCheckBox("Se repite cada año")
        layout_grid.addWidget(self.check_es_fijo, 7, 1)

        layout_grid.addWidget(QLabel("Observaciones"), 8, 0)
        self.text_observaciones = QTextEdit()
        self.text_observaciones.setPlaceholderText("Notas adicionales")
        layout_grid.addWidget(self.text_observaciones, 8, 1)

        layout_buttons.addStretch()
        self.button_aplicar = QPushButton("Aplicar")
        self.button_aplicar.clicked.connect(self.on_aplicar)
        layout_buttons.addWidget(self.button_aplicar)

        self.button_cancelar = QPushButton("Cancelar")
        self.button_cancelar.clicked.connect(self.close)
        layout_buttons.addWidget(self.button_cancelar)

        self.setLayout(layout_main)

    @staticmethod
    def _configurar_fecha(campo: QDateEdit):
        campo.setCalendarPopup(True)
        campo.setDisplayFormat("yyyy-MM-dd")
        campo.setDate(QDate.currentDate())

    def _cargar_facultades(self) -> bool:
        consulta = QSqlQuery(db=self.modelo.database())
        if not consulta.exec(
            "SELECT id_facultad, siglas, nombre FROM Facultad ORDER BY siglas"
        ):
            self._mostrar_error(
                "No se pudieron cargar las facultades",
                consulta.lastError().text(),
            )
            return False

        while consulta.next():
            facultad_id = consulta.value("id_facultad")
            siglas = consulta.value("siglas")
            nombre = consulta.value("nombre")
            self.combo_facultad.addItem(
                f"{siglas} - {nombre}",
                userData=facultad_id,
            )

        if not self.combo_facultad.count():
            QMessageBox.information(
                self,
                "Datos insuficientes",
                "Debes registrar una facultad antes de agregar eventos institucionales.",
            )
            return False
        return True

    def _cargar_campos(self) -> bool:
        if self.fila is None:
            return True

        registro = self.modelo.record(self.fila)
        consulta = QSqlQuery(db=self.modelo.database())
        if not consulta.prepare(
            "SELECT id_facultad FROM Calendario_Institucional "
            "WHERE id_evento = :id_evento"
        ):
            self._mostrar_error(
                "No se pudo cargar la facultad del evento",
                consulta.lastError().text(),
            )
            return False
        consulta.bindValue(":id_evento", registro.value("id_evento"))
        if not consulta.exec() or not consulta.next():
            self._mostrar_error(
                "No se pudo cargar el evento seleccionado",
                consulta.lastError().text() or "El evento ya no existe.",
            )
            return False

        indice_facultad = self.combo_facultad.findData(consulta.value("id_facultad"))
        if indice_facultad >= 0:
            self.combo_facultad.setCurrentIndex(indice_facultad)

        self.text_descripcion.setPlainText(str(registro.value("descripcion") or ""))
        self.line_tipo_evento.setText(str(registro.value("tipo_evento") or ""))
        self.line_estado.setText(str(registro.value("estado") or ""))
        self.check_es_fijo.setChecked(bool(registro.value("es_fijo")))
        self.text_observaciones.setPlainText(
            str(registro.value("observaciones") or "")
        )
        self._cargar_fecha(self.date_inicio, registro.value("fecha_inicio"))
        self._cargar_fecha_opcional(
            self.check_fecha_fin,
            self.date_fin,
            registro.value("fecha_fin"),
        )
        self._cargar_fecha_opcional(
            self.check_fecha_registro,
            self.date_registro,
            registro.value("fecha_registro"),
        )
        return True

    @staticmethod
    def _cargar_fecha(campo: QDateEdit, valor):
        texto = str(valor or "")
        fecha = QDate.fromString(texto, Qt.DateFormat.ISODate)
        if fecha.isValid():
            campo.setDate(fecha)
        else:
            LOGGER.warning("Fecha de inicio institucional no válida: %s", texto)

    @staticmethod
    def _cargar_fecha_opcional(check: QCheckBox, campo: QDateEdit, valor):
        texto = str(valor or "")
        if not texto:
            return
        fecha = QDate.fromString(texto, Qt.DateFormat.ISODate)
        if fecha.isValid():
            check.setChecked(True)
            campo.setDate(fecha)
        else:
            LOGGER.warning("Fecha institucional no válida: %s", texto)

    def on_aplicar(self):
        descripcion = self.text_descripcion.toPlainText().strip()
        tipo_evento = self.line_tipo_evento.text().strip()
        estado = self.line_estado.text().strip()
        if not descripcion or not tipo_evento or not estado:
            QMessageBox.warning(
                self,
                "Advertencia",
                "La descripción, el tipo de evento y el estado son obligatorios.",
            )
            return
        if self.combo_facultad.currentData() is None:
            QMessageBox.warning(self, "Advertencia", "Selecciona una facultad.")
            return

        fecha_inicio = self.date_inicio.date()
        fecha_fin = self.date_fin.date() if self.check_fecha_fin.isChecked() else None
        if fecha_fin is not None and fecha_fin < fecha_inicio:
            QMessageBox.warning(
                self,
                "Advertencia",
                "La fecha de fin no puede ser anterior a la fecha de inicio.",
            )
            return

        fecha_registro = (
            self.date_registro.date()
            if self.check_fecha_registro.isChecked()
            else None
        )
        if self.fila is None:
            self.fila = self.modelo.rowCount()
            if not self.modelo.insertRow(self.fila):
                self._mostrar_error(
                    "No se pudo agregar el evento institucional",
                    self.modelo.lastError().text(),
                )
                return

        valores = (
            ("id_facultad", self.combo_facultad.currentData()),
            ("fecha_inicio", fecha_inicio.toString(Qt.DateFormat.ISODate)),
            (
                "fecha_fin",
                fecha_fin.toString(Qt.DateFormat.ISODate) if fecha_fin else None,
            ),
            ("descripcion", descripcion),
            ("tipo_evento", tipo_evento),
            ("es_fijo", int(self.check_es_fijo.isChecked())),
            ("estado", estado),
            ("observaciones", self.text_observaciones.toPlainText().strip() or None),
            (
                "fecha_registro",
                fecha_registro.toString(Qt.DateFormat.ISODate) if fecha_registro else None,
            ),
        )
        for campo, valor in valores:
            if not self.modelo.setData(
                self.modelo.index(self.fila, INDICES_COLUMNAS[campo]),
                valor,
            ):
                self.modelo.revertAll()
                self._mostrar_error(
                    f"No se pudo actualizar el campo {campo}",
                    self.modelo.lastError().text(),
                )
                return

        if not self.modelo.submitAll():
            error = self.modelo.lastError().text()
            self.modelo.revertAll()
            self._mostrar_error("No se pudo guardar el evento institucional", error)
            return

        if not self.modelo.select():
            LOGGER.error(
                "Error al actualizar el calendario institucional: %s",
                self.modelo.lastError().text(),
            )
        else:
            self.tabla.resizeColumnsToContents()
        self.tabla.clearSelection()
        self.close()

    def _mostrar_error(self, mensaje: str, error: str):
        LOGGER.error("%s: %s", mensaje, error)
        QMessageBox.warning(self, "Error", f"{mensaje}: {error}")
