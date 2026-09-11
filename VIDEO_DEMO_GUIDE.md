# Video Demostrativo - HDT 4

## Objetivo del Video

Grabar una demostración que muestre:
1. ✅ Script de carga (`load_embeddings.py`) procesando FAQs y generando embeddings
2. ✅ Agente (`agent.py`) respondiendo múltiples preguntas del corpus

**Duración recomendada:** 2-5 minutos (lo más corto posible)

---

## Pasos para Grabar el Video

### Preparación (antes de grabar)

1. **Levanta PostgreSQL con Docker:**

```bash
docker compose up -d
# Espera 15-20 segundos a que PostgreSQL esté listo
docker compose ps
```

2. **Configura el .env:**

```bash
cp .env.example .env
# Abre .env y rellena:
# - GROQ_API_KEY=tu_clave_de_groq (desde https://console.groq.com/keys)
# O
# - NVIDIA_API_KEY=tu_clave_de_nvidia (desde https://build.nvidia.com)
```

3. **Instala dependencias:**

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

### Grabación de Pantalla (comienza la grabación aquí)

#### Parte 1: Script de Carga (1-2 minutos)

**Comando:**
```bash
python load_embeddings.py
```

**Qué esperar:**
```
================================================
Cargar FAQs
================================================

Total de fichas encontradas: 120

Cargando modelo de embeddings: all-MiniLM-L6-v2
[████████████████] 120/120

Generando embeddings...
[████████████████] 120/120

Conectando a PostgreSQL...
✓ Conexión establecida

Insertando 120 FAQs en la base de datos...
[████████████████] 120/120

✓ Carga completada
```

**Lo que debes mostrar en el video:**
- El script se ejecuta
- Se cargan 120 FAQs
- Los embeddings se generan correctamente
- La tabla se crea en PostgreSQL

---

#### Parte 2: Agente Conversacional (3-5 minutos)

**Comando:**
```bash
python agent.py
```

**Qué esperar:**
```
============================================================
Agente de FAQs - Parachute S.A
============================================================

Modelo de embeddings: all-MiniLM-L6-v2
Proveedor LLM: Groq
Total de FAQs disponibles: 120

Escribe tus preguntas o 'Bye' para salir:
```

**Preguntas de ejemplo a hacer (elige 3-5):**

1. **Pregunta sobre límite de peso:**
   ```
   Usted: ¿Cuál es el peso máximo permitido para saltar?
   ```
   Resultado esperado: El agente responde con FAQ-021 sobre el límite de 100 kg

2. **Pregunta sobre precio:**
   ```
   Usted: ¿Cuánto cuesta un salto tándem?
   ```
   Resultado esperado: El agente busca en FAQs y responde

3. **Pregunta sobre ubicación:**
   ```
   Usted: ¿Dónde está ubicada la zona de saltos?
   ```
   Resultado esperado: El agente responde con ubicación del evento

4. **Pregunta que NO está en el corpus:**
   ```
   Usted: ¿Cuál es la capital de Francia?
   ```
   Resultado esperado: El agente admite que no tiene esa información

5. **Otra pregunta del corpus:**
   ```
   Usted: ¿Hay edad máxima para saltar?
   ```
   Resultado esperado: El agente responde basado en FAQs

**Termina la sesión:**
```
Usted: Bye
```

**Lo que debes mostrar en el video:**
- El agente responde múltiples preguntas correctamente
- Las herramientas se ejecutan (buscar_conocimiento)
- Se muestran los IDs de las FAQs usadas (FAQ-XXX)
- El agente rechaza preguntas ajenas al corpus
- El flujo de conversación funciona correctamente

---

## Detalles Técnicos (opcional incluir en el video)

El video puede mostrar opcionalmente (explicado brevemente):

### Herramientas configuradas (Función Calling)

En `agent.py` se define una herramienta:

```python
HERRAMIENTAS = [
    {
        "type": "function",
        "function": {
            "name": "buscar_conocimiento",
            "description": "Busca en la BD vectorial...",
            ...
        }
    }
]
```

Esta herramienta es invocada automáticamente por el LLM (Groq/NVIDIA) para:
- Buscar FAQs por similitud semántica
- Generar embeddings de la pregunta del usuario
- Consultar PostgreSQL con pgvector

### Base de Datos Vectorial

- **Tecnología:** PostgreSQL 16 + pgvector
- **Embeddings:** all-MiniLM-L6-v2 (384 dimensiones)
- **Métrica:** Distancia coseno
- **Índice:** HNSW para búsqueda rápida

---

## Salida Esperada Completa

```
============================================================
Agente de FAQs - Parachute S.A
============================================================

Modelo de embeddings: all-MiniLM-L6-v2
Proveedor LLM: Groq (openai/gpt-oss-120b)
Total de FAQs disponibles: 120

Escribe tus preguntas o 'Bye' para salir:

Usted: ¿Cuál es el peso máximo permitido para saltar?

   [tool] buscar_conocimiento(consulta='¿Cuál es el peso máximo permitido para saltar?', top_k=4)
          -> FAQ-021 | distancia=0.0896 | ¿Cuál es el peso máximo permitido para saltar?
          -> FAQ-022 | distancia=0.2602 | ¿Por qué existe un límite de peso para el salto tándem?
          -> FAQ-025 | distancia=0.2803 | ¿Hay una edad máxima para realizar el salto?

Agente: El peso máximo permitido para realizar un salto tándem es de 100 kg; si el
peso está entre 90 kg y 100 kg se aplicará un recargo administrativo adicional de
Q250 por balance de carga de la aeronave. (Fuente: FAQ-021)

Usted: ¿Cuál es la capital de Francia?

   [tool] buscar_conocimiento(consulta='¿Cuál es la capital de Francia?', top_k=4)
          -> FAQ-019 | distancia=0.4595 | ¿Hay áreas con sombra para el público?
          -> FAQ-021 | distancia=0.4627 | ¿Cuál es el peso máximo permitido para saltar?

Agente: Lo siento, pero no dispongo de esa información en la base de conocimientos
de Parachute S.A. Le sugiero escribir a soporte@parachutesa.gt.

Usted: Bye
```

---

## Requisitos para Grabar

- **Micrófono:** Opcional (puede ser solo demostrativo sin audio)
- **Herramienta de grabación:** 
  - macOS: QuickTime Player (built-in)
  - Windows: Xbox Game Bar o OBS (gratis)
  - Linux: SimpleScreenRecorder o OBS
- **Formato:** MP4 o WebM
- **Resolución:** 1280x720 o superior

---

## Checklist Final

Antes de entregar:

- [ ] Docker está corriendo con PostgreSQL
- [ ] El .env está configurado con una API key válida (Groq o NVIDIA)
- [ ] `load_embeddings.py` se ejecutó exitosamente (120 FAQs cargadas)
- [ ] `agent.py` responde preguntas del corpus correctamente
- [ ] Las herramientas se ejecutan (se ve `[tool] buscar_conocimiento(...)`)
- [ ] El agente rechaza preguntas ajenas al corpus
- [ ] El video muestra ambas partes (carga + agente)
- [ ] El archivo `.env` NO se incluyó en el repositorio (git lo ignora)

---

## Subir el Video

Una vez grabado, sube el video al repositorio o a un drive compartido según
las indicaciones de tu profesor.

**Nombre sugerido:** `HDT4_Demo.mp4` o `parachute_faq_agent_demo.mp4`
