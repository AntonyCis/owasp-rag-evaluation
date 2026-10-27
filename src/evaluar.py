import json
import re
import sys
from pathlib import Path

sys.path.insert(0, "src")
from index import buscar

PREGUNTAS = Path("eval/questions.jsonl")


def codigo(texto: str) -> str | None:
    """Extrae el código de categoría, por ejemplo 'A01', de cualquier formato de nombre."""
    m = re.search(r"A\d{2}", texto)
    return m.group(0) if m else None


def evaluar(k: int = 3) -> None:
    preguntas = [
        json.loads(linea)
        for linea in PREGUNTAS.read_text(encoding="utf-8").splitlines()
        if linea.strip()
    ]

    hits_categoria = 0
    hits_seccion = 0

    for q in preguntas:
        resultados = buscar(q["pregunta"], k=k)
        cat_ref = codigo(q["fuente"])

        hit_cat = any(codigo(r["fuente"]) == cat_ref for r in resultados)
        hit_sec = any(
            codigo(r["fuente"]) == cat_ref and r["fuente_seccion"] == q["fuente_seccion"]
            for r in resultados
        )

        hits_categoria += hit_cat
        hits_seccion += hit_sec

        primero = resultados[0]
        print(
            f"{q['id']} | cat {'OK' if hit_cat else 'NO'} | sec {'OK' if hit_sec else 'NO'} "
            f"| top1: {codigo(primero['fuente'])} {primero['fuente_seccion']}"
        )

    n = len(preguntas)
    print(f"\nRecall@{k} categoría: {hits_categoria}/{n}")
    print(f"Recall@{k} sección:   {hits_seccion}/{n}")


if __name__ == "__main__":
    evaluar(k=3)