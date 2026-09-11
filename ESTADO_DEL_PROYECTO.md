# Estado del Proyecto HDT-4 - Análisis Final

## ✅ Lo que YA ESTÁ HECHO

### 1. **Herramientas Configuradas (30 pts)** ✅
- `agent.py` líneas 52-84: Define la herramienta `buscar_conocimiento`
- Implementa function calling con OpenAI SDK (compatible con Groq/NVIDIA)
- La herramienta busca en la base de datos vectorial mediante similitud semántica
- Parámetros: `consulta` y `top_k`

### 2. **Base de Datos Vectorial (20 pts)** ✅
- **Archivo:** `docker-compose.yml`
- **Servicio:** `pgvector/pgvector:pg16`
- **Extensión:** pgvector habilitada en PostgreSQL
- **Almacenamiento:** Tabla `faqs` con columna `embedding` de tipo `vector(384)`
- **Índice:** HNSW para búsqueda rápida (HNSW es más preciso que IVFFlat para corpus pequeños)
- **Métrica:** Distancia coseno usando operador `<=>` de pgvector

### 3. **Script de Carga (20 pts)** ✅
- **Archivo:** `load_embeddings.py`
- **Funcionalidad:**
  - Parsea `Corpus_FAQs_Parachute_SA_2026.txt` (120 FAQs)
  - Genera embeddings usando `all-MiniLM-L6-v2` (384 dimensiones)
  - Los embeddings se normalizan (normalize_embeddings=True)
  - Carga datos a PostgreSQL
  - El script es idempotente (elimina tabla y recrea en cada ejecución)
- **Decisión de diseño:** Solo vectoriza la pregunta, no la respuesta
  - Motivo: Las respuestas usan plantilla repetida que degrada los embeddings

### 4. **Agente Funcional** ✅ (casi)
- **Archivo:** `agent.py`
- **Funcionalidad:**
  - Loop de conversación en terminal
  - Soporta múltiples turnos hasta escribir "Bye" o Ctrl-C
  - Invoca automáticamente la herramienta `buscar_conocimiento`
  - Solo responde basado en información del corpus
  - Rechaza preguntas ajenas al corpus
  - Cita las FAQs usadas (ej: "Fuente: FAQ-021")
  - Soporta Groq y NVIDIA Build como proveedores LLM

### 5. **Archivos de Configuración** ✅
- `.env.example` ✅ - Plantilla de variables
- `requirements.txt` ✅ - Dependencias Python
- `docker-compose.yml` ✅ - Infraestructura
- `README.md` ✅ - Documentación completa
- `Corpus_FAQs_Parachute_SA_2026.txt` ✅ - 120 FAQs del cliente
- `knowledge_base.py` ✅ - Módulo compartido
- `initdb/01_extension.sql` ✅ - Inicialización de BD

---

## ❌ LO QUE FALTA: VIDEO DEMOSTRATIVO (30 pts)

### Requisito

Grabar un video que muestre:
1. **El script de carga ejecutándose** (1-2 minutos)
   - Procesando el corpus de 120 FAQs
   - Generando embeddings
   - Cargando a PostgreSQL
   
2. **El agente respondiendo preguntas** (3-5 minutos)
   - Mínimo 3-5 preguntas del corpus
   - El agente invocando la herramienta `buscar_conocimiento`
   - Las fichas recuperadas con sus distancias
   - El agente citando las fuentes

### Ejemplo de Preguntas para Grabar

```
1. ¿Cuál es el peso máximo permitido para saltar?
   → Espera respuesta con FAQ-021 (distancia baja)

2. ¿Cuánto cuesta un salto tándem?
   → Espera respuesta del corpus

3. ¿Dónde está ubicada la zona de saltos?
   → Espera respuesta del corpus

4. ¿Cuál es la capital de Francia?
   → Espera rechazo (pregunta fuera del corpus)

5. ¿Hay edad máxima para saltar?
   → Espera respuesta del corpus
```

---

## 📋 Pasos para Completar el Proyecto

### Paso 1: Configurar el Entorno

```bash
# Clonar o ir al repositorio
cd /ruta/a/ai-hdt-3

# Crear .env desde template
cp .env.example .env

# Editar .env y agregar una API key:
# - GROQ_API_KEY (desde https://console.groq.com/keys) 
# O
# - NVIDIA_API_KEY (desde https://build.nvidia.com)
```

### Paso 2: Levantar la Base de Datos

