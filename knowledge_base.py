"""Configuracion compartida: conexion a PostgreSQL/pgvector, modelo de
embeddings y busqueda por similitud.

Lo usan tanto el script de carga (load_embeddings.py) como el agente
(agent.py), de modo que ambos generan embeddings con el mismo modelo.
"""

from __future__ import annotations

import os
from functools import lru_cache

import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector

load_dotenv()

TABLE_NAME = "faqs"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIM = 384
TOP_K = int(os.getenv("TOP_K", "4"))
MAX_DISTANCE = float(os.getenv("MAX_DISTANCE", "0.75"))


def get_connection() -> psycopg.Connection:
    """Abre una conexion a PostgreSQL con la extension vector habilitada."""
    conn = psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5433")),
        user=os.getenv("POSTGRES_USER", "parachute"),
        password=os.getenv("POSTGRES_PASSWORD", "parachute"),
        dbname=os.getenv("POSTGRES_DB", "parachute_faqs"),
    )
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    conn.commit()
    register_vector(conn)
    return conn


def to_vector_literal(vector) -> str:
    """Convierte una lista de floats al literal que pgvector espera: [a,b,c]."""
    return "[" + ",".join(f"{float(x):.8f}" for x in vector) + "]"


@lru_cache(maxsize=1)
def get_embedder():
    """Carga el modelo de embeddings una sola vez por proceso."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBEDDING_MODEL)


def embed(text: str) -> list[float]:
    """Devuelve el embedding normalizado de un texto."""
    return get_embedder().encode(text, normalize_embeddings=True).tolist()


def buscar_similares(consulta: str, top_k: int = TOP_K) -> list[dict]:
    """Busca en pgvector las fichas mas cercanas a la consulta.

    Usa el operador <=> de pgvector (distancia coseno). MAX_DISTANCE actua
    solo como filtro grueso: el modelo all-MiniLM-L6-v2 esta entrenado en
    ingles y agrupa el texto en espanol, de modo que los rangos de distancia
    dentro y fuera del corpus se traslapan. La decision final de relevancia
    queda a cargo del LLM, guiado por el system prompt.
    """
    vector = to_vector_literal(embed(consulta))
    sql = f"""
        SELECT faq_id, categoria, pregunta, respuesta,
               embedding <=> %s::vector AS distancia
        FROM {TABLE_NAME}
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """
    with get_connection() as conn:
        filas = conn.execute(sql, (vector, vector, top_k)).fetchall()

    resultados = []
    for faq_id, categoria, pregunta, respuesta, distancia in filas:
        if distancia > MAX_DISTANCE:
            continue
        resultados.append(
            {
                "faq_id": faq_id,
                "categoria": categoria,
                "pregunta": pregunta,
                "respuesta": respuesta,
                "distancia": round(float(distancia), 4),
            }
        )
    return resultados
