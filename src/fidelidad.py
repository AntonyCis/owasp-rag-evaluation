import json
import re
from pathlib import Path

import numpy as np

from index import buscar, cargar_modelo

PREGUNTAS = Path("eval/questions.jsonl")


def frases(texto: str) -> list[str]:
    partes = re.split(r"(?<=[.!?])\s+", texto.strip())
    return [p for p in partes if len(p.split()) >= 4]


def similitud_media(respuesta: str, fragmentos: list[dict]) -> float:
    """Media, sobre las frases de la respuesta, de su similitud máxima con algún fragmento recuperado."""
    oraciones = frases(respuesta)
    if not oraciones or not fragmentos:
        return 0.0
    m = cargar_modelo()
    v = m.encode(oraciones, normalize_embeddings=True)
    f = m.encode([x["documento"] for x in fragmentos], normalize_embeddings=True)
    return float((v @ f.T).max(axis=1).mean())


def cargar_preguntas() -> list[dict]:
    return [
        json.loads(linea)
        for linea in PREGUNTAS.read_text(encoding="utf-8").splitlines()
        if linea.strip()
    ]


def calibrar() -> None:
    """Controles: referencias con sus propios fragmentos (positivo) y con los de otra pregunta (negativo)."""
    preguntas = cargar_preguntas()
    propios, ajenos = [], []

    for i, q in enumerate(preguntas):
        otra = preguntas[(i + 1) % len(preguntas)]
        s_prop = similitud_media(q["respuesta_ref"], buscar(q["pregunta"], k=3))
        s_aj = similitud_media(q["respuesta_ref"], buscar(otra["pregunta"], k=3))
        propios.append(s_prop)
        ajenos.append(s_aj)
        print(f"{q['id']} | propios {s_prop:.3f} | ajenos {s_aj:.3f}")

    print(f"\nPropios: mediana {np.median(propios):.3f}, mínimo {min(propios):.3f}")
    print(f"Ajenos:  mediana {np.median(ajenos):.3f}, máximo {max(ajenos):.3f}")


if __name__ == "__main__":
    calibrar()