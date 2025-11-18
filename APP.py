import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import mysql.connector
from mysql.connector import Error
import os
import openpyxl
import tempfile 
import sys
import subprocess
from email.message import EmailMessage
import smtplib
from registrarAlumnos import ExcelToMySQLApp

def conexion_db():
    try:
        conexion = mysql.connector.connect(
            host="localhost",       # si MySQL está en tu PC
            user="root",            # tu usuario de MySQL
            password="root",  # tu contraseña de MySQL
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

    # ============================
    # Validación de campos vacíos
    # ============================
    if not usuario or not clave:
        messagebox.showerror("Error", "Completa todos los campos")
        return

    # ============================
    # Conecta a la base de datos
    # ============================
    conexion = conexion_db()
    if conexion is None:
        return

    cursor = conexion.cursor(dictionary=True)

    try:
        alumno = None

        # ==========================================
        # 1. Buscar en tablas de alumnos
        # ==========================================
        tablas_alumnos = ["alumnos", "alumnos_backup"]

        for tabla in tablas_alumnos:
            try:
                cursor.execute(
                    f"SELECT * FROM `{tabla}` WHERE Num_Cuenta = %s AND Clave = %s",
                    (usuario, clave)
                )
                alumno = cursor.fetchone()
                if alumno:
                    break
            except:
                continue  # si la tabla no existe, sigue con la siguiente

        admin = None

        # ==========================================
        # 2. Buscar en tabla administrador
        # ==========================================
        if not alumno:
            try:
                cursor.execute(
                    "SELECT * FROM administrador WHERE cuentaAd = %s AND clave = %s",
                    (usuario, clave)
                )
                admin = cursor.fetchone()
            except:
                pass

        # ==================================================
        # 3. Validación final (Alumno, Admin o Error)
        # ==================================================

        # -------- ALUMNO ENCONTRADO --------
        if alumno:
            id_usuario_actual = alumno.get("Num_Cuenta")
            nombre = alumno.get("nombre_completo", "Alumno")

            # Administrador desde ALUMNOS (Num_Cuenta = 111111)
            if str(alumno.get("Num_Cuenta")) == "111111":
                messagebox.showinfo("Bienvenido", "Inicio de sesión correcto (Administrador)")
                mostrar_frame(frame_admin_menu)
            else:
                messagebox.showinfo("Bienvenido", f"Bienvenido {nombre}")
                cargar_actividades_alumno()
                mostrar_frame(frame_index)
            return

        # -------- ADMIN ENCONTRADO --------
        if admin:
            id_usuario_actual = admin.get("cuentaAd")
            nombre_admin = admin.get("nombre", "Administrador")
            messagebox.showinfo("Bienvenido", f"Inicio de sesión correcto (Administrador): {nombre_admin}")
            mostrar_frame(frame_admin_menu)
            return

        # -------- NADIE COINCIDE --------
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

# ================== FUNCION PARA SUBIR EXCEL ==================
def subir_excel_y_enviar():
    archivo = filedialog.askopenfilename(
        title="Selecciona el archivo Excel",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")]
    )
    if not archivo:
        return

    try:
        wb = openpyxl.load_workbook(archivo)
        sheet = wb.active
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el archivo Excel:\n{e}")
        return

    conexion = conexion_db()
    if not conexion:
        return
    cursor = conexion.cursor()

    alumnos_insertados = 0

    for fila in sheet.iter_rows(min_row=2, values_only=True):  # min_row=2 si la primera fila es encabezado
        num_cuenta = fila[0]
        nombre_completo = fila[1]
        correo = fila[2]
        clave = fila[3]

        try:
            # Insertar en la base de datos
            cursor.execute("""
                INSERT INTO alumnos (Num_Cuenta, nombre_completo, correo, clave)
                VALUES (%s, %s, %s, %s)
            """, (num_cuenta, nombre_completo, correo, clave))
            conexion.commit()
            alumnos_insertados += 1

            # Enviar correo de confirmación
            enviar_correo(correo, nombre_completo, num_cuenta, clave)

        except mysql.connector.IntegrityError:
            # Por ejemplo si ya existe el alumno
            continue
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo insertar o enviar correo:\n{e}")
            continue

    cursor.close()
    conexion.close()
    messagebox.showinfo("Éxito", f"{alumnos_insertados} alumnos fueron agregados y se enviaron los correos.")
# IMPORTA LA CLASE DEL IMPORTADOR

def abrir_importador_excel():
    nueva = ctk.CTkToplevel()
    nueva.geometry("950x620")
    nueva.title("Importar Excel")

    ExcelToMySQLApp(master=nueva)
# ================== FUNCION PARA ENVIAR CORREO ==================
def enviar_correo(destinatario, nombre, num_cuenta, clave):
    try:
        mensaje = EmailMessage()
        mensaje["Subject"] = "Confirmación de registro"
        mensaje["From"] = "tu_correo@gmail.com"
        mensaje["To"] = destinatario
        mensaje.set_content(f"Hola {nombre},\n\nTu cuenta ha sido registrada.\nNúmero de cuenta: {num_cuenta}\nClave: {clave}")

        # Configura tu SMTP
        servidor = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        servidor.login("bionicmandks@gmail.com", "gkqw dqbe fidr mhoo")  # Usa contraseña de aplicación si es Gmail
        servidor.send_message(mensaje)
        servidor.quit()
    except Exception as e:
        print(f"No se pudo enviar correo a {destinatario}: {e}")

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

# Botón para subir Excel y registrar alumnos
btn_subir_excel = ctk.CTkButton(frame_admin_list, text="Subir lista de alumnos",
                                width=200, height=40, fg_color=COLOR_BOTON, hover_color="#222",
                                font=fuente(),
                                command=abrir_importador_excel)
btn_subir_excel.place(x=270, y=70)  # Al lado de "Nueva Actividad"

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


btn_volver_header = ctk.CTkButton(
    frame_admin_detalle,
    text="⬅ Regresar",
    width=160,
    height=38,
    fg_color="#888",
    hover_color="#666",
    font=fuente(),
    command=lambda: mostrar_frame(frame_admin_list)   # 🔥 ESTA es la pantalla correcta
)

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
    # limpiar tabla
    for w in scroll_tabla.winfo_children():
        w.destroy()

    conexion = conexion_db()
    if conexion is None:
        return

    cursor = conexion.cursor(dictionary=True)

    try:
        # Obtener datos de la actividad
        cursor.execute("""
            SELECT nombre_actividad, descripcion
            FROM actividades
            WHERE id = %s
        """, (id_actividad,))
        actividad = cursor.fetchone()

        if not actividad:
            messagebox.showwarning("Atención", "No se encontró la actividad.")
            return

        # Mostrar nombre y descripción
        lbl_admin_detalle.configure(text=actividad["nombre_actividad"])
        txt_descripcion_admin.delete("1.0", "end")
        txt_descripcion_admin.insert("end", actividad["descripcion"])

        # ========================================
        # 🔥 OBTENER SOLO ENTREGAS COMPLETAS
        # archivo != NULL  Y realizado = 1
        # ========================================
        cursor.execute("""
            SELECT 
                e.alumno_num_cuenta AS cuenta,
                a.nombre_completo AS nombre,
                e.realizado,
                e.archivo,
                e.archivo_nombre
            FROM entregas e
            INNER JOIN alumnos a ON a.Num_Cuenta = e.alumno_num_cuenta
            WHERE e.actividad_id = %s
              AND e.archivo IS NOT NULL
              AND e.realizado = 1
            ORDER BY a.nombre_completo ASC
        """, (id_actividad,))

        entregas = cursor.fetchall()

        # Si no hay entregas completas
        if not entregas:
            ctk.CTkLabel(scroll_tabla, text="Nadie ha entregado aún.",
                         text_color="gray", font=fuente()).pack(pady=10)
            return

        # ========================================
        # MOSTRAR RESULTADOS
        # ========================================
        for reg in entregas:
            fila = ctk.CTkFrame(scroll_tabla, fg_color="#f9f9f9",
                                border_color="#ccc", border_width=1,
                                corner_radius=8, width=540, height=35)
            fila.pack(padx=5, pady=4)
            fila.pack_propagate(False)

            ctk.CTkLabel(
                fila,
                text=str(reg["cuenta"]),
                font=fuente(-2),
                text_color="black",
                width=100,
                anchor="w"
            ).pack(side="left", padx=(5, 2))

            ctk.CTkLabel(
                fila,
                text=reg["nombre"],
                font=fuente(-2),
                text_color="black",
                width=250,
                anchor="w"
            ).pack(side="left", padx=2)

            ctk.CTkLabel(
                fila,
                text="Entregado ✔",
                font=fuente(-2),
                text_color="#2ecc71",
                width=120,
                anchor="w"
            ).pack(side="left", padx=5)

            # Botón Descargar archivo
            def descargar(entrada=reg):
                conexion2 = conexion_db()
                if conexion2 is None:
                    return
                cur = conexion2.cursor(dictionary=True)
                try:
                    cur.execute("""
                        SELECT archivo, archivo_nombre 
                        FROM entregas
                        WHERE alumno_num_cuenta = %s AND actividad_id = %s
                    """, (entrada["cuenta"], id_actividad))

                    datos = cur.fetchone()
                    if not datos or not datos["archivo"]:
                        messagebox.showwarning("Aviso", "No hay archivo.")
                        return

                    contenido = datos["archivo"]
                    nombre_archivo = datos["archivo_nombre"] or "archivo"

                    ext = os.path.splitext(nombre_archivo)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                        tmp.write(contenido)
                        ruta_tmp = tmp.name

                    # Abrir archivo
                    if sys.platform.startswith("win"):
                        os.startfile(ruta_tmp)
                    else:
                        subprocess.run(["xdg-open", ruta_tmp])

                finally:
                    cur.close()
                    conexion2.close()

            ctk.CTkButton(
                fila,
                text="Descargar",
                width=70,
                fg_color="#333",
                hover_color="#222",
                font=fuente(-2),
                command=descargar
            ).pack(side="right", padx=5)

    except mysql.connector.Error as err:
        messagebox.showerror("Error MySQL", f"No se pudo cargar el detalle:\n{err}")

    finally:
        cursor.close()
        conexion.close()

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
def cargar_actividades_alumno():
    for w in scroll_index.winfo_children():
        w.destroy()

    conexion = conexion_db()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre_actividad, descripcion FROM actividades ORDER BY id DESC")
        actividades = cursor.fetchall()
        cursor.close()

        if not actividades:
            ctk.CTkLabel(scroll_index, text="No hay actividades registradas.",
                         text_color="gray", font=fuente()).pack(pady=20)
            return

        # ===== COLORES DEL BORDE =====
        COLOR_VERDE = "#2ecc71"
        COLOR_ROJO = "#e74c3c"
        COLOR_CAFE  = "#d9e620"   # archivo subido pero no marcado como realizado

        conexion2 = conexion_db()
        cur2 = conexion2.cursor(dictionary=True)

        # ===== GENERAR TARJETAS =====
        for act in actividades:

            # 🔥 Revisar si el alumno ya entregó
            cur2.execute("""
                SELECT archivo, realizado 
                FROM entregas
                WHERE alumno_num_cuenta = %s AND actividad_id = %s
            """, (id_usuario_actual, act["id"]))
            entrega = cur2.fetchone()

                        # ===== Determinar color =====
            if entrega:
                archivo = entrega["archivo"]
                realizado = entrega["realizado"]

                if archivo is not None and realizado == 1:
                    borde = COLOR_VERDE                # 🟢 entregado + realizado
                elif archivo is not None and (realizado is None or realizado == 0):
                    borde = COLOR_CAFE                 # 🟤 archivo subido PERO no realizado
                else:
                    borde = COLOR_ROJO                 # 🔴 no entregó nada
            else:
                borde = COLOR_ROJO                     # 🔴 sin registro = pendiente
            # -------- Marco con color dinámico --------
            contenedor = ctk.CTkFrame(
                scroll_index,
                fg_color="#ffffff",
                border_color=borde,
                border_width=3,
                corner_radius=10,
                width=760,
                height=95
            )
            contenedor.pack(padx=5, pady=7)
            contenedor.pack_propagate(False)

            # Título de la actividad
            ctk.CTkLabel(
                contenedor,
                text=f"{act['id']}. {act['nombre_actividad']}",
                text_color="black",
                font=fuente(1, bold=True),
                anchor="w"
            ).pack(anchor="w", padx=10, pady=(5, 0))

            # Descripción recortada
            ctk.CTkLabel(
                contenedor,
                text=(act['descripcion'][:150] + "...") if len(act['descripcion']) > 150 else act['descripcion'],
                text_color="#333",
                font=fuente(-1),
                anchor="w",
                wraplength=720,
                justify="left"
            ).pack(anchor="w", padx=10, pady=(0, 5))

            # Botón para abrir el detalle
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

        cur2.close()
        conexion2.close()

    except Exception as e:
        messagebox.showerror("Error MySQL", f"No se pudieron cargar las actividades:\n{e}")
    finally:
        try:
            conexion.close()
        except:
            pass

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
# FUNCIONES DE Verificar estado de entrega
# =======================
def verificar_estado_entrega():
    global id_usuario_actual, id_actividad_actual

    conexion = conexion_db()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT realizado 
            FROM entregas
            WHERE alumno_num_cuenta = %s AND actividad_id = %s
        """, (id_usuario_actual, id_actividad_actual))
        
        entrega = cursor.fetchone()
        cursor.close()




        # 🔥 Caso 1: NO EXISTE ningún registro → botones habilitados
        if not entrega:
            btn_subir.configure(state="normal", fg_color="#888")
            btn_realizado.configure(state="normal", fg_color="#888")
            return

        # Proteger si la columna NO existe
        if "realizado" not in entrega:
            messagebox.showerror("Error", "La tabla 'entregas' no tiene la columna 'realizado'")
            return

        valor = entrega["realizado"]
        
        # 🔥 Caso 2: Existe un registro pero realizado es NULL o 0 → habilitar
        if valor in (None, 0, "0"):
            btn_subir.configure(state="normal", fg_color="#888")
            btn_realizado.configure(state="normal", fg_color="#888")
            return

        # 🔥 Caso 3: realizado = 1 → bloquear
        if valor in (True, 1, "1"):
            btn_subir.configure(state="disabled", fg_color="#999")
            btn_realizado.configure(state="disabled", fg_color="#999")
            return

    except mysql.connector.Error as err:
        messagebox.showerror("Error MySQL", f"No se pudo verificar estado:\n{err}")
        # 🔍 DEPURACIÓN COMPLETA — muestra lo que recibe
        messagebox.showinfo(
            "DEPURACIÓN",
            f"id_usuario_actual = {id_usuario_actual}\n"
            f"id_actividad_actual = {id_actividad_actual}\n"
            f"entrega completa = {entrega}\n"
            f"valor realizado = {entrega.get('realizado') if entrega else 'NO EXISTE'}"
        )
    finally:
        conexion.close()




# =======================
# FUNCIONES DE DETALLE
# =======================
def abrir_detalle_alumno(id_actividad):
    global id_actividad_actual
    id_actividad_actual = id_actividad

    conexion = conexion_db()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT nombre_actividad, descripcion FROM actividades WHERE id = %s",
            (id_actividad,)
        )
        actividad = cursor.fetchone()
        cursor.close()

        if actividad:
            lbl_detalle_nombre.configure(text=actividad["nombre_actividad"])
            txt_descripcion.delete("1.0", "end")
            txt_descripcion.insert("1.0", actividad["descripcion"] or "")

            mostrar_frame(frame_detalle)

            # 🔥 SOLO revisamos si entregó para bloquear botones
            verificar_estado_entrega()

        else:
            messagebox.showerror("Error", "No se encontró la actividad.")

    except mysql.connector.Error as err:
        messagebox.showerror("Error MySQL", f"No se pudo abrir el detalle:\n{err}")

    finally:
        conexion.close()



def marcar_como_realizado():
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
        # Primero verificar si ya existe
        cursor.execute("""
            SELECT id_entrega FROM entregas
            WHERE alumno_num_cuenta = %s AND actividad_id = %s
            LIMIT 1
        """, (id_usuario_actual, id_actividad_actual))

        existe = cursor.fetchone()

        if existe:
            # ----- SI EXISTE → SOLO ACTUALIZAR -----
            cursor.execute("""
                UPDATE entregas
                SET realizado = 1
                WHERE alumno_num_cuenta = %s AND actividad_id = %s
            """, (id_usuario_actual, id_actividad_actual))
        else:
            # ----- SI NO EXISTE → CREAR SIN DUPLICAR -----
            cursor.execute("""
                INSERT INTO entregas (alumno_num_cuenta, actividad_id, realizado)
                VALUES (%s, %s, 1)
            """, (id_usuario_actual, id_actividad_actual))

        conexion.commit()
        messagebox.showinfo("Éxito", "Actividad marcada como realizada.")

        verificar_estado_entrega()

    except mysql.connector.Error as err:
        messagebox.showerror("Error MySQL", f"No se pudo marcar como realizada:\n{err}")
    finally:
        cursor.close()
        conexion.close()




def subir_archivo_actividad():
    global id_usuario_actual, id_actividad_actual

    if id_actividad_actual is None:
        messagebox.showwarning("Advertencia", "No hay actividad seleccionada.")
        return
    if id_usuario_actual is None:
        messagebox.showwarning("Advertencia", "No hay usuario logueado.")
        return

    # -------------------------
    # Seleccionar archivo real
    # -------------------------
    ruta = filedialog.askopenfilename(title="Seleccionar archivo")
    if not ruta:
        return

    with open(ruta, "rb") as f:
        contenido_archivo = f.read()

    # ================================
    # OBTENER DATOS PARA RENOMBRAR
    # ================================
    conexion = conexion_db()
    if conexion is None:
        return

    cursor = conexion.cursor(dictionary=True)

    try:
        # ---- obtener nombre de la actividad ----
        cursor.execute("SELECT nombre_actividad FROM actividades WHERE id = %s", (id_actividad_actual,))
        act = cursor.fetchone()
        nombre_actividad = act["nombre_actividad"].replace(" ", "_")

        # ---- obtener nombre del alumno ----
        cursor.execute("SELECT nombre_completo FROM alumnos WHERE Num_Cuenta = %s", (id_usuario_actual,))
        alum = cursor.fetchone()
        nombre_alumno = alum["nombre_completo"] #.replace(" ", "_")

        # ---- extensión original ----
        extension = os.path.splitext(ruta)[1]

        # ================================
        # CREAR EL NUEVO NOMBRE DEL ARCHIVO
        # ================================
        nombre_archivo_nuevo = f"{nombre_actividad}_{nombre_alumno}{extension}"

        # -------------------------
        # Verificar si ya existe registro
        # -------------------------
        cursor.execute("""
            SELECT id_entrega FROM entregas
            WHERE alumno_num_cuenta = %s AND actividad_id = %s
            LIMIT 1
        """, (id_usuario_actual, id_actividad_actual))

        existe = cursor.fetchone()

        if existe:
            # actualizar
            cursor.execute("""
                UPDATE entregas
                SET archivo = %s, archivo_nombre = %s, realizado = 1
                WHERE alumno_num_cuenta = %s AND actividad_id = %s
            """, (contenido_archivo, nombre_archivo_nuevo, id_usuario_actual, id_actividad_actual))
        else:
            # insertar
            cursor.execute("""
                INSERT INTO entregas (alumno_num_cuenta, actividad_id, archivo, archivo_nombre)
                VALUES (%s, %s, %s, %s)
            """, (id_usuario_actual, id_actividad_actual, contenido_archivo, nombre_archivo_nuevo))

        conexion.commit()

        messagebox.showinfo("Éxito", f"Archivo subido como:\n{nombre_archivo_nuevo}")

        verificar_estado_entrega()

    except mysql.connector.Error as err:
        messagebox.showerror("Error MySQL", f"No se pudo subir el archivo:\n{err}")

    finally:
        cursor.close()
        conexion.close()


def regresar_y_actualizar():
    cargar_actividades_alumno()   # 🔥 Recarga de colores
    mostrar_frame(frame_index)    # 🔥 Regresa al panel principal



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

btn_regresar = ctk.CTkButton(
    panel_detalle,
    text="Regresar",
    width=160,
    height=35,
    fg_color="#888",
    hover_color="#666",
    font=fuente(),
    command=lambda: regresar_y_actualizar()
)
btn_regresar.place(x=280, y=160)

# =======================
# INICIO EN LOGIN
# =======================
mostrar_frame(frame_login)
root.mainloop()