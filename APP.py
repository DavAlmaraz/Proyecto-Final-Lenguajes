import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import mysql.connector
from mysql.connector import Error
import os
import tempfile 
import sys
import subprocess

def conexion_db():
    try:
        conexion = mysql.connector.connect(
            host="127.0.0.1",       # si MySQL está en tu PC
            user="root",            # tu usuario de MySQL
            password="Angrybirds12xx1@",  # tu contraseña de MySQL
            database="lenguajes"    # el nombre de tu base de datos
        )
        return conexion
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"No se pudo conectar a la base de datos:\n{err}")
        return None

# =======================
# CONFIGURACIÓN DE TEMA Y COLORES
# =======================
COLOR_FONDO = "#f8cfa0"
COLOR_FORM = "#6b0000"
COLOR_PANEL = "white"
COLOR_TEXTO = "white"
COLOR_BOTON = "#333333"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
ctk.set_widget_scaling(1.2)

# =======================
# VENTANA PRINCIPAL
# =======================
root = ctk.CTk()
root.title("Sistema de Gestión de Alumnos")
root.geometry("1200x900")
root.configure(fg_color=COLOR_FONDO)
root.resizable(False, False)

# =======================
# FUENTE GLOBAL
# =======================
font_size = ctk.IntVar(value=14)
def fuente(size_offset=0, bold=False):
    size = font_size.get() + size_offset
    return ctk.CTkFont(family="Arial Black" if bold else "Arial", size=size)

# =======================
# FUNCION PARA CAMBIO DE FRAME
# =======================
def mostrar_frame(frame):
    for f in [frame_login, frame_registro, frame_index, frame_detalle,
              frame_admin_menu, frame_admin_alumnos, frame_admin_list, frame_admin_detalle]:
        f.pack_forget()
    frame.pack(expand=True)

# =======================
# FUNCIONES PARA LLENAR LISTAS
# =======================

