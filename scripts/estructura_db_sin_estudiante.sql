PRAGMA foreign_keys = ON;

-- =========================================================
-- Catálogos / entidades independientes
-- =========================================================

CREATE TABLE IF NOT EXISTS Facultad (
    id_facultad INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT NOT NULL,
    siglas      TEXT NOT NULL DEFAULT '',
    descripcion TEXT,
    correo      TEXT
);

CREATE TABLE IF NOT EXISTS Profesor (
    id_profesor INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT NOT NULL,
    apellido    TEXT NOT NULL,
    correo      TEXT UNIQUE,
    telefono    TEXT
);

CREATE TABLE IF NOT EXISTS Asignatura (
    id_asignatura INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo        TEXT UNIQUE NOT NULL,
    nombre        TEXT NOT NULL,
    credito       REAL NOT NULL CHECK (credito >= 0)
);

CREATE TABLE IF NOT EXISTS TipoActividad (
    id_tipoactividad INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre           TEXT NOT NULL,
    siglas           TEXT,
    descripcion      TEXT,
    prioridad        TEXT CHECK (prioridad IN ('alta','media','baja'))
);

CREATE TABLE IF NOT EXISTS Carrera (
    id_carrera       INTEGER PRIMARY KEY AUTOINCREMENT,
    id_facultad      INTEGER,
    codigo           TEXT UNIQUE NOT NULL,
    nombre           TEXT NOT NULL,
    descripcion      TEXT,
    modalidad        TEXT,
    duracion         INTEGER CHECK (duracion IS NULL OR duracion > 0),
    titulacion       TEXT,
    plan_curricular  INTEGER,
    FOREIGN KEY (id_facultad) REFERENCES Facultad (id_facultad) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS HorasSemanales (
    id_horassemanales INTEGER PRIMARY KEY AUTOINCREMENT,
    id_asignatura     INTEGER UNIQUE NOT NULL,
    teoricas          REAL CHECK (teoricas IS NULL OR teoricas >= 0),
    practicas         REAL CHECK (practicas IS NULL OR practicas >= 0),
    htd               REAL CHECK (htd IS NULL OR htd >= 0),
    hti               REAL CHECK (hti IS NULL OR hti >= 0),
    FOREIGN KEY (id_asignatura) REFERENCES Asignatura (id_asignatura) ON DELETE CASCADE
);

-- =========================================================
-- Historial académico del (único) estudiante
-- =========================================================

CREATE TABLE IF NOT EXISTS Inscripcion (
    id_inscripcion    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_asignatura     INTEGER NOT NULL,
    id_profesor       INTEGER,
    fecha_inscripcion TEXT CHECK (
                          fecha_inscripcion IS NULL
                          OR date(fecha_inscripcion) = fecha_inscripcion
                      ),
    semestre          TEXT CHECK (semestre IN ('1er Semestre','2do Semestre')),
    periodo           TEXT CHECK (periodo IN ('1er Periodo','2do. Periodo')),
    seccion           TEXT,
    puntaje           REAL CHECK (puntaje IS NULL OR puntaje >= 0),
    nota              REAL CHECK (nota IS NULL OR (nota >= 0 AND nota <= 100)),
    estado            TEXT NOT NULL DEFAULT 'Cursando'
                      CHECK (estado IN ('Cursando','Aprobado','Reprobado','Retirado')),
    FOREIGN KEY (id_asignatura) REFERENCES Asignatura (id_asignatura) ON DELETE CASCADE,
    FOREIGN KEY (id_profesor)   REFERENCES Profesor   (id_profesor)   ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS Actividad (
    id_actividad     INTEGER PRIMARY KEY AUTOINCREMENT,
    id_inscripcion   INTEGER NOT NULL,
    id_tipoactividad INTEGER NOT NULL,
    titulo           TEXT NOT NULL,
    descripcion      TEXT,
    fecha_inicio     TEXT CHECK (
                        fecha_inicio IS NULL
                        OR date(fecha_inicio) = fecha_inicio
                     ),
    fecha_entrega    TEXT CHECK (
                        fecha_entrega IS NULL
                        OR date(fecha_entrega) = fecha_entrega
                     ),
    dias_desarrollo  INTEGER CHECK (dias_desarrollo IS NULL OR dias_desarrollo >= 0),
    puntaje          REAL CHECK (puntaje IS NULL OR puntaje >= 0),
    estado           TEXT NOT NULL DEFAULT 'Pendiente'
                     CHECK (estado IN ('Pendiente','Entregada','Calificada','No Entregada')),
    CHECK (
        fecha_inicio IS NULL
        OR fecha_entrega IS NULL
        OR fecha_entrega >= fecha_inicio
    ),
    FOREIGN KEY (id_inscripcion)   REFERENCES Inscripcion   (id_inscripcion)   ON DELETE CASCADE,
    FOREIGN KEY (id_tipoactividad) REFERENCES TipoActividad (id_tipoactividad) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Matricula (
    id_matricula      INTEGER PRIMARY KEY AUTOINCREMENT,
    id_carrera        INTEGER NOT NULL,
    ano_matriculacion INTEGER CHECK (
                          ano_matriculacion IS NULL
                          OR ano_matriculacion > 0
                      ),
    plan              TEXT,
    FOREIGN KEY (id_carrera) REFERENCES Carrera (id_carrera) ON DELETE CASCADE
);

-- =========================================================
-- Calendarios (por facultad)
-- =========================================================

CREATE TABLE IF NOT EXISTS Calendario_Academico (
    id_calendario     INTEGER PRIMARY KEY AUTOINCREMENT,
    id_facultad       INTEGER NOT NULL,
    periodo_academico TEXT NOT NULL,
    actividad         TEXT NOT NULL,
    detalle           TEXT,
    fecha_inicio      TEXT NOT NULL,
    fecha_fin         TEXT,
    hora              TEXT,
    texto_original    TEXT,
    FOREIGN KEY (id_facultad) REFERENCES Facultad (id_facultad) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Calendario_Institucional (
    id_evento      INTEGER PRIMARY KEY AUTOINCREMENT,
    id_facultad    INTEGER NOT NULL,
    fecha_inicio   TEXT NOT NULL,
    fecha_fin      TEXT,
    descripcion    TEXT NOT NULL,
    tipo_evento    TEXT NOT NULL,
    es_fijo        INTEGER NOT NULL DEFAULT 0 CHECK (es_fijo IN (0,1)),
    estado         TEXT NOT NULL DEFAULT 'Activo',
    observaciones  TEXT,
    fecha_registro TEXT,
    FOREIGN KEY (id_facultad) REFERENCES Facultad (id_facultad) ON DELETE CASCADE
);

-- =========================================================
-- Plan de estudios
-- =========================================================

CREATE TABLE IF NOT EXISTS Malla_Curricular (
    id_carrera    INTEGER NOT NULL,
    id_asignatura INTEGER NOT NULL,
    PRIMARY KEY (id_carrera, id_asignatura),
    FOREIGN KEY (id_carrera)    REFERENCES Carrera    (id_carrera)    ON DELETE CASCADE,
    FOREIGN KEY (id_asignatura) REFERENCES Asignatura (id_asignatura) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Prerequisito (
    id_asignatura   INTEGER NOT NULL,
    id_prerequisito INTEGER NOT NULL,
    PRIMARY KEY (id_asignatura, id_prerequisito),
    FOREIGN KEY (id_asignatura)   REFERENCES Asignatura (id_asignatura) ON DELETE CASCADE,
    FOREIGN KEY (id_prerequisito) REFERENCES Asignatura (id_asignatura) ON DELETE CASCADE,
    CHECK (id_asignatura <> id_prerequisito)
);

-- =========================================================
-- Índices
-- =========================================================

-- Unicidad del historial de matrícula (ya sin estudiante)
CREATE UNIQUE INDEX IF NOT EXISTS uq_matricula_historial ON Matricula (
    id_carrera,
    COALESCE(ano_matriculacion, -1),
    COALESCE(plan, '')
);

-- Unicidad de inscripción por asignatura/periodo (ya sin estudiante)
CREATE UNIQUE INDEX IF NOT EXISTS uq_inscripcion_periodo ON Inscripcion (
    id_asignatura,
    COALESCE(semestre, ''),
    COALESCE(periodo, ''),
    COALESCE(seccion, '')
);

CREATE INDEX IF NOT EXISTS idx_carrera_facultad        ON Carrera         (id_facultad);
CREATE INDEX IF NOT EXISTS idx_horas_asignatura        ON HorasSemanales   (id_asignatura);
CREATE INDEX IF NOT EXISTS idx_inscripcion_asignatura  ON Inscripcion      (id_asignatura);
CREATE INDEX IF NOT EXISTS idx_inscripcion_profesor    ON Inscripcion      (id_profesor);
CREATE INDEX IF NOT EXISTS idx_inscripcion_estado      ON Inscripcion      (estado);
CREATE INDEX IF NOT EXISTS idx_actividad_inscripcion   ON Actividad        (id_inscripcion);
CREATE INDEX IF NOT EXISTS idx_actividad_tipo          ON Actividad        (id_tipoactividad);
CREATE INDEX IF NOT EXISTS idx_actividad_fecha_entrega ON Actividad        (fecha_entrega);
CREATE INDEX IF NOT EXISTS idx_matricula_carrera       ON Matricula        (id_carrera);
CREATE INDEX IF NOT EXISTS idx_malla_asignatura        ON Malla_Curricular (id_asignatura);
CREATE INDEX IF NOT EXISTS idx_prereq_asignatura       ON Prerequisito     (id_asignatura);
CREATE INDEX IF NOT EXISTS idx_prereq_prerequisito     ON Prerequisito     (id_prerequisito);