from typing import ClassVar

from nucleo.daos import (
    ActividadDAO,
    AsignaturaDAO,
    BaseDatosSQLite,
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


class _ServicioCRUD:
    __slots__ = ()

    dao_type: ClassVar[type[BaseDatosSQLite]]

    def insertar(self) -> int | None:
        return self.dao_type().insertar(dto=self)

    def existe(self) -> bool:
        return self.dao_type().existe(dto=self)

    def instancie(self) -> bool:
        return self.dao_type().instancie(dto=self)

    def eliminar(self) -> bool:
        return self.dao_type().eliminar(dto=self)

    def actualizar(self) -> bool:
        return self.dao_type().actualizar(dto=self)


class Estudiante(EstudianteDTO, _ServicioCRUD):
    dao_type = EstudianteDAO


class Facultad(FacultadDTO, _ServicioCRUD):
    dao_type = FacultadDAO


class Profesor(ProfesorDTO, _ServicioCRUD):
    dao_type = ProfesorDAO


class Asignatura(AsignaturaDTO, _ServicioCRUD):
    dao_type = AsignaturaDAO


class TipoActividad(TipoActividadDTO, _ServicioCRUD):
    dao_type = TipoActividadDAO


class Carrera(CarreraDTO, _ServicioCRUD):
    dao_type = CarreraDAO


class HorasSemanales(HorasSemanalesDTO, _ServicioCRUD):
    dao_type = HorasSemanalesDAO


class Inscripcion(InscripcionDTO, _ServicioCRUD):
    dao_type = InscripcionDAO


class Actividad(ActividadDTO, _ServicioCRUD):
    dao_type = ActividadDAO


class Matricula(MatriculaDTO, _ServicioCRUD):
    dao_type = MatriculaDAO


class CalendarioAcademico(CalendarioAcademicoDTO, _ServicioCRUD):
    dao_type = CalendarioAcademicoDAO


class CalendarioInstitucional(CalendarioInstitucionalDTO, _ServicioCRUD):
    dao_type = CalendarioInstitucionalDAO


class MallaCurricular(MallaCurricularDTO, _ServicioCRUD):
    dao_type = MallaCurricularDAO


class Prerequisito(PrerequisitoDTO, _ServicioCRUD):
    dao_type = PrerequisitoDAO
