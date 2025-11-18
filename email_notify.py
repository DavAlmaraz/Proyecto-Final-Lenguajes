import customtkinter as ctk
import threading
import time
from conexion import conectar_mysql
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import smtplib
from tkinter import messagebox

# ==============================
# CONFIGURACIÓN SMTP
# ==============================
SMTP_CONFIG = {
    "host": "smtp.gmail.com",
    "port": 587,
    "user": "gabomxhost@gmail.com",
    "password": "rqjt frgy zudq pixb"  # ⚠️ Asegúrate de manejar la contraseña de manera segura
}

# ==============================
# FUNCIONES DE BASE DE DATOS
# ==============================
def obtener_alumnos_desde_mysql(tabla="alumnos"):
    try:
        conn, cursor = conectar_mysql()
        if not conn:
            return []
        cursor.execute(f"SELECT nombre_completo, correo, clave FROM `{tabla}`;")
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultados
    except Exception as e:
        print(f"Error: {e}")
        return []

# ==============================
# ENVÍO DE CORREOS
# ==============================
def enviar_correo_registro(nombre, correo_destino, clave):
    try:
        remitente = formataddr(("Sistema Académico", SMTP_CONFIG["user"]))
        subject = "📚 Registro Exitoso - Sistema de Gestión de Alumnos"

        html = f"""
        <html><body style="font-family: Poppins; background-color:#f6f9fc; padding: 20px;">
            <div style="max-width:600px;margin:auto;background:#fff;padding:20px;
            border-radius:10px;box-shadow:0 0 10px rgba(0,0,0,0.1)">
                <h2 style="color:#2b6cb0;text-align:center;">¡Registro exitoso, {nombre}!</h2>
                <p>Tu registro se completó correctamente.</p>
                <div style="background:#edf2f7;padding:10px 15px;border-left:4px solid #2b6cb0;">
                    <p><b>Datos de acceso:</b></p>
                    <p>Correo: <b>{correo_destino}</b></p>
                    <p>Contraseña: <b>{clave}</b></p>
                </div>
                <p style="font-size:12px;color:#718096;">⚠️ No compartas tu contraseña ni este correo.</p>
            </div>
        </body></html>
        """
        msg = MIMEMultipart("alternative")
        msg["From"] = remitente
        msg["To"] = correo_destino
        msg["Subject"] = subject
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(SMTP_CONFIG["host"], SMTP_CONFIG["port"]) as server:
            server.starttls()
            server.login(SMTP_CONFIG["user"], SMTP_CONFIG["password"])
            server.sendmail(remitente, correo_destino, msg.as_string())

        return True
    except Exception as e:
        print(f"Error al enviar a {correo_destino}: {e}")
        return False

# ==============================
# INTERFAZ CON CTk (VENTANA INDEPENDIENTE)
# ==============================
def mostrar_progreso_envio(tabla="alumnos", master=None):
    lista_alumnos = obtener_alumnos_desde_mysql(tabla)
    if not lista_alumnos:
        messagebox.showerror("Error", "No se encontraron registros en la base de datos.")
        return

    total = len(lista_alumnos)
    enviados = 0

    # --- Ventana independiente ---
    win = ctk.CTk()
    win.title("📤 Enviando correos...")
    win.geometry("600x500")
    win.resizable(False, False)

    ctk.CTkLabel(win, text="Enviando correos de confirmación...",
                 font=("Poppins", 16, "bold"),
                 text_color="#2b6cb0").pack(pady=10)

    barra = ctk.CTkProgressBar(win, width=500)
    barra.set(0)
    barra.pack(pady=10)

    lbl_progreso = ctk.CTkLabel(win, text=f"0 de {total} enviados (0%)", font=("Poppins", 12))
    lbl_progreso.pack(pady=5)

    txt_estado = ctk.CTkTextbox(win, width=550, height=200)
    txt_estado.pack(pady=10)
    txt_estado.configure(state="disabled")

    btn_aceptar = ctk.CTkButton(win, text="Aceptar", command=win.destroy, width=200)
    btn_aceptar.pack(pady=10)
    btn_aceptar.pack_forget()  # oculto hasta que termine

    # --- Funciones auxiliares ---
    def agregar_log(mensaje):
        def inner():
            txt_estado.configure(state="normal")
            txt_estado.insert("end", mensaje + "\n")
            txt_estado.see("end")
            txt_estado.configure(state="disabled")
        win.after(0, inner)

    def actualizar_barra(i):
        porcentaje = i / total
        def inner():
            barra.set(porcentaje)
            lbl_progreso.configure(text=f"{i} de {total} enviados ({porcentaje*100:.1f}%)")
        win.after(0, inner)

    def segundos_a_texto(seg):
        minutos = int(seg // 60)
        segundos = int(seg % 60)
        return f"{minutos:02d}:{segundos:02d}"

    # --- Hilo de envío ---
    def enviar_todo():
        nonlocal enviados
        inicio_total = time.time()

        for i, (nombre, correo, clave) in enumerate(lista_alumnos, start=1):
            exito = enviar_correo_registro(nombre, correo, clave)
            if exito:
                enviados += 1
                agregar_log(f"✅ Enviado a {nombre} ({correo})")
            else:
                agregar_log(f"❌ Falló el envío a {nombre} ({correo})")

            actualizar_barra(i)

        agregar_log(f"\n✅ Envío completado: {enviados}/{total} correctos.")
        tiempo_total = time.time() - inicio_total
        agregar_log(f"⏱️ Tiempo total: {segundos_a_texto(tiempo_total)}")

        # Mostrar botón aceptar al final
        def mostrar_boton():
            btn_aceptar.pack(pady=10)
        win.after(0, mostrar_boton)

    threading.Thread(target=enviar_todo, daemon=True).start()

    win.mainloop()

# ==============================
# DEMO LOCAL
# ==============================
if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.geometry("500x250")
    root.title("Demo Envío Correo CTk")

    ctk.CTkLabel(root, text="📬 Enviar correos desde MySQL",
                 font=("Poppins", 14, "bold"), text_color="#2b6cb0").pack(pady=30)

    ctk.CTkButton(root, text="Iniciar envío de correos",
                  command=lambda: mostrar_progreso_envio("alumnos"),
                  width=250, height=40, fg_color="#6b0000", hover_color="#4b0000").pack()

    root.mainloop()
