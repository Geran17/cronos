from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtSql import QSqlQuery, QSqlRelationalTableModel, QSqlRelation
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
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
    "id_matricula": 0,
    "id_carrera": 1,
    "ano_matriculacion": 2,
    "plan": 3,
}


class Matriculacion(QWidget):
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

        label_titulo = QLabel(" 📝 Matriculación")
        layout_titulo.addWidget(label_titulo)
        font = QFont()
        font.setPointSize(14)
        label_titulo.setFont(font)
        frame_linea = QFrame()
        frame_linea.setFrameShape(QFrame.Shape.HLine)
        layout_titulo.addWidget(frame_linea)

        self.line_buscar = QLineEdit()
        self.line_buscar.setPlaceholderText("Busca por carrera, año o plan")
        self.line_buscar.textChanged.connect(self.on_buscar)
        layout_operaciones.addWidget(self.line_buscar)

        self.push_agregar = QPushButton("Agregar")
        self.push_agregar.clicked.connect(self.on_dialogo_agregar)
        self.push_agregar.setToolTip("Registra una nueva matrícula")
        self.push_agregar.setStyleSheet(ESTILO_PUSH_BUTTON_AGREGAR)
        layout_operaciones.addWidget(self.push_agregar)

        self.push_editar = QPushButton("Editar")
        self.push_editar.clicked.connect(self.on_dialogo_editar)
        self.push_editar.setToolTip("Edita la matrícula seleccionada")
        self.push_editar.setStyleSheet(ESTILO_PUSH_BUTTON_EDITAR)
        layout_operaciones.addWidget(self.push_editar)

        self.push_eliminar = QPushButton("Eliminar")
        self.push_eliminar.clicked.connect(self.on_dialogo_eliminar)
        self.push_eliminar.setToolTip("Elimina la matrícula seleccionada")
        self.push_eliminar.setStyleSheet(ESTILO_PUSH_BUTTON_ELIMINAR)
        layout_operaciones.addWidget(self.push_eliminar)

        self.tabla = QTableView()
        layout_tabla.addWidget(self.tabla)
        self.setLayout(layout_main)

    def configurar_tabla(self):
        if self.modelo is None:
            LOGGER.warning("El modelo de la tabla no se pudo cargar: %s", self.modelo)
            return

        self.modelo.setTable("Matricula")
        self.modelo.setRelation(
            INDICES_COLUMNAS["id_carrera"],
            QSqlRelation("Carrera", "id_carrera", "nombre"),
        )

        self.modelo.setEditStrategy(QSqlRelationalTableModel.EditStrategy.OnManualSubmit)
        if not self.modelo.select():
            LOGGER.error("Error al cargar las matrículas: %s", self.modelo.lastError().text())

        encabezados = {
            "id_matricula": "Id",
            "id_carrera": "Carrera",
            "ano_matriculacion": "Año",
            "plan": "Plan",
        }
        for campo, encabezado in encabezados.items():
            self.modelo.setHeaderData(
                INDICES_COLUMNAS[campo],
                Qt.Orientation.Horizontal,
                encabezado,
            )

        self.tabla.setModel(self.modelo)
        self.tabla.resizeColumnsToContents()
        self.tabla.setColumnHidden(INDICES_COLUMNAS["id_matricula"], True)
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

    def on_buscar(self, texto: str):
        if self.modelo is None:
            return

        patron = texto.replace("'", "''")
        if patron:
            patron = f"'%{patron}%'"
            filtros = [
                "Matricula.id_carrera IN ("
                "SELECT id_carrera FROM Carrera "
                f"WHERE codigo LIKE {patron} OR nombre LIKE {patron})",
                f"CAST(Matricula.ano_matriculacion AS TEXT) LIKE {patron}",
                f"Matricula.plan LIKE {patron}",
            ]
            self.modelo.setFilter(" OR ".join(filtros))
        else:
            self.modelo.setFilter("")

        if not self.modelo.select():
            LOGGER.error("Error al buscar matrículas: %s", self.modelo.lastError().text())

    def on_dialogo_agregar(self):
        if self.modelo is None:
            return
        self.dialog = DialogoMatriculacion(self.modelo, self.tabla)
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()

    def on_dialogo_editar(self):
        index = self.tabla.currentIndex()
        if not index.isValid():
            QMessageBox.information(self, "Seleccione", "Seleccione una matrícula para editar")
            return
        if self.modelo is None:
            return

        self.dialog = DialogoMatriculacion(self.modelo, self.tabla, fila=index.row())
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()

    def on_dialogo_eliminar(self):
        index = self.tabla.currentIndex()
        if not index.isValid():
            QMessageBox.information(self, "Seleccione", "Seleccione una matrícula para eliminar")
            return
        if self.modelo is None:
            return

        respuesta = QMessageBox.question(
            self,
            "Eliminar matrícula",
            "¿Está seguro de que quiere eliminar la matrícula seleccionada?",
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return

        if not self.modelo.removeRow(index.row()) or not self.modelo.submitAll():
            error = self.modelo.lastError().text()
            LOGGER.error("Error al eliminar la matrícula: %s", error)
            self.modelo.revertAll()
            QMessageBox.warning(self, "Error", f"No se pudo eliminar la matrícula: {error}")
            return

        if not self.modelo.select():
            LOGGER.error("Error al actualizar las matrículas: %s", self.modelo.lastError().text())
        self.tabla.clearSelection()


class DialogoMatriculacion(QWidget):
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
            "Editar matrícula seleccionada" if fila is not None else "Agregar matrícula"
        )

        self._crear_formulario()
        if not self._cargar_carreras():
            self.button_aplicar.setEnabled(False)
            return
        if self.fila is not None:
            self._cargar_campos()

    def _crear_formulario(self):
        layout_main = QVBoxLayout()
        layout_grid = QGridLayout()
        layout_main.addLayout(layout_grid)
        layout_buttons = QHBoxLayout()
        layout_main.addLayout(layout_buttons)

        layout_grid.addWidget(QLabel("Carrera *"), 0, 0)
        self.combo_carrera = QComboBox()
        layout_grid.addWidget(self.combo_carrera, 0, 1)

        layout_grid.addWidget(QLabel("Año de matriculación"), 1, 0)
        self.line_ano = QLineEdit()
        self.line_ano.setPlaceholderText("Ej. 2025")
        layout_grid.addWidget(self.line_ano, 1, 1)

        layout_grid.addWidget(QLabel("Plan"), 2, 0)
        self.line_plan = QLineEdit()
        self.line_plan.setPlaceholderText("Plan de estudios")
        layout_grid.addWidget(self.line_plan, 2, 1)

        layout_buttons.addStretch()
        self.button_aplicar = QPushButton("Aplicar")
        self.button_aplicar.clicked.connect(self.on_aplicar)
        layout_buttons.addWidget(self.button_aplicar)

        self.button_cancelar = QPushButton("Cancelar")
        self.button_cancelar.clicked.connect(self.close)
        layout_buttons.addWidget(self.button_cancelar)

        self.setLayout(layout_main)

    def _cargar_carreras(self) -> bool:
        consulta = QSqlQuery(db=self.modelo.database())
        if not consulta.exec("SELECT id_carrera, codigo, nombre FROM Carrera ORDER BY codigo"):
            self._mostrar_error("No se pudieron cargar las carreras", consulta.lastError().text())
            return False

        while consulta.next():
            carrera_id = consulta.value("id_carrera")
            codigo = consulta.value("codigo")
            nombre = consulta.value("nombre")
            self.combo_carrera.addItem(f"{codigo} - {nombre}", userData=carrera_id)

        if self.combo_carrera.count() == 0:
            QMessageBox.information(
                self,
                "Datos insuficientes",
                "Debes registrar al menos una carrera antes de crear una matrícula.",
            )
            return False
        return True

    def _cargar_campos(self):
        if self.fila is None:
            return

        carrera_id = self.modelo.data(
            self.modelo.index(self.fila, INDICES_COLUMNAS["id_carrera"]),
            Qt.ItemDataRole.EditRole,
        )
        indice = self.combo_carrera.findData(carrera_id)
        if indice >= 0:
            self.combo_carrera.setCurrentIndex(indice)

        registro = self.modelo.record(self.fila)
        self.line_ano.setText(str(registro.value("ano_matriculacion") or ""))
        self.line_plan.setText(str(registro.value("plan") or ""))

    def on_aplicar(self):
        ano_texto = self.line_ano.text().strip()
        try:
            ano = int(ano_texto) if ano_texto else None
        except ValueError:
            QMessageBox.warning(self, "Advertencia", "El año debe ser un número entero")
            return

        if ano is not None and ano <= 0:
            QMessageBox.warning(self, "Advertencia", "El año debe ser mayor que cero")
            return

        if self.fila is None:
            self.fila = self.modelo.rowCount()
            if not self.modelo.insertRow(self.fila):
                self._mostrar_error("No se pudo agregar la matrícula", self.modelo.lastError().text())
                return

        valores = (
            ("id_carrera", self.combo_carrera.currentData()),
            ("ano_matriculacion", ano),
            ("plan", self.line_plan.text().strip() or None),
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
            self._mostrar_error("No se pudo guardar la matrícula", error)
            return

        if not self.modelo.select():
            LOGGER.error("Error al actualizar las matrículas: %s", self.modelo.lastError().text())
        self.tabla.clearSelection()
        self.close()

    def _mostrar_error(self, mensaje: str, error: str):
        LOGGER.error("%s: %s", mensaje, error)
        QMessageBox.warning(self, "Error", f"{mensaje}: {error}")
