import customtkinter as ctk
from tkinter import messagebox
import subprocess
import sys
from PIL import Image

# =======================
# Colores y tema
# =======================
COLOR_FONDO = "#f8cfa0"
COLOR_FORM = "#6b0000"
COLOR_PANEL = "white"
COLOR_TEXTO = "white"
COLOR_BOTON = "#333333"

# =======================
# Ventana principal
# =======================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Registro de Usuario")
root.geometry("1200x900")
root.configure(fg_color=COLOR_FONDO)
root.resizable(False, False)

# =======================
# Encabezado
# =======================
header = ctk.CTkFrame(root, fg_color=COLOR_FORM, height=100, corner_radius=0)
header.pack(fill="x", side="top")

try:
    img = Image.open("image.png")
    img = img.resize((60, 60), Image.LANCZOS)
    icon_img = ctk.CTkImage(light_image=img, dark_image=img, size=(60, 60))
    icon_label = ctk.CTkLabel(header, image=icon_img, text="")
    icon_label.pack(side="left", padx=(20, 10), pady=20)
except Exception:
    icon_label = ctk.CTkLabel(header, text="👤", font=ctk.CTkFont(size=45))
    icon_label.pack(side="left", padx=(20, 10), pady=20)

titulo = ctk.CTkLabel(
    header, text="Registro de Usuario", font=ctk.CTkFont(family="Arial Black", size=28), text_color=COLOR_TEXTO
)
titulo.pack(side="left", padx=10)

# =======================
# Frame registro
# =======================
frame = ctk.CTkFrame(root, fg_color=COLOR_FORM, width=480, height=460, corner_radius=15)
frame.place(relx=0.5, rely=0.55, anchor="center")
frame.pack_propagate(False)

titulo_frame = ctk.CTkLabel(
    frame, text="Ingrese sus datos", font=ctk.CTkFont(family="Arial Black", size=20), text_color=COLOR_TEXTO
)
titulo_frame.pack(pady=(20, 15))

panel = ctk.CTkFrame(frame, fg_color=COLOR_PANEL, width=360, height=260, corner_radius=20)
panel.pack(pady=10)
panel.pack_propagate(False)

# =======================
# Entradas con labels arriba
# =======================
lbl_nombre = ctk.CTkLabel(panel, text="Nombre completo (Texto)", font=ctk.CTkFont(size=13, weight="bold"), text_color="black", anchor="w")
lbl_nombre.pack(fill="x", padx=20, pady=(15, 5))
entrada_nombre = ctk.CTkEntry(panel, placeholder_text="Ej. Juan Pérez", width=280, height=40,
                              corner_radius=10, border_color="#cccccc", fg_color="#f9f9f9", text_color="black",
                              font=ctk.CTkFont(size=13))
entrada_nombre.pack(padx=20, pady=(0, 12))

lbl_cuenta = ctk.CTkLabel(panel, text="Número de cuenta (Número)", font=ctk.CTkFont(size=13, weight="bold"), text_color="black", anchor="w")
lbl_cuenta.pack(fill="x", padx=20, pady=(0, 5))
entrada_cuenta = ctk.CTkEntry(panel, placeholder_text="Ej. 526768", width=280, height=40,
                              corner_radius=10, border_color="#cccccc", fg_color="#f9f9f9", text_color="black",
                              font=ctk.CTkFont(size=13))
entrada_cuenta.pack(padx=20, pady=(0, 12))

lbl_clave = ctk.CTkLabel(panel, text="Contraseña (Texto)", font=ctk.CTkFont(size=13, weight="bold"), text_color="black", anchor="w")
lbl_clave.pack(fill="x", padx=20, pady=(0, 5))
entrada_clave = ctk.CTkEntry(panel, placeholder_text="********", width=280, height=40,
                             corner_radius=10, border_color="#cccccc", fg_color="#f9f9f9",
                             text_color="black", show="*", font=ctk.CTkFont(size=13))
entrada_clave.pack(padx=20, pady=(0, 8))

# =======================
# Funciones
# =======================
def registrar():
    if entrada_nombre.get() and entrada_cuenta.get() and entrada_clave.get():
        messagebox.showinfo("Registro exitoso", "Usuario registrado correctamente.")
        root.destroy()
        subprocess.Popen([sys.executable, "login.py"])
    else:
        messagebox.showerror("Error", "Por favor completa todos los campos.")

def abrir_login():
    root.destroy()
    subprocess.Popen([sys.executable, "login.py"])

# =======================
# Botones
# =======================
boton_registrar = ctk.CTkButton(
    frame, text="Registrar", command=registrar, width=220, height=45, corner_radius=15,
    fg_color=COLOR_BOTON, hover_color="#222222",
    font=ctk.CTkFont(family="Arial", size=14, weight="bold")
)
boton_registrar.pack(pady=(25, 2))

boton_login = ctk.CTkButton(
    frame, text="Volver al Login", command=abrir_login, width=220, height=40, corner_radius=15,
    fg_color="#888888", hover_color="#666666",
    font=ctk.CTkFont(family="Arial", size=13, weight="bold")
)
boton_login.pack(pady=(5, 10))

# =======================
# Bucle principal
# =======================
root.mainloop()
