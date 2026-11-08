from dataclasses import dataclass, field, asdict, astuple
from typing import Optional, Dict, Tuple
from utilidades.configuraciones import LOGGER


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


@dataclass
class Facultad:
    pass
