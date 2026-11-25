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
    QListWidget,
    QListWidgetItem,
    QMessageBox,
)
from PySide6.QtSql import QSqlRelationalTableModel, QSqlRelation, QSqlQuery
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from interfaz.pyside6.estilos import ESTILO_PUSH_BUTTON_AGREGAR
from utilidades.configuraciones import LOGGER
from interfaz.pyside6.auxiliares import obtener_conexion


class MallaCurricular(QWidget):
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

        label_titulo = QLabel(" 🪜 Malla Curricular")
        layout_titulo.addWidget(label_titulo)
        font = QFont()
        font.setPointSize(14)
        label_titulo.setFont(font)
        frame_linea = QFrame()
        frame_linea.setFrameShape(QFrame.Shape.HLine)
        layout_titulo.addWidget(frame_linea)

        self.line_buscar = QLineEdit()
        self.line_buscar.setPlaceholderText("Busca por codigo o nombre de carrera o asignatura")
        self.line_buscar.textChanged.connect(self.on_buscar)
        layout_operaciones.addWidget(self.line_buscar)

        self.push_asociar = QPushButton("Asociar")
        self.push_asociar.clicked.connect(self.on_dialogo_asociar)
        self.push_asociar.setToolTip("Asocia varias asignaturas a una carrera")
        self.push_asociar.setStyleSheet(ESTILO_PUSH_BUTTON_AGREGAR)
        layout_operaciones.addWidget(self.push_asociar)

        self.tabla = QTableView()
        layout_tabla.addWidget(self.tabla)
        self.setLayout(layout_main)

    def configurar_tabla(self):
        if self.modelo is None:
            LOGGER.warning("El modelo de la tabla no se pudo cargar: %s", self.modelo)
            return

        self.modelo.setTable("Malla_Curricular")
        self.modelo.setRelation(0, QSqlRelation("Carrera", "id_carrera", "nombre"))
        self.modelo.setRelation(1, QSqlRelation("Asignatura", "id_asignatura", "nombre"))
        if not self.modelo.select():
            LOGGER.error("Error al cargar la malla curricular: %s", self.modelo.lastError().text())

        self.modelo.setHeaderData(0, Qt.Orientation.Horizontal, "Carrera")
        self.modelo.setHeaderData(1, Qt.Orientation.Horizontal, "Asignatura")
        self.tabla.setModel(self.modelo)
        self.tabla.resizeColumnsToContents()
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
                "Malla_Curricular.id_carrera IN ("
                "SELECT id_carrera FROM Carrera "
                f"WHERE codigo LIKE {patron} OR nombre LIKE {patron}) "
                "OR Malla_Curricular.id_asignatura IN ("
                "SELECT id_asignatura FROM Asignatura "
                f"WHERE codigo LIKE {patron} OR nombre LIKE {patron})"
            )
        else:
            self.modelo.setFilter("")

        if not self.modelo.select():
            LOGGER.error(
                "Error al buscar en la malla curricular: %s",
                self.modelo.lastError().text(),
            )

    def on_dialogo_asociar(self):
        if self.modelo is None:
            return
        self.dialog = DialogoMallaCurricular(self.modelo, self.tabla)
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()


