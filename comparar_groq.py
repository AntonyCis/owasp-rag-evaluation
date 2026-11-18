import json
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

ETIQUETAS = Path("eval/etiquetas_groq.jsonl")
GENERADAS = Path("eval/respuestas_groq.jsonl")


def leer(ruta: Path) -> list[dict]:
    return [json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> None:
    etiquetas = {e["id"]: e for e in leer(ETIQUETAS)}
    generadas = {g["id"]: g for g in leer(GENERADAS)}

    fieles, no_fieles = [], []
    for qid in sorted(etiquetas):
        e = etiquetas[qid]
        if e["tipo"] == "negativa":
            continue  # las negativas honestas se reportan aparte
        s = generadas[qid]["fidelidad"]
        (fieles if e["tipo"] == "fiel" else no_fieles).append(s)

    negativas = [generadas[q]["fidelidad"] for q, e in etiquetas.items() if e["tipo"] == "negativa"]

    print(f"Fieles:    n={len(fieles)}, mediana {np.median(fieles):.3f}")
    print(f"No fieles: n={len(no_fieles)}, mediana {np.median(no_fieles):.3f}")
    print(f"Negativas honestas (aparte): n={len(negativas)}, valores {negativas}")

    y = [1] * len(fieles) + [0] * len(no_fieles)
    x = fieles + no_fieles
    print(f"\nAUC Groq (sin negativas): {roc_auc_score(y, x):.3f}")


if __name__ == "__main__":
    main()