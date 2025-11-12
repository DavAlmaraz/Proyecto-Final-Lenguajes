"""
email_notifier.py
Envía correos de confirmación mostrando una pestaña de progreso si el registro fue exitoso.
Al finalizar, muestra un mensaje temporal de "Envío completado" y luego un botón para cerrar o revisar.
"""

import smtplib
import time
import threading
import tkinter as tk
from tkinter import ttk
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from smtplib import SMTPException
from mysql.connector import Error
from conexion import conectar_mysql  # ✅ Tu módulo de conexión


# ======================================================
# CONFIGURACIÓN SMTP
# ======================================================
SMTP_CONFIG = {
    "host": "smtp.gmail.com",
    "port": 587,
    "user": "gabomxhost@gmail.com",
    "password": "rqjt frgy zudq pixb"
}


# ======================================================
# BASE DE DATOS
# ======================================================
def obtener_alumnos_desde_mysql(tabla="alumnos"):
    try:
        conn, cursor = conectar_mysql()
        if not conn:
            raise Exception("No se pudo conectar a MySQL.")
        cursor.execute(f"SELECT nombre_completo, correo, clave FROM `{tabla}`;")
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultados
    except Error as e:
        print(f"❌ Error MySQL: {e}")
        return []
    except Exception as e:
        print(f"⚠️ Error inesperado: {e}")
        return []


