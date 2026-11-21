"""
Import the Eurostat Census Grid 2021 (V3, 1 km, EPSG:3035) straight into the database.
Runs on your machine, not in the image. Needs the schema: start the backend once (or `alembic upgrade head`).

    DBURL=postgresql+psycopg://... python -m scripts.eurostat ESTAT_Census_2021_V3.csv

Uses COPY: 1.9 million cells in about 30 s with constant memory.
One transaction: on any error nothing is imported. Running it twice fails on the unique grid.
"""
import csv
import sys

from app.models.db import STORAGE_SRID
from app.repositories.db import get_engine

GRID = ("Eurostat Census 2021", 1000, 3035)


def cells(lines):
    """(x, y, population) of the centre of every inhabited cell, GRD_ID names the lower left corner"""
    for row in csv.DictReader(lines):
        population = int(row["T"])
        if population <= 0 or not row["GRD_ID"].startswith("CRS3035RES1000mN"):
            continue  # empty, -8888 confidential, -9999 missing, or 'XX_unallocated' without a location
        north, east = row["GRD_ID"].removeprefix("CRS3035RES1000mN").split("E")
        yield int(east) + 500, int(north) + 500, population


def main(path: str):
    """insert the grid and all its cells in one transaction"""
    conn = get_engine().raw_connection()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO grid (name, cell_size_m, srid) VALUES (%s, %s, %s) RETURNING id",
                    GRID)
        grid_id = cur.fetchone()[0]
        count = 0
        with open(path, newline="", encoding="utf-8") as file, \
                cur.copy("COPY location (grid_id, geom, population) FROM STDIN") as copy:
            for x, y, population in cells(file):
                copy.write_row((grid_id, f"SRID={STORAGE_SRID};POINT({x} {y})", population))
                count += 1
        cur.execute("ANALYZE location")
        conn.commit()
    finally:
        conn.close()
    print(f"grid {grid_id}: {count} cells")


if __name__ == "__main__":
    main(sys.argv[1])
