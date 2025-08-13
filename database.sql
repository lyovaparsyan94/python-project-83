DROP TABLE IF EXISTS url_checks;
DROP TABLE IF EXISTS urls;

CREATE TABLE urls (
    id serial PRIMARY KEY,
    name varchar(255) UNIQUE NOT NULL,
    created_at date DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE url_checks (
    id serial PRIMARY KEY,
    url_id bigint REFERENCES urls (id),
    status_code int,
    h1 varchar(255),
    title varchar(255),
    description varchar(255),
    created_at date DEFAULT CURRENT_TIMESTAMP
);