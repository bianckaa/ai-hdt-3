#!/bin/bash

# Activar venv
source .venv/bin/activate

echo "=================================================="
echo "PASO 5: Cargando FAQs..."
echo "=================================================="
python3 load_embeddings.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ FAQs cargadas exitosamente"
    echo ""
    echo "=================================================="
    echo "PASO 6: Iniciando Agente..."
    echo "=================================================="
    echo ""
    python3 agent.py
else
    echo "❌ Error al cargar FAQs"
    exit 1
fi
