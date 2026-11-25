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
from interfaz.pyside6.estilos import (
    ESTILO_PUSH_BUTTON_AGREGAR,
)
from utilidades.configuraciones import LOGGER
from interfaz.pyside6.auxiliares import obtener_conexion


class Prerequisitos(QWidget):
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

        label_titulo = QLabel(" ⛓️ Prerrequisitos")
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

        self.push_asociar = QPushButton("Asociar")
        self.push_asociar.clicked.connect(self.on_dialogo_asociar)
        self.push_asociar.setToolTip("Asocia varios prerrequisitos a una asignatura")
        self.push_asociar.setStyleSheet(ESTILO_PUSH_BUTTON_AGREGAR)
        layout_operaciones.addWidget(self.push_asociar)

        self.tabla = QTableView()
        layout_tabla.addWidget(self.tabla)
        self.setLayout(layout_main)

    def configurar_tabla(self):
        if self.modelo is None:
            LOGGER.warning("El modelo de la tabla no se pudo cargar: %s", self.modelo)
            return

        self.modelo.setTable("Prerequisito")
        self.modelo.setRelation(0, QSqlRelation("Asignatura", "id_asignatura", "nombre"))
        self.modelo.setRelation(1, QSqlRelation("Asignatura", "id_asignatura", "nombre"))
        if not self.modelo.select():
            LOGGER.error("Error al cargar los prerrequisitos: %s", self.modelo.lastError().text())

        self.modelo.setHeaderData(0, Qt.Orientation.Horizontal, "Asignatura")
        self.modelo.setHeaderData(1, Qt.Orientation.Horizontal, "Prerrequisito")
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
                "Prerequisito.id_asignatura IN ("
                "SELECT id_asignatura FROM Asignatura "
                f"WHERE codigo LIKE {patron} OR nombre LIKE {patron}) "
                "OR Prerequisito.id_prerequisito IN ("
                "SELECT id_asignatura FROM Asignatura "
                f"WHERE codigo LIKE {patron} OR nombre LIKE {patron})"
            )
        else:
            self.modelo.setFilter("")

        if not self.modelo.select():
            LOGGER.error("Error al buscar prerrequisitos: %s", self.modelo.lastError().text())

    def on_dialogo_asociar(self):
        if self.modelo is None:
            return
        self.dialog = DialogoPrerequisito(self.modelo, self.tabla)
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()


