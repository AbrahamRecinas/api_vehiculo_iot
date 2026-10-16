from fastapi import FastAPI
from routers import api_vehiculos, ws_rutas

app = FastAPI(
    title="API Vehículo IoT",
    description="API para la gestión de la Grúa RC IoT mediante Amazon RDS y WebSockets",
    version="1.0.0"
)

app.include_router(api_vehiculos.router)
app.include_router(ws_rutas.router)

# Ejecución: uvicorn main:app --reload