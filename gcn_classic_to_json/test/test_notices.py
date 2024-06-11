import importlib.resources
import json

import pytest

from .. import notices

files = importlib.resources.files(notices)


@pytest.mark.parametrize('key', notices.keys)
def test_notices(key, generate):
    bin_path = files / key / 'example.bin'
    json_path = files / key / 'example.json'

    value = bin_path.read_bytes()
    actual = notices.parse(key, value)

    if generate:
        with json_path.open('w') as f:
            json.dump(actual, f, indent=2)
        pytest.skip(f'saved expected output to {json_path}')

    with json_path.open('r') as f:
        expected = json.load(f)
    assert actual == expected
