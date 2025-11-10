"""
mysql_connection.py
Módulo de conexión a MySQL


Proporciona funciones reutilizables para conectarse a una base de datos MySQL.
"""

import mysql.connector
from mysql.connector import Error

# 🔹 Configuración centralizada de conexión
CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",  # <--- Aquí colocas tu contraseña de MySQL
    "database": "labsphere"  # <--- Aquí el nombre de tu base de datos
}


def conectar_mysql():
    """
    Establece conexión con una base de datos MySQL usando la configuración global.
    Retorna el objeto de conexión y cursor si la conexión es exitosa.

    Retorna:
        tuple: (conexion, cursor) si es exitosa
        tuple: (None, None) si ocurre un error
    """
    try:
        conn = mysql.connector.connect(**CONFIG)

        if conn.is_connected():
            cursor = conn.cursor()
            print(f"✅ Conectado a MySQL ({CONFIG['database']}) en {CONFIG['host']}")
            return conn, cursor

    except Error as e:
        print(f"❌ Error de conexión a MySQL: {e}")
        return None, None
