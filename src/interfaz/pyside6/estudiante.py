import re

from PySide6.QtSql import QSqlDatabase, QSqlQuery
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from utilidades.configuraciones import LOGGER


class DialogoEstudiante(QDialog):
    def __init__(self, base_datos: QSqlDatabase, parent=None):
        super().__init__(parent)
        self.base_datos = base_datos
        self.es_nuevo = True
        self.carga_valida = True

        self.setModal(True)
        # self.resize(450, 230)
        self._crear_formulario()
        self.carga_valida = self._cargar_estudiante()

    def _crear_formulario(self):
        layout_principal = QVBoxLayout(self)
        layout_formulario = QGridLayout()
        layout_principal.addLayout(layout_formulario)

        layout_formulario.addWidget(QLabel("Nombres *"), 0, 0)
        self.line_nombres = QLineEdit()
        self.line_nombres.setPlaceholderText("Tus nombres")
        layout_formulario.addWidget(self.line_nombres, 0, 1)

        layout_formulario.addWidget(QLabel("Apellidos *"), 1, 0)
        self.line_apellidos = QLineEdit()
        self.line_apellidos.setPlaceholderText("Tus apellidos")
        layout_formulario.addWidget(self.line_apellidos, 1, 1)

        layout_formulario.addWidget(QLabel("Correo *"), 2, 0)
        self.line_correo = QLineEdit()
        self.line_correo.setPlaceholderText("correo@ejemplo.com")
        layout_formulario.addWidget(self.line_correo, 2, 1)

        layout_botones = QHBoxLayout()
        layout_principal.addLayout(layout_botones)
        layout_botones.addStretch()

        self.button_guardar = QPushButton("Guardar")
        self.button_guardar.clicked.connect(self.on_guardar)
        layout_botones.addWidget(self.button_guardar)

        self.button_cancelar = QPushButton("Cancelar")
        self.button_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(self.button_cancelar)

    def _cargar_estudiante(self) -> bool:
        consulta = QSqlQuery(db=self.base_datos)
        if (
            not consulta.prepare(
                "SELECT nombres, apellidos, correo " "FROM Estudiante WHERE id_estudiante = 1"
            )
            or not consulta.exec()
        ):
            self._mostrar_error("No se pudieron cargar los datos del estudiante", consulta)
            return False

        if consulta.next():
            self.es_nuevo = False
            self.setWindowTitle("Editar datos del estudiante")
            self.button_guardar.setText("Guardar cambios")
            self.line_nombres.setText(str(consulta.value("nombres") or ""))
            self.line_apellidos.setText(str(consulta.value("apellidos") or ""))
            self.line_correo.setText(str(consulta.value("correo") or ""))
        else:
            self.setWindowTitle("Agregar datos del estudiante")

        return True

    def on_guardar(self):
        nombres = self.line_nombres.text().strip()
        apellidos = self.line_apellidos.text().strip()
        correo = self.line_correo.text().strip()

        if not nombres or not apellidos or not correo:
            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Los nombres, apellidos y correo son obligatorios.",
            )
            return
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", correo):
            QMessageBox.warning(self, "Correo invalido", "Ingresa un correo valido.")
            return

        consulta = QSqlQuery(db=self.base_datos)
        if self.es_nuevo:
            sql = (
                "INSERT INTO Estudiante "
                "(id_estudiante, nombres, apellidos, correo) "
                "VALUES (1, :nombres, :apellidos, :correo)"
            )
        else:
            sql = (
                "UPDATE Estudiante "
                "SET nombres = :nombres, apellidos = :apellidos, correo = :correo "
                "WHERE id_estudiante = 1"
            )

        if not consulta.prepare(sql):
            self._mostrar_error("No se pudo preparar el guardado", consulta)
            return

        consulta.bindValue(":nombres", nombres)
        consulta.bindValue(":apellidos", apellidos)
        consulta.bindValue(":correo", correo)
        if not consulta.exec():
            self._mostrar_error("No se pudieron guardar los datos del estudiante", consulta)
            return
        if not self.es_nuevo and consulta.numRowsAffected() == 0:
            QMessageBox.warning(
                self,
                "Registro no encontrado",
                "El estudiante ya no existe. Cierra y vuelve a abrir este dialogo.",
            )
            return

        self.accept()

    def _mostrar_error(self, mensaje: str, consulta: QSqlQuery):
        error = consulta.lastError().text()
        LOGGER.error("%s: %s", mensaje, error)
        QMessageBox.warning(self, "Error", f"{mensaje}: {error}")
