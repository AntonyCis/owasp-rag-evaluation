import json
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

ETIQUETAS = Path("eval/etiquetas_fidelidad.jsonl")
GENERADAS = Path("eval/respuestas_generadas.jsonl")


def leer(ruta: Path) -> list[dict]:
    return [json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> None:
    etiquetas = {e["id"]: e for e in leer(ETIQUETAS)}
    generadas = {g["id"]: g for g in leer(GENERADAS)}

    fieles, no_fieles = [], []
    print(f"{'id':6} {'humana':8} {'similitud':10}")
    for qid in sorted(etiquetas):
        e = etiquetas[qid]
        s = generadas[qid]["fidelidad"]
        humana = "fiel" if e["fiel"] else "no fiel"
        print(f"{qid:6} {humana:8} {s:.3f}")
        (fieles if e["fiel"] else no_fieles).append(s)

    print(f"\nFieles:    n={len(fieles)}, mediana {np.median(fieles):.3f}, rango {min(fieles):.3f}-{max(fieles):.3f}")
    print(f"No fieles: n={len(no_fieles)}, mediana {np.median(no_fieles):.3f}, rango {min(no_fieles):.3f}-{max(no_fieles):.3f}")

    y = [1] * len(fieles) + [0] * len(no_fieles)
    x = fieles + no_fieles
    auc = roc_auc_score(y, x)
    print(f"\nAUC (capacidad de la similitud para separar fieles de no fieles): {auc:.3f}")
    print("0.5 = no separa; 1.0 = separa perfectamente.")


if __name__ == "__main__":
    main()