import importlib
import pkgutil

import numpy as np

_parsers = {
    module: importlib.import_module(f".{module}", __package__).parse
    for _, module, _ in pkgutil.iter_modules(__path__)
}

keys = tuple(_parsers.keys())


def parse(key, value):
    ints = np.frombuffer(value, dtype=">i4")
    assert len(ints) == 40
    parser = _parsers[key]
    return parser(ints)
