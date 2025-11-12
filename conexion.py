"""
mysql_connection.py
Módulo de conexión a MySQL

Proporciona funciones reutilizables para conectarse a una base de datos MySQL
y muestra visualmente si la conexión fue exitosa o no.
"""

import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import messagebox

# 🔹 Configuración centralizada de conexión
CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",       # <--- Cambia por tu contraseña de MySQL
    "database": "lenguajes"   # <--- Cambia por tu base de datos
}


def mostrar_alerta(titulo, mensaje, tipo="info"):
    """Muestra una alerta visual con Tkinter."""
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal
    if tipo == "info":
        messagebox.showinfo(titulo, mensaje)
    elif tipo == "error":
        messagebox.showerror(titulo, mensaje)
    else:
        messagebox.showwarning(titulo, mensaje)
    root.destroy()


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
            mostrar_alerta("Conexión Exitosa", f"Conectado a la base de datos '{CONFIG['database']}' correctamente ✅", "info")
            return conn, cursor

    except Error as e:
        print(f"❌ Error de conexión a MySQL: {e}")
        mostrar_alerta("Error de Conexión", f"No se pudo conectar a MySQL:\n\n{e}", "error")
        return None, None


# 🔹 Ejecución directa (para probar la conexión)
#if __name__ == "__main__":
 #   conectar_mysql()
