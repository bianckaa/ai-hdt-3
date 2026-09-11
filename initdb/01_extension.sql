-- Habilita pgvector al crear el volumen por primera vez.
-- El script de carga tambien la habilita, de modo que la base queda lista
-- aunque el volumen ya existiera antes de agregar este archivo.
CREATE EXTENSION IF NOT EXISTS vector;
