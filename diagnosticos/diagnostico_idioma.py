import sys
sys.path.insert(0, "src")
from index import buscar

preguntas = [
    "¿Qué riesgos aborda la categoría A05:2025 Injection?",
    "What risks does the A05:2025 Injection category address?",
]

for p in preguntas:
    print("PREGUNTA:", p)
    for r in buscar(p, k=5):
        print("  ", r["fuente_seccion"], "|", r["fuente"][:3], "|", round(r["distancia"], 3))
    print()