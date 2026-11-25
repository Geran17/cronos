import sys
from utilidades.configuraciones import LOGGER, insercion_datos_iniciales, BASE_DATOS_CRONO
from PySide6.QtWidgets import QApplication
from interfaz.pyside6.mainWindow import MainWindow


def main():
    # insertamos los datos iniciales a la base de datos
    # insercion_datos_iniciales()

    # arrancamos la aplicacion principal
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
