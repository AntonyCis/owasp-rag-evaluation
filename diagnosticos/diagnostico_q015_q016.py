import sys
sys.path.insert(0, "src")
from index import buscar

consultas = {
    "q015": "¿Qué buenas prácticas se deben aplicar para evitar vulnerabilidades de inyección en las consultas de bases de datos?",
    "q016": "¿Cómo aborda la edición 2025 el riesgo derivado de librerías y componentes con vulnerabilidades conocidas?",
}

for qid, p in consultas.items():
    print(f"=== {qid} ===")
    for r in buscar(p, k=5):
        print("  ", r["fuente"][:3], "|", r["fuente_seccion"], "|", round(r["distancia"], 3))
        print("     ", r["texto"][:150])
    print()