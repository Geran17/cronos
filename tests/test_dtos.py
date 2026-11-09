import pytest

from nucleo.dtos import (
    ActividadDTO,
    AsignaturaDTO,
    CalendarioAcademicoDTO,
    CalendarioInstitucionalDTO,
    CarreraDTO,
    EstudianteDTO,
    Facultad,
    HorasSemanalesDTO,
    InscripcionDTO,
    MatriculaDTO,
    MallaCurricularDTO,
    PrerequisitoDTO,
    ProfesorDTO,
    TipoActividadDTO,
)


DTO_CASES = [
    (
        EstudianteDTO,
        ("id_estudiante", "nombres", "apellidos", "correo"),
        (1, "Ana", "Pérez", "ana@example.com"),
    ),
    (
        Facultad,
        ("id_facultad", "nombre", "siglas", "descripcion", "correo"),
        (2, "Ingeniería", "ING", "Facultad de Ingeniería", "ing@example.com"),
    ),
    (
        ProfesorDTO,
        ("id_profesor", "nombre", "apellido", "correo", "telefono"),
        (3, "Luis", "García", "luis@example.com", "555-0100"),
    ),
    (
        AsignaturaDTO,
        ("id_asignatura", "codigo", "nombre", "credito"),
        (4, "MAT101", "Matemática", 4.5),
    ),
    (
        TipoActividadDTO,
        ("id_tipoactividad", "nombre", "siglas", "descripcion", "prioridad"),
        (5, "Examen", "EX", "Evaluación parcial", "alta"),
    ),
    (
        CarreraDTO,
        (
            "id_carrera",
            "id_facultad",
            "codigo",
            "nombre",
            "descripcion",
            "modalidad",
            "duracion",
            "titulacion",
            "plan_curricular",
        ),
        (6, 2, "SIS", "Sistemas", "Carrera de sistemas", "Presencial", 4, "Ingeniero", 2025),
    ),
    (
        HorasSemanalesDTO,
        ("id_horassemanales", "id_asignatura", "teoricas", "practicas", "htd", "hti"),
        (7, 4, 3.0, 2.0, 1.5, 2.5),
    ),
    (
        InscripcionDTO,
        (
            "id_inscripcion",
            "id_asignatura",
            "id_profesor",
            "fecha_inscripcion",
            "semestre",
            "periodo",
            "seccion",
            "puntaje",
            "nota",
            "estado",
        ),
        (8, 4, 3, "2025-03-01", "1er Semestre", "1er Periodo", "A", 90.0, 85.5, "Aprobado"),
    ),
    (
        ActividadDTO,
        (
            "id_actividad",
            "id_inscripcion",
            "id_tipoactividad",
            "titulo",
            "descripcion",
            "fecha_inicio",
            "fecha_limite",
            "fecha_entrega",
            "dias_desarrollo",
            "puntaje",
            "estado",
        ),
        (
            9,
            8,
            5,
            "Proyecto",
            "Proyecto final",
            "2025-03-01",
            "2025-03-15",
            "2025-03-14",
            14,
            95.0,
            "Calificada",
        ),
    ),
    (
        MatriculaDTO,
        ("id_matricula", "id_carrera", "ano_matriculacion", "plan"),
        (10, 6, 2025, "Plan A"),
    ),
    (
        CalendarioAcademicoDTO,
        (
            "id_calendario",
            "id_facultad",
            "periodo_academico",
            "actividad",
            "detalle",
            "fecha_inicio",
            "fecha_fin",
            "hora",
            "texto_original",
        ),
        (
            11,
            2,
            "2025-1",
            "Inicio de clases",
            "Primer día de clases",
            "2025-03-10",
            "2025-03-10",
            "08:00",
            "Inicio de clases 2025",
        ),
    ),
    (
        CalendarioInstitucionalDTO,
        (
            "id_evento",
            "id_facultad",
            "fecha_inicio",
            "fecha_fin",
            "descripcion",
            "tipo_evento",
            "es_fijo",
            "estado",
            "observaciones",
            "fecha_registro",
        ),
        (
            12,
            2,
            "2025-05-01",
            "2025-05-01",
            "Feriado",
            "Institucional",
            1,
            "Activo",
            "Sin actividades",
            "2025-01-15",
        ),
    ),
    (
        MallaCurricularDTO,
        ("id_carrera", "id_asignatura"),
        (6, 4),
    ),
    (
        PrerequisitoDTO,
        ("id_asignatura", "id_prerequisito"),
        (4, 2),
    ),
]


@pytest.mark.parametrize(("dto_type", "field_names", "values"), DTO_CASES)
def test_dto_serialization_matches_schema_fields(dto_type, field_names, values):
    dto = dto_type(**dict(zip(field_names, values, strict=True)))
    expected_dict = dict(zip(field_names, values, strict=True))

    assert dto.to_dict == expected_dict
    assert dto.to_tuple == values


DEFAULT_OVERRIDES = {
    InscripcionDTO: {"estado": "Cursando"},
    ActividadDTO: {"estado": "Pendiente"},
    CalendarioInstitucionalDTO: {"es_fijo": 0, "estado": "Activo"},
    MallaCurricularDTO: {"id_asignatura": 0},
    PrerequisitoDTO: {"id_prerequisito": 0},
}


@pytest.mark.parametrize(("dto_type", "field_names", "values"), DTO_CASES)
def test_dto_defaults_are_serialized(dto_type, field_names, values):
    dto = dto_type()
    expected_defaults = {
        field_name: 0 if field_name == field_names[0] else None
        for field_name in field_names
    }
    expected_defaults.update(DEFAULT_OVERRIDES.get(dto_type, {}))

    assert dto.to_dict == expected_defaults
    assert dto.to_tuple == tuple(expected_defaults.values())
    assert len(dto.to_tuple) == len(values)
