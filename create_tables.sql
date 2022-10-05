BEGIN;

CREATE TABLE IF NOT EXISTS updates (
    id SERIAL PRIMARY KEY,
    indicator TEXT NOT NULL,
    updated DATE DEFAULT Now()
);

COMMIT;

