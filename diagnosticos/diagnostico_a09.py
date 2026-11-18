import json
import sys
from pathlib import Path

sys.path.insert(0, "src")
from index import buscar

#Parte 1: contenido d elos fragmentos de A09 "Como prevenir"
chunks = [
    json.loads(linea)
    for linea in Path("data/chunks.jsonl").read_text(encoding="utf-8").splitlines()
]

print("=== Fragmentos de AO9 Cómo prevenir ===")
for c in chunks:
    if c["fuente"].startswith("A09") and c["fuente_seccion"] == "Cómo prevenir":
        print(c["chunk_id"], "|", c["texto"][:200], "...")
        print()

#Parte 2: que recupera el sistema para consultas genericas y para q023
consultas = [
    "¿Qué controles se deben aplicar para gestionar el riesgo de componentes y dependencias externas?",
    "¿Qué controles se deben implementar para proteger una aplicación?",
    "¿Qué medidas de control reducen el riesgo en un sistema de software?",
    "¿Cómo puede un atacante comprometer la integridad de los datos o actualizaciones en tránsito?",
]

for p in consultas:
    print("PREGUNTA:", p)
    for r in buscar(p, k=5):
        print("  ", r["fuente"][:3], "|", r["fuente_seccion"], "|", round(r["distancia"], 3))
    print()