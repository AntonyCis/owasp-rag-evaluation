# OWASP RAG Evaluation

Sistema RAG (Retrieval-Augmented Generation) que responde preguntas sobre el **OWASP Top 10 2025**, con un framework de evaluación medible para su calidad de recuperación y de respuesta.

El objetivo no es solo construir un chatbot, sino **medir** si las respuestas son correctas, fieles a la fuente y basadas en el documento correcto.

## Corpus

- **Fuente:** OWASP Top 10 2025 (https://top10.owasp.org/2025/)
- **Fecha de consulta:** 23/10/2026
- **Alcance:** las 10 categorías, con sus secciones de descripción, prevención y antecedentes.

## Dataset de evaluación

El archivo `eval/questions.jsonl` contiene preguntas de referencia, una por línea, con los siguientes campos:

| Campo | Descripción |
|---|---|
| `id` | Identificador único de la pregunta |
| `pregunta` | Pregunta en español |
| `respuesta_ref` | Respuesta de referencia, escrita a partir de la fuente |
| `fuente` | Categoría de OWASP que contiene la respuesta |
| `fuente_seccion` | Sección exacta dentro de la categoría |
| `tipo` | Tipo de pregunta: `definicion`, `concepto`, `vulnerabilidad`, `novedad` o `procedimiento` |

El dataset se versiona en Git. Cualquier cambio queda registrado en el historial.

## Estructura del proyecto

```
owasp-rag-evaluation/
└── eval/
    ├── questions.jsonl   # Dataset de evaluación
    └── README.md         # Notas sobre el dataset
```

## Estado

- [x] Dataset de evaluación v1 (25 preguntas)
- [ ] Ingesta y limpieza del corpus
- [ ] Indexación y recuperación
- [ ] Generación de respuestas
- [ ] Métricas de evaluación (recuperación y fidelidad)

## Stack previsto

- Python
- Embeddings y base vectorial (por definir)
- Evaluación con preguntas etiquetadas

## Limitaciones

- El dataset es pequeño (25 preguntas en la v1) y servirá para validar el pipeline, no para conclusiones estadísticas.
- Las respuestas de referencia fueron escritas manualmente y pueden contener sesgos del autor.

## Autor

Antony Cisneros

