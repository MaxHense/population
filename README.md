# Population

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install all requirements.

```bash
pip install -r requirements.txt
```

To run this project you need a running PostGIS Database. Add a environmen file with the variable `DBURL`.

| Variable | Required | Meaning |
|---|---|---|
| `DBURL` | yes | PostGIS connection URL |
| `ADMIN_TOKEN` | no | Enables `POST /admin/grids` (upload). Send as `Authorization: Bearer <token>`. Unset = admin API disabled (404). Use a long random value, e.g. `openssl rand -hex 32`. |

## Usage

Run Fastapi App with uvicorn, it is necessary that DBURL is set. For that either mak an environment variable or use the following command with an `.env` environment file

```bash
uvicorn app.main:app --env-file=./.env
```

## Test

```bash
pytest tests/unit         # fast, no database
pytest tests/integration  # needs Docker (testcontainers PostGIS)
pytest                   # all
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
