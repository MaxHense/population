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
- Admin token: `dev-token`

Load data:

```bash
curl -H 'Authorization: Bearer dev-token' \
  -F file=@population.csv \
  --form-string grid='{"name":"Zensus 2022 1km","size":"1km","srid":3035}' \
  --form-string data_definition='{"population_key":"Einwohner","x_column":"x_mp_1km","y_column":"y_mp_1km","delimiter":";","decode":"utf-8"}' \
  http://localhost:8000/admin/grids
```

## Configuration

| Variable | Required | Meaning |
|---|---|---|
| `DBURL` | yes | PostGIS connection URL, e.g. `postgresql+psycopg://user:pw@host:5432/db` |
| `ADMIN_TOKEN` | no | Enables `POST /admin/grids` (upload). Send as `Authorization: Bearer <token>`. Unset = admin API disabled (404). Use a long random value, e.g. `openssl rand -hex 32`. |
| `CORS_ORIGINS` | no | Comma separated browser origins allowed to call the API, e.g. `https://population.example.org`. Unset = no cross-origin access. |
| `PORT` | no | Port inside the container, default `8000`. |

See `.env.example`.

## Production image

```bash
docker build -t population-api .
docker run -e DBURL=... -e ADMIN_TOKEN=... -e CORS_ORIGINS=... -p 8000:8000 population-api
```

On start the container runs `alembic upgrade head` (creates the PostGIS extension and tables if needed), then the API.
Running several replicas? Run `alembic upgrade head` once as a separate job instead.

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
