##  ESTA pantalla no se va a usar,  no tiene nigun fin en este proyecto
##  pero por si las dudas no se eliminara el archivo

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import subprocess
import sys

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

# Número de cuenta
lbl_num_cuenta = ctk.CTkLabel(panel, text="Número de Cuenta", text_color="black", anchor="w",
                              font=ctk.CTkFont(size=15, weight="bold"))
lbl_num_cuenta.pack(fill="x", padx=20, pady=(20, 6))

entrada_cuenta = ctk.CTkEntry(panel, placeholder_text="Ej. 526768", width=280, height=40, corner_radius=10,
                              border_color="#cccccc", fg_color="#f9f9f9", text_color="black",
                              font=ctk.CTkFont(size=13))
entrada_cuenta.pack(padx=20, pady=(0, 12))

# Clave
lbl_clave = ctk.CTkLabel(panel, text="Clave", text_color="black", anchor="w",
                         font=ctk.CTkFont(size=15, weight="bold"))
lbl_clave.pack(fill="x", padx=20, pady=(0, 6))

entrada_clave = ctk.CTkEntry(panel, placeholder_text="********", width=280, height=40, corner_radius=10,
                             border_color="#cccccc", fg_color="#f9f9f9", text_color="black",
                             show="*", font=ctk.CTkFont(size=13))
entrada_clave.pack(padx=20, pady=(0, 8))

# =======================
# Funciones
# =======================
def iniciar_sesion():
    cuenta = entrada_cuenta.get()
    clave = entrada_clave.get()
    if cuenta == "526768" and clave == "1234":
        messagebox.showinfo("Acceso permitido", "Bienvenido al sistema.")
        root.destroy()
        subprocess.Popen([sys.executable, "index_alumno.py"])
    else:
        messagebox.showerror("Error", "Número de cuenta o clave incorrectos.")


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
boton_login.pack(pady=(25, 0))  # ajustamos margen inferior a 0 para subir el siguiente botón

boton_registrar = ctk.CTkButton(
    frame_login, text="Registrarse", width=220, height=40, corner_radius=15,
    fg_color="#888888", hover_color="#666666", command=abrir_registro,
    font=ctk.CTkFont(family="Arial", size=13, weight="bold")
)
boton_registrar.pack(pady=(5, 10))  # pequeño margen superior en lugar de negativo


# =======================
# Bucle principal
# =======================
root.mainloop()
