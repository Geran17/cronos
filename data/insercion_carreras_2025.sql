INSERT
OR IGNORE INTO Facultad (nombre, siglas, descripcion, correo)
SELECT
    'Facultad de Ciencias Exactas y Naturales',
    'FACEN',
    'Facultad de la Universidad Nacional de Asunción dedicada a la formación de profesionales en ciencias básicas (Física, Química, Biología, Matemática, Estadística, Geología, Ciencias del Ambiente y afines), así como a la investigación científica y la extensión universitaria.',
    'info@facen.una.py'
WHERE
    NOT EXISTS (
        SELECT
            1
        FROM
            Facultad
        WHERE
            siglas = 'FACEN'
    );

-- Se asume que la facultad tiene id_facultad = 1 (FACEN)
INSERT
OR IGNORE INTO Carrera (
    id_facultad,
    codigo,
    nombre,
    modalidad,
    plan_curricular
)
VALUES
    (
        1,
        'BIO-2025',
        'Licenciatura en Ciencias Mención Biología',
        'Presencial',
        2025
    ),
    (
        1,
        'BIOTEC-2025',
        'Licenciatura en Biotecnología',
        'Presencial',
        2025
    ),
    (
        1,
        'FIS-2025',
        'Licenciatura en Ciencias Mención Física',
        'Presencial',
        2025
    ),
    (
        1,
        'FIS-MED-2025',
        'Licenciatura en Física Médica',
        'Presencial',
        2025
    ),
    (
        1,
        'RAD-2025',
        'Licenciatura en Radiología e Imagenología',
        'Presencial',
        2025
    ),
    (
        1,
        'GEO-2025',
        'Licenciatura en Ciencias Mención Geología',
        'Presencial',
        2025
    ),
    (
        1,
        'MAT-EST-2025',
        'Licenciatura en Ciencias Mención Matemática Estadística',
        'Presencial',
        2025
    ),
    (
        1,
        'MAT-PURA-2025',
        'Licenciatura en Ciencias Mención Matemática Pura',
        'Presencial',
        2025
    ),
    (
        1,
        'QUIM-2025',
        'Licenciatura en Ciencias Mención Química',
        'Presencial',
        2025
    ),
    (
        1,
        'TEC-PROD-2025',
        'Licenciatura en Tecnología de Producción',
        'Presencial',
        2025
    ),
    (
        1,
        'LOG-2025',
        'Licenciatura en Logística y Gestión del Transporte',
        'Presencial',
        2025
    ),
    (
        1,
        'EDU-CS-BAS-2025',
        'Licenciatura en Educación de Ciencias Básicas y sus Tecnologías',
        'Presencial',
        2025
    ),
    (
        1,
        'EDU-MAT-2025',
        'Licenciatura en Educación Matemática',
        'Presencial',
        2025
    );