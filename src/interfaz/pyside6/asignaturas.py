import csv
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
    QMessageBox,
    QFileDialog,
)
from PySide6.QtSql import QSqlTableModel, QSqlQuery
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from interfaz.pyside6.estilos import (
    ESTILO_PUSH_BUTTON_AGREGAR,
    ESTILO_PUSH_BUTTON_EDITAR,
    ESTILO_PUSH_BUTTON_ELIMINAR,
)
from utilidades.configuraciones import LOGGER
from interfaz.pyside6.auxiliares import conectar_modelo


def _leer_asignaturas_csv(ruta: str) -> list[tuple[str, str, float]]:
    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        muestra = archivo.read(8192)
        if not muestra.strip():
            raise ValueError("El archivo CSV esta vacio")
        archivo.seek(0)
        try:
            dialecto = csv.Sniffer().sniff(muestra, delimiters=",;")
        except csv.Error as error:
            raise ValueError("No se pudo detectar el separador del archivo CSV") from error

        lector = csv.DictReader(archivo, dialect=dialecto)
        if not lector.fieldnames:
            raise ValueError("El archivo CSV debe incluir encabezados")

        encabezados = [encabezado.strip().casefold() for encabezado in lector.fieldnames]
        if len(set(encabezados)) != len(encabezados):
            raise ValueError("El archivo CSV contiene encabezados duplicados")
        columnas = dict(zip(encabezados, lector.fieldnames))
        requeridas = {"codigo", "nombre", "credito"}
        if not requeridas.issubset(columnas):
            raise ValueError("El CSV debe incluir las columnas codigo, nombre y credito")

        asignaturas = []
        codigos = set()
        for registro in lector:
            numero_fila = lector.line_num
            if None in registro:
                raise ValueError(f"La fila {numero_fila} tiene mas columnas de las esperadas")
            if all(valor is None or not valor.strip() for valor in registro.values()):
                continue

            codigo = (registro.get(columnas["codigo"]) or "").strip()
            nombre = (registro.get(columnas["nombre"]) or "").strip()
            credito_texto = (registro.get(columnas["credito"]) or "").strip()
            if not codigo or not nombre or not credito_texto:
                raise ValueError(f"La fila {numero_fila} debe tener codigo, nombre y credito")
            if codigo in codigos:
                raise ValueError(f"El codigo {codigo} esta duplicado en el archivo")
            codigos.add(codigo)

            if dialecto.delimiter == ";" and "," in credito_texto and "." not in credito_texto:
                credito_texto = credito_texto.replace(",", ".")
            try:
                credito = float(credito_texto)
            except ValueError as error:
                raise ValueError(
                    f"Los creditos de la fila {numero_fila} no son un numero valido"
                ) from error
            if not math.isfinite(credito) or credito < 0:
                raise ValueError(
                    f"Los creditos de la fila {numero_fila} deben ser mayor o igual a cero"
                )
            asignaturas.append((codigo, nombre, credito))

        if not asignaturas:
            raise ValueError("El archivo CSV no contiene asignaturas para importar")
        return asignaturas


