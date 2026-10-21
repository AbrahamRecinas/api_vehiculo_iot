from fastapi import APIRouter, HTTPException
from models.schemas import MovimientoRequest
from services import db_services
from ws_manager import manager
from datetime import datetime
from models.schemas import (
    VehiculoBase, VehiculoUpdate, ComandoBase, ComandoUpdate, 
    DemoBase, DemoUpdate, MovimientoDemoBase
)

router = APIRouter(prefix="/api/vehiculos", tags=["Vehículos y Comandos"])

@router.get("/{id_vehiculo}/historial")
def obtener_historial(id_vehiculo: int):
    """Consulta el historial y devuelve COMO MÁXIMO los diez movimientos más recientes."""
    try:
        registros = db_services.obtener_historial_limitado(id_vehiculo)
        return {"id_vehiculo": id_vehiculo, "historial": registros}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{id_vehiculo}/movimiento", status_code=201)
async def registrar_movimiento(id_vehiculo: int, req: MovimientoRequest):
    """Ejecuta un movimiento individual guardándolo en la base de datos y notificando por WebSocket."""
    try:
        exito = db_services.procesar_movimiento_individual(id_vehiculo, req.id_comando)
        if exito:
            # Notificar vía WebSocket
            evento = {
                "tipo": "MOVIMIENTO_INDIVIDUAL",
                "id_vehiculo": id_vehiculo,
                "id_comando": req.id_comando,
                "timestamp": datetime.now().isoformat()
            }
            await manager.broadcast_to_vehiculo(id_vehiculo, evento)
            return {"mensaje": "Movimiento registrado y notificado exitosamente."}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error al registrar movimiento: Verifica que el comando pertenezca al vehículo.")

# ==========================================
# VEHÍCULOS (5 SPs)
# ==========================================
@router.get("/")
def obtener_vehiculos():
    return db_services.ejecutar_sp_lectura('sp_obtener_vehiculos')

@router.get("/{id_vehiculo}")
def obtener_vehiculo(id_vehiculo: int):
    resultado = db_services.ejecutar_sp_lectura('sp_obtener_vehiculo', (id_vehiculo,))
    if not resultado: raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return resultado[0]

@router.post("/", status_code=201)
def crear_vehiculo(req: VehiculoBase):
    nuevo_id = db_services.ejecutar_sp_escritura('sp_crear_vehiculo', 
        (req.nombre, req.modelo, req.descripcion, req.microcontrolador))
    return {"mensaje": "Vehículo creado", "id_vehiculo": nuevo_id}

@router.post("/{id_vehiculo}/actualizar")
def actualizar_vehiculo(id_vehiculo: int, req: VehiculoUpdate):
    db_services.ejecutar_sp_escritura('sp_actualizar_vehiculo', 
        (id_vehiculo, req.nombre, req.modelo, req.descripcion, req.microcontrolador, req.activo))
    return {"mensaje": "Vehículo actualizado"}

@router.post("/{id_vehiculo}/eliminar")
def eliminar_vehiculo(id_vehiculo: int):
    db_services.ejecutar_sp_escritura('sp_eliminar_vehiculo', (id_vehiculo,))
    return {"mensaje": "Vehículo eliminado"}

# ==========================================
# ESTADO (1 SP Extra - el de actualización ya está en POST individual)
# ==========================================
@router.get("/{id_vehiculo}/estado")
def obtener_estado(id_vehiculo: int):
    return db_services.ejecutar_sp_lectura('sp_obtener_estado', (id_vehiculo,))

# ==========================================
# COMANDOS (4 SPs)
# ==========================================
@router.get("/{id_vehiculo}/comandos")
def obtener_comandos(id_vehiculo: int):
    return db_services.ejecutar_sp_lectura('sp_obtener_comandos_vehiculo', (id_vehiculo,))

@router.post("/{id_vehiculo}/comandos", status_code=201)
def crear_comando(id_vehiculo: int, req: ComandoBase):
    nuevo_id = db_services.ejecutar_sp_escritura('sp_crear_comando', 
        (id_vehiculo, req.nombre, req.codigo, req.descripcion))
    return {"mensaje": "Comando creado", "id_comando": nuevo_id}

@router.post("/comandos/{id_comando}/actualizar")
def actualizar_comando(id_comando: int, req: ComandoUpdate):
    db_services.ejecutar_sp_escritura('sp_actualizar_comando', 
        (id_comando, req.nombre, req.codigo, req.descripcion, req.activo))
    return {"mensaje": "Comando actualizado"}

@router.post("/comandos/{id_comando}/eliminar")
def eliminar_comando(id_comando: int):
    db_services.ejecutar_sp_escritura('sp_eliminar_comando', (id_comando,))
    return {"mensaje": "Comando eliminado"}

# ==========================================
# DEMOS (4 SPs)
# ==========================================
@router.get("/{id_vehiculo}/demos")
def obtener_demos(id_vehiculo: int):
    return db_services.ejecutar_sp_lectura('sp_obtener_demos', (id_vehiculo,))

@router.post("/{id_vehiculo}/demos", status_code=201)
def crear_demo(id_vehiculo: int, req: DemoBase):
    nuevo_id = db_services.ejecutar_sp_escritura('sp_crear_demo', 
        (id_vehiculo, req.nombre, req.descripcion))
    return {"mensaje": "Demo creada", "id_demo": nuevo_id}

@router.post("/demos/{id_demo}/actualizar")
def actualizar_demo(id_demo: int, req: DemoUpdate):
    db_services.ejecutar_sp_escritura('sp_actualizar_demo', 
        (id_demo, req.nombre, req.descripcion, req.activo))
    return {"mensaje": "Demo actualizada"}

@router.post("/demos/{id_demo}/eliminar")
def eliminar_demo(id_demo: int):
    db_services.ejecutar_sp_escritura('sp_eliminar_demo', (id_demo,))
    return {"mensaje": "Demo eliminada"}

# ==========================================
# MOVIMIENTOS DEMO (4 SPs)
# ==========================================
@router.get("/demos/{id_demo}/movimientos")
def obtener_movimientos_demo_http(id_demo: int):
    return db_services.ejecutar_sp_lectura('sp_obtener_movimientos_demo', (id_demo,))

@router.post("/demos/{id_demo}/movimientos", status_code=201)
def agregar_movimiento_demo(id_demo: int, req: MovimientoDemoBase):
    db_services.ejecutar_sp_escritura('sp_agregar_movimiento_demo', 
        (id_demo, req.id_comando, req.orden, req.duracion_ms, req.pausa_ms))
    return {"mensaje": "Movimiento de demo agregado"}

@router.post("/movimientos_demo/{id_demo_movimiento}/actualizar")
def actualizar_movimiento_demo(id_demo_movimiento: int, req: MovimientoDemoBase):
    db_services.ejecutar_sp_escritura('sp_actualizar_movimiento_demo', 
        (id_demo_movimiento, req.id_comando, req.orden, req.duracion_ms, req.pausa_ms))
    return {"mensaje": "Movimiento de demo actualizado"}

@router.post("/movimientos_demo/{id_demo_movimiento}/eliminar")
def eliminar_movimiento_demo(id_demo_movimiento: int):
    db_services.ejecutar_sp_escritura('sp_eliminar_movimiento_demo', (id_demo_movimiento,))
    return {"mensaje": "Movimiento de demo eliminado"}