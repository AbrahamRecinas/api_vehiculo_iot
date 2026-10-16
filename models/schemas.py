from pydantic import BaseModel

class MovimientoRequest(BaseModel):
    id_comando: int

class DemoRequest(BaseModel):
    id_demo: int