"""Carga el corpus de FAQs de Parachute S.A. en PostgreSQL + pgvector.

Parseo del corpus
-----------------
El archivo original agrupa las fichas en bloques regulares separados por
una linea de guiones:

    ID: FAQ-001
    CATEGORIA: Logistica y Ubicacion
    PREGUNTA: ...
    RESPUESTA: ...
    METADATA: {...}

Cada ficha se convierte en un registro (un chunk). Se vectoriza unicamente
el texto de la pregunta; la categoria y la respuesta se almacenan pero no se
vectorizan, porque en este corpus todas las respuestas repiten la misma
plantilla y su inclusion vuelve casi indistinguibles a los embeddings.

El script es idempotente: elimina y recrea la tabla en cada corrida.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from knowledge_base import (
    EMBEDDING_DIM,
    EMBEDDING_MODEL,
    TABLE_NAME,
    get_connection,
    get_embedder,
    to_vector_literal,
)

CORPUS_POR_OMISION = Path(__file__).parent / "Corpus_FAQs_Parachute_SA_2026.txt"

PATRON_FICHA = re.compile(
    r"^ID:\s*(?P<id>\S+)\s*$"
    r"(?:\r?\n)CATEGOR[IÍ]A:\s*(?P<categoria>.*?)\s*$"
    r"(?:\r?\n)PREGUNTA:\s*(?P<pregunta>.*?)\s*$"
    r"(?:\r?\n)RESPUESTA:\s*(?P<respuesta>.*?)\s*$"
    r"(?:(?:\r?\n)METADATA:\s*(?P<metadata>.*?)\s*$)?",
    re.MULTILINE,
)


def parsear_corpus(ruta: Path) -> list[dict]:
    """Extrae las fichas del archivo de texto plano."""
    texto = ruta.read_text(encoding="utf-8")
    fichas = []
    for coincidencia in PATRON_FICHA.finditer(texto):
        metadata_cruda = coincidencia.group("metadata")
        try:
            metadata = json.loads(metadata_cruda) if metadata_cruda else {}
        except json.JSONDecodeError:
            metadata = {"raw": metadata_cruda}

        categoria = coincidencia.group("categoria")
        pregunta = coincidencia.group("pregunta")
        respuesta = coincidencia.group("respuesta")

        fichas.append(
            {
                "faq_id": coincidencia.group("id"),
                "categoria": categoria,
                "pregunta": pregunta,
                "respuesta": respuesta,
                "metadata": json.dumps(metadata, ensure_ascii=False),
                "contenido": pregunta,
            }
        )
    return fichas


def recrear_tabla(conn) -> None:
    """Elimina y vuelve a crear la tabla para permitir cargas repetidas."""
    with conn.cursor() as cur:
        cur.execute(f"DROP TABLE IF EXISTS {TABLE_NAME};")
        cur.execute(
            f"""
            CREATE TABLE {TABLE_NAME} (
                id          SERIAL PRIMARY KEY,
                faq_id      TEXT NOT NULL UNIQUE,
                categoria   TEXT NOT NULL,
                pregunta    TEXT NOT NULL,
                respuesta   TEXT NOT NULL,
                contenido   TEXT NOT NULL,
                metadata    JSONB,
                embedding   VECTOR({EMBEDDING_DIM}) NOT NULL
            );
            """
        )
    conn.commit()


def crear_indice(conn, total: int) -> None:
    """Crea un indice HNSW con distancia coseno.

    Se descarto IVFFlat: con un corpus de 120 filas el indice queda en unas
    pocas listas y, como por omision solo se sondea una, la busqueda devuelve
    vecinos equivocados. HNSW mantiene una recuperacion practicamente exacta
    en corpus pequenos.
    """
    with conn.cursor() as cur:
        cur.execute(
            f"""
            CREATE INDEX {TABLE_NAME}_embedding_idx
            ON {TABLE_NAME}
            USING hnsw (embedding vector_cosine_ops);
            """
        )
    conn.commit()


def main() -> int:
    parser = argparse.ArgumentParser(description="Carga las FAQs en pgvector.")
    parser.add_argument(
        "--corpus",
        type=Path,
        default=CORPUS_POR_OMISION,
        help="Ruta al archivo de FAQs.",
    )
    args = parser.parse_args()

    if not args.corpus.exists():
        print(f"[ERROR] No se encontro el corpus: {args.corpus}")
        return 1

    print(f"[1/4] Leyendo corpus: {args.corpus.name}")
    fichas = parsear_corpus(args.corpus)
    if not fichas:
        print("[ERROR] El corpus no produjo ninguna ficha. Revise el formato del archivo.")
        return 1
    print(f"      Fichas detectadas: {len(fichas)}")

    print(f"[2/4] Generando embeddings con {EMBEDDING_MODEL}")
    modelo = get_embedder()
    vectores = modelo.encode(
        [f["contenido"] for f in fichas],
        normalize_embeddings=True,
        show_progress_bar=True,
        batch_size=32,
    )

    print("[3/4] Recreando la tabla en PostgreSQL")
    conn = get_connection()
    try:
        recrear_tabla(conn)

        print("[4/4] Insertando registros")
        filas = [
            (
                f["faq_id"],
                f["categoria"],
                f["pregunta"],
                f["respuesta"],
                f["contenido"],
                f["metadata"],
                to_vector_literal(vector),
            )
            for f, vector in zip(fichas, vectores)
        ]
        with conn.cursor() as cur:
            cur.executemany(
                f"""
                INSERT INTO {TABLE_NAME}
                    (faq_id, categoria, pregunta, respuesta, contenido, metadata, embedding)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s::vector)
                """,
                filas,
            )
        conn.commit()
        crear_indice(conn, len(filas))

        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME};")
            total = cur.fetchone()[0]
    finally:
        conn.close()

    print(f"\nCarga completada. Registros en la tabla '{TABLE_NAME}': {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
