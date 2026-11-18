import json
import re
import sys
from pathlib import Path

sys.path.insert(0, "src")
from index import buscar

PREGUNTAS = Path("eval/questions.jsonl")
SECCION_GENERAL = "Descripción"


def codigo(texto: str) -> str | None:
    """Extrae el código de categoría, por ejemplo 'A01', de cualquier formato de nombre."""
    m = re.search(r"A\d{2}", texto)
    return m.group(0) if m else None

def cargar_preguntas() -> list[dict]:
    return [
        json.loads(linea)
        for linea in PREGUNTAS.read_text(encoding="utf-8").splitlines()
        if linea.strip()
    ]


def evaluar(k: int = 3) -> None:
    preguntas = cargar_preguntas()
    hits_cat = hits_estricta = hits_flexible = 0

    for q in preguntas:
        resultados = buscar(q["pregunta"], k=k)
        cat_ref = codigo(q["fuente"])
        seccion_ref = q["fuente_seccion"]

        # Resultados de la categoria correcta, en el orden en que los devolvio el sistema
        misma_cat = [r for r in resultados if codigo(r["fuente"]) == cat_ref]

        hit_cat = bool(misma_cat)
        #Estricta
        hit_estricta = any(r["fuente_seccion"] == seccion_ref for r in misma_cat)
        #Flexible
        hit_flexible = any(
            r["fuente_seccion"] in (seccion_ref, SECCION_GENERAL) for r in misma_cat
        )
        

        hits_cat += hit_cat
        hits_estricta += hit_estricta
        hits_flexible += hit_flexible

        primero = resultados[0]
        print(
            f"{q['id']} | cat {'OK' if hit_cat else 'NO'} "
            f"| sec estricta {'OK' if hit_estricta else 'NO'} "
            f"| sec flexible {'OK' if hit_flexible else 'NO'} "
            f"| top1: {codigo(primero['fuente'])} {primero['fuente_seccion']}"
        )

    n = len(preguntas)
    print(f"\nRecall@{k} categoría:        {hits_cat}/{n}")
    print(f"Recall@{k} sección estricta: {hits_estricta}/{n}")
    print(f"Recall@{k} sección flexible: {hits_flexible}/{n}")


if __name__ == "__main__":
    evaluar(k=3)