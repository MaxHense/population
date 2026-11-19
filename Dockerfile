FROM python:3.15.2-slim-trixie@sha256:65a65fc7b30b06cb6df4930fd4650697cb23f4c2698ab81fc87e4b031bc36928

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app
COPY requirements.txt .
# lock file with hashes: every package, incl. transitive, is verified
RUN pip install --no-cache-dir --require-hashes -r requirements.txt

COPY alembic.ini .
COPY migrations migrations
COPY app app

RUN useradd --system --uid 10001 app
USER app

EXPOSE 8000
# ponytail: migrations on every start, fine for one instance; with replicas run `alembic upgrade head` as a separate job
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
