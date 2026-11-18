import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import requests

sys.path.insert(0, "src")
from fidelidad import cargar_preguntas, similitud_media
from index import buscar

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
SALIDA = Path("eval/respuestas_groq.jsonl")

PROMPT = (
    "Responde la pregunta usando solo el contexto. "
    "Si el contexto no basta, dilo. Responde en español y de forma breve.\n\n"
    "Contexto:\n{contexto}\n\nPregunta: {pregunta}\nRespuesta:"
)


def generar_groq(prompt: str, reintentos: int = 5) -> str:
    for intento in range(reintentos):
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
            },
            timeout=60,
        )
        if r.status_code == 429:
            espera = 20 * (intento + 1)
            print(f"  límite alcanzado, esperando {espera} s...")
            time.sleep(espera)
            continue
        r.raise_for_status()
        time.sleep(3)  # pausa normal entre preguntas
        return r.json()["choices"][0]["message"]["content"].strip()
    raise RuntimeError("Se agotaron los reintentos por límite de uso")


def main() -> None:
    resultados = []
    inicio_total = time.time()

    for q in cargar_preguntas():
        fragmentos = buscar(q["pregunta"], k=3)
        contexto = "\n\n".join(
            f"[{f['fuente'][:3]} | {f['fuente_seccion']}]\n{f['documento']}" for f in fragmentos
        )
        respuesta = generar_groq(PROMPT.format(contexto=contexto, pregunta=q["pregunta"]))
        fidelidad = similitud_media(respuesta, fragmentos)
        resultados.append({"id": q["id"], "respuesta": respuesta, "fidelidad": round(fidelidad, 3)})
        print(f"{q['id']} | fidelidad {fidelidad:.3f}")

    with SALIDA.open("w", encoding="utf-8") as f:
        for r in resultados:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    fid = [r["fidelidad"] for r in resultados]
    print(f"\nModelo: {GROQ_MODEL}")
    print(f"Fidelidad: mediana {np.median(fid):.3f}, media {np.mean(fid):.3f}")
    print(f"Tiempo total: {time.time() - inicio_total:.1f} s")
    print(f"Guardado en {SALIDA}")


if __name__ == "__main__":
    main()