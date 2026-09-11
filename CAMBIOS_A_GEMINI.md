# Cambios Realizados: Migración a Google Gemini

## 📝 Resumen

El código ha sido modificado para usar **Google Generative AI (Gemini)** en lugar de Groq/NVIDIA Build como proveedor LLM.

## ✅ Cambios Realizados

### 1. `agent.py`
- **Antes:** Usaba `OpenAI` SDK con compatibilidad OpenAI (Groq, NVIDIA)
- **Ahora:** Usa `google-generativeai` SDK directamente
- **Cambios:**
  - Reemplazó `from openai import OpenAI` por `import google.generativeai as genai`
  - Eliminó diccionario `PROVEEDORES` (Groq/NVIDIA)
  - Nueva función `configurar_gemini()` en lugar de `seleccionar_proveedor()`
  - Definición de herramientas ahora usa `genai.protos` en lugar de diccionarios OpenAI
  - Función `responder()` completamente reescrita para usar la API de Gemini
  - Manejo de function calling adaptado al formato de Gemini

### 2. `requirements.txt`
- **Antes:** `openai>=1.51.0`
- **Ahora:** `google-generativeai>=0.8.0`

### 3. `.env.example`
- **Antes:** 
  ```
  GROQ_API_KEY=
  GROQ_MODEL=openai/gpt-oss-120b
  NVIDIA_API_KEY=
  NVIDIA_MODEL=meta/llama-3.3-70b-instruct
  ```
- **Ahora:**
  ```
  GEMINI_API_KEY=
  GEMINI_MODEL=gemini-2.0-flash
  ```

### 4. `README.md`
- Actualizado para indicar que se usa Gemini
- URL actualizada: https://aistudio.google.com/apikey para obtener API key
- Documentación de requisitos actualizada

---

## 🔄 Cómo Usar

### Paso 1: Obtener API Key de Gemini

1. Ve a: https://aistudio.google.com/apikey
2. Inicia sesión con tu cuenta Google
3. Haz clic en "Create API Key"
4. Copia tu API key

### Paso 2: Configurar .env

```bash
cp .env.example .env
```

Edita `.env` y agrega tu API key:

```env
GEMINI_API_KEY=tu_clave_aqui
GEMINI_MODEL=gemini-2.0-flash
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Ejecutar

**Cargar FAQs:**
```bash
python load_embeddings.py
```

**Ejecutar agente:**
```bash
python agent.py
```

---

## 🎯 Ventajas de Gemini

✅ **Gratis:** Nivel gratuito generoso sin límite de consultas  
✅ **Rápido:** Modelos muy rápidos (gemini-2.0-flash)  
✅ **Function Calling:** Soporte nativo para herramientas configuradas  
✅ **Multilingüe:** Buen soporte para español  
✅ **Sin dependencias adicionales de OpenAI**

---

## 📋 Verificación

Todos los cambios mantienen la misma funcionalidad:

- ✅ Script de carga (`load_embeddings.py`): **Sin cambios**
- ✅ Base de datos (`knowledge_base.py`): **Sin cambios**
- ✅ Búsqueda vectorial: **Sin cambios**
- ✅ Interface de terminal: **Sin cambios**
- ✅ Function calling: **Adaptado a Gemini** ✨
- ✅ Respuestas del agente: **Idénticas**

---

## 🚀 Próximos Pasos

1. Obtén tu API key de Gemini
2. Configura tu `.env`
3. Levanta PostgreSQL: `docker compose up -d`
4. Instala dependencias: `pip install -r requirements.txt`
5. Carga FAQs: `python load_embeddings.py`
6. Ejecuta el agente: `python agent.py`
7. Graba el video demostrativo

---

## ⚠️ Notas Importantes

- **No requiere Groq ni NVIDIA API keys** - Solo Gemini
- **La API de Gemini es gratis** - Sin límites en el nivel gratuito
- **Compatible con todos los modelos Gemini** - Puedes cambiar `GEMINI_MODEL` en `.env`
- **El código es más simple** - Eliminamos toda la lógica de múltiples proveedores

---

## 📞 Soporte

Si encuentras problemas:

1. Verifica que `GEMINI_API_KEY` está correctamente configurada en `.env`
2. Asegúrate de que PostgreSQL está corriendo: `docker compose ps`
3. Prueba la carga de FAQs primero: `python load_embeddings.py`
4. Revisa los errores en la consola del agente
