BEGIN;

CREATE TABLE updates (
    id SERIAL PRIMARY KEY,
    indicator TEXT NOT NULL,
    updated DATE DEFAULT Now()
);

COMMIT;

