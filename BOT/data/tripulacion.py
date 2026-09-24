import json
import os

"""
Módulo para gestionar la tripulación del rol.
Carga y guarda los miembros en tripulacion.json
"""

DB_FILE = "tripulacion.json"

# ---------- CARGAR TRIPULACION ----------
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        tripulacion = {}
        for k, v in data.items():
            try:
                tripulacion[int(k)] = v
            except ValueError:
                print(f"Clave inválida en {DB_FILE}: {k}")
else:
    tripulacion = {}
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(tripulacion, f, ensure_ascii=False, indent=4)

# ---------- GUARDAR TRIPULACION ----------
def guardar_tripulacion():
    """Guarda el diccionario tripulacion en tripulacion.json"""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(tripulacion, f, ensure_ascii=False, indent=4)
