import math

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
    QComboBox,
    QMessageBox,
)
from PySide6.QtSql import QSqlRelationalTableModel, QSqlRelation, QSqlQuery
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from interfaz.pyside6.estilos import (
    ESTILO_PUSH_BUTTON_AGREGAR,
    ESTILO_PUSH_BUTTON_EDITAR,
    ESTILO_PUSH_BUTTON_ELIMINAR,
)
from utilidades.configuraciones import LOGGER
from interfaz.pyside6.auxiliares import obtener_conexion

INDICES_COLUMNAS = {
    "id_asignatura": 1,
    "teoricas": 2,
    "practicas": 3,
    "htd": 4,
    "hti": 5,
}


class HorasSemanales(QWidget):
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

        label_titulo = QLabel(" ⌛ Horas Semanales")
        layout_titulo.addWidget(label_titulo)
        font = QFont()
        font.setPointSize(14)
        label_titulo.setFont(font)
        frame_linea = QFrame()
        frame_linea.setFrameShape(QFrame.Shape.HLine)
        layout_titulo.addWidget(frame_linea)

        self.line_buscar = QLineEdit()
        self.line_buscar.setPlaceholderText("Busca por codigo o nombre de asignatura")
        self.line_buscar.textChanged.connect(self.on_buscar)
        layout_operaciones.addWidget(self.line_buscar)

        self.push_agregar = QPushButton("Agregar")
        self.push_agregar.clicked.connect(self.on_dialogo_agregar)
        self.push_agregar.setToolTip("Agrega las horas semanales de una asignatura")
        self.push_agregar.setStyleSheet(ESTILO_PUSH_BUTTON_AGREGAR)
        layout_operaciones.addWidget(self.push_agregar)

        self.push_editar = QPushButton("Editar")
        self.push_editar.clicked.connect(self.on_dialogo_editar)
        self.push_editar.setToolTip("Edita las horas semanales seleccionadas")
        self.push_editar.setStyleSheet(ESTILO_PUSH_BUTTON_EDITAR)
        layout_operaciones.addWidget(self.push_editar)

        self.push_eliminar = QPushButton("Eliminar")
        self.push_eliminar.clicked.connect(self.on_dialogo_eliminar)
        self.push_eliminar.setToolTip("Elimina las horas semanales seleccionadas")
        self.push_eliminar.setStyleSheet(ESTILO_PUSH_BUTTON_ELIMINAR)
        layout_operaciones.addWidget(self.push_eliminar)

        self.tabla = QTableView()
        layout_tabla.addWidget(self.tabla)
        self.setLayout(layout_main)

    def configurar_tabla(self):
        if self.modelo is None:
            LOGGER.warning("El modelo de la tabla no se pudo cargar: %s", self.modelo)
            return

        self.modelo.setTable("HorasSemanales")
        self.modelo.setRelation(1, QSqlRelation("Asignatura", "id_asignatura", "codigo"))
        self.modelo.setEditStrategy(QSqlRelationalTableModel.EditStrategy.OnManualSubmit)
        if not self.modelo.select():
            LOGGER.error("Error al cargar las horas semanales: %s", self.modelo.lastError().text())

        encabezados = ("Id", "Asignatura", "Teoricas", "Practicas", "HTD", "HTI")
        for columna, encabezado in enumerate(encabezados):
            self.modelo.setHeaderData(columna, Qt.Orientation.Horizontal, encabezado)

        self.tabla.setModel(self.modelo)
        self.tabla.resizeColumnsToContents()
        self.tabla.setColumnHidden(0, True)
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
                "HorasSemanales.id_asignatura IN ("
                "SELECT id_asignatura FROM Asignatura "
                f"WHERE codigo LIKE {patron} OR nombre LIKE {patron})"
            )
        else:
            self.modelo.setFilter("")

        if not self.modelo.select():
            LOGGER.error("Error al buscar horas semanales: %s", self.modelo.lastError().text())

    def on_dialogo_agregar(self):
        if self.modelo is None:
            return
        self.dialog = DialogoHorasSemanales(self.modelo, self.tabla)
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()

    def on_dialogo_editar(self):
        index = self.tabla.currentIndex()
        if not index.isValid():
            QMessageBox.information(self, "Seleccione", "Seleccione un registro para editar")
            return
        if self.modelo is None:
            return

        self.dialog = DialogoHorasSemanales(self.modelo, self.tabla, fila=index.row())
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()

    def on_dialogo_eliminar(self):
        index = self.tabla.currentIndex()
        if not index.isValid():
            QMessageBox.information(self, "Seleccione", "Seleccione un registro para eliminar")
            return
        if self.modelo is None:
            return

        respuesta = QMessageBox.question(
            self,
            "Eliminar horas semanales",
            "Esta seguro que quiere eliminar el registro seleccionado?",
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return

        if not self.modelo.removeRow(index.row()) or not self.modelo.submitAll():
            error = self.modelo.lastError().text()
            LOGGER.error("Error al eliminar las horas semanales: %s", error)
            self.modelo.revertAll()
            QMessageBox.warning(self, "Error", f"No se pudo eliminar el registro: {error}")
            return

        if not self.modelo.select():
            LOGGER.error(
                "Error al actualizar las horas semanales: %s",
                self.modelo.lastError().text(),
            )
        self.tabla.clearSelection()


class DialogoHorasSemanales(QWidget):
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
        self.id_asignatura = None
        titulo = "Edita las horas semanales" if fila is not None else "Agrega horas semanales"
        self.setWindowTitle(titulo)
        # self.resize(600, 300)

        if self.fila is not None:
            self.id_asignatura = self._obtener_id_asignatura(self.fila)

        self._crear_formulario()
        if self.fila is not None and self.id_asignatura is None:
            self.button_aplicar.setEnabled(False)
            return

        asignaturas_cargadas = self._cargar_asignaturas()
        if self.fila is not None:
            self._cargar_campos()
        elif asignaturas_cargadas and self.combo_asignatura.count() == 0:
            QMessageBox.information(
                self,
                "Sin asignaturas disponibles",
                "Todas las asignaturas ya tienen horas semanales registradas.",
            )
            self.button_aplicar.setEnabled(False)

    def _obtener_id_asignatura(self, fila: int) -> int | None:
        id_registro = self.modelo.record(fila).value("id_horassemanales")
        consulta = QSqlQuery(db=self.modelo.database())
        if not consulta.prepare(
            "SELECT id_asignatura FROM HorasSemanales "
            "WHERE id_horassemanales = :id_horassemanales"
        ):
            error = consulta.lastError().text()
            LOGGER.error("Error al preparar la consulta de horas semanales: %s", error)
            QMessageBox.warning(self, "Error", f"No se pudo cargar la asignatura: {error}")
            return None

        consulta.bindValue(":id_horassemanales", id_registro)
        if not consulta.exec() or not consulta.next():
            error = consulta.lastError().text()
            LOGGER.error("Error al recuperar la asignatura de las horas semanales: %s", error)
            QMessageBox.warning(self, "Error", f"No se pudo cargar la asignatura: {error}")
            return None
        return int(consulta.value("id_asignatura"))

    def _crear_formulario(self):
        layout_main = QVBoxLayout()
        layout_grid = QGridLayout()
        layout_main.addLayout(layout_grid)
        layout_buttons = QHBoxLayout()
        layout_main.addLayout(layout_buttons)

        label_asignatura = QLabel("Asignatura *")
        layout_grid.addWidget(label_asignatura, 0, 0, 1, 4)
        self.combo_asignatura = QComboBox()
        layout_grid.addWidget(self.combo_asignatura, 1, 0, 1, 4)

        campos = (
            ("Teoricas", "teoricas"),
            ("Practicas", "practicas"),
            ("HTD", "htd"),
            ("HTI", "hti"),
        )
        self.lineas_horas: dict[str, QLineEdit] = {}
        for indice, (etiqueta, campo) in enumerate(campos):
            columna = indice % 2 * 2
            fila = 2 + indice // 2 * 2
            label = QLabel(etiqueta)
            layout_grid.addWidget(label, fila, columna, 1, 2)
            line = QLineEdit()
            line.setPlaceholderText("Horas por semana (opcional)")
            layout_grid.addWidget(line, fila + 1, columna, 1, 2)
            self.lineas_horas[campo] = line

        layout_buttons.addStretch()
        self.button_aplicar = QPushButton("Aplicar")
        self.button_aplicar.clicked.connect(self.on_aplicar)
        layout_buttons.addWidget(self.button_aplicar)

        self.button_cancelar = QPushButton("Cancelar")
        self.button_cancelar.clicked.connect(self.close)
        layout_buttons.addWidget(self.button_cancelar)

        self.setLayout(layout_main)

    def _cargar_asignaturas(self) -> bool:
        consulta = QSqlQuery(db=self.modelo.database())
        sql = (
            "SELECT a.id_asignatura, a.codigo, a.nombre FROM Asignatura a "
            "WHERE NOT EXISTS ("
            "SELECT 1 FROM HorasSemanales hs "
            "WHERE hs.id_asignatura = a.id_asignatura)"
        )
        if self.id_asignatura is not None:
            sql += " OR a.id_asignatura = :id_asignatura"
        sql += " ORDER BY a.nombre"

        if not consulta.prepare(sql):
            error = consulta.lastError().text()
            LOGGER.error("Error al preparar la consulta de asignaturas: %s", error)
            QMessageBox.warning(self, "Error", f"No se pudieron cargar las asignaturas: {error}")
            return False
        if self.id_asignatura is not None:
            consulta.bindValue(":id_asignatura", self.id_asignatura)
        if not consulta.exec():
            error = consulta.lastError().text()
            LOGGER.error("Error al cargar las asignaturas: %s", error)
            QMessageBox.warning(self, "Error", f"No se pudieron cargar las asignaturas: {error}")
            return False

        while consulta.next():
            asignatura_id = consulta.value("id_asignatura")
            codigo = consulta.value("codigo")
            nombre = consulta.value("nombre")
            self.combo_asignatura.addItem(f"{codigo} - {nombre}", userData=asignatura_id)
        return True

    def _cargar_campos(self):
        if self.fila is None:
            return

        registro = self.modelo.record(self.fila)
        indice = self.combo_asignatura.findData(self.id_asignatura)
        if indice >= 0:
            self.combo_asignatura.setCurrentIndex(indice)
        for campo, line in self.lineas_horas.items():
            valor = registro.value(campo)
            line.setText("" if valor is None else str(valor))

    def on_aplicar(self):
        asignatura_id = self.combo_asignatura.currentData()
        if asignatura_id is None:
            QMessageBox.warning(self, "Advertencia", "Seleccione una asignatura")
            return

        valores_horas = {}
        for campo, line in self.lineas_horas.items():
            texto = line.text().strip()
            if not texto:
                valores_horas[campo] = None
                continue
            try:
                horas = float(texto)
            except ValueError:
                QMessageBox.warning(
                    self,
                    "Advertencia",
                    f"El valor de {campo} debe ser un numero valido",
                )
                return
            if not math.isfinite(horas) or horas < 0:
                QMessageBox.warning(
                    self,
                    "Advertencia",
                    f"El valor de {campo} debe ser mayor o igual a cero",
                )
                return
            valores_horas[campo] = horas

        if self.fila is None:
            self.fila = self.modelo.rowCount()
            if not self.modelo.insertRow(self.fila):
                self._mostrar_error("No se pudieron agregar las horas semanales")
                return

        valores = {"id_asignatura": asignatura_id, **valores_horas}
        for columna, valor in valores.items():
            indice_columna = INDICES_COLUMNAS[columna]
            if not self.modelo.setData(self.modelo.index(self.fila, indice_columna), valor):
                self.modelo.revertAll()
                self._mostrar_error(f"No se pudo actualizar el campo {columna}")
                return

        if not self.modelo.submitAll():
            self.modelo.revertAll()
            self._mostrar_error("No se pudieron guardar las horas semanales")
            return

        if not self.modelo.select():
            LOGGER.error(
                "Error al actualizar las horas semanales: %s",
                self.modelo.lastError().text(),
            )
        self.tabla.clearSelection()
        self.close()

    def _mostrar_error(self, mensaje: str):
        error = self.modelo.lastError().text()
        LOGGER.error("%s: %s", mensaje, error)
        QMessageBox.warning(self, "Error", f"{mensaje}: {error}")
