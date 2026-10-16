from typing import Any, List, Dict
from database import get_db_connection

def ejecutar_sp_lectura(sp_name: str, params: tuple = ()) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.callproc(sp_name, params)
        resultados = []
        for result in cursor.stored_results():
            resultados.extend(result.fetchall())
        return resultados
    finally:
        cursor.close()
        conn.close()

def ejecutar_sp_escritura(sp_name: str, params: tuple = ()) -> Any:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.callproc(sp_name, params)
        inserted_id = None
        
        for result in cursor.stored_results():
            rows = result.fetchall()
            if rows:
                # Convertimos explícitamente a lista para evitar el error de Pylance
                primera_fila = list(rows[0])
                inserted_id = primera_fila[0]
                
        conn.commit()
        return inserted_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def obtener_historial_limitado(id_vehiculo: int) -> List[Dict[str, Any]]:
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

def procesar_movimiento_individual(id_vehiculo: int, id_comando: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Transacción atómica
        conn.start_transaction()
        
        # 1er SP: Actualizar estado
        cursor.callproc('sp_actualizar_estado', [id_vehiculo, id_comando, True])
        
        # Limpiamos los resultados remanentes del cursor
        for _ in cursor.stored_results():
            _.fetchall()
            
        # 2do SP: Registrar en historial
        cursor.callproc('sp_registrar_historial', [id_vehiculo, id_comando, 'API_POST'])
        
        # Limpieza final
        for _ in cursor.stored_results():
            _.fetchall()
            
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def obtener_movimientos_demo(id_demo: int) -> List[Dict[str, Any]]:
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

def actualizar_estado_simple(id_vehiculo: int, id_comando: int) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.callproc('sp_actualizar_estado', [id_vehiculo, id_comando, True])
        
        # Limpieza de seguridad
        for _ in cursor.stored_results():
            _.fetchall()
            
        conn.commit()
    finally:
        cursor.close()
        conn.close()