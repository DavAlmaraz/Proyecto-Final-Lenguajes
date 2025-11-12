"""
excel_to_mysql_gui.py
GUI para importar Excel y crear tabla SQL en MySQL Workbench

Requisitos:
 1- Abrir la terminal con la dirección del proyecto
 2- Instalar librerías:
    pip install pandas openpyxl mysql-connector-python
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from conexion import conectar_mysql
# 🔹 Importamos la función del otro archivo
from email_notify import mostrar_progreso_envio

class ExcelToMySQLApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Importar Excel de Alumnos a MySQL")
        self.geometry("900x600")

        self.filepath = None
        self.df = None

        # --- Frame superior ---
        frame_top = ttk.Frame(self, padding=10)
        frame_top.pack(fill="x")

        ttk.Button(frame_top, text="Seleccionar archivo Excel", command=self.load_excel).pack(side="left", padx=5)
        self.file_label = ttk.Label(frame_top, text="Ningún archivo seleccionado", foreground="gray")
        self.file_label.pack(side="left")

        # --- Frame medio (vista previa) ---
        frame_mid = ttk.Frame(self)
        frame_mid.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(frame_mid, show="headings")
        self.tree.pack(fill="both", expand=True, side="left")
        vsb = ttk.Scrollbar(frame_mid, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscroll=vsb.set)

        # --- Frame inferior ---
        frame_bottom = ttk.LabelFrame(self, text="Configuración de importación", padding=10)
        frame_bottom.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame_bottom, text="Nombre de tabla:").grid(row=0, column=0, sticky="e")
        self.table_entry = ttk.Entry(frame_bottom)
        self.table_entry.insert(0, "alumnos")
        self.table_entry.grid(row=0, column=1, padx=5, pady=3)

        ttk.Button(frame_bottom, text="Enviar a MySQL", command=self.send_to_mysql).grid(row=1, column=0, columnspan=2, pady=8)

        # Footer
        self.status_label = ttk.Label(self, text="Listo", relief="sunken", anchor="w")
        self.status_label.pack(fill="x", side="bottom")

    # --- Cargar Excel ---
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
            self.file_label.config(text=filepath)
            self.show_table(df)
            self.status_label.config(text=f"{len(df)} filas cargadas correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo Excel:\n{e}")
            self.status_label.config(text="Error al cargar Excel")

    # --- Mostrar DataFrame en Treeview ---
    def show_table(self, df: pd.DataFrame, max_rows=1000):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)

        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, stretch=True)

        for _, row in df.head(max_rows).iterrows():
            self.tree.insert("", "end", values=list(row))

    # --- Enviar datos a MySQL ---
    def send_to_mysql(self):
        if self.df is None:
            messagebox.showwarning("Advertencia", "Primero carga un archivo Excel.")
            return

        table = self.table_entry.get().strip()
        if not table:
            messagebox.showwarning("Advertencia", "Por favor ingresa un nombre de tabla.")
            return

        conn, cursor = conectar_mysql()
        if not conn:
            messagebox.showerror("Error", "No se pudo conectar a MySQL.")
            return

        try:
            # 🔹 Crear tabla fija de alumnos
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS `{table}` (
                    num_cuenta INT PRIMARY KEY,
                    nombre_completo VARCHAR(150),
                    correo VARCHAR(100),
                    clave VARCHAR(100)
                );
            """)
            conn.commit()

            # --- Detectar columnas equivalentes ---
            col_map = {
                "num_cuenta": None,
                "nombre_completo": None,
                "correo": None,
                "clave": None
            }

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

            # --- Verificar que se hayan detectado todas las columnas ---
            faltantes = [k for k, v in col_map.items() if v is None]
            if faltantes:
                raise ValueError(f"No se encontraron las columnas requeridas: {', '.join(faltantes)} en el Excel")

            # --- Insertar datos ---
            insert_sql = f"""
                INSERT INTO `{table}` (num_cuenta, nombre_completo, correo, clave)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    nombre_completo=VALUES(nombre_completo),
                    correo=VALUES(correo),
                    clave=VALUES(clave);
            """

            for _, row in self.df.iterrows():
                cursor.execute(insert_sql, (
                    int(row[col_map["num_cuenta"]]),
                    str(row[col_map["nombre_completo"]]),
                    str(row[col_map["correo"]]),
                    str(row[col_map["clave"]])
                ))


            conn.commit()
            messagebox.showinfo("Éxito", f"Se registraron {len(self.df)} alumnos correctamente en '{table}'.")
            self.status_label.config(text=f"Tabla '{table}' creada y datos insertados correctamente.")
            # 🔹 Aquí se abre la ventana del envío de correos
            mostrar_progreso_envio(self, table)

        except Exception as e:
            messagebox.showerror("Error MySQL", f"Ocurrió un error durante la importación:\n{e}")
            self.status_label.config(text="Error durante la importación.")
        finally:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    app = ExcelToMySQLApp()
    app.mainloop()
