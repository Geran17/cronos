import re

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtSql import QSqlTableModel
from PySide6.QtWidgets import (
    QAbstractItemView,
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

from interfaz.pyside6.auxiliares import conectar_modelo
from interfaz.pyside6.estilos import (
    ESTILO_PUSH_BUTTON_AGREGAR,
    ESTILO_PUSH_BUTTON_EDITAR,
    ESTILO_PUSH_BUTTON_ELIMINAR,
)
from utilidades.configuraciones import LOGGER


class Profesores(QWidget):
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

        label_titulo = QLabel(" 👨‍🏫 Profesores")
        layout_titulo.addWidget(label_titulo)
        font = QFont()
        font.setPointSize(14)
        label_titulo.setFont(font)
        frame_linea = QFrame()
        frame_linea.setFrameShape(QFrame.Shape.HLine)
        layout_titulo.addWidget(frame_linea)

        self.line_buscar = QLineEdit()
        self.line_buscar.setPlaceholderText("Busca por nombre, apellido, correo o telefono")
        self.line_buscar.textChanged.connect(self.on_buscar)
        layout_operaciones.addWidget(self.line_buscar)

        self.push_agregar = QPushButton("Agregar")
        self.push_agregar.clicked.connect(self.on_dialogo_agregar)
        self.push_agregar.setToolTip("Agrega un nuevo profesor")
        self.push_agregar.setStyleSheet(ESTILO_PUSH_BUTTON_AGREGAR)
        layout_operaciones.addWidget(self.push_agregar)

        self.push_editar = QPushButton("Editar")
        self.push_editar.clicked.connect(self.on_dialogo_editar)
        self.push_editar.setToolTip("Edita el profesor seleccionado")
        self.push_editar.setStyleSheet(ESTILO_PUSH_BUTTON_EDITAR)
        layout_operaciones.addWidget(self.push_editar)

        self.push_eliminar = QPushButton("Eliminar")
        self.push_eliminar.clicked.connect(self.on_dialogo_eliminar)
        self.push_eliminar.setToolTip("Elimina el profesor seleccionado")
        self.push_eliminar.setStyleSheet(ESTILO_PUSH_BUTTON_ELIMINAR)
        layout_operaciones.addWidget(self.push_eliminar)

        self.tabla = QTableView()
        layout_tabla.addWidget(self.tabla)
        self.setLayout(layout_main)

    def configurar_tabla(self):
        if self.modelo is None:
            LOGGER.warning("No se pudo cargar el modelo de profesores")
            return

        self.modelo.setTable("Profesor")
        self.modelo.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)
        if not self.modelo.select():
            LOGGER.error("Error al cargar los profesores: %s", self.modelo.lastError().text())

        encabezados = ("Id", "Nombre", "Apellido", "Correo", "Telefono")
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
                f"nombre LIKE {patron} OR apellido LIKE {patron} "
                f"OR correo LIKE {patron} OR telefono LIKE {patron}"
            )
        else:
            self.modelo.setFilter("")

        if not self.modelo.select():
            LOGGER.error("Error al buscar profesores: %s", self.modelo.lastError().text())

    def on_dialogo_agregar(self):
        if self.modelo is None:
            return

        self.dialog = DialogoProfesor(self.modelo, self.tabla)
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()

    def on_dialogo_editar(self):
        index = self.tabla.currentIndex()
        if not index.isValid():
            QMessageBox.information(self, "Seleccione", "Seleccione un profesor para editar")
            return
        if self.modelo is None:
            return

        self.dialog = DialogoProfesor(self.modelo, self.tabla, fila=index.row())
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()

    def on_dialogo_eliminar(self):
        index = self.tabla.currentIndex()
        if not index.isValid():
            QMessageBox.information(self, "Seleccione", "Seleccione un profesor para eliminar")
            return
        if self.modelo is None:
            return

        respuesta = QMessageBox.question(
            self,
            "Eliminar profesor",
            "Esta seguro que quiere eliminar el profesor seleccionado?",
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return

        if not self.modelo.removeRow(index.row()) or not self.modelo.submitAll():
            error = self.modelo.lastError().text()
            LOGGER.error("Error al eliminar el profesor: %s", error)
            self.modelo.revertAll()
            QMessageBox.warning(self, "Error", f"No se pudo eliminar el profesor: {error}")
            return

        if not self.modelo.select():
            error = self.modelo.lastError().text()
            LOGGER.error("Error al actualizar los profesores: %s", error)
            QMessageBox.warning(
                self,
                "Error",
                f"El profesor se elimino, pero no se pudo actualizar la tabla: {error}",
            )
        self.tabla.clearSelection()


class DialogoProfesor(QWidget):
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
            "Edita el profesor seleccionado" if fila is not None else "Agrega un nuevo profesor"
        )
        # self.resize(450, 300)

        self._crear_formulario()
        if self.fila is not None:
            self._cargar_campos()

    def _crear_formulario(self):
        layout_main = QVBoxLayout()
        layout_grid = QGridLayout()
        layout_main.addLayout(layout_grid)
        layout_buttons = QHBoxLayout()
        layout_main.addLayout(layout_buttons)

        self.line_nombre = QLineEdit()
        self.line_nombre.setPlaceholderText("Nombre del profesor")
        self.line_apellido = QLineEdit()
        self.line_apellido.setPlaceholderText("Apellido del profesor")
        self.line_correo = QLineEdit()
        self.line_correo.setPlaceholderText("correo@ejemplo.com")
        self.line_telefono = QLineEdit()
        self.line_telefono.setPlaceholderText("Telefono de contacto")

        campos = (
            ("Nombre *", self.line_nombre),
            ("Apellido *", self.line_apellido),
            ("Correo", self.line_correo),
            ("Telefono", self.line_telefono),
        )
        for fila, (etiqueta, campo) in enumerate(campos):
            layout_grid.addWidget(QLabel(etiqueta), fila, 0)
            layout_grid.addWidget(campo, fila, 1)

        layout_buttons.addStretch()
        self.button_aplicar = QPushButton("Aplicar")
        self.button_aplicar.clicked.connect(self.on_aplicar)
        layout_buttons.addWidget(self.button_aplicar)

        self.button_cancelar = QPushButton("Cancelar")
        self.button_cancelar.clicked.connect(self.close)
        layout_buttons.addWidget(self.button_cancelar)

        self.setLayout(layout_main)

    def _cargar_campos(self):
        if self.fila is None:
            return

        registro = self.modelo.record(self.fila)
        self.line_nombre.setText(str(registro.value("nombre") or ""))
        self.line_apellido.setText(str(registro.value("apellido") or ""))
        self.line_correo.setText(str(registro.value("correo") or ""))
        self.line_telefono.setText(str(registro.value("telefono") or ""))

    def on_aplicar(self):
        nombre = self.line_nombre.text().strip()
        apellido = self.line_apellido.text().strip()
        correo = self.line_correo.text().strip()
        telefono = self.line_telefono.text().strip()

        if not nombre or not apellido:
            QMessageBox.warning(self, "Advertencia", "El nombre y el apellido son obligatorios")
            return
        if correo and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", correo):
            QMessageBox.warning(self, "Advertencia", "El correo no tiene un formato valido")
            return

        fila = self.fila
        es_nuevo = fila is None
        if es_nuevo:
            fila = self.modelo.rowCount()
            if not self.modelo.insertRow(fila):
                self._mostrar_error("No se pudo agregar el profesor")
                return

        valores = {
            "nombre": nombre,
            "apellido": apellido,
            "correo": correo or None,
            "telefono": telefono or None,
        }
        for campo, valor in valores.items():
            indice = self.modelo.index(fila, self.modelo.fieldIndex(campo))
            if not indice.isValid() or not self.modelo.setData(indice, valor):
                self.modelo.revertAll()
                self._mostrar_error(f"No se pudo actualizar el campo {campo}")
                return

        if not self.modelo.submitAll():
            self.modelo.revertAll()
            self._mostrar_error("No se pudo guardar el profesor")
            return

        if not self.modelo.select():
            error = self.modelo.lastError().text()
            LOGGER.error("Error al actualizar los profesores: %s", error)
            QMessageBox.warning(
                self,
                "Error",
                f"El profesor se guardo, pero no se pudo actualizar la tabla: {error}",
            )

        self.tabla.clearSelection()
        self.tabla.resizeColumnsToContents()
        self.close()

    def _mostrar_error(self, mensaje: str):
        error = self.modelo.lastError().text()
        LOGGER.error("%s: %s", mensaje, error)
        QMessageBox.warning(self, "Error", f"{mensaje}: {error}")