```bash
# Inicia PostgreSQL con pgvector
docker compose up -d

# Verifica que esté corriendo
docker compose ps
```

### Paso 3: Instalar Dependencias

```bash
# Opción A: En contenedor (recomendado en Windows)
docker compose --profile app build app
docker compose --profile app run --rm app python load_embeddings.py
docker compose --profile app run --rm app python agent.py

# Opción B: Entorno virtual local
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python load_embeddings.py
python agent.py
```

### Paso 4: Grabar el Video

Consulta el archivo `VIDEO_DEMO_GUIDE.md` para instrucciones detalladas.

**Lo que DEBE verse en el video:**
- ✅ Script de carga procesando 120 FAQs
- ✅ Embeddings siendo generados
- ✅ Agente respondiendo preguntas del corpus
- ✅ Herramientas siendo invocadas (`[tool] buscar_conocimiento(...)`)
- ✅ FAQs siendo citadas correctamente
- ✅ Rechazo de preguntas ajenas al corpus

### Paso 5: Entregar

1. Sube el video al repositorio (branch `feature/hdt-4`)
2. Asegúrate de que:
   - El `.env` NO está en el repo (está en .gitignore)
   - Todos los scripts están presentes
   - El README tiene instrucciones claras

---

## 🔧 Verificación de Componentes

### Herramientas (Función Calling)
```
Ubicación: agent.py, líneas 52-84
Estado: ✅ IMPLEMENTADO
Verificación: Ejecuta agent.py y verifica que se imprima "[tool] buscar_conocimiento(...)"
```

### Base de Datos Vectorial
```
Ubicación: docker-compose.yml
Estado: ✅ IMPLEMENTADO
Verificación: docker compose ps debe mostrar pgvector/pgvector:pg16 corriendo
```

### Script de Carga
```
Ubicación: load_embeddings.py
Estado: ✅ IMPLEMENTADO
Verificación: Ejecuta y debería procesar 120 FAQs con embeddings
```

### Agente Funcional
```
Ubicación: agent.py
Estado: ✅ IMPLEMENTADO
Verificación: Ejecuta y responde preguntas correctamente
```

### Video Demostrativo
```
Ubicación: [POR GRABAR]
Estado: ❌ NO HECHO
Requisito: Grabar demo de carga y agente respondiendo preguntas
```

---

## 📊 Rúbrica vs Estado Actual

| Criterio | Valor | Estado | Falta |
|----------|-------|--------|-------|
| Herramientas | 30 pts | ✅ Completo | Nada |
| Base de datos Vectorial | 20 pts | ✅ Completo | Nada |
| Script de carga | 20 pts | ✅ Completo | Nada |
| Agente funciona (video) | 30 pts | ❌ Falta video | **Grabar video** |
| **TOTAL** | **100 pts** | **70 pts** | **30 pts** |

---

## 🎬 Próximos Pasos

1. **Instala las herramientas necesarias:**
   - Docker Desktop (si no lo tienes)
   - Una API key de Groq o NVIDIA Build (gratis)

2. **Sigue los pasos 1-4** de "Pasos para Completar el Proyecto"

3. **Graba el video** siguiendo `VIDEO_DEMO_GUIDE.md`

4. **Sube el video** al repositorio

5. **Verifica el checklist** final antes de entregar

---

## ⚙️ Configuración Técnica Resumida

| Componente | Tecnología | Versión |
|------------|-----------|---------|
| BD Vectorial | PostgreSQL + pgvector | 16 |
| Embeddings | sentence-transformers | all-MiniLM-L6-v2 |
| Dimensiones | - | 384 |
| LLM | Groq o NVIDIA | Vía OpenAI SDK |
| Métrica | Distancia Coseno | pgvector `<=>` |
| Interfaz | Terminal | Python |

---

## 💡 Notas Importantes

1. **El corpus se proporciona:** `Corpus_FAQs_Parachute_SA_2026.txt` contiene 120 FAQs reales de Parachute S.A.

2. **No requiere Anthropic:** El proyecto usa Groq o NVIDIA Build (APIs gratuitas con LLMs rápidos)

3. **El modelo de embeddings es pequeño:** all-MiniLM-L6-v2 se descarga localmente y funciona sin GPU

4. **La búsqueda es semántica:** Usa distancia coseno para recuperar FAQs relevantes

5. **El agente es inteligente:** Solo responde basado en el corpus, rechaza preguntas ajenas

---

**Estimado:** 15-30 minutos para completar (sin contar el tiempo de descarga de modelos)
