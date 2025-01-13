import importlib
import pkgutil

import numpy as np
from gcn import NoticeType

_parsers = {
    module: importlib.import_module(f".{module}", __package__).parse
    for _, module, _ in pkgutil.iter_modules(__path__)
}

keys = tuple(_parsers.keys())


def _frombuffer(value):
    return np.frombuffer(value, dtype=">i4")


def parse(key, value):
    ints = _frombuffer(value)
    assert len(ints) == 40
    assert ints[0] == NoticeType[key], "Field 0 must equal the notice type"
    ints[1]  # Unused. According to docs: 'Generally set to 1.'
    ints[2]  # Unused. According to docs: 'hopcount item is defunct'.
    ints[3]  # Unused. According to docs: 'seconds of day when packet was created'.
    assert ints[-1] == np.asarray("\0\0\0\n", dtype="c").view(">i4")[0], (
        "Field 39 must be a newline"
    )
    parser = _parsers[key]
    return parser(ints)
