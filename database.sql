CREATE TABLE IF NOT EXISTS urls (
        id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        name VARCHAR(255) UNIQUE NOT NULL,
        created_at DATE DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS url_checks (
        id SERIAL PRIMARY KEY,
        url_id INT REFERENCES urls (id) NOT NULL,
        status_code INT,
        h1 VARCHAR(255),
        title VARCHAR(255) NOT NULL,
        description VARCHAR(255),
        created_at DATE DEFAULT CURRENT_TIMESTAMP
);