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
    QFormLayout,
    QTextEdit,
    QMessageBox,
)
from PySide6.QtSql import QSqlDatabase, QSqlTableModel
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from interfaz.pyside6.estilos import (
    ESTILO_PUSH_BUTTON_AGREGAR,
    ESTILO_PUSH_BUTTON_EDITAR,
    ESTILO_PUSH_BUTTON_ELIMINAR,
)
from utilidades.configuraciones import BASE_DATOS_CRONO, LOGGER
from interfaz.pyside6.auxiliares import conectar_modelo


class Facultades(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.modelo: QSqlTableModel | None = None

        # creamos los componentes
        self._crear()

        # nos conectamos a la base de datos
        self.modelo = conectar_modelo()

        # configuramos la tabla
        self.configurar_tabla()

    def configurar_tabla(self):
        if self.modelo is None:
            LOGGER.warning("El modelo de la tabla no se pudo cargar: %s", self.modelo)
            return

        # conectamos el modelo a la tabla
        self.modelo.setTable("Facultad")
        if not self.modelo.select():
            LOGGER.error("Error al cargar las facultades %s", self.modelo.lastError().text())

        # configuramos la cabecera de la tablaTEXTO
        self.modelo.setHeaderData(0, Qt.Orientation.Horizontal, "Id")
        self.modelo.setHeaderData(1, Qt.Orientation.Horizontal, "Nombre")
        self.modelo.setHeaderData(2, Qt.Orientation.Horizontal, "Siglas")
        self.modelo.setHeaderData(3, Qt.Orientation.Horizontal, "Descripcion")
        self.modelo.setHeaderData(4, Qt.Orientation.Horizontal, "Correo")

        # configuramos la tabla
        self.tabla.setModel(self.modelo)
        self.tabla.resizeColumnsToContents()
        # escondemos la primera columna
        self.tabla.setColumnHidden(0, True)
        self.tabla.setColumnHidden(3, True)

        # tabla no editable directamente
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # selección de una única fila en lugar de celdas por defecto
        self.tabla.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

    def _crear(self):

        # Layouts
        # ==================================================
        layout_main = QVBoxLayout()
        layout_titulo = QVBoxLayout()
        layout_main.addLayout(layout_titulo)
        layout_operaciones = QHBoxLayout()
        layout_main.addLayout(layout_operaciones)
        layout_tabla = QVBoxLayout()
        layout_main.addLayout(layout_tabla)

        # Widgets Titulo
        # ==================================================
        label_titulo = QLabel(" 🏛️ Facultades")
        layout_titulo.addWidget(label_titulo)
        # Amplaimos la fuente
        font = QFont()
        font.setPointSize(14)
        label_titulo.setFont(font)
        # linea
        frame_linea = QFrame()
        frame_linea.setFrameShape(QFrame.Shape.HLine)
        layout_titulo.addWidget(frame_linea)

        # Widgets Operaciones
        # ==================================================
        self.line_buscar = QLineEdit()
        self.line_buscar.setPlaceholderText("Busca por nombre, sigla o correo")
        self.line_buscar.textChanged.connect(self.on_buscar)
        layout_operaciones.addWidget(self.line_buscar)

        self.push_agregar = QPushButton("Agregar")
        self.push_agregar.clicked.connect(self.on_dialogo_agregar)
        self.push_agregar.setToolTip("Agrega una nueva Faculdad")
        self.push_agregar.setStyleSheet(ESTILO_PUSH_BUTTON_AGREGAR)
        layout_operaciones.addWidget(self.push_agregar)

        self.push_editar = QPushButton("Editar")
        self.push_editar.setToolTip("Edita la Facultad seleccionada en la tabla")
        self.push_editar.clicked.connect(self.on_dialogo_editar)
        self.push_editar.setStyleSheet(ESTILO_PUSH_BUTTON_EDITAR)
        layout_operaciones.addWidget(self.push_editar)

        self.push_eliminar = QPushButton("Eliminar")
        self.push_eliminar.setToolTip("Elimina los datos de la Facultad seleccionada en la tabla")
        self.push_eliminar.clicked.connect(self.on_dialogo_eliminar)
        self.push_eliminar.setStyleSheet(ESTILO_PUSH_BUTTON_ELIMINAR)
        layout_operaciones.addWidget(self.push_eliminar)

        # Widgets Tabla
        # ==================================================
        self.tabla = QTableView()
        layout_tabla.addWidget(self.tabla)

        # agremos el layout principal
        self.setLayout(layout_main)

    # ┌──────────────────────────────────────────────────┐
    # │ Eventos
    # └──────────────────────────────────────────────────┘
    def on_dialogo_eliminar(self):

        index = self.tabla.currentIndex()

        if not index.isValid():
            QMessageBox.information(self, "Seleccione", "Seleccione una fila para poder editar")
            return

        resp = QMessageBox.question(
            self, "Eliminar registro", "Esta seguro que quiere eliminar el registro?"
        )

        if QMessageBox.StandardButton.No == resp:
            return

        if self.modelo is None:
            return

        # Procedemos a eliminar el registro
        fila = index.row()
        self.modelo.removeRow(fila)
        # actualizamos la tabla para mostrar sin el registro borrado
        self.modelo.select()
        self.tabla.clearSelection()

    def on_dialogo_editar(self):
        index = self.tabla.currentIndex()

        if not index.isValid():
            QMessageBox.information(self, "Seleccione", "Seleccione una fila para poder editar")
            return

        self.dialog = DialogoEditar(self.modelo, self.tabla)
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()

    def on_dialogo_agregar(self):
        self.dialog = DialogoAgregar(self.modelo, self.tabla)
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()

    def on_buscar(self, texto: str):
        if self.modelo is None:
            return

        # Escapamos comillas porque setFilter recibe una expresión SQL.
        texto_filtro = texto.replace("'", "''")
        if texto_filtro:
            patron = f"'%{texto_filtro}%'"
            self.modelo.setFilter(
                f"nombre LIKE {patron} OR siglas LIKE {patron} OR correo LIKE {patron}"
            )
        else:
            self.modelo.setFilter("")

        if not self.modelo.select():
            LOGGER.error("Error al realizar la consulta %s", self.modelo.lastError().text())


# ┌──────────────────────────────────────────────────┐
# │ Dialogos
# └──────────────────────────────────────────────────┘
class DialogoEditar(QWidget):

    def __init__(self, modelo: QSqlTableModel | None, tabla: QTableView | None):
        super().__init__()
        # Para maqnejar el modelo de la tabla
        self.modelo = modelo
        self.tabla = tabla
        # Atributos del dialog
        self.setWindowTitle("Edita la facultad seleccionada")
        self.resize(400, 400)

        self._crear_formulario()

        # cargamos los campos con los datos seleccionados
        self._cargar_campos()

    def _crear_formulario(self):
        # Layouts
        # --------------------------------------------------
        layout_main = QVBoxLayout()
        self.setLayout(layout_main)
        layout_form = QFormLayout()
        layout_main.addLayout(layout_form)
        layout_bottom = QHBoxLayout()
        layout_main.addLayout(layout_bottom)

        # Widgets
        # --------------------------------------------------
        self.line_nombre = QLineEdit()
        self.line_nombre.setPlaceholderText("Escribe el nombre la facultad")
        layout_form.addRow("Nombre *", self.line_nombre)

        self.line_siglas = QLineEdit()
        self.line_siglas.setPlaceholderText("Escribe la siglas de la falcultad")
        layout_form.addRow("Siglas *", self.line_siglas)

        self.line_correo = QLineEdit()
        self.line_correo.setPlaceholderText("facultad_nueva@correo.com")
        layout_form.addRow("Correo *", self.line_correo)

        self.text_descripcion = QTextEdit()
        self.text_descripcion.setPlaceholderText("Escribe una descripcion sobre la facultad")
        layout_form.addRow("Descripcion", self.text_descripcion)

        # agregamos un espacio
        layout_bottom.addStretch()

        push_aplicar = QPushButton("Aplicar")
        push_aplicar.clicked.connect(self.on_aplicar)
        layout_bottom.addWidget(push_aplicar)

        push_cancelar = QPushButton("Cancelar")
        push_cancelar.clicked.connect(self.on_cancelar)
        layout_bottom.addWidget(push_cancelar)

    # ┌──────────────────────────────────────────────────┐
    # │ Metodos
    # └──────────────────────────────────────────────────┘

    def _cargar_campos(self):
        # descartamos que la tabla no sea None
        if self.tabla is None or self.modelo is None:
            return
        # Verificanos que exista una seleccion
        index = self.tabla.currentIndex()
        if not index.isValid():
            return

        # obtenemos la fila
        fila = index.row()

        nombre = str(self.modelo.index(fila, 1).data())
        siglas = str(self.modelo.index(fila, 2).data())
        descripcion = str(self.modelo.index(fila, 3).data())
        correo = str(self.modelo.index(fila, 4).data())

        self.line_nombre.setText(nombre)
        self.line_siglas.setText(siglas)
        self.text_descripcion.setText(descripcion)
        self.line_correo.setText(correo)

    # ┌──────────────────────────────────────────────────┐
    # │ Eventos
    # └──────────────────────────────────────────────────┘
    def on_cancelar(self):
        self.close()

    def on_aplicar(self):
        if self.modelo is None or self.tabla is None:
            return

        # recuperamos el contenido de las lineas
        nombre = self.line_nombre.text()
        siglas = self.line_siglas.text()
        correo = self.line_correo.text()
        descripcion = self.text_descripcion.toPlainText()

        if len(nombre) == 0 or len(siglas) == 0 or len(correo) == 0:
            QMessageBox.warning(
                self,
                "Advertencia",
                "Los campos nombres, siglas y correo no pueden estar vacios",
            )
            return

        if correo.find('@') == -1:
            QMessageBox.warning(
                self,
                "Advertencia",
                "El correo no es valido",
            )
            return

        # Verificanos que exista una seleccion
        index = self.tabla.currentIndex()
        if not index.isValid():
            return

        # obtenemos la fila
        fila = index.row()

        # definimos los campos de la nueva fila
        self.modelo.setData(self.modelo.index(fila, 1), nombre)
        self.modelo.setData(self.modelo.index(fila, 2), siglas)
        self.modelo.setData(self.modelo.index(fila, 3), descripcion)
        self.modelo.setData(self.modelo.index(fila, 4), correo)

        # confirmamos los campos del modelo
        if not self.modelo.submit():
            LOGGER.error("Error al guardar los cambios %s", self.modelo.lastError().text())
            return


class DialogoAgregar(QWidget):

    def __init__(self, modelo: QSqlTableModel | None, tabla: QTableView | None):
        super().__init__()
        # Para maqnejar el modelo de la tabla
        self.modelo = modelo
        self.tabla = tabla
        # Atributos del dialog
        self.setWindowTitle("Agrega una nueva facultad")
        self.resize(400, 400)

        self._crear_fromulario()

    def _crear_fromulario(self):
        # Layouts
        # --------------------------------------------------
        layout_main = QVBoxLayout()
        self.setLayout(layout_main)
        layout_form = QFormLayout()
        layout_main.addLayout(layout_form)
        layout_bottom = QHBoxLayout()
        layout_main.addLayout(layout_bottom)

        # Widgets
        # --------------------------------------------------
        self.line_nombre = QLineEdit()
        self.line_nombre.setPlaceholderText("Escribe el nombre la facultad")
        layout_form.addRow("Nombre *", self.line_nombre)

        self.line_siglas = QLineEdit()
        self.line_siglas.setPlaceholderText("Escribe la siglas de la falcultad")
        layout_form.addRow("Siglas *", self.line_siglas)

        self.line_correo = QLineEdit()
        self.line_correo.setPlaceholderText("facultad_nueva@correo.com")
        layout_form.addRow("Correo *", self.line_correo)

        self.text_descripcion = QTextEdit()
        self.text_descripcion.setPlaceholderText("Escribe una descripcion sobre la facultad")
        layout_form.addRow("Descripcion", self.text_descripcion)

        # agregamos un espacio
        layout_bottom.addStretch()

        push_aplicar = QPushButton("Aplicar")
        push_aplicar.clicked.connect(self.on_aplicar)
        layout_bottom.addWidget(push_aplicar)

        push_cancelar = QPushButton("Cancelar")
        push_cancelar.clicked.connect(self.on_cancelar)
        layout_bottom.addWidget(push_cancelar)

    # ┌──────────────────────────────────────────────────┐
    # │ Eventos
    # └──────────────────────────────────────────────────┘
    def on_cancelar(self):
        self.close()

    def on_aplicar(self):
        if self.modelo is None or self.tabla is None:
            return

        # recuperamos el contenido de las lineas
        nombre = self.line_nombre.text()
        siglas = self.line_siglas.text()
        correo = self.line_correo.text()
        descripcion = self.text_descripcion.toPlainText()

        if len(nombre) == 0 or len(siglas) == 0 or len(correo) == 0:
            QMessageBox.warning(
                self,
                "Advertencia",
                "Los campos nombres, siglas y correo no pueden estar vacios",
            )
            return

        if correo.find('@') == -1:
            QMessageBox.warning(
                self,
                "Advertencia",
                "El correo no es valido",
            )
            return

        # contamos las filas y anadimos una nueva
        fila = self.modelo.rowCount()
        self.modelo.insertRow(fila)

        # definimos los campos de la nueva fila
        self.modelo.setData(self.modelo.index(fila, 1), nombre)
        self.modelo.setData(self.modelo.index(fila, 2), siglas)
        self.modelo.setData(self.modelo.index(fila, 3), descripcion)
        self.modelo.setData(self.modelo.index(fila, 4), correo)

        # confirmamos los campos del modelo
        if not self.modelo.submit():
            LOGGER.error("Error al guardar los cambios %s", self.modelo.lastError().text())
            return

        # Reseteamos los cambios
        self.line_nombre.setText("")
        self.line_siglas.setText("")
        self.line_correo.setText("")
        self.text_descripcion.setText("")

        # limpiamos la selecciona actual
        self.tabla.clearSelection()
        self.tabla.resizeColumnsToContents()
