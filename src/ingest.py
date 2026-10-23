import json
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://top10.owasp.org/2025/"
HEADERS = {"User-Agent": "owasp-rag-evaluation/0.1 (proyecto educativo; contacto: AntonyCis en GitHub)"}
RAW_DIR = Path("data/raw")
OUTPUT = Path("data/chunks.jsonl")
PAUSA_SEGUNDOS = 2

# Las URLs de cada categoría las tomamos de la página índice de la pagina de top10.
CATEGORIAS = [
    "A01_2025-Broken_Access_Control",
    "A02_2025-Security_Misconfiguration",
    "A03_2025-Software_Supply_Chain_Failures",
    "A04_2025-Cryptographic_Failures",
    "A05_2025-Injection",
    "A06_2025-Insecure_Design",
    "A07_2025-Authentication_Failures",
    "A08_2025-Software_or_Data_Integrity_Failures",
    "A09_2025-Security_Logging_and_Alerting_Failures",
    "A10_2025-Mishandling_of_Exceptional_Conditions",
]

def descargar(slug: str) -> Path:
    """Descarga el HTML de una categoría y lo guarda en data/raw/. Si ya existe, no lo vuelve a descargar."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    destino = RAW_DIR / f"{slug}.html"
    if destino.exists():
        return destino

    url = BASE_URL + slug + "/"
    respuesta = requests.get(url, headers=HEADERS, timeout=30)
    respuesta.raise_for_status()
    destino.write_text(respuesta.text, encoding="utf-8")
    time.sleep(PAUSA_SEGUNDOS)
    return destino

MAPA_SECCIONES = {
    "Background.": "Antecedentes",
    "Score table.": "Tabla de puntuación",
    "Description.": "Descripción",
    "How to prevent.": "Cómo prevenir",
    "Example attack scenarios.": "Escenarios de ataque",
    "References.": "Referencias",
    "References": "Referencias",
    "List of Mapped CWEs": "CWEs asociados",
}

def extraer_secciones(html_path: Path, slug: str) -> list[dict]:
    """Extrae el texto de cada sección con encabezado conocido, hasta el siguiente encabezado."""
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    fuente = slug.replace("_", " ")
    secciones = []

    for encabezado in soup.find_all(["h1", "h2", "h3"]):
        titulo_original = encabezado.get_text(strip=True)
        if titulo_original not in MAPA_SECCIONES:
            continue

        partes = []
        for elemento in encabezado.find_all_next(["p", "li", "h1", "h2", "h3"]):
            if elemento.name in ("h1", "h2", "h3"):
                break
            texto = elemento.get_text(" ", strip=True)
            if texto:
                partes.append(texto)

        texto_seccion = " ".join(partes)
        # Las listas de CWEs son códigos sin texto explicativo: ruido para la recuperación
        if MAPA_SECCIONES[titulo_original] == "CWEs asociados":
            continue

        if texto_seccion:
            secciones.append({
                "fuente": fuente,
                "fuente_seccion": MAPA_SECCIONES[titulo_original],
                "texto": texto_seccion,
            })
    return secciones

def main() -> None:
    fragmentos = []
    for slug in CATEGORIAS:
        ruta = descargar(slug)
        fragmentos.extend(extraer_secciones(ruta, slug))
        print(f"OK: {slug}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as f:
        for i, frag in enumerate(fragmentos, start=1):
            frag["chunk_id"] = f"c{i:04d}"
            f.write(json.dumps(frag, ensure_ascii=False) + "\n")

    print(f"Listo: {len(fragmentos)} fragmentos en {OUTPUT}")

if __name__ == "__main__":
    main()