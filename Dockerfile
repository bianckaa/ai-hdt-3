# Imagen para ejecutar el script de carga y el agente dentro de un contenedor.
# Es la ruta recomendada en equipos Windows donde Smart App Control bloquea
# las DLL de scipy o psycopg. En Linux o macOS puede usarse un venv normal.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/models

WORKDIR /app

COPY requirements.txt .

# Se instala torch en su variante CPU para reducir el tamano de la imagen.
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "agent.py"]
