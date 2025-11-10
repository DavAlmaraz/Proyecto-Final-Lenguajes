import customtkinter as ctk
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

root = ctk.CTk()
root.title("Index Alumno")
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
except Exception as e:
    print("No se pudo cargar la imagen:", e)
    icon_label = ctk.CTkLabel(header, text="👤", font=ctk.CTkFont(size=45))
    icon_label.pack(side="left", padx=(20, 10), pady=20)

titulo = ctk.CTkLabel(
    header, text="Alumno", font=ctk.CTkFont(family="Arial Black", size=28), text_color=COLOR_TEXTO
)
titulo.pack(side="left", padx=10)

# =======================
# Cuadro principal
# =======================
frame_main = ctk.CTkFrame(root, fg_color=COLOR_FORM, width=700, height=550, corner_radius=15)
frame_main.pack(pady=60)
frame_main.pack_propagate(False)

panel = ctk.CTkFrame(frame_main, fg_color=COLOR_PANEL, width=500, height=400, corner_radius=20)
panel.pack(pady=40)
panel.pack_propagate(False)

titulo_actividades = ctk.CTkLabel(
    panel, text="Actividades", font=ctk.CTkFont(family="Arial Black", size=20), text_color="black"
)
titulo_actividades.pack(pady=(20, 25))

def crear_actividad(nombre):
    act_frame = ctk.CTkFrame(panel, fg_color="#f9f9f9", border_color="black", border_width=1, corner_radius=10)
    act_frame.pack(fill="x", padx=40, pady=8)

    label = ctk.CTkLabel(act_frame, text=nombre, text_color="black", anchor="w", font=ctk.CTkFont(size=14))
    label.pack(side="left", padx=15, pady=10)

    boton = ctk.CTkButton(
        act_frame, text="➜", width=35, height=30, fg_color=COLOR_BOTON,
        hover_color="#222222", corner_radius=8, font=ctk.CTkFont(size=15, weight="bold")
    )
    boton.pack(side="right", padx=10, pady=5)

crear_actividad("Actividad 1")
crear_actividad("Actividad 2")
crear_actividad("Actividad 3")

root.mainloop()

