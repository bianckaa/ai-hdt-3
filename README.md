# HDT 4 — Agente de FAQs con pgvector y function calling

Agente de preguntas frecuentes de **Parachute S.A.** (Gran Evento de Paracaidismo
Guatemala 2026). El agente responde únicamente con la información del corpus
oficial de FAQs y consulta ese corpus mediante una herramienta (*function
calling*) que ejecuta búsqueda vectorial sobre PostgreSQL con pgvector.

## Arquitectura

| Componente | Tecnología |
|---|---|
| Base de datos vectorial | PostgreSQL 16 + extensión `pgvector` (contenedor) |
| Embeddings | `sentence-transformers`, modelo `all-MiniLM-L6-v2` (384 dimensiones, local) |
| Métrica de similitud | Distancia coseno, operador `<=>` de pgvector |
| Índice | HNSW con `vector_cosine_ops` |
| LLM | Google Generative AI (Gemini) con SDK `google-generativeai` |
| Interfaz | Terminal |

El corpus **no** se inyecta en el prompt. El modelo recibe la definición de la
herramienta `buscar_conocimiento` y debe invocarla para obtener contexto. El
agente ejecuta la búsqueda, devuelve las fichas al modelo y obtiene la respuesta
final.

### Archivos

| Archivo | Función |
|---|---|
| `docker-compose.yml` | Servicio `pgvector` (base de datos) y servicio opcional `app` (Python) |
| `Dockerfile` | Imagen de Python para ejecutar los scripts dentro del contenedor |
| `initdb/01_extension.sql` | Habilita la extensión `vector` al crear el volumen |
| `knowledge_base.py` | Conexión a PostgreSQL, modelo de embeddings y búsqueda por similitud |
| `load_embeddings.py` | Parsea el corpus, genera embeddings y carga la tabla |
| `agent.py` | Loop de conversación con function calling |
| `test_busqueda.py` | Prueba de humo de la búsqueda vectorial, sin LLM |
| `.env.example` | Plantilla de variables de entorno |

## Requisitos

