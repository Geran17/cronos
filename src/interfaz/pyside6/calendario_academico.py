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
    "id_calendario": 0,
    "id_facultad": 1,
    "periodo_academico": 2,
    "actividad": 3,
    "detalle": 4,
    "fecha_inicio": 5,
    "fecha_fin": 6,
    "hora": 7,
    "texto_original": 8,
}


class CalendarioAcademico(QWidget):
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

        label_titulo = QLabel(" 📚 Calendario Académico")
        layout_titulo.addWidget(label_titulo)
        font = QFont()
        font.setPointSize(14)
        label_titulo.setFont(font)
        frame_linea = QFrame()
        frame_linea.setFrameShape(QFrame.Shape.HLine)
        layout_titulo.addWidget(frame_linea)

        self.line_buscar = QLineEdit()
        self.line_buscar.setPlaceholderText(
            "Busca por facultad, período, actividad, fecha u hora"
        )
        self.line_buscar.textChanged.connect(self.on_buscar)
        layout_operaciones.addWidget(self.line_buscar)

        self.push_agregar = QPushButton("Agregar")
        self.push_agregar.clicked.connect(self.on_dialogo_agregar)
        self.push_agregar.setToolTip("Agrega una actividad al calendario académico")
        self.push_agregar.setStyleSheet(ESTILO_PUSH_BUTTON_AGREGAR)
        layout_operaciones.addWidget(self.push_agregar)

        self.push_editar = QPushButton("Editar")
        self.push_editar.clicked.connect(self.on_dialogo_editar)
        self.push_editar.setToolTip("Edita la actividad seleccionada")
        self.push_editar.setStyleSheet(ESTILO_PUSH_BUTTON_EDITAR)
        layout_operaciones.addWidget(self.push_editar)

        self.push_eliminar = QPushButton("Eliminar")
        self.push_eliminar.clicked.connect(self.on_dialogo_eliminar)
        self.push_eliminar.setToolTip("Elimina la actividad seleccionada")
        self.push_eliminar.setStyleSheet(ESTILO_PUSH_BUTTON_ELIMINAR)
        layout_operaciones.addWidget(self.push_eliminar)

        self.tabla = QTableView()
        layout_tabla.addWidget(self.tabla)
        self.setLayout(layout_main)

    def configurar_tabla(self):
        if self.modelo is None:
            LOGGER.warning("El modelo del calendario académico no se pudo cargar")
            return

        self.modelo.setTable("Calendario_Academico")
        self.modelo.setRelation(
            INDICES_COLUMNAS["id_facultad"],
            QSqlRelation("Facultad", "id_facultad", "nombre"),
        )
        self.modelo.setJoinMode(QSqlRelationalTableModel.JoinMode.LeftJoin)
        self.modelo.setEditStrategy(QSqlRelationalTableModel.EditStrategy.OnManualSubmit)
        if not self.modelo.select():
            LOGGER.error(
                "Error al cargar el calendario académico: %s",
                self.modelo.lastError().text(),
            )

        encabezados = (
            "Id",
            "Facultad",
            "Período académico",
            "Actividad",
            "Detalle",
            "Fecha inicio",
            "Fecha fin",
            "Hora",
            "Texto original",
        )
        for columna, encabezado in enumerate(encabezados):
            self.modelo.setHeaderData(columna, Qt.Orientation.Horizontal, encabezado)

        self.tabla.setModel(self.modelo)
        self.tabla.resizeColumnsToContents()
        self.tabla.setColumnHidden(INDICES_COLUMNAS["id_calendario"], True)
        self.tabla.setColumnHidden(INDICES_COLUMNAS["texto_original"], True)
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
                "Calendario_Academico.id_facultad IN ("
                "SELECT id_facultad FROM Facultad "
                f"WHERE nombre LIKE {patron} OR siglas LIKE {patron}) "
                f"OR Calendario_Academico.periodo_academico LIKE {patron} "
                f"OR Calendario_Academico.actividad LIKE {patron} "
                f"OR Calendario_Academico.detalle LIKE {patron} "
                f"OR Calendario_Academico.fecha_inicio LIKE {patron} "
                f"OR Calendario_Academico.fecha_fin LIKE {patron} "
                f"OR Calendario_Academico.hora LIKE {patron} "
                f"OR Calendario_Academico.texto_original LIKE {patron}"
            )
        else:
            self.modelo.setFilter("")

        if not self.modelo.select():
            LOGGER.error(
                "Error al buscar en el calendario académico: %s",
                self.modelo.lastError().text(),
            )
        else:
            self.tabla.resizeColumnsToContents()

    def on_dialogo_agregar(self):
        if self.modelo is None:
            return
        self.dialog = DialogoCalendarioAcademico(self.modelo, self.tabla)
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()

    def on_dialogo_editar(self):
        index = self.tabla.currentIndex()
        if not index.isValid():
            QMessageBox.information(
                self,
                "Seleccione",
                "Seleccione una actividad para editar",
            )
            return
        if self.modelo is None:
            return

        self.dialog = DialogoCalendarioAcademico(
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
                "Seleccione una actividad para eliminar",
            )
            return
        if self.modelo is None:
            return

        respuesta = QMessageBox.question(
            self,
            "Eliminar actividad académica",
            "¿Está seguro de eliminar la actividad seleccionada?",
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return

        if not self.modelo.removeRow(index.row()) or not self.modelo.submitAll():
            error = self.modelo.lastError().text()
            LOGGER.error("Error al eliminar actividad académica: %s", error)
            self.modelo.revertAll()
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudo eliminar la actividad académica: {error}",
            )
            return

        if not self.modelo.select():
            LOGGER.error(
                "Error al actualizar el calendario académico: %s",
                self.modelo.lastError().text(),
            )
        else:
            self.tabla.resizeColumnsToContents()
        self.tabla.clearSelection()


