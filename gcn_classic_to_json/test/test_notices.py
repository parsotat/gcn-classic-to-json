import importlib.resources
from json import load, loads

import numpy as np
import pytest

from .. import notices
from ..json import dumps
from ..notices import _frombuffer as _orig_frombuffer

files = importlib.resources.files(notices)


class NDArrayNanny(np.ndarray):
    """A ndarray subclass that tracks which elements have been accessed.

    >>> array = np.zeros(5, dtype='>i4').view(NDArrayNanny)
    >>> foobar = array[2:4]
    >>> array.used
    array([False, False,  True,  True, False])
    >>> subarray = array[1:]
    >>> subarray.used
    array([False, False, False, False])
    >>> subarray_halfprecision = subarray.view('>i2')
    >>> batbaz = subarray_halfprecision[1]
    >>> subarray_halfprecision.used
    array([False,  True, False, False, False, False, False, False])
    """

    @property
    def used(self):
        if not hasattr(self, "_used"):
            self._used = np.zeros(self.shape, dtype=bool)
        return self._used

    def __getitem__(self, i):
        self.used[i] = True
        return super().__getitem__(i)


@pytest.mark.parametrize("key", notices.keys)
def test_all_fields_used(key, monkeypatch):
    """Check that every field in the binary packet is used in the conversion."""

    used = None

    def mock_frombuffer(*args, **kwargs):
        nonlocal used
        result = _orig_frombuffer(*args, **kwargs).view(NDArrayNanny)
        used = result.used
        return result

    monkeypatch.setattr(notices, "_frombuffer", mock_frombuffer)

    bin_path = files / key / "example.bin"
    value = bin_path.read_bytes()
    notices.parse(key, value)

    if not used.all():
        raise AssertionError(
            f"All fields in the binary packet must be used. The fields with the following indices were unused: {' '.join(np.flatnonzero(~used).astype(str))}"
        )


@pytest.mark.parametrize("key", notices.keys)
def test_notices(key, generate):
    """Check the output of the parser against known JSON output."""
    bin_path = files / key / "example.bin"
    json_path = files / key / "example.json"

    value = bin_path.read_bytes()
    actual_str = dumps(notices.parse(key, value), indent=2)
    actual = loads(actual_str)

    if generate:
        with json_path.open("w") as f:
            print(actual_str, file=f)
        pytest.skip(f"saved expected output to {json_path}")

    with json_path.open("r") as f:
        expected = load(f)
    assert actual == expected
