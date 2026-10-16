# API Grúa RC IoT - Práctica 2.5

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg)
![AWS RDS](https://img.shields.io/badge/AWS_RDS-Database-FF9900.svg)

Esta API RESTful fue desarrollada con **Python** y el framework **FastAPI**, aplicando principios de Programación Orientada a Objetos (POO). Su objetivo principal es la gestión, registro y transmisión en tiempo real de los comandos enviados a una **Grúa de Control Remoto (RC) IoT** de 12 canales (controlada por hardware ESP8266, registros 74HC595 y optoacopladores).

El sistema se conecta a una base de datos **MySQL** alojada en la nube mediante **Amazon RDS**, integrando una arquitectura basada en **21 procedimientos almacenados** para garantizar la seguridad e integridad de las transacciones.

---

## Requisitos Previos

Para ejecutar este proyecto en un entorno local, necesitas tener instalado:

* **Python 3.10** o superior.
* **Git** instalado en tu computadora.
* Credenciales de acceso a la instancia activa de **Amazon RDS** (base de datos `vehiculo_iot`).

---

## Instalación y Ejecución Local (Entorno de Desarrollo)

Sigue estos pasos para levantar el servidor en tu máquina local:

**1. Clonar este repositorio:**
```bash
git clone <tu-url-de-github>
cd api_vehiculo_iot
```

**2. Crear y activar el entorno virtual:**
```bash
python -m venv .venv

# En Windows (Símbolo del sistema o PowerShell):
.venv\Scripts\activate

# En macOS o Linux:
source .venv/bin/activate
```

**3. Instalar las dependencias:**
```bash
pip install -r requirements.txt
```

**4. Configurar las variables de entorno:**
Copia el archivo de ejemplo y renómbralo:
```bash
cp .env.example .env
```
Abre el archivo `.env` y reemplaza los valores genéricos con las credenciales reales de tu instancia de Amazon RDS.

> **Importante:** El archivo `.env` está excluido en el `.gitignore` por seguridad. **Nunca** subas tus credenciales o contraseñas de AWS a GitHub.

**5. Ejecutar el servidor local:**
```bash
uvicorn main:app --reload
```

---

## Documentación de Endpoints HTTP (Swagger UI)

Una vez que el servidor local esté corriendo, puedes explorar la documentación interactiva de la API, ver los modelos de datos y probar los endpoints (GET, POST, PUT, DELETE) directamente desde tu navegador:

 **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## Monitoreo en Tiempo Real (WebSockets)

Swagger UI no soporta pruebas de conexiones WebSockets de forma nativa. Para monitorear la telemetría y los comandos de la grúa en tiempo real, utiliza una herramienta como [Thunder Client](https://www.thunderclient.com/), Postman o cualquier cliente WebSocket.

**URL de Conexión WebSocket:** `ws://localhost:8000/ws/vehiculo/{id_vehiculo}`  
**Ejemplo de conexión:** `ws://localhost:8000/ws/vehiculo/1`

### Eventos Transmitidos por el Servidor

El servidor emitirá eventos JSON a todos los clientes conectados bajo diferentes escenarios:

#### 1. Movimiento Individual
Se emite automáticamente a todos los clientes que monitorean un vehículo cuando se registra con éxito una petición HTTP `POST` en el endpoint `/api/vehiculos/{id_vehiculo}/movimiento`.

```json
{
  "tipo": "MOVIMIENTO_INDIVIDUAL",
  "id_vehiculo": 1,
  "id_comando": 9,
  "timestamp": "2026-10-15T10:00:00.123456"
}
```

#### 2. Ejecución de Rutina DEMO
Al iniciar una secuencia automática enviando un `POST` a `/api/vehiculos/{id_vehiculo}/demo`, el servidor transmitirá la siguiente secuencia. Se respetarán estrictamente los tiempos de `duracion_ms` y `pausa_ms` configurados en la base de datos para la simulación física, y estos eventos automáticos **no** se guardarán en el historial general.

**Evento de Inicio:**
```json
{
  "evento": "INICIO_DEMO",
  "timestamp": "2026-10-15T10:01:00.123456"
}
```

**Mensaje por cada Movimiento** *(Transmitido secuencialmente según la rutina programada)*:
```json
{
  "evento": "MOVIMIENTO_DEMO",
  "orden": 1,
  "comando": "ELEVACION_GANCHO",
  "duracion_ms": 500,
  "pausa_ms": 200
}
```

**Evento de Finalización:**
```json
{
  "evento": "FIN_DEMO",
  "timestamp": "2026-10-15T10:01:10.123456"
}
```