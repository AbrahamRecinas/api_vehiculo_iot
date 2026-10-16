from pydantic import BaseModel
from typing import Optional

# Vehículos
class VehiculoBase(BaseModel):
    nombre: str
    modelo: Optional[str] = None
    descripcion: Optional[str] = None
    microcontrolador: Optional[str] = None

class VehiculoUpdate(VehiculoBase):
    activo: bool

# Comandos
class ComandoBase(BaseModel):
    nombre: str
    codigo: int
    descripcion: Optional[str] = None

class ComandoUpdate(ComandoBase):
    activo: bool

# Demos
class DemoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class DemoUpdate(DemoBase):
    activo: bool

# Movimientos Demo
class MovimientoDemoBase(BaseModel):
    id_comando: int
    orden: int
    duracion_ms: int
    pausa_ms: int = 0

# (Conserva las clases MovimientoRequest y DemoRequest que ya tenías)
class MovimientoRequest(BaseModel):
    id_comando: int

class DemoRequest(BaseModel):
    id_demo: int