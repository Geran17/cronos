import pytest

from nucleo.daos import (
    ActividadDAO,
    AsignaturaDAO,
    CalendarioAcademicoDAO,
    CalendarioInstitucionalDAO,
    CarreraDAO,
    EstudianteDAO,
    FacultadDAO,
    HorasSemanalesDAO,
    InscripcionDAO,
    MatriculaDAO,
    MallaCurricularDAO,
    PrerequisitoDAO,
    ProfesorDAO,
    TipoActividadDAO,
)
from nucleo.dtos import (
    ActividadDTO,
    AsignaturaDTO,
    CalendarioAcademicoDTO,
    CalendarioInstitucionalDTO,
    CarreraDTO,
    EstudianteDTO,
    Facultad as FacultadDTO,
    HorasSemanalesDTO,
    InscripcionDTO,
    MatriculaDTO,
    MallaCurricularDTO,
    PrerequisitoDTO,
    ProfesorDTO,
    TipoActividadDTO,
)
from nucleo.services import (
    Actividad,
    Asignatura,
    CalendarioAcademico,
    CalendarioInstitucional,
    Carrera,
    Estudiante,
    Facultad,
    HorasSemanales,
    Inscripcion,
    Matricula,
    MallaCurricular,
    Prerequisito,
    Profesor,
    TipoActividad,
)


SERVICE_CASES = [
    (Estudiante, EstudianteDTO, EstudianteDAO),
    (Facultad, FacultadDTO, FacultadDAO),
    (Profesor, ProfesorDTO, ProfesorDAO),
    (Asignatura, AsignaturaDTO, AsignaturaDAO),
    (TipoActividad, TipoActividadDTO, TipoActividadDAO),
    (Carrera, CarreraDTO, CarreraDAO),
    (HorasSemanales, HorasSemanalesDTO, HorasSemanalesDAO),
    (Inscripcion, InscripcionDTO, InscripcionDAO),
    (Actividad, ActividadDTO, ActividadDAO),
    (Matricula, MatriculaDTO, MatriculaDAO),
    (CalendarioAcademico, CalendarioAcademicoDTO, CalendarioAcademicoDAO),
    (CalendarioInstitucional, CalendarioInstitucionalDTO, CalendarioInstitucionalDAO),
    (MallaCurricular, MallaCurricularDTO, MallaCurricularDAO),
    (Prerequisito, PrerequisitoDTO, PrerequisitoDAO),
]


@pytest.mark.parametrize(("service_type", "dto_type", "dao_type"), SERVICE_CASES)
def test_servicio_hereda_de_su_dto_y_delega_operaciones(
    service_type, dto_type, dao_type, monkeypatch
):
    servicio = service_type()
    assert isinstance(servicio, dto_type)

    for operacion in ("insertar", "existe", "instancie", "eliminar", "actualizar"):
        resultado_esperado = 42 if operacion == "insertar" else True
        llamadas = []

        def fake(dao, dto):
            llamadas.append(dto)
            return resultado_esperado

        monkeypatch.setattr(dao_type, operacion, fake)

        assert getattr(servicio, operacion)() == resultado_esperado
        assert llamadas == [servicio]
