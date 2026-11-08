from nucleo.daos import *
from nucleo.dtos import *


class Estudiante(EstudianteDTO):

    def insertar(self) -> int | None:
        dao = EstudianteDAO()
        return dao.insertar(dto=self)

    def existe(self) -> bool:
        dao = EstudianteDAO()
        return dao.existe(dto=self)

    def instancie(self) -> bool:
        dao = EstudianteDAO()
        return dao.instancie(dto=self)

    def eliminar(self) -> bool:
        dao = EstudianteDAO()
        return dao.eliminar(dto=self)

    def actualizar(self) -> bool:
        dao = EstudianteDAO()
        return dao.actualizar(dto=self)