class Asignaturas(QWidget):
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

        label_titulo = QLabel(" 📚 Asignaturas")
        layout_titulo.addWidget(label_titulo)
        font = QFont()
        font.setPointSize(14)
        label_titulo.setFont(font)
        frame_linea = QFrame()
        frame_linea.setFrameShape(QFrame.Shape.HLine)
        layout_titulo.addWidget(frame_linea)

        self.line_buscar = QLineEdit()
        self.line_buscar.setPlaceholderText("Busca por codigo o nombre")
        self.line_buscar.textChanged.connect(self.on_buscar)
        layout_operaciones.addWidget(self.line_buscar)

        self.push_importar = QPushButton("Importar CSV")
        self.push_importar.clicked.connect(self.on_importar_csv)
        self.push_importar.setToolTip("Importa un CSV con las columnas codigo, nombre y credito")
        layout_operaciones.addWidget(self.push_importar)

        self.push_agregar = QPushButton("Agregar")
        self.push_agregar.clicked.connect(self.on_dialogo_agregar)
        self.push_agregar.setToolTip("Agrega una nueva asignatura")
        self.push_agregar.setStyleSheet(ESTILO_PUSH_BUTTON_AGREGAR)
        layout_operaciones.addWidget(self.push_agregar)

        self.push_editar = QPushButton("Editar")
        self.push_editar.clicked.connect(self.on_dialogo_editar)
        self.push_editar.setToolTip("Edita la asignatura seleccionada en la tabla")
        self.push_editar.setStyleSheet(ESTILO_PUSH_BUTTON_EDITAR)
        layout_operaciones.addWidget(self.push_editar)

        self.push_eliminar = QPushButton("Eliminar")
        self.push_eliminar.clicked.connect(self.on_dialogo_eliminar)
        self.push_eliminar.setToolTip("Elimina la asignatura seleccionada en la tabla")
        self.push_eliminar.setStyleSheet(ESTILO_PUSH_BUTTON_ELIMINAR)
        layout_operaciones.addWidget(self.push_eliminar)

        self.tabla = QTableView()
        layout_tabla.addWidget(self.tabla)
        self.setLayout(layout_main)

    def configurar_tabla(self):
        if self.modelo is None:
            LOGGER.warning("El modelo de la tabla no se pudo cargar: %s", self.modelo)
            return

        self.modelo.setTable("Asignatura")
        self.modelo.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)
        if not self.modelo.select():
            LOGGER.error("Error al cargar las asignaturas: %s", self.modelo.lastError().text())

        encabezados = ("Id", "Codigo", "Nombre", "Creditos")
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
            self.modelo.setFilter(f"codigo LIKE {patron} OR nombre LIKE {patron}")
        else:
            self.modelo.setFilter("")

        if not self.modelo.select():
            LOGGER.error("Error al buscar asignaturas: %s", self.modelo.lastError().text())

    def on_importar_csv(self):
        if self.modelo is None:
            return

        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Importar asignaturas desde CSV",
            "",
            "Archivos CSV (*.csv);;Todos los archivos (*)",
        )
        if not ruta:
            return

        try:
            asignaturas = _leer_asignaturas_csv(ruta)
        except (OSError, UnicodeError, csv.Error, ValueError) as error:
            LOGGER.error("Error al leer el archivo CSV de asignaturas: %s", error)
            QMessageBox.warning(self, "Error al importar", str(error))
            return

        base_datos = self.modelo.database()
        if not base_datos.transaction():
            error = base_datos.lastError().text()
            LOGGER.error("No se pudo iniciar la importacion de asignaturas: %s", error)
            QMessageBox.warning(self, "Error al importar", error)
            return

        consulta = QSqlQuery(db=base_datos)
        if not consulta.prepare(
            "INSERT INTO Asignatura (codigo, nombre, credito) "
            "VALUES (:codigo, :nombre, :credito)"
        ):
            base_datos.rollback()
            error = consulta.lastError().text()
            LOGGER.error("No se pudo preparar la importacion de asignaturas: %s", error)
            QMessageBox.warning(self, "Error al importar", error)
            return

        for numero_fila, (codigo, nombre, credito) in enumerate(asignaturas, start=2):
            consulta.bindValue(":codigo", codigo)
            consulta.bindValue(":nombre", nombre)
            consulta.bindValue(":credito", credito)
            if not consulta.exec():
                base_datos.rollback()
                error = consulta.lastError().text()
                LOGGER.error(
                    "Error al importar la fila %s del CSV de asignaturas: %s",
                    numero_fila,
                    error,
                )
                QMessageBox.warning(
                    self,
                    "Error al importar",
                    f"No se pudo importar la fila {numero_fila}: {error}",
                )
                return

        if not base_datos.commit():
            base_datos.rollback()
            error = base_datos.lastError().text()
            LOGGER.error("No se pudo confirmar la importacion de asignaturas: %s", error)
            QMessageBox.warning(self, "Error al importar", error)
            return

        self.line_buscar.clear()
        if not self.modelo.select():
            error = self.modelo.lastError().text()
            LOGGER.error("No se pudo actualizar la tabla de asignaturas: %s", error)
            QMessageBox.warning(
                self,
                "Error",
                f"Se importaron las asignaturas, pero no se pudo actualizar la tabla: {error}",
            )
            return

        self.tabla.resizeColumnsToContents()
        QMessageBox.information(
            self,
            "Importacion completada",
            f"Se importaron {len(asignaturas)} asignaturas",
        )

    def on_dialogo_agregar(self):
        if self.modelo is None:
            return
        self.dialog = DialogoAsignatura(self.modelo, self.tabla)
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()

    def on_dialogo_editar(self):
        index = self.tabla.currentIndex()
        if not index.isValid():
            QMessageBox.information(self, "Seleccione", "Seleccione una asignatura para editar")
            return
        if self.modelo is None:
            return

        self.dialog = DialogoAsignatura(self.modelo, self.tabla, fila=index.row())
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.show()

    def on_dialogo_eliminar(self):
        index = self.tabla.currentIndex()
        if not index.isValid():
            QMessageBox.information(self, "Seleccione", "Seleccione una asignatura para eliminar")
            return
        if self.modelo is None:
            return

        respuesta = QMessageBox.question(
            self,
            "Eliminar asignatura",
            "Esta seguro que quiere eliminar la asignatura seleccionada? "
            "Tambien se eliminaran sus horas, inscripciones, prerequisitos y registros de malla.",
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return

        if not self.modelo.removeRow(index.row()) or not self.modelo.submitAll():
            error = self.modelo.lastError().text()
            LOGGER.error("Error al eliminar la asignatura: %s", error)
            self.modelo.revertAll()
            QMessageBox.warning(self, "Error", f"No se pudo eliminar la asignatura: {error}")
            return

        if not self.modelo.select():
            LOGGER.error("Error al actualizar las asignaturas: %s", self.modelo.lastError().text())
        self.tabla.clearSelection()


class DialogoAsignatura(QWidget):
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
        titulo = "Edita la asignatura seleccionada" if fila is not None else "Agrega una asignatura"
        self.setWindowTitle(titulo)
        # self.resize(550, 250)

        self._crear_formulario()
        if self.fila is not None:
            self._cargar_campos()

    def _crear_formulario(self):
        layout_main = QVBoxLayout()
        layout_grid = QGridLayout()
        layout_main.addLayout(layout_grid)
        layout_buttons = QHBoxLayout()
        layout_main.addLayout(layout_buttons)

        label_codigo = QLabel("Codigo *")
        layout_grid.addWidget(label_codigo, 0, 0)
        self.line_codigo = QLineEdit()
        self.line_codigo.setPlaceholderText("Codigo de la asignatura")
        layout_grid.addWidget(self.line_codigo, 1, 0)

        label_credito = QLabel("Creditos *")
        layout_grid.addWidget(label_credito, 0, 1)
        self.line_credito = QLineEdit()
        self.line_credito.setPlaceholderText("Cantidad de creditos")
        layout_grid.addWidget(self.line_credito, 1, 1)

        label_nombre = QLabel("Nombre *")
        layout_grid.addWidget(label_nombre, 2, 0, 1, 2)
        self.line_nombre = QLineEdit()
        self.line_nombre.setPlaceholderText("Nombre de la asignatura")
        layout_grid.addWidget(self.line_nombre, 3, 0, 1, 2)

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
        self.line_codigo.setText(str(registro.value("codigo") or ""))
        self.line_nombre.setText(str(registro.value("nombre") or ""))
        self.line_credito.setText(str(registro.value("credito") or "0"))

    def on_aplicar(self):
        codigo = self.line_codigo.text().strip()
        nombre = self.line_nombre.text().strip()
        credito_texto = self.line_credito.text().strip()
        if not codigo or not nombre or not credito_texto:
            QMessageBox.warning(
                self,
                "Advertencia",
                "El codigo, el nombre y los creditos son obligatorios",
            )
            return

        try:
            credito = float(credito_texto)
        except ValueError:
            QMessageBox.warning(self, "Advertencia", "Los creditos deben ser un numero valido")
            return

        if not math.isfinite(credito) or credito < 0:
            QMessageBox.warning(
                self,
                "Advertencia",
                "Los creditos deben ser un numero mayor o igual a cero",
            )
            return

        if self.fila is None:
            self.fila = self.modelo.rowCount()
            if not self.modelo.insertRow(self.fila):
                self._mostrar_error("No se pudo agregar la asignatura")
                return

        valores = {
            "codigo": codigo,
            "nombre": nombre,
            "credito": credito,
        }
        for columna, valor in valores.items():
            indice_columna = self.modelo.fieldIndex(columna)
            if not self.modelo.setData(self.modelo.index(self.fila, indice_columna), valor):
                self.modelo.revertAll()
                self._mostrar_error(f"No se pudo actualizar el campo {columna}")
                return

        if not self.modelo.submitAll():
            self.modelo.revertAll()
            self._mostrar_error("No se pudo guardar la asignatura")
            return

        if not self.modelo.select():
            LOGGER.error("Error al actualizar las asignaturas: %s", self.modelo.lastError().text())
        self.tabla.clearSelection()
        self.close()

    def _mostrar_error(self, mensaje: str):
        error = self.modelo.lastError().text()
        LOGGER.error("%s: %s", mensaje, error)
        QMessageBox.warning(self, "Error", f"{mensaje}: {error}")