# ======================================================
# ENVÍO DE CORREOS
# ======================================================
def enviar_correo_registro(nombre, correo_destino, clave):
    """Envía un correo individual."""
    try:
        remitente = formataddr(("Sistema Académico", SMTP_CONFIG["user"]))
        subject = "📚 Registro Exitoso - Sistema de Gestión de Alumnos"

        html = f"""
        <html><body style="font-family: Arial; background-color:#f6f9fc; padding: 20px;">
            <div style="max-width:600px;margin:auto;background:#fff;padding:20px;
            border-radius:10px;box-shadow:0 0 10px rgba(0,0,0,0.1)">
                <h2 style="color:#2b6cb0;text-align:center;">¡Registro exitoso, {nombre}!</h2>
                <p>Tu registro en el sistema se ha completado correctamente.</p>
                <div style="background:#edf2f7;padding:10px 15px;border-left:4px solid #2b6cb0;">
                    <p><b>Datos de acceso:</b></p>
                    <p>Correo: <b>{correo_destino}</b></p>
                    <p>Contraseña: <b>{clave}</b></p>
                </div>
                <p style="font-size:12px;color:#718096;">⚠️ No compartas tu contraseña ni este correo con nadie.</p>
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
        print(f"⚠️ Error al enviar correo a {correo_destino}: {e}")
        return False


# ======================================================
# INTERFAZ DE PROGRESO MEJORADA
# ======================================================
def mostrar_progreso_envio(ventana_padre, tabla="alumnos"):
    lista_alumnos = obtener_alumnos_desde_mysql(tabla)
    if not lista_alumnos:
        tk.messagebox.showerror("Error", "No se encontraron registros en la base de datos.")
        return

    total = len(lista_alumnos)
    enviados = 0
    tiempos_envio = []

    win = tk.Toplevel(ventana_padre)
    win.title("📤 Enviando correos...")
    win.geometry("560x569")
    win.configure(bg="#f8fafc")
    win.resizable(False, False)

    tk.Label(
        win, text="Enviando correos de confirmación...",
        bg="#f8fafc", font=("Arial", 12, "bold"), fg="#2b6cb0"
    ).pack(pady=10)

    barra = ttk.Progressbar(win, length=450, mode="determinate", maximum=total)
    barra.pack(pady=10)

    lbl_progreso = tk.Label(win, text=f"0 de {total} enviados (0%)", bg="#f8fafc", font=("Arial", 10))
    lbl_progreso.pack()

    lbl_tiempo = tk.Label(win, text="⏳ Estimando tiempo restante...", bg="#f8fafc", font=("Arial", 9, "italic"), fg="#555")
    lbl_tiempo.pack(pady=5)

    txt_estado = tk.Text(win, height=10, width=65, state="disabled", wrap="word", font=("Consolas", 9))
    txt_estado.pack(padx=10, pady=10)

    lbl_final = tk.Label(win, text="", bg="#f8fafc", fg="#2b6cb0", font=("Arial", 10, "bold"))
    btn_aceptar = tk.Button(win, text="Aceptar", bg="#2b6cb0", fg="white", font=("Arial", 10, "bold"),
                            relief="flat", cursor="hand2", command=win.destroy)
    btn_aceptar.pack_forget()  # Ocultamos al inicio

    def agregar_log(mensaje):
        txt_estado.config(state="normal")
        txt_estado.insert("end", mensaje + "\n")
        txt_estado.see("end")
        txt_estado.config(state="disabled")
        win.update_idletasks()

    def segundos_a_texto(seg):
        minutos = int(seg // 60)
        segundos = int(seg % 60)
        return f"{minutos:02d}:{segundos:02d}"

    def enviar_todo():
        nonlocal enviados
        inicio_total = time.time()

        for i, (nombre, correo, clave) in enumerate(lista_alumnos, start=1):
            try:
                exito = enviar_correo_registro(nombre, correo, clave)
                if exito:
                    enviados += 1
                    agregar_log(f"✅ Enviado a {nombre} ({correo})")
                else:
                    agregar_log(f"❌ Falló el envío a {nombre} ({correo})")
            except Exception as e:
                agregar_log(f"⚠️ Error con {correo}: {e}")

            duracion = time.time() - inicio_total
            promedio = duracion / i
            restante = promedio * (total - i)
            porcentaje = (i / total) * 100

            barra["value"] = i
            lbl_progreso.config(text=f"{i} de {total} enviados ({porcentaje:.1f}%)")
            lbl_tiempo.config(text=f"⏳ Estimado restante: {segundos_a_texto(restante)}")


        # --- Calcular totales ---
        no_enviados = total - enviados
        total_tiempo = time.time() - inicio_total
        agregar_log(f"\n✅ Envío completado: {enviados}/{total} correctos.")
        agregar_log(f"⏱️ Tiempo total: {segundos_a_texto(total_tiempo)}")

        # --- Frame final elegante ---
        frame_resumen = tk.Frame(win, bg="#f8fafc")
        frame_resumen.pack(pady=15)

        # ✅ Enviados
        lbl_enviados = tk.Label(
            frame_resumen,
            text=f"✅ Enviados correctamente: {enviados}",
            fg="#16a34a",  # Verde elegante
            bg="#f8fafc",
            font=("Arial", 11, "bold")
        )
        lbl_enviados.pack(pady=2)

        # ❌ No enviados
        lbl_no_enviados = tk.Label(
            frame_resumen,
            text=f"❌ No enviados: {no_enviados}",
            fg="#dc2626",  # Rojo elegante
            bg="#f8fafc",
            font=("Arial", 11, "bold")
        )
        lbl_no_enviados.pack(pady=2)

        # ⏱️ Tiempo total
        lbl_tiempo_total = tk.Label(
            frame_resumen,
            text=f"⏱️ Tiempo total: {segundos_a_texto(total_tiempo)}",
            fg="#2563eb",  # Azul elegante
            bg="#f8fafc",
            font=("Arial", 11, "bold")
        )
        lbl_tiempo_total.pack(pady=2)

        # --- Botón de cierre ---
        btn_aceptar.pack(pady=15)


        # Mostrar el botón "Aceptar" inmediatamente
        btn_aceptar.pack(pady=10)

    threading.Thread(target=enviar_todo, daemon=True).start()


# ======================================================
# DEMO LOCAL
# ======================================================
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Demo Envío desde Base de Datos")
    root.geometry("420x220")
    root.configure(bg="#f0f4f8")

    tk.Label(root, text="📬 Enviar correos desde la base de datos MySQL",
             font=("Arial", 11, "bold"), bg="#f0f4f8", fg="#2b6cb0").pack(pady=30)

    tk.Button(
        root, text="Iniciar envío de correos",
        font=("Arial", 10), bg="#2b6cb0", fg="white",
        padx=15, pady=5, relief="flat", cursor="hand2",
        command=lambda: mostrar_progreso_envio(root, "alumnos")
    ).pack()

    root.mainloop()
