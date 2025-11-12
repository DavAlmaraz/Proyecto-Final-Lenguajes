import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import subprocess
import sys
import json
import tempfile
from conexion import conectar_mysql  # tu módulo central de conexión

# =======================
# Colores
# =======================
COLOR_FONDO = "#f8cfa0"
COLOR_FORM = "#6b0000"
COLOR_BOTON = "#333333"
COLOR_TEXTO = "black"
COLOR_PANEL = "white"

# =======================
# Ventana principal
# =======================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Formulario de Inicio de Sesión")
root.geometry("1200x900")
root.configure(fg_color=COLOR_FONDO)
root.resizable(False, False)

# =======================
# FRANJA SUPERIOR
# =======================
franja_superior = ctk.CTkFrame(root, fg_color=COLOR_FONDO, height=160, corner_radius=0)
franja_superior.pack(fill="x", side="top")

# Logo
try:
    logo = ctk.CTkImage(light_image=Image.open("LOGO_GARZA.jpg"), size=(600, 150))
    logo_label = ctk.CTkLabel(franja_superior, image=logo, text="")
    logo_label.pack(side="left", padx=0, pady=0)
except Exception:
    logo_label = ctk.CTkLabel(
        franja_superior, text="[LOGO]", font=ctk.CTkFont(size=30, weight="bold"), text_color="white"
    )
    logo_label.pack(side="left", padx=20, pady=20)

titulo_label = ctk.CTkLabel(
    franja_superior,
    text="Sistema de Gestión de Alumnos",
    font=ctk.CTkFont(family="Arial Black", size=30),
    text_color=COLOR_TEXTO
)
titulo_label.pack(side="left", padx=30, pady=0)

# =======================
# Frame login
# =======================
frame_login = ctk.CTkFrame(root, fg_color=COLOR_FORM, width=480, height=460, corner_radius=15)
frame_login.place(relx=0.5, rely=0.55, anchor="center")
frame_login.pack_propagate(False)

titulo_login = ctk.CTkLabel(
    frame_login, text="INICIO DE SESIÓN", font=ctk.CTkFont(family="Arial Black", size=20), text_color=COLOR_TEXTO
)
titulo_login.pack(pady=(20, 15))

panel = ctk.CTkFrame(frame_login, fg_color=COLOR_PANEL, width=360, height=260, corner_radius=20)
panel.pack(pady=10)
panel.pack_propagate(False)

# =======================
# Validaciones (máscaras)
# =======================
def validar_cuenta(value):
    """Permite solo números y máximo 6 dígitos."""
    return value.isdigit() and len(value) <= 6 or value == ""

def validar_clave(value):
    """Permite solo números y máximo 4 dígitos."""
    return value.isdigit() and len(value) <= 4 or value == ""

validacion_cuenta = root.register(validar_cuenta)
validacion_clave = root.register(validar_clave)

# =======================
# Campos
# =======================
lbl_num_cuenta = ctk.CTkLabel(panel, text="Número de Cuenta / Usuario", text_color="black", anchor="w",
                              font=ctk.CTkFont(size=15, weight="bold"))
lbl_num_cuenta.pack(fill="x", padx=20, pady=(20, 6))

entrada_cuenta = ctk.CTkEntry(panel, placeholder_text="Ej. 526768 o admin", width=280, height=40, corner_radius=10,
                              border_color="#cccccc", fg_color="#f9f9f9", text_color="black",
                              font=ctk.CTkFont(size=13),
                              validate="key", validatecommand=(validacion_cuenta, "%P"))
entrada_cuenta.pack(padx=20, pady=(0, 12))

lbl_clave = ctk.CTkLabel(panel, text="Clave", text_color="black", anchor="w",
                         font=ctk.CTkFont(size=15, weight="bold"))
lbl_clave.pack(fill="x", padx=20, pady=(0, 6))

entrada_clave = ctk.CTkEntry(panel, placeholder_text="****", width=280, height=40, corner_radius=10,
                             border_color="#cccccc", fg_color="#f9f9f9", text_color="black",
                             show="*", font=ctk.CTkFont(size=13),
                             validate="key", validatecommand=(validacion_clave, "%P"))
entrada_clave.pack(padx=20, pady=(0, 8))

# =======================
# Funciones
# =======================
def abrir_mantenimiento(nombre, cuenta):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    data = {"nombre": nombre, "cuenta": cuenta}
    json.dump(data, open(temp.name, "w"))
    root.destroy()
    subprocess.Popen([sys.executable, "mantenimiento.py", temp.name])

def iniciar_sesion():
    cuenta = entrada_cuenta.get().strip()
    clave = entrada_clave.get().strip()

    if not cuenta or not clave:
        messagebox.showwarning("Campos vacíos", "Por favor, completa todos los campos.")
        return

    conn, cur = conectar_mysql()
    if not conn:
        return

    try:
        try:
            cur.close()
        except Exception:
            pass
        cursor = conn.cursor(dictionary=True)

        # Verificar en ambas tablas
        cursor.execute("SELECT num_cuenta, clave, nombre_completo FROM alumnos WHERE num_cuenta = %s AND clave = %s", (cuenta, clave))
        alumno = cursor.fetchone()

        admin = None
        if not alumno:
            cursor.execute("SELECT cuentaAd, clave, nombre FROM administrador WHERE cuentaAd = %s AND clave = %s", (cuenta, clave))
            admin = cursor.fetchone()

        if alumno:
            nombre_alumno = alumno.get("nombre_completo") or alumno.get("num_cuenta")
            messagebox.showinfo("Bienvenido", f"Inicio de sesión correcto (Alumno): {nombre_alumno}")
            abrir_mantenimiento(nombre_alumno, cuenta)

        elif admin:
            nombre_admin = admin.get("nombre") or admin.get("cuentaAd")
            messagebox.showinfo("Bienvenido", f"Inicio de sesión correcto (Administrador): {nombre_admin}")
            abrir_mantenimiento(nombre_admin, cuenta)
        else:
            messagebox.showerror("Error", "Número de cuenta/usuario o clave incorrectos.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al iniciar sesión:\n{e}")
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conn.close()

def abrir_registro():
    root.destroy()
    subprocess.Popen([sys.executable, "register.py"])

# =======================
# Botones
# =======================
boton_login = ctk.CTkButton(
    frame_login, text="Iniciar Sesión", width=220, height=45, corner_radius=15,
    fg_color=COLOR_BOTON, hover_color="#222222", command=iniciar_sesion,
    font=ctk.CTkFont(family="Arial", size=14, weight="bold")
)
boton_login.pack(pady=(25, 0))

boton_registrar = ctk.CTkButton(
    frame_login, text="Registrarse", width=220, height=40, corner_radius=15,
    fg_color="#888888", hover_color="#666666", command=abrir_registro,
    font=ctk.CTkFont(family="Arial", size=13, weight="bold")
)
boton_registrar.pack(pady=(5, 10))

# =======================
# Bucle principal
# =======================
root.mainloop()
