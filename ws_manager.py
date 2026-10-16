from fastapi import WebSocket
from typing import Dict, List
import json

class ConnectionManager:
    def __init__(self):
        # Diccionario: { id_vehiculo: [WebSocket, WebSocket, ...] }
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, id_vehiculo: int):
        await websocket.accept()
        if id_vehiculo not in self.active_connections:
            self.active_connections[id_vehiculo] = []
        self.active_connections[id_vehiculo].append(websocket)

    def disconnect(self, websocket: WebSocket, id_vehiculo: int):
        if id_vehiculo in self.active_connections:
            self.active_connections[id_vehiculo].remove(websocket)

    async def broadcast_to_vehiculo(self, id_vehiculo: int, message: dict):
        if id_vehiculo in self.active_connections:
            for connection in self.active_connections[id_vehiculo]:
                await connection.send_text(json.dumps(message))

manager = ConnectionManager()