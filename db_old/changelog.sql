-- changeset maximilian.hense:1
CREATE EXTENSION IF NOT EXISTS postgis;

-- changeset maximilian.hense:2
CREATE TABLE grid (
    grid_id SERIAL PRIMARY KEY,
    name VARCHAR(MAX),
    grid_size VARCHAR(50),
    grid_type VARCHAR(100),
    grid_year INTEGER NOT NULL
    );

-- changeset maximilian.hense:3
CREATE TABLE coord (
    coord_id SERIAL PRIMARY KEY,
    geom GEOMETRY(Point, 3035) NOT NULL,
    coord_population INTEGER NOT NULL,
    CONSTRAINT fk_grid
        FOREIGN_KEY(grid_id)
            REFERENCES grid(grid_id)
    );
