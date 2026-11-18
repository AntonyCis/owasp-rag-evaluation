import json
import re
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS = Path("data/chunks.jsonl")
INDEX_DIR = Path("data/index")
COLECCION = "owasp_2025"
MODELO = "paraphrase-multilingual-MiniLM-L12-v2"
PATRON_CATEGORIA = re.compile(r"\bA(0[1-9]|10)\b")

_modelo = None


def cargar_modelo() -> SentenceTransformer:
    """Carga el modelo de embeddings una sola vez por proceso."""
    global _modelo
    if _modelo is None:
        _modelo = SentenceTransformer(MODELO)
    return _modelo


def cargar_chunks() -> list[dict]:
    with CHUNKS.open(encoding="utf-8") as f:
        return [json.loads(linea) for linea in f]


def construir_indice() -> None:
    chunks = cargar_chunks()
    modelo = cargar_modelo()

    cliente = chromadb.PersistentClient(path=str(INDEX_DIR))
    # Reconstruimos la colección desde cero para que el índice siempre refleje el corpus
    try:
        cliente.delete_collection(COLECCION)
    except Exception:
        pass
    coleccion = cliente.create_collection(COLECCION, metadata={"hnsw:space": "cosine"})

    textos = [c["texto"] for c in chunks]
    embeddings = modelo.encode(textos, show_progress_bar=True).tolist()

    coleccion.add(
        ids=[c["chunk_id"] for c in chunks],
        embeddings=embeddings,
        documents=textos,
        metadatas=[
            {
                "fuente": c["fuente"],
                "fuente_seccion": c["fuente_seccion"],
                "categoria": c["fuente"][:3],  # "A01", "A02", ...
            }
            for c in chunks
        ],
    )
    print(f"Indice creado: {coleccion.count()} fragmentos en {INDEX_DIR}")


def buscar(pregunta: str, k: int = 3) -> list[dict]:
    modelo = cargar_modelo()
    cliente = chromadb.PersistentClient(path=str(INDEX_DIR))
    coleccion = cliente.get_collection(COLECCION)

    vector = modelo.encode(pregunta).tolist()
    m = PATRON_CATEGORIA.search(pregunta)

    resultados = []
    if m:
        codigo = m.group(0)  # "A01"
        filtrado = coleccion.query(
            query_embeddings=[vector],
            n_results=k,
            where={"categoria": codigo},
        )
        resultados = _formatear(filtrado)

    if len(resultados) < k:
        # Completa con búsqueda general si la categoría no tiene suficientes fragmentos
        general = coleccion.query(query_embeddings=[vector], n_results=k)
        ids_vistos = {r["chunk_id"] for r in resultados}
        for r in _formatear(general):
            if r["chunk_id"] not in ids_vistos and len(resultados) < k:
                resultados.append(r)

    return resultados


def _formatear(resultado) -> list[dict]:
    return [
        {
            "chunk_id": id_,
            "fuente": meta["fuente"],
            "fuente_seccion": meta["fuente_seccion"],
            "distancia": dist,
            "texto": doc[:200] + "...",
            "documento": doc,
        }
        for id_, meta, dist, doc in zip(
            resultado["ids"][0],
            resultado["metadatas"][0],
            resultado["distances"][0],
            resultado["documents"][0],
        )
    ]


if __name__ == "__main__":
    construir_indice()