import sys
sys.path.insert(0, "src")
from index import buscar

variantes = [
    "¿De qué manera un atacante compromete un sistema a través de dependencias externas en el desarrollo moderno?",
    "¿Cómo puede un atacante comprometer un sistema mediante librerías de terceros?",
    "¿Qué riesgo implica usar componentes de código abierto de terceros en un proyecto?",
    "¿Qué ocurre si un atacante inyecta código malicioso en una dependencia que usa el proyecto?",
]

for p in variantes:
    print("PREGUNTA", p)
    for r in buscar(p, k=3):
        print(" ", r["fuente"][:3], "|", r["fuente_seccion"], "|", round(r["distancia"], 3))
    print()