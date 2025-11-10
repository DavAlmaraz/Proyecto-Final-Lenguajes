"""
excel_to_mysql_gui.py
GUI para importar Excel y crear tabla SQL en MySQL Workbench


Requisitos:
 1- Abrir la terminal con la direccion de tu proyecto
 2- intalar las sigientes librerias
 pip install pandas openpyxl mysql-connector-python

"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from conexion import conectar_mysql  # ✅ Importación corregida


class ExcelToMySQLApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Importar Excel a MySQL")
        self.geometry("900x600")

        self.filepath = None
        self.df = None

        # --- Frame superior ---
        frame_top = ttk.Frame(self, padding=10)
        frame_top.pack(fill="x")

        ttk.Button(frame_top, text="Seleccionar archivo Excel", command=self.load_excel).pack(side="left", padx=5)
        self.file_label = ttk.Label(frame_top, text="Ningún archivo seleccionado", foreground="gray")
        self.file_label.pack(side="left")

        # --- Frame medio (vista previa tabla) ---
        frame_mid = ttk.Frame(self)
        frame_mid.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(frame_mid, show="headings")
        self.tree.pack(fill="both", expand=True, side="left")
        vsb = ttk.Scrollbar(frame_mid, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscroll=vsb.set)

        # --- Frame inferior (nombre de tabla) ---
        frame_bottom = ttk.LabelFrame(self, text="Configuración de importación", padding=10)
        frame_bottom.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame_bottom, text="Nombre de tabla:").grid(row=0, column=0, sticky="e")
        self.table_entry = ttk.Entry(frame_bottom)
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
            df.columns = [str(c).strip() for c in df.columns]

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
            self.tree.column(col, width=120, stretch=True)

        for _, row in df.head(max_rows).iterrows():
            self.tree.insert("", "end", values=list(row))

        if len(df) > max_rows:
            self.status_label.config(text=f"Mostrando primeras {max_rows} de {len(df)} filas.")

    # --- Detectar tipo SQL adecuado ---
    def infer_sql_type(self, series: pd.Series) -> str:
        if pd.api.types.is_integer_dtype(series):
            return "INT"
        elif pd.api.types.is_float_dtype(series):
            return "FLOAT"
        elif pd.api.types.is_bool_dtype(series):
            return "BOOLEAN"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "DATETIME"
        else:
            max_len = series.astype(str).map(len).max()
            length = min(max_len + 10, 255)
            return f"VARCHAR({length})"

    # --- Enviar datos a MySQL ---
    def send_to_mysql(self):
        if self.df is None:
            messagebox.showwarning("Advertencia", "Primero carga un archivo Excel.")
            return

        table = self.table_entry.get()
        if not table:
            messagebox.showwarning("Campos incompletos", "Por favor ingresa el nombre de la tabla.")
            return

        # 🔹 Conexión usando configuración centralizada
        conn, cursor = conectar_mysql()

        if not conn:
            messagebox.showerror("Error MySQL", "No se pudo conectar a la base de datos. Revisa la configuración en 'mysql_connection.py'.")
            self.status_label.config(text="Error al conectar a MySQL")
            return

        try:
            # Crear tabla con tipos adecuados
            cols = []
            for col in self.df.columns:
                col_name = col.replace(" ", "_").replace(".", "_")
                sql_type = self.infer_sql_type(self.df[col])
                cols.append(f"`{col_name}` {sql_type}")
            col_defs = ", ".join(cols)
            create_sql = f"CREATE TABLE IF NOT EXISTS `{table}` ({col_defs});"
            cursor.execute(create_sql)
            conn.commit()

            # Insertar datos
            placeholders = ", ".join(["%s"] * len(self.df.columns))
            insert_sql = f"INSERT INTO `{table}` ({', '.join(['`'+c.replace(' ', '_').replace('.', '_')+'`' for c in self.df.columns])}) VALUES ({placeholders})"

            for _, row in self.df.iterrows():
                cursor.execute(insert_sql, tuple(row.values))
            conn.commit()

            messagebox.showinfo("Éxito", f"Tabla '{table}' creada e importada correctamente en MySQL Workbench.")
            self.status_label.config(text=f"Tabla '{table}' creada con éxito.")
        except Exception as e:
            messagebox.showerror("Error MySQL", f"Ocurrió un error durante la importación:\n{e}")
            self.status_label.config(text="Error durante importación")
        finally:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    app = ExcelToMySQLApp()
    app.mainloop()
