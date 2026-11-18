import sys
sys.path.insert(0, "src")
from index import buscar

for r in buscar("¿Qué riesgo cubre A01:2025 Broken Access Control?", k=3):
    print(r["fuente"][:3], "|", r["fuente_seccion"], "|", round(r["distancia"], 3))