class DialogoMallaCurricular(QWidget):
    def __init__(
        self,
        modelo: QSqlRelationalTableModel,
        tabla: QTableView,
    ):
        super().__init__()
        self.modelo = modelo
        self.tabla = tabla
        self.carreras: list[tuple[int, str, str]] = []
        self.asignaturas: list[tuple[int, str, str]] = []
        self.ids_asignaturas_actuales: set[int] = set()
        self.setWindowTitle("Asociar asignaturas a una carrera")
        self.resize(900, 600)

        self._crear_formulario()
        if not self._cargar_catalogos():
            self.button_asociar.setEnabled(False)
            return
        if not self.carreras or not self.asignaturas:
            QMessageBox.information(
                self,
                "Datos insuficientes",
                "Se necesitan al menos una carrera y una asignatura para asociar.",
            )
            self.button_asociar.setEnabled(False)
            return

        self._cargar_listas()

    def _crear_formulario(self):
        layout_main = QVBoxLayout()
        layout_grid = QGridLayout()
        layout_main.addLayout(layout_grid)

        layout_grid.addWidget(
            QLabel(
                "Selecciona una carrera y marca las asignaturas de su malla. "
                "Al asociar, la selección reemplaza las asignaturas actuales."
            ),
            0,
            0,
            1,
            2,
        )

        layout_grid.addWidget(QLabel("Carrera *"), 1, 0)
        layout_grid.addWidget(QLabel("Asignaturas de la malla *"), 1, 1)

        self.line_buscar_carrera = QLineEdit()
        self.line_buscar_carrera.setPlaceholderText("Filtrar carreras")
        self.line_buscar_carrera.textChanged.connect(self._filtrar_carreras)
        layout_grid.addWidget(self.line_buscar_carrera, 2, 0)

        self.line_buscar_asignatura = QLineEdit()
        self.line_buscar_asignatura.setPlaceholderText("Filtrar asignaturas")
        self.line_buscar_asignatura.textChanged.connect(self._filtrar_asignaturas)
        layout_grid.addWidget(self.line_buscar_asignatura, 2, 1)

        self.lista_carreras = QListWidget()
        self.lista_carreras.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.lista_carreras.currentItemChanged.connect(
            self._cargar_asignaturas_actuales
        )
        layout_grid.addWidget(self.lista_carreras, 3, 0)

        self.lista_asignaturas = QListWidget()
        self.lista_asignaturas.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection
        )
        self.lista_asignaturas.itemChanged.connect(self._actualizar_contador)
        layout_grid.addWidget(self.lista_asignaturas, 3, 1)

        self.label_seleccionadas = QLabel("Seleccionadas: 0")
        layout_grid.addWidget(self.label_seleccionadas, 4, 1)
        layout_grid.setColumnStretch(0, 1)
        layout_grid.setColumnStretch(1, 1)

        layout_buttons = QHBoxLayout()
        layout_main.addLayout(layout_buttons)
        layout_buttons.addStretch()

        self.button_asociar = QPushButton("Asociar")
        self.button_asociar.clicked.connect(self.on_asociar)
        layout_buttons.addWidget(self.button_asociar)

        self.button_cancelar = QPushButton("Cancelar")
        self.button_cancelar.clicked.connect(self.close)
        layout_buttons.addWidget(self.button_cancelar)

        self.setLayout(layout_main)

    def _cargar_catalogos(self) -> bool:
        consulta_carreras = QSqlQuery(db=self.modelo.database())
        if not consulta_carreras.exec(
            "SELECT id_carrera, codigo, nombre FROM Carrera ORDER BY codigo"
        ):
            error = consulta_carreras.lastError().text()
            LOGGER.error("Error al cargar las carreras: %s", error)
            QMessageBox.warning(self, "Error", f"No se pudieron cargar las carreras: {error}")
            return False
        while consulta_carreras.next():
            self.carreras.append(
                (
                    int(consulta_carreras.value("id_carrera")),
                    str(consulta_carreras.value("codigo")),
                    str(consulta_carreras.value("nombre")),
                )
            )

        consulta_asignaturas = QSqlQuery(db=self.modelo.database())
        if not consulta_asignaturas.exec(
            "SELECT id_asignatura, codigo, nombre FROM Asignatura ORDER BY codigo"
        ):
            error = consulta_asignaturas.lastError().text()
            LOGGER.error("Error al cargar las asignaturas: %s", error)
            QMessageBox.warning(self, "Error", f"No se pudieron cargar las asignaturas: {error}")
            return False
        while consulta_asignaturas.next():
            self.asignaturas.append(
                (
                    int(consulta_asignaturas.value("id_asignatura")),
                    str(consulta_asignaturas.value("codigo")),
                    str(consulta_asignaturas.value("nombre")),
                )
            )
        return True

    def _cargar_listas(self):
        for id_carrera, codigo, nombre in self.carreras:
            item = QListWidgetItem(f"{codigo} - {nombre}")
            item.setData(Qt.ItemDataRole.UserRole, id_carrera)
            self.lista_carreras.addItem(item)

        for id_asignatura, codigo, nombre in self.asignaturas:
            item = QListWidgetItem(f"{codigo} - {nombre}")
            item.setData(Qt.ItemDataRole.UserRole, id_asignatura)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.lista_asignaturas.addItem(item)

        self.lista_asignaturas.setEnabled(False)
        self.button_asociar.setEnabled(False)

    def _filtrar_carreras(self, texto: str):
        patron = texto.casefold().strip()
        for indice in range(self.lista_carreras.count()):
            item = self.lista_carreras.item(indice)
            item.setHidden(patron not in item.text().casefold())
        actual = self.lista_carreras.currentItem()
        if actual is not None and actual.isHidden():
            self.lista_carreras.setCurrentRow(-1)

    def _filtrar_asignaturas(self, texto: str):
        patron = texto.casefold().strip()
        for indice in range(self.lista_asignaturas.count()):
            item = self.lista_asignaturas.item(indice)
            item.setHidden(patron not in item.text().casefold())

    def _cargar_asignaturas_actuales(
        self,
        item: QListWidgetItem | None,
        _anterior=None,
    ):
        self.ids_asignaturas_actuales.clear()
        if item is None:
            self.lista_asignaturas.setEnabled(False)
            self.button_asociar.setEnabled(False)
            self._actualizar_contador()
            return

        id_carrera = item.data(Qt.ItemDataRole.UserRole)
        consulta = QSqlQuery(db=self.modelo.database())
        if not consulta.prepare(
            "SELECT id_asignatura FROM Malla_Curricular WHERE id_carrera = :id_carrera"
        ):
            self._mostrar_error(
                "No se pudieron cargar las asignaturas de la carrera",
                consulta.lastError().text(),
            )
            self.lista_asignaturas.setEnabled(False)
            self.button_asociar.setEnabled(False)
            return

        consulta.bindValue(":id_carrera", id_carrera)
        if not consulta.exec():
            self._mostrar_error(
                "No se pudieron cargar las asignaturas de la carrera",
                consulta.lastError().text(),
            )
            self.lista_asignaturas.setEnabled(False)
            self.button_asociar.setEnabled(False)
            return

        while consulta.next():
            self.ids_asignaturas_actuales.add(int(consulta.value("id_asignatura")))

        patron = self.line_buscar_asignatura.text().casefold().strip()
        for indice in range(self.lista_asignaturas.count()):
            asignatura = self.lista_asignaturas.item(indice)
            id_asignatura = asignatura.data(Qt.ItemDataRole.UserRole)
            asignatura.setCheckState(
                Qt.CheckState.Checked
                if id_asignatura in self.ids_asignaturas_actuales
                else Qt.CheckState.Unchecked
            )
            asignatura.setHidden(patron not in asignatura.text().casefold())

        self.lista_asignaturas.setEnabled(True)
        self.button_asociar.setEnabled(True)
        self._actualizar_contador()

    def _actualizar_contador(self, _item=None):
        seleccionadas = sum(
            self.lista_asignaturas.item(indice).checkState() == Qt.CheckState.Checked
            for indice in range(self.lista_asignaturas.count())
        )
        self.label_seleccionadas.setText(f"Seleccionadas: {seleccionadas}")

    def on_asociar(self):
        carrera = self.lista_carreras.currentItem()
        if carrera is None:
            QMessageBox.warning(self, "Advertencia", "Seleccione una carrera")
            return

        id_carrera = int(carrera.data(Qt.ItemDataRole.UserRole))
        seleccionadas = {
            int(self.lista_asignaturas.item(indice).data(Qt.ItemDataRole.UserRole))
            for indice in range(self.lista_asignaturas.count())
            if self.lista_asignaturas.item(indice).checkState() == Qt.CheckState.Checked
        }

        if seleccionadas == self.ids_asignaturas_actuales:
            QMessageBox.information(self, "Sin cambios", "La malla ya está actualizada.")
            return

        if not seleccionadas and self.ids_asignaturas_actuales:
            respuesta = QMessageBox.question(
                self,
                "Quitar asignaturas",
                "No hay asignaturas marcadas. Se quitarán todas las asignaturas actuales "
                "de la malla. ¿Desea continuar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if respuesta != QMessageBox.StandardButton.Yes:
                return

        base_datos = self.modelo.database()
        if not base_datos.transaction():
            self._mostrar_error(
                "No se pudo guardar la malla curricular",
                base_datos.lastError().text(),
            )
            return

        borrar = QSqlQuery(db=base_datos)
        if not borrar.prepare(
            "DELETE FROM Malla_Curricular WHERE id_carrera = :id_carrera"
        ):
            base_datos.rollback()
            self._mostrar_error(
                "No se pudieron reemplazar las asignaturas",
                borrar.lastError().text(),
            )
            return
        borrar.bindValue(":id_carrera", id_carrera)
        if not borrar.exec():
            base_datos.rollback()
            self._mostrar_error(
                "No se pudieron reemplazar las asignaturas",
                borrar.lastError().text(),
            )
            return

        if seleccionadas:
            insertar = QSqlQuery(db=base_datos)
            if not insertar.prepare(
                "INSERT INTO Malla_Curricular (id_carrera, id_asignatura) "
                "VALUES (:id_carrera, :id_asignatura)"
            ):
                base_datos.rollback()
                self._mostrar_error(
                    "No se pudieron guardar las asignaturas",
                    insertar.lastError().text(),
                )
                return
            for id_asignatura in seleccionadas:
                insertar.bindValue(":id_carrera", id_carrera)
                insertar.bindValue(":id_asignatura", id_asignatura)
                if not insertar.exec():
                    base_datos.rollback()
                    self._mostrar_error(
                        "No se pudieron guardar las asignaturas",
                        insertar.lastError().text(),
                    )
                    return

        if not base_datos.commit():
            base_datos.rollback()
            self._mostrar_error(
                "No se pudo confirmar la malla curricular",
                base_datos.lastError().text(),
            )
            return

        if not self.modelo.select():
            self._mostrar_error("No se pudo actualizar la tabla", self.modelo.lastError().text())
            return

        self.tabla.resizeColumnsToContents()
        self.tabla.clearSelection()
        QMessageBox.information(
            self,
            "Malla curricular actualizada",
            f"Se asociaron {len(seleccionadas)} asignaturas a {carrera.text()}.",
        )
        self.close()

    def _mostrar_error(self, mensaje: str, error: str):
        LOGGER.error("%s: %s", mensaje, error)
        QMessageBox.warning(self, "Error", f"{mensaje}: {error}")
