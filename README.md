# Cronos

Cronos es una aplicación de escritorio para organizar información académica
universitaria. Permite administrar facultades, carreras, profesores,
asignaturas, tipos de actividades, prerrequisitos y mallas curriculares,
además de gestionar información del estudiante, matrículas e inscripciones.
El color elegido para cada tipo de actividad se guarda en `crono.ini`.

La interfaz está desarrollada con PySide6 y los datos se almacenan en SQLite.

## Requisitos

- Python 3.14, según la versión declarada en `Pipfile`.
- Pipenv.

## Instalación y ejecución

Desde la raíz del repositorio:

```bash
pipenv sync --dev
pipenv run python src/cronos.py
```

La aplicación crea su configuración y base de datos en el directorio de
configuración del usuario:

- Linux: `~/.config/cronos`
- macOS: `~/Library/Application Support/cronos`
- Windows: `%APPDATA%\cronos`

## Pruebas

```bash
pipenv run pytest
```

## Estructura del proyecto

- `src/interfaz/pyside6/`: ventanas y componentes de la interfaz gráfica.
- `src/nucleo/`: modelos de datos, acceso a SQLite y servicios.
- `src/utilidades/`: configuración y registro de eventos.
- `scripts/`: esquemas SQL de la base de datos.
- `data/`: scripts SQL con datos académicos iniciales.
- `tests/`: pruebas automatizadas.
