# HDT 3 - Agente de preguntas frecuentes con RAG simple (Parachute S.A.)

Curso CC3116. Demo de terminal de un agente que responde preguntas sobre el evento
de paracaidismo de Parachute S.A., usando **únicamente** el archivo de FAQs que la
empresa compartió.

## Arquitectura

RAG en su forma más simple, sin embeddings ni vector store:

```
data/FAQs_Parachute_SA_Guatemala_2026.txt
              │
              │  (1) Retrieval: se lee el archivo del file system
              ▼
     system prompt del agente          <-- la KB va inyectada completa aquí
              │
              │  (2) Augmented: cada pregunta viaja junto al system prompt
              ▼
   proveedor compatible con la API de OpenAI (Groq)
              │
              │  (3) Generation
              ▼
        respuesta en la terminal  ──►  se guarda en el historial (loop)
```

Como el archivo es pequeño (unos 4,650 caracteres, ~1.5k tokens) cabe entero en el
contexto, así que no hace falta partirlo en chunks ni hacer búsqueda por similitud.
Esa es la decisión de diseño que pide el enunciado: priorizar la rapidez del demo.

## Requisitos

- Python 3.9 o superior
- Una API key de un proveedor compatible con el esquema de API de OpenAI
  ([Groq](https://console.groq.com) tiene tier gratuito sin tarjeta)

## Instalación

```bash
git clone https://github.com/bianckaa/ai-hdt-3.git
cd ai-hdt-3

python -m venv .venv
source .venv/bin/activate        # en PowerShell: .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Configuración

```bash
cp .env.example .env
```

Editar `.env` y colocar la llave:

```
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_API_KEY=gsk_...
MODEL=openai/gpt-oss-120b
```

El archivo `.env` está en `.gitignore`, así que **la API key nunca se sube al
repositorio**.

Para usar Nvidia Build en lugar de Groq basta con cambiar dos variables:

```
OPENAI_BASE_URL=https://integrate.api.nvidia.com/v1
MODEL=meta/llama-3.3-70b-instruct
```

## Ejecución

```bash
python agent.py
```

El agente queda en un loop: se pueden hacer todas las preguntas que se quieran en
la misma sesión. Para salir se escribe `Bye` o se presiona `Ctrl-C`.

## Cómo se cumple lo que pide el enunciado

| Requisito | Dónde se resuelve |
|---|---|
| SDK compatible con el esquema de API de OpenAI | `openai.OpenAI(...)` con `base_url` apuntando a Groq (`build_client`) |
| Base de conocimiento inyectada directo al prompt | `SYSTEM_PROMPT_TEMPLATE.format(knowledge_base=...)`, un solo mensaje `system` |
| Responder solo con el archivo | Reglas 1 a 5 del system prompt + `temperature=0.2` |
| Admitir cuando no sabe | Regla 2: contesta que no tiene esa información y da los contactos del documento |
| Múltiples preguntas por sesión | `while True` acumulando `messages` (mantiene el contexto entre turnos) |
| Salir con `Bye` o `Ctrl-C` | `EXIT_WORDS` y captura de `KeyboardInterrupt` / `EOFError` |
| No pushear la API key | `.env` en `.gitignore`, se versiona solo `.env.example` |

## Preguntas para probar en el video

Preguntas que **sí** están en el archivo (el agente debe contestar bien):

1. ¿Cuándo y dónde es el evento? → 29 de septiembre de 2026, Pista de Aterrizaje de
   Puerto San José, Escuintla, 07:00 AM
2. ¿Cuál es el límite de peso? → 100 kg (220 lbs)
3. ¿Puedo llevar mi Go-Pro? → No, por normativas de seguridad aeronáutica
4. ¿Qué pasa si llueve ese día? → Se reprograma (30 de septiembre o siguiente fin de
   semana) o se da un crédito válido por 1 año
5. ¿Qué incluye el paquete VIP? → Salto tándem + fotografía y video HD + playera
6. ¿Cuánto dura la experiencia completa? → 3 a 4 horas

Preguntas que **no** están en el archivo (el agente debe admitir que no sabe):

7. ¿Cuánto cuesta el boleto? (el archivo habla de métodos de pago, nunca de precios)
8. ¿Hay parqueo en el lugar?
9. ¿Aceptan pago con criptomonedas?
10. ¿Cuál es la capital de Francia? (pregunta fuera de dominio)

Después se escribe `Bye` para mostrar la salida del loop.

## Video de demostración

[Ver el video de demostración](docs/video-demostrativo.mp4) (33 segundos). Muestra preguntas que
están en el archivo, preguntas que el agente admite no poder responder y la salida con
`Bye` y con `Ctrl-C`.

## Estructura del repositorio

```
.
├── agent.py            # agente: carga la KB, la inyecta al prompt y corre el loop
├── data/
│   └── FAQs_Parachute_SA_Guatemala_2026.txt
├── docs/
│   └── video-demostrativo.mp4
├── requirements.txt
├── .env.example        # plantilla de configuración (sin llaves reales)
├── .gitignore
└── README.md
```
