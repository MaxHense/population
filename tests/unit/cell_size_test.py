import pytest

from app.services.location import cell_size_m


@pytest.mark.parametrize("size, metres", [("1km", 1000), ("1 km", 1000), ("100m", 100), ("0.5km", 500), ("250 M", 250)])
def test_cell_size_in_metres(size, metres):
    assert cell_size_m(size) == metres


@pytest.mark.parametrize("size", ["", "km", "1 mile", "-1km", "1kmx"])
def test_unknown_cell_size_is_an_error(size):
    with pytest.raises(ValueError, match="cell size"):
        cell_size_m(size)
