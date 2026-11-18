import sys
sys.path.insert(0, "src")
from index import buscar

variantes = [
    "¿Qué controles se deben aplicar para gestionar el riesgo de componentes y dependencias externas?",
    "¿Cómo se deben gestionar las librerías de terceros para reducir riesgos en un proyecto?",
    "¿Qué medidas preventivas existen contra dependencias desactualizadas o no verificadas?",
    "¿Qué debe hacer un equipo de desarrollo para controlar las dependencias que usa su software?",
]

for p in variantes:
    print("PREGUNTA:", p)
    for r in buscar(p, k=3):
        print("  ", r["fuente"][:3], "|", r["fuente_seccion"], "|", round(r["distancia"], 3))
    print()