import json
from pathlib import Path

chunks = [
    json.loads(linea)
    for linea in Path("data/chunks.jsonl").read_text(encoding="utf-8").splitlines()
]

print("=== Fragmentos de A08 Descripción ===")
for c in chunks:
    if c["fuente"].startswith("A08") and c["fuente_seccion"] == "Descripción":
        print(c["chunk_id"], "|", c["texto"])
        print()

print("=== Recuento de términos clave en A08 ===")
terminos = ["integrity", "integridad", "tampering", "signature", "firma", "transit", "tránsito", "update", "actualiz"]
textos_a08 = " ".join(
    c["texto"].lower() for c in chunks if c["fuente"].startswith("A08")
)
for t in terminos:
    print(f"{t:12} {textos_a08.count(t)}")