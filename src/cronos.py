from utilidades.configuraciones import LOGGER, insercion_datos_iniciales, BASE_DATOS_CRONO


def main():
    # iniciamos las configuraciones principales de la aplicacion
    # insertamos los datos iniciales a la base de datos
    insercion_datos_iniciales()


if __name__ == "__main__":
    main()
