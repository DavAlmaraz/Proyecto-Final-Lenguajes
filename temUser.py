import json
import tempfile

# Guardar los datos en un archivo temporal
def abrir_mantenimiento(nombre, cuenta):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    data = {"nombre": nombre, "cuenta": cuenta}
    json.dump(data, open(temp.name, "w"))
    root.destroy()
    subprocess.Popen([sys.executable, "mantenimiento.py", temp.name])
