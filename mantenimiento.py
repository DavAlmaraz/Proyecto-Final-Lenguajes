import customtkinter as ctk
from ttkbootstrap.icons import Icon
import subprocess
import sys
import json
import os

# =========================
# Configuración inicial
# =========================
ctk.set_appearance_mode("light")

def abrir_registro():
    """Abre la ventana de registro de alumnos."""
    root.destroy()
    subprocess.Popen([sys.executable, "registrarAlumnos.py"])

def crear_mantenimiento(usuario_nombre="Administrador", usuario_cuenta="000000"):
    global root, menu_visible, ignorar_click
    root = ctk.CTk()
    root.title("Página en mantenimiento")
    root.geometry("900x600")
    root.resizable(False, False)
    root.configure(fg_color="#fff4e6")

    menu_visible = False
    ignorar_click = False  # Evita que el clic que abre el menú lo cierre de inmediato

    # =========================
    # Funciones del menú lateral
    # =========================
    def toggle_menu(event=None):
        """Abre o cierra el menú lateral."""
        global menu_visible, ignorar_click
        ignorar_click = True  # Evita que el mismo clic dispare 'click_fuera'
        if not menu_visible:
            mostrar_menu()
        else:
            ocultar_menu()

        # Restablecer bandera después de un breve retraso
        root.after(200, lambda: set_ignore(False))

    def set_ignore(value: bool):
        """Cambia el estado de la variable ignorar_click."""
        global ignorar_click
        ignorar_click = value

    def mostrar_menu():
        """Despliega el menú lateral con animación."""
        global menu_visible
        menu_visible = True
        x = 900
        menu_frame.place(x=x, y=0)
        for i in range(30):
            x -= 10
            menu_frame.place(x=x, y=0)
            root.update()
        menu_frame.place(x=600, y=0)

    def ocultar_menu(event=None):
        """Oculta el menú lateral si se hace clic fuera."""
        global menu_visible
        if not menu_visible:
            return
        x = 600
        for i in range(30):
            x += 10
            menu_frame.place(x=x, y=0)
            root.update()
        menu_frame.place_forget()
        menu_visible = False

    def cerrar_sesion():
        """Cierra sesión, borra el archivo temporal y vuelve al login."""
        # Si el archivo JSON fue pasado por parámetro, eliminarlo
        if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
            try:
                os.remove(sys.argv[1])
            except Exception:
                pass  # Si ya fue eliminado o no existe, ignorar

        root.destroy()
        subprocess.Popen([sys.executable, "login.py"])  # Cambia a tu archivo de login

    # =========================
    # Barra superior
    # =========================
    barra_superior = ctk.CTkFrame(root, fg_color="#ffe8cc", height=70, corner_radius=0)
    barra_superior.pack(fill="x", side="top")

    # Ícono usuario (clickable)
    try:
        user_icon = Icon("person-fill").photoimage(size=(36, 36))
        lbl_user_icon = ctk.CTkLabel(barra_superior, image=user_icon, text="")
    except Exception:
        lbl_user_icon = ctk.CTkLabel(
            barra_superior, text="👤", font=ctk.CTkFont(size=30), text_color="#6b0000"
        )

    lbl_user_icon.pack(side="right", padx=(15, 10))
    lbl_user_icon.bind("<Button-1>", toggle_menu)  # Clic para abrir/cerrar

    # =========================
    # Contenido principal
    # =========================
    frame = ctk.CTkFrame(root, fg_color="#fff4e6", corner_radius=15)
    frame.pack(expand=True, fill="both", padx=40, pady=40)

    lbl = ctk.CTkLabel(
        frame,
        text="🚧 Página en mantenimiento 🚧\n\nEstamos trabajando para mejorar la experiencia.",
        font=ctk.CTkFont(size=24, weight="bold"),
        text_color="#c2410c",
        justify="center"
    )
    lbl.pack(expand=True, pady=(40, 0))

    # =========================
    # Botón agregar alumnos
    # =========================
    try:
        add_icon = Icon("person-plus-fill").photoimage(size=(28, 28))
        boton_agregar = ctk.CTkButton(
            frame,
            image=add_icon,
            text="Agregar Alumno",
            width=220,
            height=50,
            corner_radius=20,
            fg_color="#6b0000",
            hover_color="#4b0000",
            command=abrir_registro,
            font=ctk.CTkFont(size=16, weight="bold")
        )
    except Exception:
        boton_agregar = ctk.CTkButton(
            frame,
            text="➕ Agregar Alumno",
            width=220,
            height=50,
            corner_radius=20,
            fg_color="#6b0000",
            hover_color="#4b0000",
            command=abrir_registro,
            font=ctk.CTkFont(size=16, weight="bold")
        )

    boton_agregar.pack(pady=(10, 40))

    # =========================
    # Menú lateral oculto
    # =========================
    menu_frame = ctk.CTkFrame(root, width=300, height=600, fg_color="#f8e0b8", corner_radius=0)
    menu_frame.place_forget()

    # Contenido del menú lateral
    ctk.CTkLabel(
        menu_frame,
        text="👤 Información del Usuario",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color="#4b0000"
    ).pack(pady=(20, 10))

    ctk.CTkLabel(
        menu_frame,
        text=f"Nombre:\n{usuario_nombre}\n\nCuenta:\n{usuario_cuenta}",
        font=ctk.CTkFont(size=14),
        text_color="#333",
        justify="left"
    ).pack(pady=10, padx=20, anchor="w")

    ctk.CTkButton(
        menu_frame,
        text="Cerrar sesión",
        fg_color="#6b0000",
        hover_color="#4b0000",
        corner_radius=10,
        command=cerrar_sesion
    ).pack(pady=(30, 10))

    # =========================
    # Detectar clic fuera del menú
    # =========================
    def click_fuera(event):
        global ignorar_click
        if ignorar_click:  # si acaba de abrirse el menú, ignorar este clic
            return
        x, y = event.x_root, event.y_root
        widget = root.winfo_containing(x, y)
        if menu_visible and widget not in (menu_frame, lbl_user_icon):
            ocultar_menu()

    root.bind("<Button-1>", click_fuera)

    root.mainloop()


# =========================
# Ejecución directa
# =========================
if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        with open(sys.argv[1], "r") as f:
            data = json.load(f)
        nombre = data.get("nombre", "Desconocido")
        cuenta = data.get("cuenta", "000000")
    else:
        nombre = "Invitado"
        cuenta = "000000"

    crear_mantenimiento(usuario_nombre=nombre, usuario_cuenta=cuenta)
