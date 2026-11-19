"""Images for testcontainers come from compose.yaml, so Dependabot's digest updates apply to tests too."""
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]

POSTGIS_IMAGE = re.search(r"image:\s*(postgis/postgis\S+)", (ROOT / "compose.yaml").read_text())[1]
