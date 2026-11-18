import json
import sys
from pathlib import Path

sys.path.insert(0, "src")
from index import buscar

GENERADAS = Path("eval/respuestas_groq.jsonl")
ETIQUETAS = Path("eval/etiquetas_groq.jsonl")
PREGUNTAS = Path("eval/questions.jsonl")


def leer_jsonl(ruta: Path) -> list[dict]:
    if not ruta.exists():
        return []
    return [json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> None:
    preguntas = {q["id"]: q for q in leer_jsonl(PREGUNTAS)}
    generadas = leer_jsonl(GENERADAS)
    ya = {e["id"] for e in leer_jsonl(ETIQUETAS)}
    pendientes = [g for g in generadas if g["id"] not in ya]
    print(f"Pendientes: {len(pendientes)} de {len(generadas)}\n")

    with ETIQUETAS.open("a", encoding="utf-8") as salida:
        for g in pendientes:
            q = preguntas[g["id"]]
            fragmentos = buscar(q["pregunta"], k=3)

            print("=" * 80)
            print(f"{g['id']} | {q['pregunta']}")
            print("-" * 80)
            print("RESPUESTA GENERADA:")
            print(g["respuesta"])
            print("-" * 80)
            print("REFERENCIA:")
            print(q["respuesta_ref"])
            print("-" * 80)
            print("FRAGMENTOS RECUPERADOS:")
            for f in fragmentos:
                print(f"  [{f['fuente'][:3]} | {f['fuente_seccion']}]")
                print(f"  {f['documento']}\n")

            while True:
                etiqueta = input("Tipo (f = fiel, n = no fiel, r = negativa honesta, q = salir): ").strip().lower()
                if etiqueta in ("f", "n", "r", "q"):
                    break
                print("Responde f, n, r o q.")

            if etiqueta == "q":
                print("Progreso guardado.")
                break

            motivo = ""
            if etiqueta == "n":
                motivo = input("Motivo breve (qué afirmación no está en los fragmentos): ").strip()

            salida.write(json.dumps({
                "id": g["id"],
                "tipo": {"f": "fiel", "n": "no_fiel", "r": "negativa"}[etiqueta],
                "motivo": motivo,
                "fidelidad_metrica": g["fidelidad"],
            }, ensure_ascii=False) + "\n")
            salida.flush()

    print(f"\nEtiquetadas en total: {len(leer_jsonl(ETIQUETAS))} de {len(generadas)}")


if __name__ == "__main__":
    main()