- Docker Desktop (o Podman con `podman-compose`).
- Python 3.11 o superior, solo si ejecuta los scripts fuera del contenedor.
- Una API key de [Google Generative AI](https://aistudio.google.com/apikey) (gratis).
- Conexión a internet en la primera ejecución: `sentence-transformers` descarga
  el modelo `all-MiniLM-L6-v2` desde Hugging Face y lo guarda en el volumen
  `hf_models`. Las corridas siguientes lo toman de ahí.

El modelo por omisión es `gemini-2.0-flash`, disponible en el nivel gratuito
de Google Generative AI y con soporte de function calling. Puede usar otros modelos
como `gemini-2.0-pro` ajustando `GEMINI_MODEL` en `.env`.

## Ejecución

### 1. Configurar las variables de entorno

```bash
cp .env.example .env
```

Abra `.env` y complete `GEMINI_API_KEY` con su clave desde https://aistudio.google.com/apikey 

### 2. Levantar la base de datos

```bash
docker compose up -d
```

Verifique que el contenedor quedó sano:

```bash
docker compose ps
```

### 3. Instalar dependencias y ejecutar

Existen dos rutas. Elija una.

#### Ruta A — todo en contenedor (recomendada en Windows)

No requiere instalar Python ni dependencias en el equipo.

```bash
docker compose --profile app build app
docker compose --profile app run --rm app python load_embeddings.py
docker compose --profile app run --rm app python agent.py
```

#### Ruta B — entorno virtual local

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate        # Linux o macOS
pip install -r requirements.txt

python load_embeddings.py
python agent.py
```

> **Nota para Windows.** Si Smart App Control está activo, bloquea las DLL sin
> firma que traen algunas ruedas de PyPI y la ruta B falla con el mensaje
> «Una directiva de Control de aplicaciones bloqueó este archivo». En este
> proyecto afecta a `scipy`, que `sentence-transformers` carga a través de
> `scikit-learn`. Por ese mismo motivo el driver de base de datos es `psycopg`
> v3 y no `psycopg2-binary`, que también queda bloqueado. Confirme el estado
> con:
>
> ```bash
> reg query "HKLM\SYSTEM\CurrentControlSet\Control\CI\Policy" /v VerifiedAndReputablePolicyState
> ```
>
> Un valor de `1` significa que está en modo de bloqueo. Use la ruta A en ese
> caso: desactivar Smart App Control es irreversible sin reinstalar Windows.

### 4. Probar la búsqueda vectorial sin el LLM

```bash
docker compose --profile app run --rm app python test_busqueda.py
```

O con una consulta propia:

```bash
docker compose --profile app run --rm app python test_busqueda.py "formas de pago aceptadas"
```

## Uso del agente

El agente acepta varias preguntas por sesión. Termina con `Ctrl-C` o al escribir
`Bye`. En cada turno imprime la llamada a la herramienta junto con las fichas
recuperadas y su distancia, de modo que la búsqueda vectorial queda a la vista.

```
Usted: cual es el peso maximo para saltar?
   [tool] buscar_conocimiento(consulta='cual es el peso maximo para saltar', top_k=5)
          -> FAQ-021 | distancia=0.0896 | ¿Cuál es el peso máximo permitido para saltar?
          -> FAQ-022 | distancia=0.2602 | ¿Por qué existe un límite de peso para el salto tándem?
          -> FAQ-025 | distancia=0.2803 | ¿Hay una edad máxima para realizar el salto?

Agente: El peso máximo permitido para realizar un salto tándem es de 100 kg; si el
peso está entre 90 kg y 100 kg se aplicará un recargo administrativo adicional de
Q250 por balance de carga de la aeronave. (Fuente: FAQ-021)
```

Ante una pregunta ajena al corpus la búsqueda igual devuelve las fichas más
cercanas, pero con distancias altas y sin relación con lo preguntado. El agente
las descarta y admite que no cuenta con esa información:

```
Usted: cual es la capital de Francia?
   [tool] buscar_conocimiento(consulta='cual es la capital de Francia?', top_k=4)
          -> FAQ-019 | distancia=0.4595 | ¿Hay áreas con sombra para el público?
          -> FAQ-021 | distancia=0.4627 | ¿Cuál es el peso máximo permitido para saltar?

Agente: Lo siento, pero no dispongo de esa información en la base de conocimientos
de Parachute S.A. Le sugiero escribir a soporte@parachutesa.gt.
```

## Decisiones de diseño

**Un chunk por ficha.** El corpus trae 120 fichas con formato regular
(`ID`, `CATEGORÍA`, `PREGUNTA`, `RESPUESTA`, `METADATA`), separadas por una línea
de guiones. Cada ficha es un registro. No hace falta partir por tamaño: las
fichas son cortas y ya constituyen unidades semánticas completas.

**Se vectoriza solo la pregunta.** Todas las respuestas del corpus comparten la
misma plantilla de texto. Al incluirlas, esa plantilla domina el embedding y
acerca entre sí a las 120 fichas: la consulta «¿dónde queda la zona de salto?»
recuperaba fichas sobre altura de salto en lugar de FAQ-001. Anteponer
`Categoría: ...` también perjudica, porque añade palabras comunes a muchas
fichas. Medido sobre FAQ-101, la distancia pasó de 0.36 con el prefijo a 0.16
sin él. La categoría y la respuesta completa se almacenan en la tabla y se
entregan al modelo, pero no se vectorizan.

**Índice HNSW, no IVFFlat.** IVFFlat reparte los vectores en listas y por
omisión sondea una sola. Con 120 filas el índice quedaba en 12 listas y la
búsqueda examinaba apenas una fracción de la tabla, así que devolvía vecinos
equivocados: FAQ-101 estaba a distancia 0.16 de su propia pregunta y aun así no
aparecía entre los primeros resultados. HNSW mantiene una recuperación
prácticamente exacta en corpus de este tamaño. Tras el cambio, esa consulta
devuelve FAQ-101 a distancia 0.03.

**El LLM decide la relevancia, no el umbral.** `MAX_DISTANCE = 0.75` actúa solo
como filtro grueso. Un umbral estricto no es viable: `all-MiniLM-L6-v2` está
entrenado en inglés y agrupa el texto en español, de modo que los rangos se
traslapan. Medido sobre este corpus, las consultas válidas llegan hasta 0.45 y
las ajenas al tema bajan hasta 0.27. El *system prompt* instruye al modelo a
juzgar cada ficha, descartar las que no respondan y admitir que no tiene la
información. Esa defensa sí funciona: «¿cuál es la capital de Francia?» y
«dame la receta de una pizza margarita» se rechazan correctamente.

**El historial no debe llevar `tool_calls` en `null`.** Cuando el modelo
responde con texto y sin llamar a la herramienta, ese mensaje se agrega al
historial **sin** la clave `tool_calls`. Enviarla con valor `null` hace que la
API rechace la petición en el turno siguiente:

```
Error code: 400 - 'messages.4' : for 'role:assistant' the following must be
satisfied[('messages.4.tool_calls' : Value is not nullable)]
```

El fallo es engañoso porque no aparece en la primera pregunta —ese mensaje aún
no se ha reenviado— sino a partir de la segunda. Cualquier cambio en `responder()`
debe conservar ese comportamiento; conviene probarlo siempre con una sesión de
varios turnos, no con una sola pregunta.

**Limitación conocida.** `all-MiniLM-L6-v2` es un modelo entrenado en inglés,
así que rinde mejor con preguntas completas que con frases sueltas en español.
«¿Qué pasa si llueve el 29 de septiembre de 2026?» recupera FAQ-101 a distancia
0.03, pero «qué pasa si llueve el día del evento» se desvía hacia fichas que
mencionan «el día del evento». Por eso el *system prompt* pide al modelo que
pase la pregunta del usuario tal como la formuló, sin resumirla. Un modelo
multilingüe como `paraphrase-multilingual-MiniLM-L12-v2` resolvería esto, pero
el enunciado fija `all-MiniLM-L6-v2`.

**Calidad del corpus.** Solo algunas fichas traen respuesta real (FAQ-021
detalla el límite de 100 kg y el recargo de Q250). La mayoría trae un texto de
plantilla. Cuando el agente responde de forma vaga, reproduce fielmente lo que
dice la ficha; no la está inventando.

**Carga idempotente.** `load_embeddings.py` elimina y recrea la tabla en cada
corrida, lo que permite repetir pruebas sin registros duplicados.

