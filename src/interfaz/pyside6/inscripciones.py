import math

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
    "id_inscripcion": 0,
    "id_asignatura": 1,
    "id_profesor": 2,
    "fecha_inscripcion": 3,
    "semestre": 4,
    "periodo": 5,
    "seccion": 6,
    "puntaje": 7,
    "nota": 8,
    "estado": 9,
}

SEMESTRES = ("1er Semestre", "2do Semestre")
PERIODOS = ("1er Periodo", "2do. Periodo")
ESTADOS = ("Cursando", "Aprobado", "Reprobado", "Retirado")


class Inscripciones(QWidget):
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

        label_titulo = QLabel(" 📋 Inscripciones")
        layout_titulo.addWidget(label_titulo)
        font = QFont()
        font.setPointSize(14)
        label_titulo.setFont(font)
        frame_linea = QFrame()
        frame_linea.setFrameShape(QFrame.Shape.HLine)
        layout_titulo.addWidget(frame_linea)

        self.line_buscar = QLineEdit()
        self.line_buscar.setPlaceholderText(
            "Busca por asignatura, profesor, semestre, sección o estado"
        )
        self.line_buscar.textChanged.connect(self.on_buscar)
        layout_operaciones.addWidget(self.line_buscar)

        self.push_agregar = QPushButton("Agregar")
        self.push_agregar.clicked.connect(self.on_dialogo_agregar)
        self.push_agregar.setToolTip("Registra una nueva inscripción")
        self.push_agregar.setStyleSheet(ESTILO_PUSH_BUTTON_AGREGAR)
        layout_operaciones.addWidget(self.push_agregar)

        self.push_editar = QPushButton("Editar")
        self.push_editar.clicked.connect(self.on_dialogo_editar)
        self.push_editar.setToolTip("Edita la inscripción seleccionada")
        self.push_editar.setStyleSheet(ESTILO_PUSH_BUTTON_EDITAR)
        layout_operaciones.addWidget(self.push_editar)

        self.push_eliminar = QPushButton("Eliminar")
        self.push_eliminar.clicked.connect(self.on_dialogo_eliminar)
        self.push_eliminar.setToolTip("Elimina la inscripción seleccionada")
        self.push_eliminar.setStyleSheet(ESTILO_PUSH_BUTTON_ELIMINAR)
        layout_operaciones.addWidget(self.push_eliminar)

        self.tabla = QTableView()
        layout_tabla.addWidget(self.tabla)
        self.setLayout(layout_main)

    def configurar_tabla(self):
        if self.modelo is None:
            LOGGER.warning("El modelo de la tabla no se pudo cargar: %s", self.modelo)
            return

        self.modelo.setTable("Inscripcion")
        self.modelo.setRelation(
            INDICES_COLUMNAS["id_asignatura"],
            QSqlRelation("Asignatura", "id_asignatura", "nombre"),
        )
        self.modelo.setRelation(
            INDICES_COLUMNAS["id_profesor"],
            QSqlRelation("Profesor", "id_profesor", "nombre"),
        )
        self.modelo.setJoinMode(QSqlRelationalTableModel.JoinMode.LeftJoin)
        self.modelo.setEditStrategy(QSqlRelationalTableModel.EditStrategy.OnManualSubmit)
        if not self.modelo.select():
            LOGGER.error("Error al cargar las inscripciones: %s", self.modelo.lastError().text())

        encabezados = (
            "Id",
            "Asignatura",
            "Profesor",
            "Fecha",
            "Semestre",
            "Periodo",
            "Sección",
            "Puntaje",
            "Nota",
            "Estado",
        )
        for columna, encabezado in enumerate(encabezados):
            self.modelo.setHeaderData(columna, Qt.Orientation.Horizontal, encabezado)

        self.tabla.setModel(self.modelo)
        self.tabla.resizeColumnsToContents()
        self.tabla.setColumnHidden(INDICES_COLUMNAS["id_inscripcion"], True)
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
                "Inscripcion.id_asignatura IN ("
                "SELECT id_asignatura FROM Asignatura "
                f"WHERE codigo LIKE {patron} OR nombre LIKE {patron}) "
                "OR Inscripcion.id_profesor IN ("
                "SELECT id_profesor FROM Profesor "
                f"WHERE nombre LIKE {patron} OR apellido LIKE {patron}) "
                f"OR Inscripcion.fecha_inscripcion LIKE {patron} "
                f"OR Inscripcion.semestre LIKE {patron} "
                f"OR Inscripcion.periodo LIKE {patron} "
                f"OR Inscripcion.seccion LIKE {patron} "
                f"OR CAST(Inscripcion.puntaje AS TEXT) LIKE {patron} "
                f"OR CAST(Inscripcion.nota AS TEXT) LIKE {patron} "
                f"OR Inscripcion.estado LIKE {patron}"
            )
        else:
            self.modelo.setFilter("")

        if not self.modelo.select():
            LOGGER.error("Error al buscar inscripciones: %s", self.modelo.lastError().text())

    def on_dialogo_agregar(self):
        if self.modelo is None:
            return
        self.dialog = DialogoInscripcion(self.modelo, self.tabla)
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()

    def on_dialogo_editar(self):
        index = self.tabla.currentIndex()
        if not index.isValid():
            QMessageBox.information(self, "Seleccione", "Seleccione una inscripción para editar")
            return
        if self.modelo is None:
            return

        self.dialog = DialogoInscripcion(self.modelo, self.tabla, fila=index.row())
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()

    def on_dialogo_eliminar(self):
        index = self.tabla.currentIndex()
        if not index.isValid():
            QMessageBox.information(self, "Seleccione", "Seleccione una inscripción para eliminar")
            return
        if self.modelo is None:
            return

        respuesta = QMessageBox.question(
            self,
            "Eliminar inscripción",
            "¿Está seguro de eliminar la inscripción seleccionada? "
            "También se eliminarán sus actividades asociadas.",
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return

        if not self.modelo.removeRow(index.row()) or not self.modelo.submitAll():
            error = self.modelo.lastError().text()
            LOGGER.error("Error al eliminar la inscripción: %s", error)
            self.modelo.revertAll()
            QMessageBox.warning(self, "Error", f"No se pudo eliminar la inscripción: {error}")
            return

        if not self.modelo.select():
            LOGGER.error("Error al actualizar las inscripciones: %s", self.modelo.lastError().text())
        self.tabla.clearSelection()


class DialogoInscripcion(QWidget):
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
            "Editar inscripción seleccionada" if fila is not None else "Agregar inscripción"
        )

        self._crear_formulario()
        if not self._cargar_catalogos():
            self.button_aplicar.setEnabled(False)
            return
        if self.fila is not None:
            if not self._cargar_campos():
                self.button_aplicar.setEnabled(False)

    def _crear_formulario(self):
        layout_main = QVBoxLayout()
        layout_grid = QGridLayout()
        layout_main.addLayout(layout_grid)
        layout_buttons = QHBoxLayout()
        layout_main.addLayout(layout_buttons)

        layout_grid.addWidget(QLabel("Asignatura *"), 0, 0)
        self.combo_asignatura = QComboBox()
        layout_grid.addWidget(self.combo_asignatura, 0, 1)

        layout_grid.addWidget(QLabel("Profesor"), 1, 0)
        self.combo_profesor = QComboBox()
        layout_grid.addWidget(self.combo_profesor, 1, 1)

        layout_grid.addWidget(QLabel("Fecha de inscripción"), 2, 0)
        layout_fecha = QHBoxLayout()
        self.check_fecha = QCheckBox("Indicar fecha")
        self.date_fecha = QDateEdit()
        self.date_fecha.setCalendarPopup(True)
        self.date_fecha.setDisplayFormat("yyyy-MM-dd")
        self.date_fecha.setDate(QDate.currentDate())
        self.date_fecha.setEnabled(False)
        self.check_fecha.toggled.connect(self.date_fecha.setEnabled)
        layout_fecha.addWidget(self.check_fecha)
        layout_fecha.addWidget(self.date_fecha)
        layout_grid.addLayout(layout_fecha, 2, 1)

        layout_grid.addWidget(QLabel("Semestre"), 3, 0)
        self.combo_semestre = QComboBox()
        layout_grid.addWidget(self.combo_semestre, 3, 1)

        layout_grid.addWidget(QLabel("Periodo"), 4, 0)
        self.combo_periodo = QComboBox()
        layout_grid.addWidget(self.combo_periodo, 4, 1)

        layout_grid.addWidget(QLabel("Sección"), 5, 0)
        self.line_seccion = QLineEdit()
        layout_grid.addWidget(self.line_seccion, 5, 1)

        layout_grid.addWidget(QLabel("Puntaje"), 6, 0)
        self.line_puntaje = QLineEdit()
        self.line_puntaje.setPlaceholderText("Opcional, mayor o igual a cero")
        layout_grid.addWidget(self.line_puntaje, 6, 1)

        layout_grid.addWidget(QLabel("Nota"), 7, 0)
        self.line_nota = QLineEdit()
        self.line_nota.setPlaceholderText("Opcional, entre 0 y 100")
        layout_grid.addWidget(self.line_nota, 7, 1)

        layout_grid.addWidget(QLabel("Estado *"), 8, 0)
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(ESTADOS)
        layout_grid.addWidget(self.combo_estado, 8, 1)

        self.combo_profesor.addItem("(Sin profesor)", userData=None)
        self.combo_semestre.addItem("(Sin semestre)", userData=None)
        for semestre in SEMESTRES:
            self.combo_semestre.addItem(semestre, userData=semestre)
        self.combo_periodo.addItem("(Sin periodo)", userData=None)
        for periodo in PERIODOS:
            self.combo_periodo.addItem(periodo, userData=periodo)

        layout_buttons.addStretch()
        self.button_aplicar = QPushButton("Aplicar")
        self.button_aplicar.clicked.connect(self.on_aplicar)
        layout_buttons.addWidget(self.button_aplicar)

        self.button_cancelar = QPushButton("Cancelar")
        self.button_cancelar.clicked.connect(self.close)
        layout_buttons.addWidget(self.button_cancelar)

        self.setLayout(layout_main)

    def _cargar_catalogos(self) -> bool:
        consulta_asignaturas = QSqlQuery(db=self.modelo.database())
        if not consulta_asignaturas.exec(
            "SELECT id_asignatura, codigo, nombre FROM Asignatura ORDER BY codigo"
        ):
            self._mostrar_error(
                "No se pudieron cargar las asignaturas",
                consulta_asignaturas.lastError().text(),
            )
            return False

        while consulta_asignaturas.next():
            asignatura_id = consulta_asignaturas.value("id_asignatura")
            codigo = consulta_asignaturas.value("codigo")
            nombre = consulta_asignaturas.value("nombre")
            self.combo_asignatura.addItem(
                f"{codigo} - {nombre}",
                userData=asignatura_id,
            )

        if self.combo_asignatura.count() == 0:
            QMessageBox.information(
                self,
                "Datos insuficientes",
                "Debes registrar al menos una asignatura antes de crear una inscripción.",
            )
            return False

        consulta_profesores = QSqlQuery(db=self.modelo.database())
        if not consulta_profesores.exec(
            "SELECT id_profesor, nombre, apellido FROM Profesor ORDER BY apellido, nombre"
        ):
            self._mostrar_error(
                "No se pudieron cargar los profesores",
                consulta_profesores.lastError().text(),
            )
            return False

        while consulta_profesores.next():
            profesor_id = consulta_profesores.value("id_profesor")
            nombre = consulta_profesores.value("nombre")
            apellido = consulta_profesores.value("apellido")
            self.combo_profesor.addItem(
                f"{nombre} {apellido}",
                userData=profesor_id,
            )
        return True

    def _cargar_campos(self) -> bool:
        if self.fila is None:
            return True

        registro = self.modelo.record(self.fila)
        consulta = QSqlQuery(db=self.modelo.database())
        if not consulta.prepare(
            "SELECT id_asignatura, id_profesor FROM Inscripcion "
            "WHERE id_inscripcion = :id_inscripcion"
        ):
            self._mostrar_error(
                "No se pudieron cargar las relaciones de la inscripción",
                consulta.lastError().text(),
            )
            return False
        consulta.bindValue(":id_inscripcion", registro.value("id_inscripcion"))
        if not consulta.exec() or not consulta.next():
            self._mostrar_error(
                "No se pudieron cargar las relaciones de la inscripción",
                consulta.lastError().text() or "La inscripción ya no existe.",
            )
            return False

        for campo, combo in (
            ("id_asignatura", self.combo_asignatura),
            ("id_profesor", self.combo_profesor),
        ):
            indice = combo.findData(consulta.value(campo))
            if indice >= 0:
                combo.setCurrentIndex(indice)

        fecha_texto = str(registro.value("fecha_inscripcion") or "")
        if fecha_texto:
            fecha = QDate.fromString(fecha_texto, Qt.DateFormat.ISODate)
            if fecha.isValid():
                self.check_fecha.setChecked(True)
                self.date_fecha.setDate(fecha)
            else:
                LOGGER.warning("Fecha de inscripción no válida en la base de datos: %s", fecha_texto)
        self._seleccionar_combo(self.combo_semestre, registro.value("semestre"))
        self._seleccionar_combo(self.combo_periodo, registro.value("periodo"))
        self.line_seccion.setText(str(registro.value("seccion") or ""))
        self.line_puntaje.setText(self._texto_numero(registro.value("puntaje")))
        self.line_nota.setText(self._texto_numero(registro.value("nota")))
        indice_estado = self.combo_estado.findText(str(registro.value("estado") or "Cursando"))
        if indice_estado >= 0:
            self.combo_estado.setCurrentIndex(indice_estado)
        return True

    @staticmethod
    def _seleccionar_combo(combo: QComboBox, valor):
        indice = combo.findData(valor) if valor is None else combo.findText(str(valor))
        if indice >= 0:
            combo.setCurrentIndex(indice)

    @staticmethod
    def _texto_numero(valor) -> str:
        if valor is None:
            return ""
        return str(valor)

    def on_aplicar(self):
        fecha_texto = (
            self.date_fecha.date().toString(Qt.DateFormat.ISODate)
            if self.check_fecha.isChecked()
            else None
        )

        puntaje = self._leer_numero(self.line_puntaje, "El puntaje", minimo=0)
        if puntaje is False:
            return
        nota = self._leer_numero(self.line_nota, "La nota", minimo=0, maximo=100)
        if nota is False:
            return

        if self.combo_asignatura.currentData() is None:
            QMessageBox.warning(self, "Advertencia", "Selecciona una asignatura.")
            return

        if self.fila is None:
            self.fila = self.modelo.rowCount()
            if not self.modelo.insertRow(self.fila):
                self._mostrar_error(
                    "No se pudo agregar la inscripción",
                    self.modelo.lastError().text(),
                )
                return

        valores = (
            ("id_asignatura", self.combo_asignatura.currentData()),
            ("id_profesor", self.combo_profesor.currentData()),
            ("fecha_inscripcion", fecha_texto),
            ("semestre", self.combo_semestre.currentData()),
            ("periodo", self.combo_periodo.currentData()),
            ("seccion", self.line_seccion.text().strip() or None),
            ("puntaje", puntaje),
            ("nota", nota),
            ("estado", self.combo_estado.currentText()),
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
            self._mostrar_error("No se pudo guardar la inscripción", error)
            return

        if not self.modelo.select():
            LOGGER.error(
                "Error al actualizar las inscripciones: %s",
                self.modelo.lastError().text(),
            )
        self.tabla.clearSelection()
        self.close()

    def _leer_numero(
        self,
        campo: QLineEdit,
        nombre: str,
        minimo: float,
        maximo: float | None = None,
    ) -> float | None | bool:
        texto = campo.text().strip()
        if not texto:
            return None

        try:
            valor = float(texto)
        except ValueError:
            QMessageBox.warning(self, "Advertencia", f"{nombre} debe ser un número válido.")
            return False

        if not math.isfinite(valor) or valor < minimo or (maximo is not None and valor > maximo):
            if maximo is None:
                mensaje = f"{nombre} debe ser mayor o igual a {minimo:g}."
            else:
                mensaje = f"{nombre} debe estar entre {minimo:g} y {maximo:g}."
            QMessageBox.warning(self, "Advertencia", mensaje)
            return False
        return valor

    def _mostrar_error(self, mensaje: str, error: str):
        LOGGER.error("%s: %s", mensaje, error)
        QMessageBox.warning(self, "Error", f"{mensaje}: {error}")