# Lista de alumnos en el scroll de Admin
def poblar_lista_alumnos():
    for w in scroll_alumnos.winfo_children():
        w.destroy()
    for alumno in alumnos_registrados:
        fila = ctk.CTkFrame(scroll_alumnos, fg_color="#f9f9f9",
                            border_color="#ccc", border_width=1, corner_radius=8, width=760, height=35)
        fila.pack(padx=5, pady=4)
        fila.pack_propagate(False)
        ctk.CTkLabel(fila, text=alumno["cuenta"], font=fuente(-2),
                     text_color="black", width=120, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(fila, text=alumno["nombre"], font=fuente(-2),
                     text_color="black", width=600, anchor="w").pack(side="left", padx=5)

# =======================
# DATOS SIMULADOS
# =======================
actividades = {
    "Actividad 1": {"descripcion": "Subir un archivo PDF.", "alumnos": [
        {"cuenta": "2023001", "nombre": "Juan Pérez"},
        {"cuenta": "2023002", "nombre": "María López"},
    ]},
    "Actividad 2": {"descripcion": "Resolver ejercicio práctico en Python.", "alumnos": [
        {"cuenta": "2023003", "nombre": "Luis Díaz"},
        {"cuenta": "2023004", "nombre": "Ana Torres"},
    ]},
}

alumnos_registrados = [
    {"cuenta": "2023001", "nombre": "Juan Pérez", "correo": "juanperez@mail.com"},
    {"cuenta": "2023002", "nombre": "María López", "correo": "marialopez@mail.com"},
    {"cuenta": "2023003", "nombre": "Luis Díaz", "correo": "luisdiaz@mail.com"},
    {"cuenta": "2023004", "nombre": "Ana Torres", "correo": "anatorres@mail.com"},
]

# =======================
# ENCABEZADO COMÚN
# =======================
header = ctk.CTkFrame(root, fg_color=COLOR_FORM, height=100, corner_radius=0)
header.pack(fill="x", side="top")

try:
    if os.path.exists("image.png"):
        img = Image.open("image.png").resize((60, 60))
        icon_img = ctk.CTkImage(light_image=img, dark_image=img, size=(60, 60))
        icon_label = ctk.CTkLabel(header, image=icon_img, text="")
    else:
        raise FileNotFoundError
except:
    icon_label = ctk.CTkLabel(header, text="👤", font=fuente(6))
icon_label.pack(side="left", padx=(20, 10), pady=20)

titulo = ctk.CTkLabel(header, text="Sistema de Gestión de Alumnos",
                      font=fuente(2, bold=True), text_color=COLOR_TEXTO)
titulo.pack(side="left", padx=10)

# =======================
# FRAME LOGIN
# =======================
frame_login = ctk.CTkFrame(root, fg_color=COLOR_FORM, width=480, height=460, corner_radius=15)
frame_login.pack_propagate(False)

ctk.CTkLabel(frame_login, text="Inicio de Sesión", font=fuente(2, bold=True),
             text_color=COLOR_TEXTO).pack(pady=(20, 15))

panel_login = ctk.CTkFrame(frame_login, fg_color=COLOR_PANEL, width=360, height=240, corner_radius=20)
panel_login.pack(pady=10)
panel_login.pack_propagate(False)

# ==== VALIDACIONES ====
def validar_usuario(texto):
    # Solo números y máximo 6 caracteres
    return texto.isdigit() and len(texto) <= 6 or texto == ""

def validar_clave(texto):
    # Solo números y máximo 4 caracteres
    return texto.isdigit() and len(texto) <= 4 or texto == ""

vcmd_usuario = root.register(validar_usuario)
vcmd_clave = root.register(validar_clave)

# ==== CAMPOS LOGIN ====
lbl_usuario = ctk.CTkLabel(panel_login, text="Usuario:", text_color="black", font=fuente())
lbl_usuario.pack(pady=(20, 5))
entry_usuario = ctk.CTkEntry(panel_login, placeholder_text="Número de cuenta", width=250,
                             validate="key", validatecommand=(vcmd_usuario, "%P"))
entry_usuario.pack(pady=5)

lbl_clave = ctk.CTkLabel(panel_login, text="Contraseña:", text_color="black", font=fuente())
lbl_clave.pack(pady=(10, 5))
entry_clave = ctk.CTkEntry(panel_login, placeholder_text="****", width=250, show="*",
                           validate="key", validatecommand=(vcmd_clave, "%P"))
entry_clave.pack(pady=5)
# variable global para saber qué alumno está logueado
id_usuario_actual = None

def login():
    global id_usuario_actual

    usuario = entry_usuario.get().strip()
    clave = entry_clave.get().strip()
    
    if not usuario or not clave:
        messagebox.showerror("Error", "Completa todos los campos")
        return
    
    # Conectar a la DB
    conexion = conexion_db()
    if conexion is None:
        return
    
    cursor = conexion.cursor(dictionary=True)
    
    try:
        # Consulta usando tus columnas Num_Cuenta y Clave
        query = "SELECT * FROM alumnos WHERE Num_Cuenta = %s AND Clave = %s"
        cursor.execute(query, (usuario, clave))
        resultado = cursor.fetchone()
        
        if resultado:
            # guardamos el identificador del alumno logueado (aquí usamos Num_Cuenta)
            id_usuario_actual = resultado.get("Num_Cuenta")  # si prefieres usar 'id' cámbialo por resultado['id']

            # Admin: si tu Num_Cuenta admin es '111111' (compara como string o int según tu DB)
            if str(resultado.get("Num_Cuenta")) == "111111":
                mostrar_frame(frame_admin_menu)
            else:
                # cuando inicie sesión el alumno, recarga su index desde BD
                cargar_actividades_alumno()
                mostrar_frame(frame_index)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al consultar la base de datos:\n{err}")
    finally:
        cursor.close()
        conexion.close()

# ==== BOTONES ====
ctk.CTkButton(frame_login, text="Ingresar", command=login,
              width=220, height=45, fg_color=COLOR_BOTON, hover_color="#222",
              font=fuente()).pack(pady=(20, 10))

# =======================
# FRAME REGISTRO
# =======================
frame_registro = ctk.CTkFrame(root, fg_color=COLOR_FORM, width=480, height=480, corner_radius=15)
frame_registro.pack_propagate(False)

ctk.CTkLabel(frame_registro, text="Registro de Usuario",
             font=fuente(2, bold=True), text_color=COLOR_TEXTO).pack(pady=20)

panel_reg = ctk.CTkFrame(frame_registro, fg_color=COLOR_PANEL, width=360, height=260, corner_radius=20)
panel_reg.pack(pady=10)
panel_reg.pack_propagate(False)

entrada_nombre = ctk.CTkEntry(panel_reg, placeholder_text="Nombre completo", width=280)
entrada_nombre.pack(pady=10)
entrada_cuenta = ctk.CTkEntry(panel_reg, placeholder_text="Número de cuenta", width=280)
entrada_cuenta.pack(pady=10)
entrada_clave = ctk.CTkEntry(panel_reg, placeholder_text="Contraseña", width=280, show="*")
entrada_clave.pack(pady=10)

def registrar():
    if entrada_nombre.get() and entrada_cuenta.get() and entrada_clave.get():
        messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
        mostrar_frame(frame_login)
    else:
        messagebox.showerror("Error", "Completa todos los campos.")

ctk.CTkButton(frame_registro, text="Registrar", command=registrar,
              width=220, height=45, fg_color=COLOR_BOTON,
              hover_color="#222", font=fuente()).pack(pady=25)
ctk.CTkButton(frame_registro, text="Volver al Login",
              command=lambda: mostrar_frame(frame_login),
              width=220, height=40, fg_color="#888", hover_color="#666",
              font=fuente()).pack(pady=5)

# =======================
# FRAME ADMIN MENU
# =======================
frame_admin_menu = ctk.CTkFrame(root, fg_color=COLOR_FORM, width=700, height=550, corner_radius=15)
frame_admin_menu.pack_propagate(False)

ctk.CTkLabel(frame_admin_menu, text="Menú del Administrador",
             font=fuente(2, bold=True), text_color=COLOR_TEXTO).pack(pady=20)

panel_menu = ctk.CTkFrame(frame_admin_menu, fg_color=COLOR_PANEL, width=500, height=400, corner_radius=20)
panel_menu.pack(pady=10)
panel_menu.pack_propagate(False)

ctk.CTkButton(panel_menu, text="📋 Lista de Alumnos Registrados",
              width=300, height=70, fg_color=COLOR_BOTON, hover_color="#222",
              font=fuente(), command=lambda: (poblar_lista_alumnos(), mostrar_frame(frame_admin_alumnos))).pack(pady=20)
ctk.CTkButton(panel_menu, text="🧾 Gestión de Actividades",
              width=300, height=70, fg_color=COLOR_BOTON, hover_color="#222",
              font=fuente(), command=lambda: (actualizar_lista_admin(), mostrar_frame(frame_admin_list))).pack(pady=20)
ctk.CTkButton(panel_menu, text="Cerrar Sesión",
              width=300, height=60, fg_color="#888", hover_color="#666",
              font=fuente(), command=lambda: mostrar_frame(frame_login)).pack(pady=25)

# =======================
# FRAME ADMIN ALUMNOS
# =======================
frame_admin_alumnos = ctk.CTkFrame(root, fg_color=COLOR_FORM, width=900, height=550)
frame_admin_alumnos.pack_propagate(False)

lbl_alumnos_titulo = ctk.CTkLabel(frame_admin_alumnos, text="Alumnos Registrados",
                                  font=fuente(2, bold=True), text_color=COLOR_TEXTO)
lbl_alumnos_titulo.place(x=50, y=15)

# --- Botón Volver al menú (arriba a la derecha) ---
btn_volver_alumnos = ctk.CTkButton(frame_admin_alumnos, text="Volver al Menú",
                                   width=160, height=40,
                                   fg_color="#888", hover_color="#666",
                                   font=fuente(),
                                   command=lambda: mostrar_frame(frame_admin_menu))
btn_volver_alumnos.place(x=720, y=15)  # <-- Ubicado arriba a la derecha

# --- Panel blanco principal ---
panel_alumnos = ctk.CTkFrame(frame_admin_alumnos, fg_color=COLOR_PANEL,
                             width=800, height=450, corner_radius=25)
panel_alumnos.place(x=50, y=60)
panel_alumnos.pack_propagate(False)

scroll_alumnos = ctk.CTkScrollableFrame(panel_alumnos, fg_color="#ffffff",
                                        width=780, height=400)
scroll_alumnos.place(x=10, y=10)

def poblar_lista_alumnos():
    for w in scroll_alumnos.winfo_children():
        w.destroy()  # limpia el scroll antes de llenarlo

    conexion = conexion_db()
    if conexion is None:
        return

    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT Num_Cuenta, nombre_completo, Correo FROM alumnos")
        resultados = cursor.fetchall()

        for alumno in resultados:
            fila = ctk.CTkFrame(scroll_alumnos, fg_color="#f9f9f9",
                                border_color="#ccc", border_width=1, corner_radius=8,
                                width=760, height=35)
            fila.pack(padx=5, pady=4)
            fila.pack_propagate(False)

            ctk.CTkLabel(fila, text=alumno["Num_Cuenta"], font=fuente(-2),
                         text_color="black", width=120, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(fila, text=alumno["nombre_completo"], font=fuente(-2),
                         text_color="black", width=400, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(fila, text=alumno["Correo"], font=fuente(-2),
                         text_color="black", width=200, anchor="w").pack(side="left", padx=5)

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al consultar la base de datos:\n{err}")
    finally:
        cursor.close()
        conexion.close()

# =======================
# FRAME ADMIN LISTA DE ACTIVIDADES
# =======================
frame_admin_list = ctk.CTkFrame(root, fg_color=COLOR_FORM, width=900, height=500, corner_radius=20)
frame_admin_list.pack_propagate(False)

# Título principal
lbl_admin_list = ctk.CTkLabel(frame_admin_list, text="Gestión de Actividades",
                              font=fuente(2, bold=True), text_color=COLOR_TEXTO)
lbl_admin_list.place(x=50, y=15)

# Botón para regresar al menú
btn_volver_list = ctk.CTkButton(frame_admin_list, text="Volver al menú",
                                width=150, height=35, fg_color="#888", hover_color="#666",
                                font=fuente(),
                                command=lambda: mostrar_frame(frame_admin_menu))
btn_volver_list.place(x=720, y=15)

# Botón para ir al frame de crear actividad
btn_ir_crear = ctk.CTkButton(frame_admin_list, text="Nueva Actividad",
                             width=200, height=40, fg_color=COLOR_BOTON, hover_color="#222",
                             font=fuente(),
                             command=lambda: mostrar_frame(frame_crear_actividad))
btn_ir_crear.place(x=50, y=70)

# Panel con scroll
panel_admin_list = ctk.CTkFrame(frame_admin_list, fg_color=COLOR_PANEL, width=800, height=350, corner_radius=25)
panel_admin_list.place(x=50, y=130)
panel_admin_list.pack_propagate(False)

scroll_admin = ctk.CTkScrollableFrame(panel_admin_list, fg_color="#ffffff",
                                      width=780, height=330)
scroll_admin.place(x=10, y=10)


# -----------------------
# Función para abrir detalle (por ID)
# -----------------------
def abrir_detalle_admin(id_actividad):
    poblar_tabla_actividad(id_actividad)
    mostrar_frame(frame_admin_detalle)


# -----------------------
# Función para actualizar la lista de actividades
# -----------------------
def actualizar_lista_admin():
    for w in scroll_admin.winfo_children():
        w.destroy()
    
    conexion = conexion_db()
    if conexion is None:
        return
    
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, nombre_actividad, descripcion FROM actividades ORDER BY id DESC")
        actividades = cursor.fetchall()
        
        for act in actividades:
            fila = ctk.CTkFrame(scroll_admin, fg_color="#f9f9f9",
                                border_color="#ccc", border_width=1,
                                corner_radius=8, width=760, height=60)
            fila.pack(padx=5, pady=5)
            fila.pack_propagate(False)
            
            ctk.CTkLabel(fila, text=f"{act['id']}. {act['nombre_actividad']}",
                         text_color="black", font=fuente(), width=500, anchor="w").pack(side="left", padx=10)
            
            # Se pasa el ID correctamente al botón
            ctk.CTkButton(fila, text="Ver Detalles", width=150, fg_color=COLOR_BOTON,
                          hover_color="#222", font=fuente(),
                          command=lambda i=act['id']: abrir_detalle_admin(i)).pack(side="right", padx=10)
    except Exception as e:
        messagebox.showerror("Error MySQL", f"No se pudo obtener la lista:\n{e}")
    finally:
        cursor.close()
        conexion.close()


# =======================
# FRAME ADMIN CREAR ACTIVIDAD
# =======================
frame_crear_actividad = ctk.CTkFrame(root, fg_color=COLOR_FORM, width=900, height=500)
frame_crear_actividad.pack_propagate(False)

ctk.CTkLabel(frame_crear_actividad, text="Nueva Actividad", font=fuente(2, bold=True),
             text_color=COLOR_TEXTO).place(x=50, y=20)

# Botón volver
def volver_a_menu_desde_crear():
    frame_crear_actividad.pack_forget()
    mostrar_frame(frame_admin_menu)

ctk.CTkButton(frame_crear_actividad, text="Volver al menú", width=150, height=35,
              fg_color="#888", hover_color="#666", font=fuente(),
              command=volver_a_menu_desde_crear).place(x=720, y=20)

# Panel de creación
panel_crear = ctk.CTkFrame(frame_crear_actividad, fg_color="#e8e8e8",
                           width=800, height=300, corner_radius=15)
panel_crear.place(x=50, y=70)

ctk.CTkLabel(panel_crear, text="Nombre de la Actividad:",
             text_color="black", font=fuente(0, bold=True)).place(x=20, y=30)
actividad_entry = ctk.CTkEntry(panel_crear, width=500)
actividad_entry.place(x=250, y=30)

ctk.CTkLabel(panel_crear, text="Descripción:",
             text_color="black", font=fuente(0, bold=True)).place(x=20, y=90)
descripcion_entry = ctk.CTkTextbox(panel_crear, width=500, height=120)
descripcion_entry.place(x=250, y=90)


# -----------------------
# Función para registrar la actividad
# -----------------------
def create_activity_columns():
    nombre_actividad = actividad_entry.get().strip()
    descripcion = descripcion_entry.get("1.0", "end").strip()
    
    if not nombre_actividad or not descripcion:
        messagebox.showwarning("Advertencia", "Debes escribir el nombre y la descripción de la actividad.")
        return
    
    conexion = conexion_db()
    if conexion is None:
        return
    
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM actividades WHERE nombre_actividad = %s", (nombre_actividad,))
        if cursor.fetchone()[0] > 0:
            messagebox.showwarning("Advertencia", "Ya existe una actividad con ese nombre.")
            return

        cursor.execute(
            "INSERT INTO actividades (nombre_actividad, descripcion) VALUES (%s, %s)",
            (nombre_actividad, descripcion)
        )
        conexion.commit()

        messagebox.showinfo("Éxito", "Actividad registrada correctamente.")
        actividad_entry.delete(0, "end")
        descripcion_entry.delete("1.0", "end")

        # Regresa a lista
        frame_crear_actividad.pack_forget()
        actualizar_lista_admin()
        mostrar_frame(frame_admin_list)

    except Exception as e:
        messagebox.showerror("Error MySQL", f"No se pudo crear la actividad:\n{e}")
    finally:
        cursor.close()
        conexion.close()

ctk.CTkButton(panel_crear, text="Guardar Actividad", width=200,
              fg_color=COLOR_BOTON, hover_color="#222", font=fuente(),
              command=create_activity_columns).place(x=300, y=230)


# =======================
# FRAME ADMIN DETALLE (corregido para trabajar con id)
# =======================
frame_admin_detalle = ctk.CTkFrame(root, fg_color=COLOR_FORM, width=900, height=500, corner_radius=20)
frame_admin_detalle.pack_propagate(False)

lbl_admin_detalle = ctk.CTkLabel(frame_admin_detalle, text="Detalle de Actividad",
                                 font=fuente(2, bold=True), text_color=COLOR_TEXTO)
lbl_admin_detalle.place(x=50, y=15)

panel_admin_detalle = ctk.CTkFrame(frame_admin_detalle, fg_color=COLOR_PANEL, width=800, height=400, corner_radius=25)
panel_admin_detalle.place(x=50, y=60)
panel_admin_detalle.pack_propagate(False)

txt_descripcion_admin = ctk.CTkTextbox(panel_admin_detalle, width=180, height=280, font=fuente(-1))
txt_descripcion_admin.place(x=20, y=20)

frame_tabla = ctk.CTkFrame(panel_admin_detalle, fg_color="#f7f7f7", width=570, height=280, corner_radius=15)
frame_tabla.place(x=220, y=20)
frame_tabla.pack_propagate(False)

scroll_tabla = ctk.CTkScrollableFrame(frame_tabla, fg_color="#ffffff", width=550, height=260)
scroll_tabla.pack(padx=10, pady=10)


btn_volver_header = ctk.CTkButton(frame_admin_detalle, text="Volver al Menú",
                                  width=160, height=38,
                                  fg_color="#888", hover_color="#666",
                                  font=fuente(),
                                  command=lambda: mostrar_frame(frame_admin_menu))
btn_volver_header.place(x=690, y=10)


btn_csv = ctk.CTkButton(panel_admin_detalle, text="Descargar CSV", width=230, height=45,
                        fg_color=COLOR_BOTON, hover_color="#222", font=fuente(),
                        command=lambda: messagebox.showinfo("Descarga CSV", "CSV descargado"))
btn_csv.place(x=180, y=320)

btn_pdf = ctk.CTkButton(panel_admin_detalle, text="Descargar PDF", width=230, height=45,
                        fg_color=COLOR_BOTON, hover_color="#222", font=fuente(),
                        command=lambda: messagebox.showinfo("Descarga PDF", "PDF descargado"))
btn_pdf.place(x=420, y=320)

def poblar_tabla_actividad(id_actividad):
    for w in scroll_tabla.winfo_children():
        w.destroy()

    conexion = conexion_db()
    if conexion is None:
        return

    cursor = conexion.cursor(dictionary=True)
    try:
        # Obtener datos de la actividad seleccionada
        cursor.execute("SELECT nombre_actividad, descripcion FROM actividades WHERE id = %s", (id_actividad,))
        actividad = cursor.fetchone()

        if not actividad:
            messagebox.showwarning("Atención", "No se encontró la actividad seleccionada.")
            return

        lbl_admin_detalle.configure(text=actividad["nombre_actividad"])
        txt_descripcion_admin.delete("1.0", "end")
        txt_descripcion_admin.insert("end", actividad["descripcion"])

        # Obtener alumnos ordenados alfabéticamente
        cursor.execute("SELECT Num_Cuenta, nombre_completo FROM alumnos ORDER BY nombre_completo ASC")
        alumnos = cursor.fetchall()

        for alumno in alumnos:
            fila = ctk.CTkFrame(scroll_tabla, fg_color="#f9f9f9",
                                border_color="#ccc", border_width=1,
                                corner_radius=8, width=540, height=35)
            fila.pack(padx=5, pady=4)
            fila.pack_propagate(False)

            ctk.CTkLabel(fila, text=alumno["Num_Cuenta"], font=fuente(-2),
                         text_color="black", width=100, anchor="w").pack(side="left", padx=(5,2))

            ctk.CTkLabel(fila, text=alumno["nombre_completo"], font=fuente(-2),
                         text_color="black", width=220, anchor="w").pack(side="left", padx=2)

            # Estado según entregas
            cursor2 = conexion.cursor(dictionary=True)
            cursor2.execute("""
                SELECT realizado 
                FROM entregas 
                WHERE alumno_num_cuenta = %s AND actividad_id = %s
            """, (alumno["Num_Cuenta"], id_actividad))
            res_estado = cursor2.fetchone()
            estado_texto = "Entregado" if res_estado and res_estado["realizado"] == 1 else "Pendiente"
            cursor2.close()

            lbl_estado = ctk.CTkLabel(fila, text=estado_texto, font=fuente(-2),
                                      text_color="black", width=80, anchor="w")
            lbl_estado.pack(side="left", padx=5)

            # Función para descargar y abrir archivo
            def descargar_archivo(a=alumno):
                conexion2 = conexion_db()
                if conexion2 is None:
                    return
                cursor3 = conexion2.cursor(dictionary=True)
                try:
                    # Obtener contenido y nombre del archivo
                    cursor3.execute("""
                        SELECT archivo, nombre_archivo
                        FROM entregas
                        WHERE alumno_num_cuenta = %s AND actividad_id = %s
                    """, (a["Num_Cuenta"], id_actividad))
                    resultado = cursor3.fetchone()
                    if resultado is None or resultado["archivo"] is None:
                        messagebox.showwarning("Aviso", f"{a['nombre_completo']} no ha subido un archivo.")
                        return

                    contenido_archivo = resultado["archivo"]
                    nombre_original = resultado["nombre_archivo"] or "archivo"
                    ext = os.path.splitext(nombre_original)[1]  # extrae la extensión original

                    # Crear archivo temporal con la misma extensión
                    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
                        tmp_file.write(contenido_archivo)
                        tmp_ruta = tmp_file.name

                    # Abrir automáticamente según el sistema operativo
                    if sys.platform.startswith("win"):
                        os.startfile(tmp_ruta)
                    elif sys.platform.startswith("darwin"):
                        subprocess.run(["open", tmp_ruta])
                    else:
                        subprocess.run(["xdg-open", tmp_ruta])

                except mysql.connector.Error as err:
                    messagebox.showerror("Error MySQL", f"No se pudo descargar el archivo:\n{err}")
                finally:
                    cursor3.close()
                    conexion2.close()

            ctk.CTkButton(fila, text="Descargar", width=40, fg_color=COLOR_BOTON,
                          hover_color="#222", command=descargar_archivo).pack(side="left", padx=5)

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al consultar la base de datos:\n{err}")
    finally:
        cursor.close()
        conexion.close()

# =======================
# FRAME INDEX ALUMNO (ACTUALIZADO)
# =======================
frame_index = ctk.CTkFrame(root, fg_color=COLOR_FORM, width=900, height=500, corner_radius=20)
frame_index.pack_propagate(False)

# Título principal
titulo_actividades = ctk.CTkLabel(
    frame_index,
    text="Actividades Disponibles",
    font=fuente(2, bold=True),
    text_color=COLOR_TEXTO
)
titulo_actividades.place(x=50, y=15)

# Botón para regresar al login (por si aplica)
btn_salir = ctk.CTkButton(
    frame_index,
    text="Cerrar Sesión",
    width=150,
    height=35,
    fg_color="#888",
    hover_color="#666",
    font=fuente(),
    command=lambda: mostrar_frame(frame_login)
)
btn_salir.place(x=720, y=15)

# Panel principal con scroll
panel_index = ctk.CTkFrame(frame_index, fg_color=COLOR_PANEL, width=800, height=400, corner_radius=25)
panel_index.place(x=50, y=60)
panel_index.pack_propagate(False)

scroll_index = ctk.CTkScrollableFrame(panel_index, fg_color="#ffffff", width=780, height=380)
scroll_index.place(x=10, y=10)

# -----------------------
# FUNCIÓN PARA CARGAR ACTIVIDADES DEL ALUMNO
# -----------------------
def cargar_actividades_alumno():
    """Llena el panel con todas las actividades registradas en la tabla 'actividades'."""
    # Limpiar el contenido actual del scroll
    for w in scroll_index.winfo_children():
        w.destroy()

    conexion = conexion_db()
    if conexion is None:
        return
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id, nombre_actividad, descripcion FROM actividades ORDER BY id DESC")
        actividades = cursor.fetchall()

        if not actividades:
            ctk.CTkLabel(
                scroll_index,
                text="No hay actividades registradas.",
                text_color="gray",
                font=fuente()
            ).pack(pady=20)
            return

        for act in actividades:
            # Contenedor por actividad
            contenedor = ctk.CTkFrame(
                scroll_index,
                fg_color="#f9f9f9",
                border_color="#ccc",
                border_width=1,
                corner_radius=8,
                width=760,
                height=90
            )
            contenedor.pack(padx=5, pady=5)
            contenedor.pack_propagate(False)

            # Nombre de la actividad
            ctk.CTkLabel(
                contenedor,
                text=f"{act['id']}. {act['nombre_actividad']}",
                text_color="black",
                font=fuente(1, bold=True),
                anchor="w"
            ).pack(anchor="w", padx=10, pady=(5, 0))

            # Descripción breve
            ctk.CTkLabel(
                contenedor,
                text=(act['descripcion'][:150] + "...") if len(act['descripcion']) > 150 else act['descripcion'],
                text_color="#333",
                font=fuente(-1),
                anchor="w",
                wraplength=720,
                justify="left"
            ).pack(anchor="w", padx=10, pady=(0, 5))

            # Botón para abrir detalle
            ctk.CTkButton(
                contenedor,
                text="Ver Detalle",
                width=140,
                height=32,
                fg_color=COLOR_BOTON,
                hover_color="#222",
                font=fuente(),
                command=lambda i=act['id']: abrir_detalle_alumno(i)
            ).pack(anchor="e", padx=10, pady=(0, 5))

    except Exception as e:
        messagebox.showerror("Error MySQL", f"No se pudieron cargar las actividades:\n{e}")
    finally:
        cursor.close()
        conexion.close()

# 🔹 Llamar esta función al iniciar el frame del alumno
cargar_actividades_alumno()


# =======================
# FRAME DETALLE ALUMNO (completo y corregido)
# =======================
from tkinter import filedialog, messagebox
import os, mysql.connector

id_usuario_actual = None   # 🔹 Debe actualizarse al iniciar sesión del alumno
id_actividad_actual = None # 🔹 Se actualizará al abrir un detalle

frame_detalle = ctk.CTkFrame(root, fg_color=COLOR_FORM, width=650, height=350, corner_radius=20)
frame_detalle.place(relx=0.5, rely=0.5, anchor="center")
frame_detalle.pack_propagate(False)
frame_detalle.place_forget()  # 🔹 Oculta el frame hasta que se abra un detalle

# Título
lbl_detalle_nombre = ctk.CTkLabel(frame_detalle, text="Detalle de Actividad",
                                  font=fuente(2, bold=True), text_color=COLOR_TEXTO)
lbl_detalle_nombre.place(relx=0.5, y=10, anchor="n")

# Panel central
panel_detalle = ctk.CTkFrame(frame_detalle, fg_color=COLOR_PANEL, width=500, height=230, corner_radius=25)
panel_detalle.place(relx=0.5, rely=0.55, anchor="center")
panel_detalle.pack_propagate(False)

# Etiqueta de descripción
ctk.CTkLabel(panel_detalle, text="Descripción", font=fuente(1, bold=True),
             text_color="black").place(x=30, y=10)

# Caja de texto
txt_descripcion = ctk.CTkTextbox(panel_detalle, width=220, height=160, font=fuente(-1))
txt_descripcion.place(x=30, y=40)

# =======================
# FUNCIONES DE DETALLE
# =======================
def abrir_detalle_alumno(id_actividad):
    """Carga los datos del detalle según el ID de la actividad"""
    global id_actividad_actual
    id_actividad_actual = id_actividad

    conexion = conexion_db()
    if conexion is None:
        return

    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT nombre_actividad, descripcion FROM actividades WHERE id = %s", (id_actividad,))
        actividad = cursor.fetchone()

        if actividad:
            lbl_detalle_nombre.configure(text=actividad["nombre_actividad"])
            txt_descripcion.delete("1.0", "end")
            txt_descripcion.insert("1.0", actividad["descripcion"] or "")
            mostrar_frame(frame_detalle)
        else:
            messagebox.showerror("Error", "No se encontró la actividad.")
    except mysql.connector.Error as err:
        messagebox.showerror("Error MySQL", f"No se pudo abrir el detalle:\n{err}")
    finally:
        cursor.close()
        conexion.close()


def marcar_como_realizado():
    """Marca una actividad como completada en la tabla 'entregas'"""
    global id_usuario_actual, id_actividad_actual
    if id_actividad_actual is None:
        messagebox.showwarning("Advertencia", "No hay actividad seleccionada.")
        return
    if id_usuario_actual is None:
        messagebox.showwarning("Advertencia", "No hay usuario logueado.")
        return

    conexion = conexion_db()
    if conexion is None:
        return

    cursor = conexion.cursor()
    try:
        cursor.execute("""
            INSERT INTO entregas (id_alumno, id_actividad, estado)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE estado = VALUES(estado)
        """, (id_usuario_actual, id_actividad_actual, "realizado"))
        conexion.commit()
        messagebox.showinfo("Éxito", "Actividad marcada como realizada.")
    except mysql.connector.Error as err:
        messagebox.showerror("Error MySQL", f"No se pudo marcar como realizada:\n{err}")
    finally:
        cursor.close()
        conexion.close()


def subir_archivo_actividad():
    """Permite al alumno subir un archivo y guardarlo en la tabla 'entregas'"""
    global id_usuario_actual, id_actividad_actual
    if id_actividad_actual is None:
        messagebox.showwarning("Advertencia", "No hay actividad seleccionada.")
        return
    if id_usuario_actual is None:
        messagebox.showwarning("Advertencia", "No hay usuario logueado.")
        return

    ruta = filedialog.askopenfilename(title="Seleccionar archivo")
    if not ruta:
        return

    with open(ruta, "rb") as f:
        contenido_archivo = f.read()

    conexion = conexion_db()
    if conexion is None:
        return

    cursor = conexion.cursor()
    try:
        cursor.execute("""
            INSERT INTO entregas (alumno_num_cuenta, actividad_id, archivo, realizado)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE archivo = VALUES(archivo), realizado = VALUES(realizado)
        """, (id_usuario_actual, id_actividad_actual, contenido_archivo, 1))
        conexion.commit()
        messagebox.showinfo("Éxito", "Archivo subido y registro actualizado.")
    except mysql.connector.Error as err:
        messagebox.showerror("Error MySQL", f"No se pudo subir el archivo:\n{err}")
    finally:
        cursor.close()
        conexion.close()


# =======================
# BOTONES
# =======================
btn_subir = ctk.CTkButton(panel_detalle, text="Subir Archivo", width=160, height=35,
                          fg_color="#888", hover_color="#666", font=fuente(),
                          command=subir_archivo_actividad)
btn_subir.place(x=280, y=60)

btn_realizado = ctk.CTkButton(panel_detalle, text="Marcar como realizado", width=160, height=35,
                              fg_color="#888", hover_color="#666", font=fuente(),
                              command=marcar_como_realizado)
btn_realizado.place(x=280, y=110)

btn_regresar = ctk.CTkButton(panel_detalle, text="Regresar", width=160, height=35,
                             fg_color="#888", hover_color="#666", font=fuente(),
                             command=lambda: mostrar_frame(frame_index))
btn_regresar.place(x=280, y=160)

# =======================
# INICIO EN LOGIN
# =======================
mostrar_frame(frame_login)
root.mainloop()