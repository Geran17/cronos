from dataclasses import dataclass, field, asdict, astuple
from typing import Optional, Dict, Tuple


@dataclass(order=True, kw_only=True, slots=True)
class EstudianteDTO:
    id_estudiante: Optional[int] = field(init=True, default=0)
    nombres: Optional[str] = field(init=True, default=None)
    apellidos: Optional[str] = field(init=True, default=None)
    correo: Optional[str] = field(init=True, default=None)

    @property
    def to_dict(self) -> Dict:
        return asdict(self)

    @property
    def to_tuple(self) -> Tuple:
        return astuple(self)


@dataclass(order=True, kw_only=True, slots=True)
class Facultad:
    id_facultad: Optional[int] = field(init=True, default=0)
    nombre: Optional[str] = field(init=True, default=None)
    siglas: Optional[str] = field(init=True, default=None)
    descripcion: Optional[str] = field(init=True, default=None)
    correo: Optional[str] = field(init=True, default=None)

    @property
    def to_dict(self) -> Dict:
        return asdict(self)

    @property
    def to_tuple(self) -> Tuple:
        return astuple(self)


@dataclass(order=True, kw_only=True, slots=True)
class ProfesorDTO:
    id_profesor: Optional[int] = field(init=True, default=0)
    nombre: Optional[str] = field(init=True, default=None)
    apellido: Optional[str] = field(init=True, default=None)
    correo: Optional[str] = field(init=True, default=None)
    telefono: Optional[str] = field(init=True, default=None)

    @property
    def to_dict(self) -> Dict:
        return asdict(self)

    @property
    def to_tuple(self) -> Tuple:
        return astuple(self)


@dataclass(order=True, kw_only=True, slots=True)
class AsignaturaDTO:
    id_asignatura: Optional[int] = field(init=True, default=0)
    codigo: Optional[str] = field(init=True, default=None)
    nombre: Optional[str] = field(init=True, default=None)
    credito: Optional[float] = field(init=True, default=None)

    @property
    def to_dict(self) -> Dict:
        return asdict(self)

    @property
    def to_tuple(self) -> Tuple:
        return astuple(self)


@dataclass(order=True, kw_only=True, slots=True)
class TipoActividadDTO:
    id_tipoactividad: Optional[int] = field(init=True, default=0)
    nombre: Optional[str] = field(init=True, default=None)
    siglas: Optional[str] = field(init=True, default=None)
    descripcion: Optional[str] = field(init=True, default=None)
    prioridad: Optional[str] = field(init=True, default=None)

    @property
    def to_dict(self) -> Dict:
        return asdict(self)

    @property
    def to_tuple(self) -> Tuple:
        return astuple(self)


@dataclass(order=True, kw_only=True, slots=True)
class CarreraDTO:
    id_carrera: Optional[int] = field(init=True, default=0)
    id_facultad: Optional[int] = field(init=True, default=None)
    codigo: Optional[str] = field(init=True, default=None)
    nombre: Optional[str] = field(init=True, default=None)
    descripcion: Optional[str] = field(init=True, default=None)
    modalidad: Optional[str] = field(init=True, default=None)
    duracion: Optional[int] = field(init=True, default=None)
    titulacion: Optional[str] = field(init=True, default=None)
    plan_curricular: Optional[int] = field(init=True, default=None)

    @property
    def to_dict(self) -> Dict:
        return asdict(self)

    @property
    def to_tuple(self) -> Tuple:
        return astuple(self)


@dataclass(order=True, kw_only=True, slots=True)
class HorasSemanalesDTO:
    id_horassemanales: Optional[int] = field(init=True, default=0)
    id_asignatura: Optional[int] = field(init=True, default=None)
    teoricas: Optional[float] = field(init=True, default=None)
    practicas: Optional[float] = field(init=True, default=None)
    htd: Optional[float] = field(init=True, default=None)
    hti: Optional[float] = field(init=True, default=None)

    @property
    def to_dict(self) -> Dict:
        return asdict(self)

    @property
    def to_tuple(self) -> Tuple:
        return astuple(self)


