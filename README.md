---
title: OWASP RAG
emoji: 🛡️
colorFrom: blue
colorTo: red
sdk: gradio
app_file: app.py
pinned: false
---

# OWASP RAG Evaluation

Sistema RAG (Retrieval-Augmented Generation) que responde preguntas sobre el **OWASP Top 10 2025**, con un framework de evaluación medible para su calidad de recuperación y de respuesta.

El objetivo no es solo construir un chatbot, sino **medir** si las respuestas son correctas, fieles a la fuente y basadas en el documento correcto.

**Demo en línea:** https://huggingface.co/spaces/Antociss11/owasp-rag

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

### Filtro por categoría

Cuando la pregunta nombra una categoría (por ejemplo, "A01:2025"), la búsqueda se limita a los fragmentos de esa categoría y solo completa con búsqueda general si no hay suficientes. Sin ese filtro, el recuperador mezclaba categorías con vocabulario parecido.

- **Efecto medido:** la recuperación por categoría se mantuvo (22/25), la flexible también (20/25), y la estricta subió de 14/25 a 15/25. La mejora está en q001, donde el primer resultado pasó a ser la sección correcta de A01.
- **Límite:** el filtro solo se activa cuando la pregunta contiene el código de categoría. Para preguntas sin código, la búsqueda sigue siendo general y puede traer fragmentos de otras categorías (por ejemplo, la pregunta sobre deserialización insegura recupera A02 y A05 junto a A08).
- **Hallazgo:** el filtro corrige la recuperación, pero no la fidelidad. Con el modelo local, una pregunta bien recuperada puede seguir obteniendo una respuesta imprecisa.

## Evaluación de fidelidad de respuestas

Además de la recuperación, el proyecto mide si las respuestas generadas son fieles a los fragmentos recuperados. La fidelidad no es lo mismo que la corrección: una respuesta puede ser fiel al contexto y aun así incorrecta, o correcta y no fiel si añade información que la fuente no respalda.

Se evaluaron dos modelos de generación, ambos con el mismo contexto recuperado (3 fragmentos por pregunta): `qwen2.5:1.5b` (local, CPU, vía Ollama) y `openai/gpt-oss-20b` (API gratuita de Groq).

### Método

1. Para cada una de las 25 preguntas, se recuperan los 3 fragmentos más cercanos y se genera una respuesta con el modelo, usando solo esos fragmentos como contexto.
2. **Métrica automática:** la respuesta se divide en frases. Para cada frase se calcula su similitud coseno máxima con los fragmentos recuperados (mismo modelo de embeddings que la recuperación). La fidelidad de la respuesta es la media de esas similitudes.
3. **Etiquetado manual:** cada respuesta se marca como fiel, no fiel o negativa honesta. Se marca "no fiel" solo si contiene al menos una afirmación concreta que no aparece ni se deduce de los fragmentos recuperados. Una "negativa honesta" es una respuesta que reconoce que el contexto no basta; se reporta aparte porque no responde la pregunta, pero no afirma nada falso.

### Resultados

| Modelo | Ejecución | Fieles | No fieles | Negativas honestas | AUC de similitud |
|---|---|---|---|---|---|
| `qwen2.5:1.5b` | Ollama, CPU local | 9 | 16 | 0 | 0.694 |
| `openai/gpt-oss-20b` | Groq, API gratuita | 20 | 3 | 2 | 0.683 |

El AUC mide cuánto separa la similitud automática a las respuestas fieles de las no fieles. Un valor de 0.5 significa que no separa; 1.0, que separa perfectamente.

**Cómo leer esta tabla:**

- Los dos modelos tienen AUC similares (0.694 y 0.683), pero el conjunto de no fieles de Groq tiene solo 3 casos. Un AUC calculado sobre tan pocos negativos cambia mucho con una sola etiqueta, así que **no permite afirmar que un modelo sea más fiel que el otro**.
- Las tasas de respuestas no fieles (16 de 25 en qwen, 3 de 23 en Groq) sugieren que el modelo más grande inventa menos, pero con estos tamaños de muestra es una tendencia, no una conclusión.

**Casos de contraste (qwen):**

- **q011** (no fiel, similitud 0.840): repite un bloque de la lista, expande SBOM incorrectamente y omite el núcleo de la pregunta. Tiene frases muy parecidas al contexto y aun así es infiel.
- **q010** (no fiel, similitud 0.755): atribuye a la deserialización insegura un compromiso por dependencias externas. La frase existe en el contexto, pero responde otra pregunta.
- **q012** (fiel, similitud 0.886): sus afirmaciones están directamente en el fragmento de A06 Descripción.
- **q008** (fiel, similitud 0.470): respuesta breve y correcta, con poco vocabulario compartido con el contexto. La métrica la penaliza por brevedad, no por infidelidad.

