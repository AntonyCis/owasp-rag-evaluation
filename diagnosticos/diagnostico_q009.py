import sys
sys.path.insert(0, "src")
from index import buscar

variantes = [
    "¿Qué sucede cuando un servidor se despliega manteniendo cuentas predeterminadas con contraseñas de fábrica?",
    "¿Qué sucede cuando un servidor se despliega manteniendo cuentas predeterminadas?",
    "¿Qué riesgo implica dejar sin modificar las configuraciones por defecto de un servidor en producción?",
    "¿Qué ocurre si un servidor se pone en producción sin cambiar sus valores de fábrica?",
]

for p in variantes:
    print("PREGUNTA:", p)
    for r in buscar(p, k=3):
        print(" ", r["fuente"][:3], "|", r["fuente_seccion"], "|", round(r["distancia"], 3))
    print()