@dataclass(order=True, kw_only=True, slots=True)
class InscripcionDTO:
    id_inscripcion: Optional[int] = field(init=True, default=0)
    id_asignatura: Optional[int] = field(init=True, default=None)
    id_profesor: Optional[int] = field(init=True, default=None)
    fecha_inscripcion: Optional[str] = field(init=True, default=None)
    semestre: Optional[str] = field(init=True, default=None)
    periodo: Optional[str] = field(init=True, default=None)
    seccion: Optional[str] = field(init=True, default=None)
    puntaje: Optional[float] = field(init=True, default=None)
    nota: Optional[float] = field(init=True, default=None)
    estado: Optional[str] = field(init=True, default="Cursando")

    @property
    def to_dict(self) -> Dict:
        return asdict(self)

    @property
    def to_tuple(self) -> Tuple:
        return astuple(self)


@dataclass(order=True, kw_only=True, slots=True)
class ActividadDTO:
    id_actividad: Optional[int] = field(init=True, default=0)
    id_inscripcion: Optional[int] = field(init=True, default=None)
    id_tipoactividad: Optional[int] = field(init=True, default=None)
    titulo: Optional[str] = field(init=True, default=None)
    descripcion: Optional[str] = field(init=True, default=None)
    fecha_inicio: Optional[str] = field(init=True, default=None)
    fecha_limite: Optional[str] = field(init=True, default=None)
    fecha_entrega: Optional[str] = field(init=True, default=None)
    dias_desarrollo: Optional[int] = field(init=True, default=None)
    puntaje: Optional[float] = field(init=True, default=None)
    estado: Optional[str] = field(init=True, default="Pendiente")

    @property
    def to_dict(self) -> Dict:
        return asdict(self)

    @property
    def to_tuple(self) -> Tuple:
        return astuple(self)


@dataclass(order=True, kw_only=True, slots=True)
class MatriculaDTO:
    id_matricula: Optional[int] = field(init=True, default=0)
    id_carrera: Optional[int] = field(init=True, default=None)
    ano_matriculacion: Optional[int] = field(init=True, default=None)
    plan: Optional[str] = field(init=True, default=None)

    @property
    def to_dict(self) -> Dict:
        return asdict(self)

    @property
    def to_tuple(self) -> Tuple:
        return astuple(self)


@dataclass(order=True, kw_only=True, slots=True)
class CalendarioAcademicoDTO:
    id_calendario: Optional[int] = field(init=True, default=0)
    id_facultad: Optional[int] = field(init=True, default=None)
    periodo_academico: Optional[str] = field(init=True, default=None)
    actividad: Optional[str] = field(init=True, default=None)
    detalle: Optional[str] = field(init=True, default=None)
    fecha_inicio: Optional[str] = field(init=True, default=None)
    fecha_fin: Optional[str] = field(init=True, default=None)
    hora: Optional[str] = field(init=True, default=None)
    texto_original: Optional[str] = field(init=True, default=None)

    @property
    def to_dict(self) -> Dict:
        return asdict(self)

    @property
    def to_tuple(self) -> Tuple:
        return astuple(self)


@dataclass(order=True, kw_only=True, slots=True)
class CalendarioInstitucionalDTO:
    id_evento: Optional[int] = field(init=True, default=0)
    id_facultad: Optional[int] = field(init=True, default=None)
    fecha_inicio: Optional[str] = field(init=True, default=None)
    fecha_fin: Optional[str] = field(init=True, default=None)
    descripcion: Optional[str] = field(init=True, default=None)
    tipo_evento: Optional[str] = field(init=True, default=None)
    es_fijo: Optional[int] = field(init=True, default=0)
    estado: Optional[str] = field(init=True, default="Activo")
    observaciones: Optional[str] = field(init=True, default=None)
    fecha_registro: Optional[str] = field(init=True, default=None)

    @property
    def to_dict(self) -> Dict:
        return asdict(self)

    @property
    def to_tuple(self) -> Tuple:
        return astuple(self)


@dataclass(order=True, kw_only=True, slots=True)
class MallaCurricularDTO:
    id_carrera: Optional[int] = field(init=True, default=0)
    id_asignatura: Optional[int] = field(init=True, default=0)

    @property
    def to_dict(self) -> Dict:
        return asdict(self)

    @property
    def to_tuple(self) -> Tuple:
        return astuple(self)


@dataclass(order=True, kw_only=True, slots=True)
class PrerequisitoDTO:
    id_asignatura: Optional[int] = field(init=True, default=0)
    id_prerequisito: Optional[int] = field(init=True, default=0)

    @property
    def to_dict(self) -> Dict:
        return asdict(self)

    @property
    def to_tuple(self) -> Tuple:
        return astuple(self)
