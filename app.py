import os
import sys

import chromadb
import gradio as gr
import requests

sys.path.insert(0, "src")
from index import COLECCION, INDEX_DIR, buscar, construir_indice

PROVEEDOR = os.getenv("PROVEEDOR_LLM", "ollama")

PROMPT = (
    "Responde la pregunta usando solo el contexto. "
    "Si el contexto no basta, dilo. Responde en español y de forma breve.\n\n"
    "Contexto:\n{contexto}\n\nPregunta: {pregunta}\nRespuesta:"
)

AVISO = (
    "Respuesta generada por un modelo pequeño. Verifica siempre contra los fragmentos mostrados: "
    "el sistema mide adherencia al contexto, no veracidad."
)

def asegurar_indice() -> None:
    """Construye el índice si no existe (por ejemplo, en el primer arranque de Spaces)."""
    cliente = chromadb.PersistentClient(path=str(INDEX_DIR))
    try:
        cliente.get_collection(COLECCION)
    except Exception:
        construir_indice()

def contexto_de(fragmentos: list[dict]) -> str:
    return "\n\n".join(
        f"[{f['fuente'][:3]} | {f['fuente_seccion']}]\n{f['documento']}" for f in fragmentos
    )

def generar_ollama(prompt: str) -> str:
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "qwen2.5:1.5b", "prompt": prompt, "stream": False},
        timeout=600,
    )
    r.raise_for_status()
    return r.json()["response"].strip()

def generar_groq(prompt: str) -> str:
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
        json={
            "model": os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()

def responder(pregunta: str) -> tuple[str, str]:
    if not pregunta.strip():
        return "Escribe una pregunta.", ""
    fragmentos = buscar(pregunta, k=3)
    prompt = PROMPT.format(contexto=contexto_de(fragmentos), pregunta=pregunta)
    respuesta = generar_groq(prompt) if PROVEEDOR == "groq" else generar_ollama(prompt)
    fuentes = "\n\n".join(
        f"**{f['fuente'][:3]} · {f['fuente_seccion']}**\n\n{f['texto']}" for f in fragmentos
    )
    return respuesta, fuentes

asegurar_indice()

with gr.Blocks(title="OWASP Top 10 2025 · RAG") as demo:
    gr.Markdown("# Consulta OWASP Top 10 2025\nRespuestas basadas en el documento oficial, con sus fuentes.")
    entrada = gr.Textbox(label="Pregunta", placeholder="¿Qué riesgo cubre A01:2025 Broken Access Control?")
    boton = gr.Button("Consultar")
    gr.Markdown("### Respuesta")
    salida = gr.Markdown()
    gr.Markdown("### Fragmentos recuperados")
    fuentes = gr.Markdown()
    gr.Markdown(f"> {AVISO}")

    boton.click(responder, inputs=entrada, outputs=[salida, fuentes])
    entrada.submit(responder, inputs=entrada, outputs=[salida, fuentes])

if __name__ == "__main__":
    demo.launch()