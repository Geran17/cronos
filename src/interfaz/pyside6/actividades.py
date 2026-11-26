import math

from PySide6.QtCore import QDate, QSettings, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPalette
from PySide6.QtSql import QSqlQuery, QSqlRelation, QSqlRelationalTableModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QCompleter,
    QDateEdit,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableView,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from interfaz.pyside6.auxiliares import obtener_conexion
from interfaz.pyside6.tipos_actividades import CLAVE_COLORES
from interfaz.pyside6.estilos import (
    ESTILO_PUSH_BUTTON_AGREGAR,
    ESTILO_PUSH_BUTTON_EDITAR,
    ESTILO_PUSH_BUTTON_ELIMINAR,
)
from utilidades.configuraciones import CONFIG_CRONO, LOGGER

INDICES_COLUMNAS = {
    "id_actividad": 0,
    "id_inscripcion": 1,
    "id_tipoactividad": 2,
    "titulo": 3,
    "descripcion": 4,
    "fecha_inicio": 5,
    "fecha_limite": 6,
    "fecha_entrega": 7,
    "dias_desarrollo": 8,
    "puntaje": 9,
    "estado": 10,
}
ESTADOS = ("Pendiente", "Entregada", "Calificada", "No Entregada")


def _formatear_inscripcion(
    codigo,
    nombre,
    fecha_inscripcion,
    periodo,
    seccion,
    estado,
) -> str:
    asignatura = (
        f"{codigo} - {nombre}" if codigo and nombre else (nombre or codigo)
    )
    anio = str(fecha_inscripcion)[:4] if fecha_inscripcion else None
    return " - ".join(
        str(parte)
        for parte in (
            asignatura,
            f"Año {anio}" if anio else None,
            periodo,
            seccion,
            estado,
        )
        if parte
    )


class DelegadoColorActividad(QStyledItemDelegate):
    def __init__(self, modelo: QSqlRelationalTableModel, parent=None):
        super().__init__(parent)
        self.modelo = modelo
        self.colores_por_actividad: dict[int, QColor] = {}
        self.actualizar_colores()

    def actualizar_colores(self):
        self.colores_por_actividad.clear()
        if CONFIG_CRONO is None:
            LOGGER.error("No se pudo acceder al archivo de configuraciones para los colores")
            return

        configuracion = QSettings(str(CONFIG_CRONO), QSettings.Format.IniFormat)
        consulta = QSqlQuery(db=self.modelo.database())
        if not consulta.exec("SELECT id_actividad, id_tipoactividad FROM Actividad"):
            LOGGER.error(
                "No se pudieron cargar los colores de actividades: %s",
                consulta.lastError().text(),
            )
            return

        while consulta.next():
            actividad_id = int(consulta.value("id_actividad"))
            tipo_id = consulta.value("id_tipoactividad")
            valor = configuracion.value(f"{CLAVE_COLORES}/{tipo_id}")
            if valor is None:
                continue
            color = QColor(str(valor))
            if not color.isValid():
                LOGGER.warning(
                    "El color guardado para el tipo %s no es válido: %s",
                    tipo_id,
                    valor,
                )
                continue
            self.colores_por_actividad[actividad_id] = color

    def initStyleOption(self, option: QStyleOptionViewItem, index):
        super().initStyleOption(option, index)
        if index.column() != INDICES_COLUMNAS["id_tipoactividad"]:
            return

        actividad_id = self.modelo.record(index.row()).value("id_actividad")
        try:
            color = self.colores_por_actividad.get(int(actividad_id))
        except (TypeError, ValueError):
            color = None
        if color is None:
            return

        option.backgroundBrush = QBrush(color)
        texto = (
            QColor(Qt.GlobalColor.white)
            if color.lightness() < 128
            else QColor(Qt.GlobalColor.black)
        )
        option.palette.setColor(QPalette.ColorRole.Text, texto)


