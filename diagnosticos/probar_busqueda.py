import sys
sys.path.insert(0, "src")
from index import buscar

for r in buscar("¿Qué riesgo cubre A01:2025 Broken Access Control?"):
    print(r["fuente_seccion"], "|", r["fuente"], "|", round(r["distancia"], 3))