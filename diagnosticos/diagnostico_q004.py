import sys
sys.path.insert(0, "src")
from index import buscar

for r in buscar("¿Qué riesgos aborda la categoría A05:2025 Injection?", k=3):
    print(r["fuente_seccion"], "|", r["fuente"], "|", round(r["distancia"], 3))
    print("   ", r["texto"][:200])
    print()