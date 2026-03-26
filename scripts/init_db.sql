-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Document chunks (RAG storage)
CREATE TABLE IF NOT EXISTS document_chunks (
    id          SERIAL PRIMARY KEY,
    doc_name    TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    content     TEXT NOT NULL,
    embedding   vector(384),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- HNSW index for fast similarity search
CREATE INDEX IF NOT EXISTS idx_chunks_embedding
    ON document_chunks USING hnsw (embedding vector_cosine_ops);

-- Transactions (used in Part 2 & 3)
CREATE TABLE IF NOT EXISTS transactions (
    id             SERIAL PRIMARY KEY,
    transaction_id TEXT UNIQUE NOT NULL,
    amount         NUMERIC(12,2) NOT NULL,
    merchant       TEXT,
    status         TEXT DEFAULT 'pending',
    risk_level     TEXT,
    risk_reason    TEXT,
    location       TEXT,
    flagged        BOOLEAN DEFAULT FALSE,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- Request logs
CREATE TABLE IF NOT EXISTS request_logs (
    id            SERIAL PRIMARY KEY,
    endpoint      TEXT NOT NULL,
    question      TEXT,
    response_time FLOAT,
    cache_hit     BOOLEAN DEFAULT FALSE,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Seed transactions for Part 2 testing
INSERT INTO transactions (transaction_id, amount, merchant, status, location)
VALUES
    ('txn_001', 125.00,   'Amazon',       'completed',  'USA'),
    ('txn_002', 8750.00,  'XYZ Corp',     'suspicious', 'Nigeria'),
    ('txn_003', 42.50,    'Starbucks',    'completed',  'USA'),
    ('txn_004', 15200.00, 'Unknown LLC',  'suspicious', 'Russia'),
    ('txn_005', 3.99,     'Netflix',      'completed',  'USA'),
    ('txn_006', 5500.00,  'TechSupplies', 'pending',    'China')
ON CONFLICT (transaction_id) DO NOTHING;