class Actividades(QWidget):
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

        label_titulo = QLabel(" 📅 Actividades")
        layout_titulo.addWidget(label_titulo)
        font = QFont()
        font.setPointSize(14)
        label_titulo.setFont(font)
        frame_linea = QFrame()
        frame_linea.setFrameShape(QFrame.Shape.HLine)
        layout_titulo.addWidget(frame_linea)

        self.line_buscar = QLineEdit()
        self.line_buscar.setPlaceholderText(
            "Busca por título, tipo, estado, inscripción o fecha"
        )
        self.line_buscar.textChanged.connect(self.on_buscar)
        layout_operaciones.addWidget(self.line_buscar)

        self.push_agregar = QPushButton("Agregar")
        self.push_agregar.clicked.connect(self.on_dialogo_agregar)
        self.push_agregar.setToolTip("Agrega una nueva actividad")
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

        layout_filtros = QHBoxLayout()
        layout_main.addLayout(layout_filtros)

        layout_filtros.addWidget(QLabel("Año"))
        self.combo_filtro_anio = QComboBox()
        self.combo_filtro_anio.addItem("Todos", userData="*")
        layout_filtros.addWidget(self.combo_filtro_anio)

        layout_filtros.addWidget(QLabel("Tipo"))
        self.combo_filtro_tipo = QComboBox()
        self.combo_filtro_tipo.addItem("Todos", userData="*")
        layout_filtros.addWidget(self.combo_filtro_tipo)

        layout_filtros.addWidget(QLabel("Estado"))
        self.combo_filtro_estado = QComboBox()
        self.combo_filtro_estado.addItem("Todos", userData="*")
        layout_filtros.addWidget(self.combo_filtro_estado)
        layout_filtros.addStretch()

        layout_tabla = QVBoxLayout()
        layout_main.addLayout(layout_tabla)
        self.tabla = QTableView()
        layout_tabla.addWidget(self.tabla)
        self.setLayout(layout_main)

    def configurar_tabla(self):
        if self.modelo is None:
            LOGGER.warning("El modelo de la tabla no se pudo cargar: %s", self.modelo)
            return

        self.modelo.setTable("Actividad")
        self.modelo.setRelation(
            INDICES_COLUMNAS["id_inscripcion"],
            QSqlRelation("Inscripcion", "id_inscripcion", "seccion"),
        )
        self.modelo.setRelation(
            INDICES_COLUMNAS["id_tipoactividad"],
            QSqlRelation("TipoActividad", "id_tipoactividad", "nombre"),
        )
        self.modelo.setJoinMode(QSqlRelationalTableModel.JoinMode.LeftJoin)
        self.modelo.setEditStrategy(QSqlRelationalTableModel.EditStrategy.OnManualSubmit)
        if not self.modelo.select():
            LOGGER.error("Error al cargar las actividades: %s", self.modelo.lastError().text())

        encabezados = (
            "Id",
            "Inscripción",
            "Tipo",
            "Título",
            "Descripción",
            "Inicio",
            "Fecha límite",
            "Fecha entrega",
            "Días desarrollo",
            "Puntaje",
            "Estado",
        )
        for columna, encabezado in enumerate(encabezados):
            self.modelo.setHeaderData(columna, Qt.Orientation.Horizontal, encabezado)

        self.tabla.setModel(self.modelo)
        self.tabla.resizeColumnsToContents()
        self.tabla.setColumnHidden(INDICES_COLUMNAS["id_actividad"], True)
        self.tabla.setColumnHidden(INDICES_COLUMNAS["descripcion"], True)
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla.setItemDelegateForColumn(
            INDICES_COLUMNAS["id_tipoactividad"],
            DelegadoColorActividad(self.modelo, self.tabla),
        )
        self._cargar_filtros()

    def _cargar_filtros(self):
        if self.modelo is None:
            return

        consulta_anios = QSqlQuery(db=self.modelo.database())
        if not consulta_anios.exec(
            "SELECT DISTINCT COALESCE(substr(fecha_inscripcion, 1, 4), '') AS anio "
            "FROM Inscripcion ORDER BY anio DESC"
        ):
            LOGGER.error(
                "No se pudieron cargar los años para filtrar actividades: %s",
                consulta_anios.lastError().text(),
            )
        else:
            while consulta_anios.next():
                anio = str(consulta_anios.value("anio") or "")
                self.combo_filtro_anio.addItem(
                    anio if anio else "(Sin año)",
                    userData=anio,
                )

        consulta_tipos = QSqlQuery(db=self.modelo.database())
        if not consulta_tipos.exec(
            "SELECT id_tipoactividad, nombre FROM TipoActividad ORDER BY nombre"
        ):
            LOGGER.error(
                "No se pudieron cargar los tipos para filtrar actividades: %s",
                consulta_tipos.lastError().text(),
            )
        else:
            while consulta_tipos.next():
                self.combo_filtro_tipo.addItem(
                    str(consulta_tipos.value("nombre")),
                    userData=int(consulta_tipos.value("id_tipoactividad")),
                )

        for estado in ESTADOS:
            self.combo_filtro_estado.addItem(estado, userData=estado)
        self.combo_filtro_anio.currentIndexChanged.connect(self.on_buscar)
        self.combo_filtro_tipo.currentIndexChanged.connect(self.on_buscar)
        self.combo_filtro_estado.currentIndexChanged.connect(self.on_buscar)

    def on_buscar(self, *_):
        if self.modelo is None:
            return

        texto = self.line_buscar.text()
        condiciones = []
        patron = texto.replace("'", "''")
        if patron:
            patron = f"'%{patron}%'"
            condiciones.append(
                f"Actividad.titulo LIKE {patron} "
                f"OR Actividad.descripcion LIKE {patron} "
                "OR Actividad.id_tipoactividad IN ("
                "SELECT id_tipoactividad FROM TipoActividad "
                f"WHERE nombre LIKE {patron} OR siglas LIKE {patron}) "
                f"OR Actividad.estado LIKE {patron} "
                f"OR Actividad.fecha_inicio LIKE {patron} "
                f"OR Actividad.fecha_limite LIKE {patron} "
                f"OR Actividad.fecha_entrega LIKE {patron} "
                "OR Actividad.id_inscripcion IN ("
                "SELECT id_inscripcion FROM Inscripcion "
                f"WHERE seccion LIKE {patron})"
            )

        anio = self.combo_filtro_anio.currentData()
        if anio == "":
            condiciones.append(
                "Actividad.id_inscripcion IN ("
                "SELECT id_inscripcion FROM Inscripcion "
                "WHERE fecha_inscripcion IS NULL OR fecha_inscripcion = '')"
            )
        elif anio != "*":
            anio_escapado = str(anio).replace("'", "''")
            condiciones.append(
                "Actividad.id_inscripcion IN ("
                "SELECT id_inscripcion FROM Inscripcion "
                f"WHERE substr(fecha_inscripcion, 1, 4) = '{anio_escapado}')"
            )

        tipo_id = self.combo_filtro_tipo.currentData()
        if tipo_id != "*":
            condiciones.append(f"Actividad.id_tipoactividad = {int(tipo_id)}")

        estado = self.combo_filtro_estado.currentData()
        if estado != "*":
            estado_escapado = str(estado).replace("'", "''")
            condiciones.append(f"Actividad.estado = '{estado_escapado}'")

        self.modelo.setFilter(" AND ".join(f"({condicion})" for condicion in condiciones))

        if not self.modelo.select():
            LOGGER.error("Error al buscar actividades: %s", self.modelo.lastError().text())
        else:
            delegado = self.tabla.itemDelegateForColumn(
                INDICES_COLUMNAS["id_tipoactividad"]
            )
            if isinstance(delegado, DelegadoColorActividad):
                delegado.actualizar_colores()
            self.tabla.resizeColumnsToContents()
            self.tabla.viewport().update()

    def on_dialogo_agregar(self):
        if self.modelo is None:
            return
        self.dialog = DialogoActividad(self.modelo, self.tabla)
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()

    def on_dialogo_editar(self):
        index = self.tabla.currentIndex()
        if not index.isValid():
            QMessageBox.information(self, "Seleccione", "Seleccione una actividad para editar")
            return
        if self.modelo is None:
            return

        self.dialog = DialogoActividad(self.modelo, self.tabla, fila=index.row())
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()

    def on_dialogo_eliminar(self):
        index = self.tabla.currentIndex()
        if not index.isValid():
            QMessageBox.information(self, "Seleccione", "Seleccione una actividad para eliminar")
            return
        if self.modelo is None:
            return

        respuesta = QMessageBox.question(
            self,
            "Eliminar actividad",
            "¿Está seguro de eliminar la actividad seleccionada?",
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return

        if not self.modelo.removeRow(index.row()) or not self.modelo.submitAll():
            error = self.modelo.lastError().text()
            LOGGER.error("Error al eliminar la actividad: %s", error)
            self.modelo.revertAll()
            QMessageBox.warning(self, "Error", f"No se pudo eliminar la actividad: {error}")
            return

        if not self.modelo.select():
            LOGGER.error("Error al actualizar las actividades: %s", self.modelo.lastError().text())
        else:
            delegado = self.tabla.itemDelegateForColumn(
                INDICES_COLUMNAS["id_tipoactividad"]
            )
            if isinstance(delegado, DelegadoColorActividad):
                delegado.actualizar_colores()
            self.tabla.resizeColumnsToContents()
            self.tabla.viewport().update()
        self.tabla.clearSelection()


class DialogoActividad(QWidget):
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
        self.inscripcion_id: int | None = None
        self.setWindowTitle(
            "Editar actividad seleccionada" if fila is not None else "Agregar actividad"
        )

        self._crear_formulario()
        if not self._cargar_catalogos():
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

        layout_grid.addWidget(QLabel("Inscripción *"), 0, 0)
        layout_inscripcion = QHBoxLayout()
        self.line_inscripcion = QLineEdit()
        self.line_inscripcion.setReadOnly(True)
        self.line_inscripcion.setPlaceholderText("Selecciona una inscripción")
        layout_inscripcion.addWidget(self.line_inscripcion)
        self.button_seleccionar_inscripcion = QPushButton("Seleccionar…")
        self.button_seleccionar_inscripcion.clicked.connect(
            self.on_seleccionar_inscripcion
        )
        layout_inscripcion.addWidget(self.button_seleccionar_inscripcion)
        layout_grid.addLayout(layout_inscripcion, 0, 1)

        layout_grid.addWidget(QLabel("Tipo *"), 1, 0)
        self.combo_tipo = QComboBox()
        layout_grid.addWidget(self.combo_tipo, 1, 1)

        layout_grid.addWidget(QLabel("Título *"), 2, 0)
        self.line_titulo = QLineEdit()
        self.line_titulo.setPlaceholderText("Título de la actividad")
        layout_grid.addWidget(self.line_titulo, 2, 1)

        layout_grid.addWidget(QLabel("Estado *"), 3, 0)
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(ESTADOS)
        layout_grid.addWidget(self.combo_estado, 3, 1)

        layout_grid.addWidget(QLabel("Días de desarrollo"), 4, 0)
        self.line_dias = QLineEdit()
        self.line_dias.setPlaceholderText("Opcional, mayor o igual a cero")
        layout_grid.addWidget(self.line_dias, 4, 1)

        layout_grid.addWidget(QLabel("Puntaje"), 5, 0)
        self.line_puntaje = QLineEdit()
        self.line_puntaje.setPlaceholderText("Opcional, mayor o igual a cero")
        layout_grid.addWidget(self.line_puntaje, 5, 1)

        layout_grid.addWidget(QLabel("Fecha de inicio"), 6, 0)
        self.check_inicio = QCheckBox("Indicar fecha")
        self.date_inicio = QDateEdit()
        self._configurar_fecha(self.date_inicio)
        self.date_inicio.setEnabled(False)
        self.check_inicio.toggled.connect(self.date_inicio.setEnabled)
        layout_fecha_inicio = QHBoxLayout()
        layout_fecha_inicio.addWidget(self.check_inicio)
        layout_fecha_inicio.addWidget(self.date_inicio)
        layout_grid.addLayout(layout_fecha_inicio, 6, 1)

        layout_grid.addWidget(QLabel("Fecha límite"), 7, 0)
        self.check_limite = QCheckBox("Indicar fecha")
        self.date_limite = QDateEdit()
        self._configurar_fecha(self.date_limite)
        self.date_limite.setEnabled(False)
        self.check_limite.toggled.connect(self.date_limite.setEnabled)
        layout_fecha_limite = QHBoxLayout()
        layout_fecha_limite.addWidget(self.check_limite)
        layout_fecha_limite.addWidget(self.date_limite)
        layout_grid.addLayout(layout_fecha_limite, 7, 1)

        layout_grid.addWidget(QLabel("Fecha de entrega"), 8, 0)
        self.check_entrega = QCheckBox("Indicar fecha")
        self.date_entrega = QDateEdit()
        self._configurar_fecha(self.date_entrega)
        self.date_entrega.setEnabled(False)
        self.check_entrega.toggled.connect(self.date_entrega.setEnabled)
        layout_fecha_entrega = QHBoxLayout()
        layout_fecha_entrega.addWidget(self.check_entrega)
        layout_fecha_entrega.addWidget(self.date_entrega)
        layout_grid.addLayout(layout_fecha_entrega, 8, 1)

        layout_grid.addWidget(QLabel("Descripción"), 9, 0)
        self.text_descripcion = QTextEdit()
        self.text_descripcion.setPlaceholderText("Descripción de la actividad")
        layout_grid.addWidget(self.text_descripcion, 9, 1)

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

    def _cargar_catalogos(self) -> bool:
        consulta_tipos = QSqlQuery(db=self.modelo.database())
        if not consulta_tipos.exec(
            "SELECT id_tipoactividad, nombre, siglas FROM TipoActividad ORDER BY nombre"
        ):
            self._mostrar_error(
                "No se pudieron cargar los tipos de actividad",
                consulta_tipos.lastError().text(),
            )
            return False

        while consulta_tipos.next():
            tipo_id = consulta_tipos.value("id_tipoactividad")
            nombre = consulta_tipos.value("nombre")
            siglas = consulta_tipos.value("siglas")
            texto = f"{siglas} - {nombre}" if siglas else str(nombre)
            self.combo_tipo.addItem(texto, userData=tipo_id)

        if self.combo_tipo.count() == 0:
            QMessageBox.information(
                self,
                "Datos insuficientes",
                "Debes registrar al menos un tipo de actividad antes de crear una actividad.",
            )
            return False
        return True

    def on_seleccionar_inscripcion(self):
        dialogo = DialogoSeleccionInscripcion(
            self.modelo.database(),
            self,
            inscripcion_id=self.inscripcion_id,
        )
        if not dialogo.carga_valida:
            return
        if dialogo.exec() != QDialog.DialogCode.Accepted:
            return

        self.inscripcion_id = dialogo.inscripcion_id
        self.line_inscripcion.setText(dialogo.inscripcion_texto)

    def _cargar_campos(self) -> bool:
        if self.fila is None:
            return True

        registro = self.modelo.record(self.fila)
        consulta = QSqlQuery(db=self.modelo.database())
        if not consulta.prepare(
            "SELECT i.id_inscripcion, i.periodo, i.seccion, i.estado, "
            "i.fecha_inscripcion, a.codigo, a.nombre, Actividad.id_tipoactividad "
            "FROM Actividad "
            "JOIN Inscripcion i ON i.id_inscripcion = Actividad.id_inscripcion "
            "LEFT JOIN Asignatura a ON a.id_asignatura = i.id_asignatura "
            "WHERE Actividad.id_actividad = :id_actividad"
        ):
            self._mostrar_error(
                "No se pudieron cargar las relaciones de la actividad",
                consulta.lastError().text(),
            )
            return False
        consulta.bindValue(":id_actividad", registro.value("id_actividad"))
        if not consulta.exec() or not consulta.next():
            self._mostrar_error(
                "No se pudieron cargar las relaciones de la actividad",
                consulta.lastError().text() or "La actividad ya no existe.",
            )
            return False

        self.inscripcion_id = int(consulta.value("id_inscripcion"))
        self.line_inscripcion.setText(
            _formatear_inscripcion(
                consulta.value("codigo"),
                consulta.value("nombre"),
                consulta.value("fecha_inscripcion"),
                consulta.value("periodo"),
                consulta.value("seccion"),
                consulta.value("estado"),
            )
        )
        indice = self.combo_tipo.findData(consulta.value("id_tipoactividad"))
        if indice >= 0:
            self.combo_tipo.setCurrentIndex(indice)

        self.line_titulo.setText(str(registro.value("titulo") or ""))
        self.text_descripcion.setPlainText(str(registro.value("descripcion") or ""))
        self.line_dias.setText(self._texto_numero(registro.value("dias_desarrollo")))
        self.line_puntaje.setText(self._texto_numero(registro.value("puntaje")))

        self._cargar_fecha(self.check_inicio, self.date_inicio, registro.value("fecha_inicio"))
        self._cargar_fecha(self.check_limite, self.date_limite, registro.value("fecha_limite"))
        self._cargar_fecha(self.check_entrega, self.date_entrega, registro.value("fecha_entrega"))

        indice_estado = self.combo_estado.findText(str(registro.value("estado") or "Pendiente"))
        if indice_estado >= 0:
            self.combo_estado.setCurrentIndex(indice_estado)
        return True

    @staticmethod
    def _cargar_fecha(check: QCheckBox, campo: QDateEdit, valor):
        texto = str(valor or "")
        if not texto:
            return
        fecha = QDate.fromString(texto, Qt.DateFormat.ISODate)
        if fecha.isValid():
            check.setChecked(True)
            campo.setDate(fecha)

    @staticmethod
    def _texto_numero(valor) -> str:
        return "" if valor is None else str(valor)

    def on_aplicar(self):
        titulo = self.line_titulo.text().strip()
        if not titulo:
            QMessageBox.warning(self, "Advertencia", "El título de la actividad es obligatorio.")
            return
        if self.inscripcion_id is None:
            QMessageBox.warning(self, "Advertencia", "Selecciona una inscripción.")
            return
        if self.combo_tipo.currentData() is None:
            QMessageBox.warning(self, "Advertencia", "Selecciona un tipo de actividad.")
            return

        dias = self._leer_entero(
            self.line_dias,
            "Los días de desarrollo",
            minimo=0,
        )
        if dias is False:
            return
        puntaje = self._leer_numero(self.line_puntaje, "El puntaje", minimo=0)
        if puntaje is False:
            return

        fecha_inicio = self._fecha_texto(self.check_inicio, self.date_inicio)
        fecha_limite = self._fecha_texto(self.check_limite, self.date_limite)
        fecha_entrega = self._fecha_texto(self.check_entrega, self.date_entrega)
        if fecha_inicio and fecha_entrega and fecha_entrega < fecha_inicio:
            QMessageBox.warning(
                self,
                "Advertencia",
                "La fecha de entrega no puede ser anterior a la fecha de inicio.",
            )
            return

        if self.fila is None:
            self.fila = self.modelo.rowCount()
            if not self.modelo.insertRow(self.fila):
                self._mostrar_error(
                    "No se pudo agregar la actividad",
                    self.modelo.lastError().text(),
                )
                return

        valores = (
            ("id_inscripcion", self.inscripcion_id),
            ("id_tipoactividad", self.combo_tipo.currentData()),
            ("titulo", titulo),
            ("descripcion", self.text_descripcion.toPlainText().strip() or None),
            ("fecha_inicio", fecha_inicio),
            ("fecha_limite", fecha_limite),
            ("fecha_entrega", fecha_entrega),
            ("dias_desarrollo", dias),
            ("puntaje", puntaje),
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
            self._mostrar_error("No se pudo guardar la actividad", error)
            return

        if not self.modelo.select():
            LOGGER.error(
                "Error al actualizar las actividades: %s",
                self.modelo.lastError().text(),
            )
        else:
            delegado = self.tabla.itemDelegateForColumn(
                INDICES_COLUMNAS["id_tipoactividad"]
            )
            if isinstance(delegado, DelegadoColorActividad):
                delegado.actualizar_colores()
            self.tabla.resizeColumnsToContents()
            self.tabla.viewport().update()
        self.tabla.clearSelection()
        self.close()

    @staticmethod
    def _fecha_texto(check: QCheckBox, campo: QDateEdit) -> str | None:
        if not check.isChecked():
            return None
        return campo.date().toString(Qt.DateFormat.ISODate)

    def _leer_entero(
        self,
        campo: QLineEdit,
        nombre: str,
        minimo: int,
    ) -> int | None | bool:
        texto = campo.text().strip()
        if not texto:
            return None
        try:
            valor = int(texto)
        except ValueError:
            QMessageBox.warning(self, "Advertencia", f"{nombre} debe ser un número entero.")
            return False
        if valor < minimo:
            QMessageBox.warning(
                self,
                "Advertencia",
                f"{nombre} debe ser mayor o igual a {minimo}.",
            )
            return False
        return valor

    def _leer_numero(
        self,
        campo: QLineEdit,
        nombre: str,
        minimo: float,
    ) -> float | None | bool:
        texto = campo.text().strip()
        if not texto:
            return None
        try:
            valor = float(texto)
        except ValueError:
            QMessageBox.warning(self, "Advertencia", f"{nombre} debe ser un número válido.")
            return False
        if not math.isfinite(valor) or valor < minimo:
            QMessageBox.warning(
                self,
                "Advertencia",
                f"{nombre} debe ser mayor o igual a {minimo:g}.",
            )
            return False
        return valor

    def _mostrar_error(self, mensaje: str, error: str):
        LOGGER.error("%s: %s", mensaje, error)
        QMessageBox.warning(self, "Error", f"{mensaje}: {error}")


class DialogoSeleccionInscripcion(QDialog):
    def __init__(self, database, parent=None, inscripcion_id: int | None = None):
        super().__init__(parent)
        self.database = database
        self.inscripcion_id: int | None = None
        self.inscripcion_texto = ""
        self.inscripciones: list[tuple[int, str, str, str, str]] = []
        self.setWindowTitle("Seleccionar inscripción")
        self.resize(800, 450)

        self._crear()
        self.carga_valida = True
        self._cargar_inscripciones(inscripcion_id)
        self.combo_anio.currentIndexChanged.connect(self._filtrar)
        self.combo_periodo.currentIndexChanged.connect(self._filtrar)
        self.combo_estado.currentIndexChanged.connect(self._filtrar)

    def _crear(self):
        layout_main = QVBoxLayout(self)
        layout_filtros = QHBoxLayout()

        layout_filtros.addWidget(QLabel("Año"))
        self.combo_anio = QComboBox()
        self.combo_anio.addItem("Todos", userData="*")
        layout_filtros.addWidget(self.combo_anio)

        layout_filtros.addWidget(QLabel("Período"))
        self.combo_periodo = QComboBox()
        self.combo_periodo.addItem("Todos", userData="*")
        layout_filtros.addWidget(self.combo_periodo)

        layout_filtros.addWidget(QLabel("Estado"))
        self.combo_estado = QComboBox()
        self.combo_estado.addItem("Todos", userData="*")
        layout_filtros.addWidget(self.combo_estado)
        layout_filtros.addStretch()
        layout_main.addLayout(layout_filtros)

        self.tabla_inscripciones = QTableWidget(0, 5)
        self.tabla_inscripciones.setHorizontalHeaderLabels(
            ("Asignatura", "Año", "Período", "Sección", "Estado")
        )
        self.tabla_inscripciones.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.tabla_inscripciones.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.tabla_inscripciones.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.tabla_inscripciones.itemSelectionChanged.connect(
            self._actualizar_boton
        )
        self.tabla_inscripciones.itemDoubleClicked.connect(self._aceptar)
        self.tabla_inscripciones.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.tabla_inscripciones.horizontalHeader().setStretchLastSection(True)
        layout_main.addWidget(self.tabla_inscripciones)

        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        self.button_aceptar = QPushButton("Seleccionar")
        self.button_aceptar.setEnabled(False)
        self.button_aceptar.clicked.connect(self._aceptar)
        layout_botones.addWidget(self.button_aceptar)
        button_cancelar = QPushButton("Cancelar")
        button_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(button_cancelar)
        layout_main.addLayout(layout_botones)

    def _cargar_inscripciones(self, inscripcion_id: int | None):
        consulta = QSqlQuery(db=self.database)
        if not consulta.exec(
            "SELECT i.id_inscripcion, a.codigo, a.nombre, i.fecha_inscripcion, "
            "i.periodo, i.seccion, i.estado "
            "FROM Inscripcion i "
            "LEFT JOIN Asignatura a ON a.id_asignatura = i.id_asignatura "
            "ORDER BY i.fecha_inscripcion DESC, a.codigo, i.periodo, i.seccion"
        ):
            error = consulta.lastError().text()
            LOGGER.error("No se pudieron cargar las inscripciones: %s", error)
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudieron cargar las inscripciones: {error}",
            )
            self.carga_valida = False
            return

        anios = set()
        periodos = set()
        estados = set()
        fila_seleccionada = None
        while consulta.next():
            inscripcion_id_fila = int(consulta.value("id_inscripcion"))
            fecha = consulta.value("fecha_inscripcion")
            anio = str(fecha)[:4] if fecha else ""
            periodo = str(consulta.value("periodo") or "")
            codigo = consulta.value("codigo")
            nombre = consulta.value("nombre")
            seccion = str(consulta.value("seccion") or "")
            estado = str(consulta.value("estado") or "")
            asignatura = (
                f"{codigo} - {nombre}"
                if codigo and nombre
                else str(nombre or codigo or "")
            )
            texto = _formatear_inscripcion(
                codigo,
                nombre,
                fecha,
                periodo,
                seccion,
                estado,
            )
            self.inscripciones.append(
                (inscripcion_id_fila, texto, anio, periodo, estado)
            )
            anios.add(anio)
            periodos.add(periodo)
            estados.add(estado)

            fila = self.tabla_inscripciones.rowCount()
            self.tabla_inscripciones.insertRow(fila)
            valores = (
                asignatura,
                anio or "(Sin año)",
                periodo or "(Sin período)",
                seccion,
                estado,
            )
            for columna, valor in enumerate(valores):
                celda = QTableWidgetItem(valor)
                if columna == 0:
                    celda.setData(Qt.ItemDataRole.UserRole, inscripcion_id_fila)
                self.tabla_inscripciones.setItem(fila, columna, celda)
            if inscripcion_id_fila == inscripcion_id:
                fila_seleccionada = fila

        for anio in sorted(anios - {""}, reverse=True):
            self.combo_anio.addItem(anio, userData=anio)
        if "" in anios:
            self.combo_anio.addItem("(Sin año)", userData="")
        for periodo in sorted(periodos - {""}):
            self.combo_periodo.addItem(periodo, userData=periodo)
        if "" in periodos:
            self.combo_periodo.addItem("(Sin período)", userData="")
        for estado in sorted(estados - {""}):
            self.combo_estado.addItem(estado, userData=estado)
        if "" in estados:
            self.combo_estado.addItem("(Sin estado)", userData="")

        if not self.inscripciones:
            QMessageBox.information(
                self,
                "Datos insuficientes",
                "Debes registrar al menos una inscripción antes de crear una actividad.",
            )
            self.carga_valida = False
            return

        self._filtrar()
        if fila_seleccionada is not None:
            self.tabla_inscripciones.selectRow(fila_seleccionada)
            item = self.tabla_inscripciones.item(fila_seleccionada, 0)
            if item is not None:
                self.tabla_inscripciones.scrollToItem(item)

    def _filtrar(self, *_):
        anio_seleccionado = self.combo_anio.currentData()
        periodo_seleccionado = self.combo_periodo.currentData()
        self.tabla_inscripciones.clearSelection()
        estado_seleccionado = self.combo_estado.currentData()
        for fila, (_, _, anio, periodo, estado) in enumerate(self.inscripciones):
            coincide_anio = anio_seleccionado == "*" or anio == anio_seleccionado
            coincide_periodo = (
                periodo_seleccionado == "*" or periodo == periodo_seleccionado
            )
            coincide_estado = estado_seleccionado == "*" or estado == estado_seleccionado
            self.tabla_inscripciones.setRowHidden(
                fila,
                not (coincide_anio and coincide_periodo and coincide_estado),
            )
        self._actualizar_boton()

    def _actualizar_boton(self):
        self.button_aceptar.setEnabled(
            bool(self.tabla_inscripciones.selectionModel().selectedRows())
        )

    def _aceptar(self, *_):
        filas = self.tabla_inscripciones.selectionModel().selectedRows()
        if not filas:
            return
        fila = filas[0].row()
        self.inscripcion_id = self.inscripciones[fila][0]
        self.inscripcion_texto = self.inscripciones[fila][1]
        self.accept()
