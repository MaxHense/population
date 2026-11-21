# Population

API that returns the population inside a polygon, based on 1 km population grids stored in PostGIS.
Stateless: one container, configured only through environment variables.

## Quick start (Docker)

```bash
docker compose up
```

Starts PostGIS and the API with hot reload (`app/` and `migrations/` are mounted).

- API docs: http://localhost:8000/docs
- Database: `localhost:54320`, user/password `postgres`

Load data: see [Data](#data-eurostat-census-grid-2021-europe-1-km).

## Configuration

| Variable | Required | Meaning |
|---|---|---|
| `DBURL` | yes | PostGIS connection URL, e.g. `postgresql+psycopg://user:pw@host:5432/db` |
| `CORS_ORIGINS` | no | Comma separated browser origins allowed to call the API, e.g. `https://population.example.org`. Unset = no cross-origin access. |
| `PORT` | no | Port inside the container, default `8000`. |

See `.env.example`.

## Production image

```bash
docker build -t population-api .
docker run -e DBURL=... -e CORS_ORIGINS=... -p 8000:8000 population-api
```

On start the container runs `alembic upgrade head` (creates the PostGIS extension and tables if needed), then the API.
Running several replicas? Run `alembic upgrade head` once as a separate job instead.

## Data: Eurostat Census Grid 2021 (Europe, 1 km)

The API is read only. Data is loaded by scripts in `scripts/` (not part of the image), from your machine straight into the database, after the backend ran once (it creates the schema):

```bash
curl -O https://gisco-services.ec.europa.eu/census/2021/Eurostat_Census-GRID_2021_V3.zip
unzip -j Eurostat_Census-GRID_2021_V3.zip '*/ESTAT_Census_2021_V3.csv'
DBURL=postgresql+psycopg://... python -m scripts.eurostat ESTAT_Census_2021_V3.csv
```

About 30 s locally, 280 MB in the database. All cells are stored in EPSG:3035, so one query covers every grid;
a script for data in another CRS transforms the cell centres on import (`ST_Transform(..., 3035)`). © European Union, source Eurostat; the data is modified (only inhabited cells, cell centres).

## Development without Docker

```bash
python -m venv .venv && . .venv/bin/activate
pip install --require-hashes -r requirements.txt -r requirements-dev.txt
cp .env.example .env            # point DBURL to a PostGIS
alembic upgrade head
uvicorn app.main:app --reload --env-file .env
```

## Dependencies

Direct dependencies live in `requirements.in` (runtime) and `requirements-dev.in` (tests, lint).
`requirements.txt` and `requirements-dev.txt` are generated lock files: every package, including transitive ones, with exact version and hashes.
Do not edit them by hand. After changing an `.in` file:

```bash
pip-compile --allow-unsafe --generate-hashes --strip-extras --output-file=requirements.txt requirements.in
pip-compile --allow-unsafe --generate-hashes --strip-extras --output-file=requirements-dev.txt requirements-dev.in
```

Dependabot updates both and regenerates the hashes.

## Test

```bash
pytest tests/unit         # fast, no database
pytest tests/integration  # needs Docker (testcontainers PostGIS)
pytest                    # all
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
