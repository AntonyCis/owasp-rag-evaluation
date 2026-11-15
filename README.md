# OWASP RAG Evaluation

Sistema RAG (Retrieval-Augmented Generation) que responde preguntas sobre el **OWASP Top 10 2025**, con un framework de evaluación medible para su calidad de recuperación y de respuesta.

El objetivo no es solo construir un chatbot, sino **medir** si las respuestas son correctas, fieles a la fuente y basadas en el documento correcto.

## Corpus

- **Fuente:** OWASP Top 10 2025 (https://top10.owasp.org/2025/)
- **Fecha de consulta:** 13/11/2026 
- **Alcance:** las 10 categorías, con sus secciones de Antecedentes, Descripción, Cómo prevenir, Escenarios de ataque y Referencias. La sección de CWEs asociados se excluye por ser listas de códigos sin texto explicativo.
- **Procesamiento:** cada sección se divide en trozos de unas 60 palabras con solapamiento de 15, para no superar el límite de tokens del modelo de embeddings. Resultado: 217 fragmentos indexados.

## Dataset de evaluación

El archivo `eval/questions.jsonl` contiene 25 preguntas de referencia, una por línea, con los siguientes campos:

| Campo | Descripción |
|---|---|
| `id` | Identificador único de la pregunta |
| `pregunta` | Pregunta en español |
| `respuesta_ref` | Respuesta de referencia, escrita a partir de la fuente |
| `fuente` | Categoría de OWASP que contiene la respuesta |
| `fuente_seccion` | Sección exacta dentro de la categoría |
| `tipo` | Tipo de pregunta: `definicion`, `concepto`, `vulnerabilidad`, `novedad`, `procedimiento` o `escenario_ataque` |

El dataset se versiona en Git. Cualquier cambio queda registrado en el historial.

## Resultados de evaluación

Medición sobre el dataset v3 (25 preguntas) y el corpus de OWASP Top 10 2025 (217 fragmentos). Recuperación con embeddings `paraphrase-multilingual-MiniLM-L12-v2`, similitud coseno, top 3.

| Métrica | Resultado |
|---|---|
| Recall@3 categoría | 22/25 (84%) |
| Recall@3 sección flexible | 20/25 (80%) |
| Recall@3 sección estricta | 14/25 (56%) |

**Definiciones:**

- **Categoría:** la categoría OWASP correcta aparece entre los 3 primeros resultados.
- **Sección flexible:** aparece la sección exacta del dataset, o la "Descripción" de la misma categoría.
- **Sección estricta:** aparece exactamente la sección indicada en el dataset.

La métrica estricta es la más exigente, y en ocasiones penaliza respuestas correctas. Por ejemplo, para una pregunta sobre cómo prevenir una vulnerabilidad, la sección "Descripción" o "Escenarios de ataque" de la misma categoría también puede contener la respuesta. Por eso se reporta también la flexible.

**Fallos conocidos:** tres preguntas fallan a nivel de categoría (q009, q010 y q018). Se documentan en los casos difíciles, con su análisis.

**Casos difíciles:**

- **q009** ("cuentas predeterminadas con contraseñas de fábrica"): el término "contraseñas" atrae resultados de criptografía y autenticación (A04 y A07). Con una redacción sin esa palabra, el sistema recupera A02 en primer lugar. Se mantiene en el dataset como caso adverso para medir la sensibilidad al léxico.
- **q010** ("compromete un sistema a través de dependencias externas"): la etiqueta correcta es A03 (Software Supply Chain Failures), pero A08 (Software or Data Integrity Failures) describe el mismo escenario en su sección Descripción, que menciona plugins, librerías de fuentes no confiables y pipelines CI/CD. En las variantes probadas, el sistema recuperó A03 en primer lugar en una de cuatro y A08 en otra. Se mantiene como caso de frontera entre categorías.
- **q015** ("buenas prácticas para evitar inyección en consultas de bases de datos"): la etiqueta correcta es A05 "Cómo prevenir", que aparece en el top 5 pero detrás de fragmentos de A10 y A09 que describen escenarios y registros. Caso de ranking: la consulta general se parece más a escenarios de ataque que a recomendaciones.
- **q016** ("cómo aborda la edición 2025 el riesgo derivado de librerías y componentes"): la etiqueta A03 "Descripción" es correcta, pero la expresión "edición 2025" atrae la sección Antecedentes de A06, que compara ediciones. Caso de frontera entre categorías, por ambigüedad de la consulta.
- **q018** ("controles para gestionar el riesgo de componentes y dependencias externas"): la etiqueta correcta es A03 "Cómo prevenir". El término genérico "controles" atrae resultados de A09 "Cómo prevenir" y de A06. Solo una de las cuatro variantes probadas recupera A03 en primer lugar. Se mantiene como caso adverso por ambigüedad de la redacción.

**Hallazgos sobre el corpus:**

- La sección "Cómo prevenir" de A09 tiene vocabulario muy genérico (controles, registros, alertas) y aparece en el top 3 de consultas que hablan de controles en general, aunque traten de otros temas. Afecta a q018. Se documenta como propiedad del corpus, no como fallo de la recuperación.

## Historial de evaluación

| Versión | Preguntas | Categoría | Sección flexible | Sección estricta | Cambio |
|---|---|---|---|---|---|
| Línea base | 7 | 7/7 | — (no medida) | 6/7 | Primera medición |
| v2 | 25 | 21/25 | 19/25 | 13/25 | Etiquetas corregidas contra OWASP 2025 |
| v3 | 25 | 22/25 | 20/25 | 14/25 | q023 reescrita contra el escenario real de A08 |

La mejora de v2 a v3 se debe a la corrección del dataset, no a un cambio en el sistema.

## Estructura del proyecto

```
owasp-rag-evaluation/
├── data/
│   ├── raw/              # HTML descargado de OWASP (ignorado en Git)
│   ├── chunks.jsonl      # Fragmentos del corpus
│   └── index/            # Índice vectorial ChromaDB (ignorado en Git)
├── eval/
│   ├── questions.jsonl   # Dataset de evaluación
│   └── README.md         # Notas sobre el dataset
└── src/
    ├── ingest.py         # Descarga, extracción y troceado del corpus
    ├── index.py          # Embeddings e índice vectorial
    └── evaluar.py        # Métricas de recuperación
```

## Estado

- [x] Dataset de evaluación v3 (25 preguntas)
- [x] Ingesta y limpieza del corpus
- [x] Indexación y recuperación
- [ ] Generación de respuestas
- [ ] Métricas de fidelidad de respuesta

## Stack

- Python
- sentence-transformers con `paraphrase-multilingual-MiniLM-L12-v2`
- ChromaDB como base vectorial local
- requests y BeautifulSoup para la ingesta

## Limitaciones

- El dataset es pequeño (25 preguntas) y sirve para validar el pipeline, no para conclusiones estadísticas.
- Las respuestas de referencia fueron escritas manualmente y pueden contener sesgos del autor.
- La métrica de sección depende de etiquetas únicas. Varias preguntas tienen más de una sección válida, lo que la métrica estricta no contempla.

## Autor

Antony Cisneros