import json
import sys
import time
from pathlib import Path

import numpy as np
import requests

sys.path.insert(0, "src")
from fidelidad import calibrar  # noqa: F401  (mantiene la misma ruta de importación)
from fidelidad import cargar_preguntas, similitud_media
from index import buscar

MODELO_LLM = "qwen2.5:1.5b"
OLLAMA_URL = "http://localhost:11434/api/generate"
SALIDA = Path("eval/respuestas_generadas.jsonl")


def generar(pregunta: str, fragmentos: list[dict]) -> str:
    contexto = "\n\n".join(
        f"[{f['fuente'][:3]} | {f['fuente_seccion']}]\n{f['documento']}" for f in fragmentos
    )
    prompt = (
        "Responde la pregunta usando solo el contexto. "
        "Si el contexto no basta, dilo. Responde en español y de forma breve.\n\n"
        f"Contexto:\n{contexto}\n\nPregunta: {pregunta}\nRespuesta:"
    )
    r = requests.post(
        OLLAMA_URL,
        json={"model": MODELO_LLM, "prompt": prompt, "stream": False},
        timeout=600,
    )
    r.raise_for_status()
    return r.json()["response"].strip()


def main() -> None:
    preguntas = cargar_preguntas()
    resultados = []
    inicio_total = time.time()

    for q in preguntas:
        inicio = time.time()
        fragmentos = buscar(q["pregunta"], k=3)
        respuesta = generar(q["pregunta"], fragmentos)
        fidelidad = similitud_media(respuesta, fragmentos)
        duracion = time.time() - inicio

        resultados.append({
            "id": q["id"],
            "respuesta": respuesta,
            "fidelidad": round(fidelidad, 3),
            "segundos": round(duracion, 1),
        })
        print(f"{q['id']} | fidelidad {fidelidad:.3f} | {duracion:.1f} s")

    with SALIDA.open("w", encoding="utf-8") as f:
        for r in resultados:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    fidelidades = [r["fidelidad"] for r in resultados]
    print(f"\nFidelidad generadas: mediana {np.median(fidelidades):.3f}, "
          f"media {np.mean(fidelidades):.3f}, mínimo {min(fidelidades):.3f}, máximo {max(fidelidades):.3f}")
    print(f"Tiempo total: {(time.time() - inicio_total) / 60:.1f} min")
    print(f"Respuestas guardadas en {SALIDA}")


if __name__ == "__main__":
    main()