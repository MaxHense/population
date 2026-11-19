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


def actions():
    return [u for f in (ROOT / ".github" / "workflows").glob("*.yml")
            for u in re.findall(r"^\s*-?\s*uses:\s*(\S+)", f.read_text(), re.M)]


def test_there_are_actions_to_check():
    assert actions()


@pytest.mark.parametrize("action", actions())
def test_action_is_pinned_by_commit_sha(action):
    # tags can be moved to other code, a full commit SHA cannot
    assert re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", action), f"{action} is not pinned to a commit SHA"
