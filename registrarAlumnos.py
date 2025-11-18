import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from conexion import conectar_mysql  # tu módulo de conexión
from email_notify import mostrar_progreso_envio  # importa tu función de envío de correos
import subprocess, sys

# =========================
# Configuración global del tema
# =========================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
CTK_FONT = ("Poppins", 14)


class ExcelToMySQLApp(ctk.CTk):
    def __init__(self, master=None):
        self.root = master if master else ctk.CTk()
        self.is_root = master is None

        self.root.title("Importar Excel de Alumnos a MySQL")
        self.root.geometry("950x620")
        self.root.resizable(False, False)
        self.root.configure(fg_color="#fff4e6")

        self.filepath = None
        self.df = None

        # =========================
        # Función para regresar al menú principal
        # =========================
        def regresar_menu():
            self.root.destroy()
            subprocess.Popen([sys.executable, "menu_principal.py"])  # <-- Cambia el nombre si tu menú usa otro archivo

        # =========================
        # Frame superior
        # =========================
        frame_top = ctk.CTkFrame(self.root, fg_color="#f8e0b8", corner_radius=10)
        frame_top.pack(fill="x", padx=10, pady=(10, 5))

        # --- Botón/icono regresar (sin imágenes, solo símbolo Unicode) ---
        self.btn_regresar = ctk.CTkButton(
            frame_top,
            text="←",                # icono vectorial Unicode
            width=40,
            height=40,
            font=ctk.CTkFont("Poppins", 24, "bold"),  # tamaño grande elegante
            fg_color="transparent",
            text_color="black",
            hover_color="#e9bf90",
            command=regresar_menu
        )
        self.btn_regresar.pack(side="left", padx=10)

        # --- Botón seleccionar archivo ---
        self.select_btn = ctk.CTkButton(
            frame_top, text="📁 Seleccionar archivo Excel",
            width=220, height=40, corner_radius=10,
            fg_color="#6b0000", hover_color="#4b0000",
            font=ctk.CTkFont(CTK_FONT[0], 14, "bold"),
            command=self.load_excel
        )
        self.select_btn.pack(side="left", padx=10, pady=10)

        self.file_label = ctk.CTkLabel(frame_top, text="Ningún archivo seleccionado", text_color="gray",
                                       font=ctk.CTkFont(CTK_FONT[0], 12))
        self.file_label.pack(side="left", padx=10)

        # =========================
        # Frame medio
        # =========================
        frame_mid = ctk.CTkFrame(self.root, fg_color="#fff4e6", corner_radius=10)
        frame_mid.pack(fill="both", expand=True, padx=10, pady=5)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#f5f5f5", foreground="#000000",
                        fieldbackground="#f5f5f5", rowheight=28, font=CTK_FONT)
        style.map("Treeview", background=[("selected", "#6b0000")])

        self.tree = ttk.Treeview(frame_mid, show="headings")
        self.tree.pack(fill="both", expand=True, side="left", padx=5, pady=5)

        vsb = ttk.Scrollbar(frame_mid, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y", pady=5)
        self.tree.configure(yscroll=vsb.set)

        # =========================
        # Frame inferior
        # =========================
        self.frame_bottom = ctk.CTkFrame(self.root, fg_color="#f8e0b8", corner_radius=10)
        self.frame_bottom.pack(fill="x", padx=10, pady=(5, 10))

        lbl_table = ctk.CTkLabel(self.frame_bottom, text="Nombre de la tabla:", font=ctk.CTkFont(CTK_FONT[0], 14))
        lbl_table.grid(row=0, column=0, sticky="e", padx=5, pady=10)

        self.table_entry = ctk.CTkEntry(self.frame_bottom, placeholder_text="alumnos", width=200,
                                        font=ctk.CTkFont(CTK_FONT[0], 13))
        self.table_entry.insert(0, "alumnos")
        self.table_entry.grid(row=0, column=1, padx=5, pady=10)

        send_btn = ctk.CTkButton(
            self.frame_bottom, text="🚀 Enviar a MySQL",
            width=180, height=40, corner_radius=10,
            fg_color="#6b0000", hover_color="#4b0000",
            font=ctk.CTkFont(CTK_FONT[0], 14, "bold"),
            command=self.send_to_mysql
        )
        send_btn.grid(row=1, column=0, columnspan=2, pady=10)

        # =========================
        # Footer
        # =========================
        self.status_label = ctk.CTkLabel(self.root, text="Listo", anchor="w",
                                         fg_color="#fff4e6", height=30,
                                         font=ctk.CTkFont(CTK_FONT[0], 12))
        self.status_label.pack(fill="x", side="bottom")

    # =========================
    # FUNCIONES PRINCIPALES
    # =========================
    def load_excel(self):
        ftypes = [("Archivos Excel", "*.xlsx *.xls")]
        filepath = filedialog.askopenfilename(title="Seleccionar archivo Excel", filetypes=ftypes)
        if not filepath:
            return
        try:
            df = pd.read_excel(filepath)
            df = df.fillna("")
            df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

            self.df = df
            self.filepath = filepath
            self.file_label.configure(text=filepath)
            self.show_table(df)
            self.status_label.configure(text=f"{len(df)} filas cargadas correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo Excel:\n{e}")
            self.status_label.configure(text="Error al cargar Excel")

    def show_table(self, df: pd.DataFrame, max_rows=1000):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, stretch=True)
        for _, row in df.head(max_rows).iterrows():
            self.tree.insert("", "end", values=list(row))

    def send_to_mysql(self):
        if self.df is None:
            messagebox.showwarning("Advertencia", "Primero carga un archivo Excel.")
            return

        table = self.table_entry.get().strip()
        if not table:
            messagebox.showwarning("Advertencia", "Por favor ingresa un nombre de tabla.")
            return

        try:
            conn, cursor = conectar_mysql()
            if not conn or not cursor:
                raise ConnectionError("No se pudo conectar a MySQL")

            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS `{table}` (
                    num_cuenta INT PRIMARY KEY,
                    nombre_completo VARCHAR(150),
                    correo VARCHAR(100),
                    clave VARCHAR(100)
                );
            """)
            conn.commit()

            col_map = {"num_cuenta": None, "nombre_completo": None, "correo": None, "clave": None}
            for col in self.df.columns:
                c = col.lower()
                if "cuenta" in c or "id" in c:
                    col_map["num_cuenta"] = col
                elif "nombre" in c:
                    col_map["nombre_completo"] = col
                elif "correo" in c or "email" in c:
                    col_map["correo"] = col
                elif "clave" in c or "contraseña" in c or "password" in c:
                    col_map["clave"] = col

            faltantes = [k for k, v in col_map.items() if v is None]
            if faltantes:
                raise ValueError(f"No se encontraron las columnas requeridas: {', '.join(faltantes)} en el Excel")

            insert_sql = f"""
                INSERT INTO `{table}` (num_cuenta, nombre_completo, correo, clave)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    nombre_completo=VALUES(nombre_completo),
                    correo=VALUES(correo),
                    clave=VALUES(clave);
            """

            for _, row in self.df.iterrows():
                try:
                    cursor.execute(insert_sql, (
                        int(row[col_map["num_cuenta"]]),
                        str(row[col_map["nombre_completo"]]),
                        str(row[col_map["correo"]]),
                        str(row[col_map["clave"]])
                    ))
                except Exception:
                    continue

            conn.commit()
            messagebox.showinfo("Éxito", f"Se registraron {len(self.df)} alumnos correctamente en '{table}'.")
            self.status_label.configure(text=f"Tabla '{table}' creada y datos insertados correctamente.")

            send_email_btn = ctk.CTkButton(
                self.frame_bottom, text="📧 Enviar correos de confirmación",
                width=250, height=40, corner_radius=10,
                fg_color="#2b6cb0", hover_color="#1e3a8a",
                font=ctk.CTkFont(CTK_FONT[0], 14, "bold"),
                command=lambda: mostrar_progreso_envio(table, master=self.root)
            )
            send_email_btn.grid(row=2, column=0, columnspan=2, pady=10)

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            messagebox.showerror("Error MySQL", f"Ocurrió un error durante la importación:\n{e}")
            self.status_label.configure(text="Error durante la importación.")
        finally:
            try:
                cursor.close()
            except:
                pass
            try:
                conn.close()
            except:
                pass


def abrir_excel_import():
    nueva_ventana = ctk.CTkToplevel()   # 🔥 NUEVA VENTANA
    ExcelToMySQLApp(master=nueva_ventana)