class DialogoCalendarioAcademico(QWidget):
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
            "Editar actividad académica"
            if fila is not None
            else "Agregar actividad académica"
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

        layout_grid.addWidget(QLabel("Período académico *"), 1, 0)
        self.line_periodo = QLineEdit()
        self.line_periodo.setPlaceholderText("Ej. 2026-1")
        layout_grid.addWidget(self.line_periodo, 1, 1)

        layout_grid.addWidget(QLabel("Actividad *"), 2, 0)
        self.line_actividad = QLineEdit()
        self.line_actividad.setPlaceholderText("Nombre de la actividad académica")
        layout_grid.addWidget(self.line_actividad, 2, 1)

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

        layout_grid.addWidget(QLabel("Hora"), 5, 0)
        self.line_hora = QLineEdit()
        self.line_hora.setPlaceholderText("Opcional, ej. 09:00")
        layout_grid.addWidget(self.line_hora, 5, 1)

        layout_grid.addWidget(QLabel("Detalle"), 6, 0)
        self.text_detalle = QTextEdit()
        self.text_detalle.setPlaceholderText("Información adicional")
        layout_grid.addWidget(self.text_detalle, 6, 1)

        layout_grid.addWidget(QLabel("Texto original"), 7, 0)
        self.text_original = QTextEdit()
        self.text_original.setPlaceholderText("Texto fuente, si corresponde")
        layout_grid.addWidget(self.text_original, 7, 1)

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
                "Debes registrar una facultad antes de agregar actividades al calendario.",
            )
            return False
        return True

    def _cargar_campos(self) -> bool:
        if self.fila is None:
            return True

        registro = self.modelo.record(self.fila)
        consulta = QSqlQuery(db=self.modelo.database())
        if not consulta.prepare(
            "SELECT id_facultad FROM Calendario_Academico "
            "WHERE id_calendario = :id_calendario"
        ):
            self._mostrar_error(
                "No se pudo cargar la facultad de la actividad",
                consulta.lastError().text(),
            )
            return False
        consulta.bindValue(":id_calendario", registro.value("id_calendario"))
        if not consulta.exec() or not consulta.next():
            self._mostrar_error(
                "No se pudo cargar la actividad seleccionada",
                consulta.lastError().text() or "La actividad ya no existe.",
            )
            return False

        indice_facultad = self.combo_facultad.findData(consulta.value("id_facultad"))
        if indice_facultad >= 0:
            self.combo_facultad.setCurrentIndex(indice_facultad)

        self.line_periodo.setText(str(registro.value("periodo_academico") or ""))
        self.line_actividad.setText(str(registro.value("actividad") or ""))
        self.text_detalle.setPlainText(str(registro.value("detalle") or ""))
        self.line_hora.setText(str(registro.value("hora") or ""))
        self.text_original.setPlainText(str(registro.value("texto_original") or ""))
        self._cargar_fecha(self.date_inicio, registro.value("fecha_inicio"))
        self._cargar_fecha_fin(registro.value("fecha_fin"))
        return True

    def _cargar_fecha(self, campo: QDateEdit, valor):
        texto = str(valor or "")
        fecha = QDate.fromString(texto, Qt.DateFormat.ISODate)
        if fecha.isValid():
            campo.setDate(fecha)
        else:
            LOGGER.warning("Fecha de calendario académico no válida: %s", texto)

    def _cargar_fecha_fin(self, valor):
        texto = str(valor or "")
        if not texto:
            return
        fecha = QDate.fromString(texto, Qt.DateFormat.ISODate)
        if fecha.isValid():
            self.check_fecha_fin.setChecked(True)
            self.date_fin.setDate(fecha)
        else:
            LOGGER.warning("Fecha de fin no válida en calendario académico: %s", texto)

    def on_aplicar(self):
        periodo = self.line_periodo.text().strip()
        actividad = self.line_actividad.text().strip()
        if not periodo or not actividad:
            QMessageBox.warning(
                self,
                "Advertencia",
                "El período académico y la actividad son obligatorios.",
            )
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

        if self.fila is None:
            self.fila = self.modelo.rowCount()
            if not self.modelo.insertRow(self.fila):
                self._mostrar_error(
                    "No se pudo agregar la actividad académica",
                    self.modelo.lastError().text(),
                )
                return

        valores = (
            ("id_facultad", self.combo_facultad.currentData()),
            ("periodo_academico", periodo),
            ("actividad", actividad),
            ("detalle", self.text_detalle.toPlainText().strip() or None),
            ("fecha_inicio", fecha_inicio.toString(Qt.DateFormat.ISODate)),
            (
                "fecha_fin",
                fecha_fin.toString(Qt.DateFormat.ISODate) if fecha_fin else None,
            ),
            ("hora", self.line_hora.text().strip() or None),
            ("texto_original", self.text_original.toPlainText().strip() or None),
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
            self._mostrar_error("No se pudo guardar la actividad académica", error)
            return

        if not self.modelo.select():
            LOGGER.error(
                "Error al actualizar el calendario académico: %s",
                self.modelo.lastError().text(),
            )
        else:
            self.tabla.resizeColumnsToContents()
        self.tabla.clearSelection()
        self.close()

    def _mostrar_error(self, mensaje: str, error: str):
        LOGGER.error("%s: %s", mensaje, error)
        QMessageBox.warning(self, "Error", f"{mensaje}: {error}")
