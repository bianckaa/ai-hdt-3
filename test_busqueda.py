"""Prueba de humo de la busqueda vectorial, sin intervencion del LLM.

Sirve para verificar que la tabla quedo cargada y que pgvector responde
antes de ejecutar el agente.

Uso:
    python test_busqueda.py
    python test_busqueda.py "como llego al aerodromo"
"""

from __future__ import annotations

import sys

from knowledge_base import TABLE_NAME, buscar_similares, get_connection

CONSULTAS_POR_OMISION = [
    "¿donde queda la zona de salto?",
    "¿que tarjetas de credito aceptan?",
    "¿cual es el peso maximo para saltar?",
    "¿que pasa si llueve el 29 de septiembre de 2026?",
    "¿cual es la capital de Francia?",
]


def main() -> int:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME};")
            total = cur.fetchone()[0]
    finally:
        conn.close()

    print(f"Registros en la tabla '{TABLE_NAME}': {total}\n")

    consultas = sys.argv[1:] or CONSULTAS_POR_OMISION
    for consulta in consultas:
        print(f"Consulta: {consulta}")
        resultados = buscar_similares(consulta)
        if not resultados:
            print("  (sin coincidencias bajo el umbral de distancia)")
        for r in resultados:
            print(f"  {r['faq_id']} | dist={r['distancia']} | {r['categoria']} | {r['pregunta']}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
