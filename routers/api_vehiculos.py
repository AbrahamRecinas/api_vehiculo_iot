from fastapi import APIRouter, HTTPException
from models.schemas import MovimientoRequest
from services import db_services
from ws_manager import manager
from datetime import datetime

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