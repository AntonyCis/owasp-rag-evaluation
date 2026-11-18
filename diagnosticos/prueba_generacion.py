import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, "src")
from index import buscar

MODELO = "qwen2.5:1.5b"
OLLAMA_URL = "http://localhost:11434/api/generate"

preguntas = [
    json.loads(linea)
    for linea in Path("eval/questions.jsonl").read_text(encoding="utf-8").splitlines()
][:3]

for q in preguntas:
    fragmentos = buscar(q["pregunta"], k=3)
    contexto = "\n\n".join(
        f"[{f['fuente'][:3]} | {f['fuente_seccion']}]\n{f['texto']}" for f in fragmentos
    )
    prompt = (
        "Responde la pregunta usando solo el contexto. "
        "Si el contexto no basta, dilo. Responde en español y de forma breve.\n\n"
        f"Contexto:\n{contexto}\n\nPregunta: {q['pregunta']}\nRespuesta:"
    )

    inicio = time.time()
    r = requests.post(
        OLLAMA_URL,
        json={"model": MODELO, "prompt": prompt, "stream": False},
        timeout=600,
    )
    r.raise_for_status()
    duracion = time.time() - inicio

    print(f"=== {q['id']} ({duracion:.1f} s) ===")
    print("Pregunta:", q["pregunta"])
    print("Respuesta:", r.json()["response"].strip())
    print("Referencia:", q["respuesta_ref"])
    print()