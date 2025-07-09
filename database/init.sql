
CREATE TABLE IF NOT EXISTS analysis_history (
    id SERIAL PRIMARY KEY,
    code_snippet TEXT NOT NULL,
    suggestions JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE analysis_history IS 'Tabela para armazenar o histórico de análises de código realizadas pelo sistema multiagente.';