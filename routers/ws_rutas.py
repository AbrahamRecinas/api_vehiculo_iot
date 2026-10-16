from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from ws_manager import manager
from services import db_services
from models.schemas import DemoRequest
from datetime import datetime

router = APIRouter(tags=["WebSocket y DEMO"])

@router.websocket("/ws/vehiculo/{id_vehiculo}")
async def websocket_endpoint(websocket: WebSocket, id_vehiculo: int):
    """Mantiene la conexión WebSocket abierta para recibir eventos del vehículo."""
    await manager.connect(websocket, id_vehiculo)
    try:
        while True:
            # Mantiene la conexión viva recibiendo mensajes vacíos (ping/pong manual)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, id_vehiculo)

@router.post("/api/vehiculos/{id_vehiculo}/demo", status_code=202)
async def iniciar_demo(id_vehiculo: int, req: DemoRequest):
    """Inicia la secuencia DEMO por WebSocket sin guardarla en el historial."""
    movimientos = db_services.obtener_movimientos_demo(req.id_demo)
    
    if not movimientos:
        return {"error": "La DEMO no existe o no tiene movimientos."}

    # Tarea en segundo plano para no bloquear el endpoint HTTP
    asyncio.create_task(ejecutar_secuencia_demo(id_vehiculo, movimientos))
    return {"mensaje": "DEMO iniciada en segundo plano vía WebSocket."}

async def ejecutar_secuencia_demo(id_vehiculo: int, movimientos: list):
    await manager.broadcast_to_vehiculo(id_vehiculo, {"evento": "INICIO_DEMO", "timestamp": str(datetime.now())})
    
    for mov in movimientos:
        # 1. Actualiza el estado (sin registrar en el historial)
        db_services.actualizar_estado_simple(id_vehiculo, mov['id_comando'])
        
        # 2. Notifica el movimiento actual
        await manager.broadcast_to_vehiculo(id_vehiculo, {
            "evento": "MOVIMIENTO_DEMO",
            "orden": mov['orden'],
            "comando": mov['comando'],
            "duracion_ms": mov['duracion_ms'],
            "pausa_ms": mov['pausa_ms']
        })
        
        # 3. Espera la duración del movimiento + la pausa definida
        tiempo_espera_segundos = (mov['duracion_ms'] + mov['pausa_ms']) / 1000.0
        await asyncio.sleep(tiempo_espera_segundos)
        
    await manager.broadcast_to_vehiculo(id_vehiculo, {"evento": "FIN_DEMO", "timestamp": str(datetime.now())})