class DialogoPrerequisito(QWidget):
    def __init__(
        self,
        modelo: QSqlRelationalTableModel,
        tabla: QTableView,
    ):
        super().__init__()
        self.modelo = modelo
        self.tabla = tabla
        self.asignaturas: list[tuple[int, str, str]] = []
        self.ids_prerequisitos_actuales: set[int] = set()
        self.setWindowTitle("Asociar prerrequisitos")
        self.resize(900, 600)

        self._crear_formulario()
        if not self._cargar_asignaturas():
            self.button_asociar.setEnabled(False)
            return

        if len(self.asignaturas) < 2:
            QMessageBox.information(
                self,
                "Asignaturas insuficientes",
                "Se necesitan al menos dos asignaturas para asociar prerrequisitos.",
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
                "Selecciona una asignatura y marca sus prerrequisitos. "
                "Al asociar, la selección reemplaza las asociaciones actuales."
            ),
            0,
            0,
            1,
            2,
        )

        layout_grid.addWidget(QLabel("Asignatura que requiere *"), 1, 0)
        layout_grid.addWidget(QLabel("Asignaturas prerrequisito *"), 1, 1)

        self.line_buscar_asignatura = QLineEdit()
        self.line_buscar_asignatura.setPlaceholderText("Filtrar asignaturas")
        self.line_buscar_asignatura.textChanged.connect(self._filtrar_asignaturas)
        layout_grid.addWidget(self.line_buscar_asignatura, 2, 0)

        self.line_buscar_prerequisito = QLineEdit()
        self.line_buscar_prerequisito.setPlaceholderText("Filtrar prerrequisitos")
        self.line_buscar_prerequisito.textChanged.connect(self._filtrar_prerequisitos)
        layout_grid.addWidget(self.line_buscar_prerequisito, 2, 1)

        self.lista_asignaturas = QListWidget()
        self.lista_asignaturas.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.lista_asignaturas.currentItemChanged.connect(
            self._cargar_prerequisitos_actuales
        )
        layout_grid.addWidget(self.lista_asignaturas, 3, 0)

        self.lista_prerequisitos = QListWidget()
        self.lista_prerequisitos.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection
        )
        self.lista_prerequisitos.itemChanged.connect(self._actualizar_contador)
        layout_grid.addWidget(self.lista_prerequisitos, 3, 1)

        self.label_seleccionados = QLabel("Seleccionados: 0")
        layout_grid.addWidget(self.label_seleccionados, 4, 1)
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

    def _cargar_asignaturas(self) -> bool:
        consulta = QSqlQuery(db=self.modelo.database())
        if not consulta.exec(
            "SELECT id_asignatura, codigo, nombre FROM Asignatura ORDER BY codigo"
        ):
            error = consulta.lastError().text()
            LOGGER.error("Error al cargar las asignaturas: %s", error)
            QMessageBox.warning(self, "Error", f"No se pudieron cargar las asignaturas: {error}")
            return False

        while consulta.next():
            self.asignaturas.append(
                (
                    int(consulta.value("id_asignatura")),
                    str(consulta.value("codigo")),
                    str(consulta.value("nombre")),
                )
            )
        if not self.asignaturas:
            QMessageBox.information(
                self,
                "Sin asignaturas",
                "Primero debe registrar asignaturas para asociar prerrequisitos.",
            )
            return False
        return True

    def _cargar_listas(self):
        for id_asignatura, codigo, nombre in self.asignaturas:
            item = QListWidgetItem(f"{codigo} - {nombre}")
            item.setData(Qt.ItemDataRole.UserRole, id_asignatura)
            self.lista_asignaturas.addItem(item)

            item_prerequisito = QListWidgetItem(f"{codigo} - {nombre}")
            item_prerequisito.setData(Qt.ItemDataRole.UserRole, id_asignatura)
            item_prerequisito.setFlags(
                item_prerequisito.flags() | Qt.ItemFlag.ItemIsUserCheckable
            )
            item_prerequisito.setCheckState(Qt.CheckState.Unchecked)
            self.lista_prerequisitos.addItem(item_prerequisito)

        self.lista_prerequisitos.setEnabled(False)
        self.button_asociar.setEnabled(False)

    def _filtrar_asignaturas(self, texto: str):
        patron = texto.casefold().strip()
        for indice in range(self.lista_asignaturas.count()):
            item = self.lista_asignaturas.item(indice)
            item.setHidden(patron not in item.text().casefold())
        actual = self.lista_asignaturas.currentItem()
        if actual is not None and actual.isHidden():
            self.lista_asignaturas.setCurrentRow(-1)

    def _filtrar_prerequisitos(self, texto: str):
        patron = texto.casefold().strip()
        id_asignatura = self.lista_asignaturas.currentItem()
        id_asignatura = (
            id_asignatura.data(Qt.ItemDataRole.UserRole)
            if id_asignatura is not None
            else None
        )
        for indice in range(self.lista_prerequisitos.count()):
            item = self.lista_prerequisitos.item(indice)
            item_id = item.data(Qt.ItemDataRole.UserRole)
            item.setHidden(
                item_id == id_asignatura or patron not in item.text().casefold()
            )

    def _cargar_prerequisitos_actuales(self, item: QListWidgetItem | None, _anterior=None):
        self.ids_prerequisitos_actuales.clear()
        if item is None:
            self.lista_prerequisitos.setEnabled(False)
            self.button_asociar.setEnabled(False)
            self._actualizar_contador()
            return

        id_asignatura = item.data(Qt.ItemDataRole.UserRole)
        consulta = QSqlQuery(db=self.modelo.database())
        if not consulta.prepare(
            "SELECT id_prerequisito FROM Prerequisito WHERE id_asignatura = :id_asignatura"
        ):
            self._mostrar_error(
                "No se pudieron cargar las asociaciones",
                consulta.lastError().text(),
            )
            self.lista_prerequisitos.setEnabled(False)
            self.button_asociar.setEnabled(False)
            return

        consulta.bindValue(":id_asignatura", id_asignatura)
        if not consulta.exec():
            self._mostrar_error(
                "No se pudieron cargar las asociaciones",
                consulta.lastError().text(),
            )
            self.lista_prerequisitos.setEnabled(False)
            self.button_asociar.setEnabled(False)
            return

        while consulta.next():
            self.ids_prerequisitos_actuales.add(int(consulta.value("id_prerequisito")))

        for indice in range(self.lista_prerequisitos.count()):
            prerequisito = self.lista_prerequisitos.item(indice)
            id_prerequisito = prerequisito.data(Qt.ItemDataRole.UserRole)
            prerequisito.setCheckState(
                Qt.CheckState.Checked
                if id_prerequisito in self.ids_prerequisitos_actuales
                else Qt.CheckState.Unchecked
            )
            prerequisito.setHidden(
                id_prerequisito == id_asignatura
                or self.line_buscar_prerequisito.text().casefold().strip()
                not in prerequisito.text().casefold()
            )

        self.lista_prerequisitos.setEnabled(True)
        self.button_asociar.setEnabled(True)
        self._actualizar_contador()

    def _actualizar_contador(self, _item=None):
        seleccionados = sum(
            self.lista_prerequisitos.item(indice).checkState() == Qt.CheckState.Checked
            for indice in range(self.lista_prerequisitos.count())
        )
        self.label_seleccionados.setText(f"Seleccionados: {seleccionados}")

    def _crear_ciclo(self, id_asignatura: int, id_prerequisito: int) -> bool | None:
        consulta = QSqlQuery(db=self.modelo.database())
        if not consulta.prepare(
            "WITH RECURSIVE alcanzables(id) AS ("
            "SELECT id_prerequisito FROM Prerequisito WHERE id_asignatura = :inicio "
            "UNION "
            "SELECT p.id_prerequisito FROM Prerequisito p "
            "JOIN alcanzables a ON p.id_asignatura = a.id) "
            "SELECT EXISTS(SELECT 1 FROM alcanzables WHERE id = :objetivo)"
        ):
            self._mostrar_error("No se pudo validar la asociación", consulta.lastError().text())
            return None

        consulta.bindValue(":inicio", id_prerequisito)
        consulta.bindValue(":objetivo", id_asignatura)
        if not consulta.exec() or not consulta.next():
            self._mostrar_error("No se pudo validar la asociación", consulta.lastError().text())
            return None
        return bool(consulta.value(0))

    def on_asociar(self):
        asignatura = self.lista_asignaturas.currentItem()
        if asignatura is None:
            QMessageBox.warning(
                self,
                "Advertencia",
                "Seleccione la asignatura que requiere prerrequisitos",
            )
            return

        id_asignatura = int(asignatura.data(Qt.ItemDataRole.UserRole))
        seleccionados = {
            int(self.lista_prerequisitos.item(indice).data(Qt.ItemDataRole.UserRole))
            for indice in range(self.lista_prerequisitos.count())
            if self.lista_prerequisitos.item(indice).checkState() == Qt.CheckState.Checked
        }

        if seleccionados == self.ids_prerequisitos_actuales:
            QMessageBox.information(self, "Sin cambios", "La asociación ya está actualizada.")
            return

        if not seleccionados and self.ids_prerequisitos_actuales:
            respuesta = QMessageBox.question(
                self,
                "Quitar prerrequisitos",
                "No hay prerrequisitos marcados. Se quitarán todas las asociaciones actuales. "
                "¿Desea continuar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if respuesta != QMessageBox.StandardButton.Yes:
                return

        for id_prerequisito in seleccionados:
            if id_prerequisito == id_asignatura:
                QMessageBox.warning(
                    self,
                    "Asociación inválida",
                    "Una asignatura no puede ser su propio prerrequisito.",
                )
                return
            crea_ciclo = self._crear_ciclo(id_asignatura, id_prerequisito)
            if crea_ciclo is None:
                return
            if crea_ciclo:
                QMessageBox.warning(
                    self,
                    "Asociación inválida",
                    "La selección crearía un ciclo de prerrequisitos.",
                )
                return

        base_datos = self.modelo.database()
        if not base_datos.transaction():
            self._mostrar_error(
                "No se pudieron guardar las asociaciones",
                base_datos.lastError().text(),
            )
            return

        borrar = QSqlQuery(db=base_datos)
        if not borrar.prepare(
            "DELETE FROM Prerequisito WHERE id_asignatura = :id_asignatura"
        ):
            base_datos.rollback()
            self._mostrar_error(
                "No se pudieron reemplazar las asociaciones",
                borrar.lastError().text(),
            )
            return
        borrar.bindValue(":id_asignatura", id_asignatura)
        if not borrar.exec():
            base_datos.rollback()
            self._mostrar_error(
                "No se pudieron reemplazar las asociaciones",
                borrar.lastError().text(),
            )
            return

        if seleccionados:
            insertar = QSqlQuery(db=base_datos)
            if not insertar.prepare(
                "INSERT INTO Prerequisito (id_asignatura, id_prerequisito) "
                "VALUES (:id_asignatura, :id_prerequisito)"
            ):
                base_datos.rollback()
                self._mostrar_error(
                    "No se pudieron guardar las asociaciones",
                    insertar.lastError().text(),
                )
                return
            for id_prerequisito in seleccionados:
                insertar.bindValue(":id_asignatura", id_asignatura)
                insertar.bindValue(":id_prerequisito", id_prerequisito)
                if not insertar.exec():
                    base_datos.rollback()
                    self._mostrar_error(
                        "No se pudieron guardar las asociaciones",
                        insertar.lastError().text(),
                    )
                    return

        if not base_datos.commit():
            base_datos.rollback()
            self._mostrar_error(
                "No se pudieron confirmar las asociaciones",
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
            "Asociación completada",
            f"Se asociaron {len(seleccionados)} prerrequisitos.",
        )
        self.close()

    def _mostrar_error(self, mensaje: str, error: str):
        LOGGER.error("%s: %s", mensaje, error)
        QMessageBox.warning(self, "Error", f"{mensaje}: {error}")
