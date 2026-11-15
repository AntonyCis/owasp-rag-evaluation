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

## Resultados de evaluación

Medición sobre el dataset v2 (25 preguntas) y el corpus de OWASP Top 10 2025, con 217 fragmentos indexados. Recuperación con embeddings `paraphrase-multilingual-MiniLM-L12-v2`, similitud coseno, top 3.

| Métrica | Resultado |
|---|---|
| Recall@3 categoría | 21/25 (84%) |
| Recall@3 sección flexible | 19/25 (76%) |
| Recall@3 sección estricta | 13/25 (52%) |

**Definiciones:**

- **Categoría:** la categoría OWASP correcta aparece entre los 3 primeros resultados.
- **Sección flexible:** aparece la sección exacta del dataset, o la "Descripción" de la misma categoría.
- **Sección estricta:** aparece exactamente la sección indicada en el dataset.

**Fallos conocidos:**

- Cuatro preguntas fallan incluso a nivel de categoría (q009, q010, q018, q023). Están pendientes de revisión: en algunos casos la redacción de la pregunta puede ser ambigua.
- La métrica estricta penaliza respuestas que están en la categoría correcta pero en una sección cercana. Por eso se reporta también la flexible.

Medición realizada el 13/11/2026.

**Casos difíciles:**
- **q009** ("cuentas predeterminadas con contraseñas de fábrica"): el término "contraseñas" atrae resultados de criptografía y autenticación (A04 y A07). Con una redacción sin esa palabra, el sistema recupera A02 en primer lugar. Se mantiene en el dataset como caso adverso para medir la sensibilidad al léxico.
- **q010** ("compromete un sistema a través de dependencias externas"): la etiqueta correcta es A03 (Software Supply Chain Failures), pero A08 (Software or Data Integrity Failures) también describe el mismo escenario en su sección Descripción, que menciona plugins, librerías de fuentes no confiables y pipelines CI/CD. En las variantes probadas, el sistema recuperó A03 en primer lugar en una de cuatro y A08 en otra. Se mantiene como caso de frontera entre categorías.

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

