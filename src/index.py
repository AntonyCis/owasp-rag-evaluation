import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS = Path("data/chunks.jsonl")
INDEX_DIR = Path("data/index")
COLECCION = "owasp_2025"
MODELO = "paraphrase-multilingual-MiniLM-L12-v2"

def cargar_chunks() -> list[dict]:
    with CHUNKS.open(encoding="utf-8") as f:
        return [json.loads(linea) for linea in f]

def construir_indice() -> None:
    chunks = cargar_chunks()
    modelo = SentenceTransformer(MODELO)

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
            {"fuente": c["fuente"], "fuente_seccion": c["fuente_seccion"]}
            for c in chunks
        ],
    )
    print(f"Indice creado: {coleccion.count()} fragmentos en {INDEX_DIR}")

def buscar(pregunta: str, k: int = 3) -> list[dict]:
    modelo = SentenceTransformer(MODELO)
    cliente = chromadb.PersistentClient(path=str(INDEX_DIR))
    coleccion = cliente.get_collection(COLECCION)

    resultado = coleccion.query(
        query_embeddings=[modelo.encode(pregunta).tolist()],
        n_results=k,
    )
    return [
        {
            "chunk_id": id_,
            "fuente": meta["fuente"],
            "fuente_seccion": meta["fuente_seccion"],
            "distancia": dist,
            "texto": doc[:200] + "...",
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

