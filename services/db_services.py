from database import get_db_connection

def obtener_historial_limitado(id_vehiculo: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.callproc('sp_obtener_historial', [id_vehiculo])
        resultados = []
        for result in cursor.stored_results():
            resultados.extend(result.fetchall())
        # Regla de negocio: Devolver únicamente los 10 más recientes
        return resultados[:10]
    finally:
        cursor.close()
        conn.close()

def procesar_movimiento_individual(id_vehiculo: int, id_comando: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Transacción atómica
        conn.start_transaction()
        # Actualiza el estado (conectado = True para simular la petición web)
        cursor.callproc('sp_actualizar_estado', [id_vehiculo, id_comando, True])
        # Registra en el historial
        cursor.callproc('sp_registrar_historial', [id_vehiculo, id_comando, 'API_POST'])
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def obtener_movimientos_demo(id_demo: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.callproc('sp_obtener_movimientos_demo', [id_demo])
        resultados = []
        for result in cursor.stored_results():
            resultados.extend(result.fetchall())
        return resultados
    finally:
        cursor.close()
        conn.close()

def actualizar_estado_simple(id_vehiculo: int, id_comando: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.callproc('sp_actualizar_estado', [id_vehiculo, id_comando, True])
        conn.commit()
    finally:
        cursor.close()
        conn.close()

# Nota: Para completar la práctica debes añadir métodos similares 
# para los SP de CRUD restantes (sp_crear_vehiculo, etc.)