**Hallazgos:**

- **La similitud mide adherencia al contexto, no veracidad.** Las respuestas infieles con frases parafraseadas del contexto obtienen puntuaciones altas.
- **La similitud penaliza las negativas correctas.** Las dos respuestas honestas de Groq ("no hay información suficiente en el contexto") son las de menor similitud del conjunto (0.245 y 0.162), porque no comparten vocabulario con los fragmentos. La métrica no debe usarse para premiar respuestas, solo para detectar afirmaciones sin respaldo, y aun así con limitaciones.
- **Buena parte de las respuestas infieles vienen de un recuperador que no trajo la sección correcta.** En las preguntas de prevención (q007, q013, q015, q021), los fragmentos recuperados eran de otras categorías o secciones, y el modelo respondió con lo que tenía. Eso vincula el problema de generación con el de recuperación.
- **El etiquetado manual cambia más el resultado que la elección del modelo.** Con 25 preguntas y una sola etiquetadora, cualquier comparación entre modelos debe leerse como exploratoria.

### Limitaciones

- 25 casos, con un solo etiquetador (el autor del proyecto).
- El criterio de etiquetado es subjetivo en respuestas largas. El criterio exacto está descrito arriba.
- Los modelos de generación son pequeños o de capa gratuita, y los resultados no se pueden extrapolar a otros modelos.
- La métrica depende del tamaño de los fragmentos (unas 60 palabras) y del modelo de embeddings.
- Groq aplica límites de uso en la capa gratuita, por lo que la generación completa puede requerir reintentos.

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
├── app.py                # Interfaz Gradio (demo en Hugging Face Spaces)
├── requirements.txt      # Dependencias de la demo
├── data/
│   ├── raw/              # HTML descargado de OWASP (ignorado en Git)
│   ├── chunks.jsonl      # Fragmentos del corpus
│   └── index/            # Índice vectorial ChromaDB (ignorado en Git)
├── eval/
│   ├── questions.jsonl         # Dataset de evaluación (v3)
│   ├── respuestas_generadas.jsonl  # Respuestas de qwen2.5:1.5b
│   ├── respuestas_groq.jsonl       # Respuestas de gpt-oss-20b
│   ├── etiquetas_fidelidad.jsonl   # Etiquetado manual (qwen)
│   └── etiquetas_groq.jsonl        # Etiquetado manual (Groq)
├── src/
│   ├── ingest.py         # Descarga, extracción y troceado del corpus
│   ├── index.py          # Embeddings e índice vectorial, con filtro por categoría
│   ├── evaluar.py        # Métricas de recuperación (categoría, sección estricta y flexible)
│   └── fidelidad.py      # Similitud media de respuestas frente a fragmentos
├── scripts/              # Generación y comparación (ejecutar desde la raíz)
│   ├── evaluar_generacion.py   # Genera respuestas con qwen (Ollama)
│   ├── evaluar_groq.py         # Genera respuestas con Groq
│   ├── etiquetar_fidelidad.py  # Etiquetado manual de respuestas
│   ├── comparar_fidelidad.py   # AUC de qwen
│   └── comparar_groq.py        # AUC de Groq
└── diagnosticos/         # Pruebas que sustentan las decisiones del README
```

Los scripts de `scripts/` y `diagnosticos/` se ejecutan desde la raíz del proyecto, por ejemplo `python scripts\evaluar_groq.py`.

## Estado

- [x] Dataset de evaluación v3 (25 preguntas)
- [x] Ingesta y limpieza del corpus
- [x] Indexación y recuperación, con filtro por categoría
- [x] Generación de respuestas (qwen2.5:1.5b local y gpt-oss-20b vía Groq)
- [x] Evaluación de fidelidad (similitud automática y etiquetado manual)
- [x] Comparación de modelos de generación
- [x] Demo en Hugging Face Spaces
- [ ] Juez LLM para fidelidad (pendiente)
- [ ] Ampliar el dataset y el etiquetado a más preguntas y etiquetadores (pendiente)

## Stack

- Python
- sentence-transformers con `paraphrase-multilingual-MiniLM-L12-v2`
- ChromaDB como base vectorial local
- Gradio para la interfaz
- Ollama (local) y Groq (nube) para la generación
- requests y BeautifulSoup para la ingesta

## Limitaciones generales

- El dataset es pequeño (25 preguntas) y sirve para validar el pipeline, no para conclusiones estadísticas.
- Las respuestas de referencia fueron escritas manualmente y pueden contener sesgos del autor.
- La métrica de sección depende de etiquetas únicas. Varias preguntas tienen más de una sección válida, lo que la métrica estricta no contempla.
- La demo usa un modelo de capa gratuita, que puede cambiar o dejar de estar disponible.

## Autor

Antony Cisneros