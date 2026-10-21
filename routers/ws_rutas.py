from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
import asyncio
from ws_manager import manager
from services import db_services
from models.schemas import DemoRequest
from datetime import datetime
import json

router = APIRouter(tags=["WebSocket y DEMO"])

# Control de simultaneidad y cancelación por vehículo (Punto 9 de la rúbrica)
demos_activas: dict[int, asyncio.Task] = {}

@router.websocket("/ws/vehiculo/{id_vehiculo}")
async def websocket_endpoint(websocket: WebSocket, id_vehiculo: int):
    await manager.connect(websocket, id_vehiculo)
    try:
        estado_actual = db_services.ejecutar_sp_lectura('sp_obtener_estado', (id_vehiculo,))
        mensaje_inicial = {
            "evento": "ESTADO_INICIAL",
            "id_vehiculo": id_vehiculo,
            "estado": estado_actual[0] if estado_actual else None,
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(mensaje_inicial, default=str))
        
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, id_vehiculo)

@router.post("/api/vehiculos/{id_vehiculo}/demo", status_code=202)
async def iniciar_demo(id_vehiculo: int, req: DemoRequest):
    """Inicia la secuencia DEMO validando que no haya otra activa en el mismo vehículo."""
    if id_vehiculo in demos_activas and not demos_activas[id_vehiculo].done():
        raise HTTPException(status_code=409, detail="Ya hay una DEMO en ejecución para este vehículo.")

    movimientos = db_services.obtener_movimientos_demo(req.id_demo)
    if not movimientos:
        raise HTTPException(status_code=404, detail="La DEMO no existe o no tiene movimientos.")

    tarea = asyncio.create_task(ejecutar_secuencia_demo(id_vehiculo, movimientos))
    demos_activas[id_vehiculo] = tarea
    return {"mensaje": "DEMO iniciada en segundo plano vía WebSocket."}

@router.post("/api/vehiculos/{id_vehiculo}/demo/cancelar")
async def cancelar_demo(id_vehiculo: int):
    """Cancela una DEMO en ejecución y avisa por WSS."""
    tarea = demos_activas.get(id_vehiculo)
    if not tarea or tarea.done():
        raise HTTPException(status_code=400, detail="No hay ninguna DEMO activa para cancelar.")
    
    tarea.cancel()
    return {"mensaje": "Solicitud de cancelación de DEMO enviada."}

async def ejecutar_secuencia_demo(id_vehiculo: int, movimientos: list):
    try:
        await manager.broadcast_to_vehiculo(id_vehiculo, {"evento": "INICIO_DEMO", "timestamp": str(datetime.now())})
        
        for mov in movimientos:
            db_services.actualizar_estado_simple(id_vehiculo, mov['id_comando'])
            
            await manager.broadcast_to_vehiculo(id_vehiculo, {
                "evento": "MOVIMIENTO_DEMO",
                "orden": mov['orden'],
                "comando": mov.get('comando', mov.get('nombre')),
                "duracion_ms": mov['duracion_ms'],
                "pausa_ms": mov['pausa_ms']
            })
            
            tiempo_espera = (mov['duracion_ms'] + mov['pausa_ms']) / 1000.0
            await asyncio.sleep(tiempo_espera)
            
        await manager.broadcast_to_vehiculo(id_vehiculo, {"evento": "FIN_DEMO", "timestamp": str(datetime.now())})
    except asyncio.CancelledError:
        await manager.broadcast_to_vehiculo(id_vehiculo, {"evento": "DEMO_CANCELADA", "timestamp": str(datetime.now())})
    finally:
        demos_activas.pop(id_vehiculo, None)