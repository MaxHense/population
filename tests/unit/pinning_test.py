"""Every container image is pinned to a digest (tag kept for readability, Dependabot updates both)."""
import re

import pytest

from tests.images import POSTGIS_IMAGE, ROOT

PINNED = re.compile(r"^[\w./-]+:[\w.-]+@sha256:[0-9a-f]{64}$")


def images():
    dockerfile = re.findall(r"^FROM\s+(\S+)", (ROOT / "Dockerfile").read_text(), re.M)
    compose = re.findall(r"^\s*image:\s*(\S+)", (ROOT / "compose.yaml").read_text(), re.M)
    return dockerfile + compose


def test_there_are_images_to_check():
    assert len(images()) >= 2


@pytest.mark.parametrize("image", images())
def test_image_is_pinned_by_tag_and_digest(image):
    assert PINNED.match(image), f"{image} is not pinned as name:tag@sha256:<digest>"


def test_testcontainers_use_the_pinned_postgis():
    assert PINNED.match(POSTGIS_IMAGE)
