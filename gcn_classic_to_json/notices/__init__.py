import importlib
import pkgutil
import struct

_int4 = struct.Struct("!l")
_parsers = {
    module: importlib.import_module(f'.{module}', __package__).parse
    for _, module, _ in pkgutil.iter_modules(__path__)
}

keys = tuple(_parsers.keys())


def parse(key, value):
    ints = [_ for _, in _int4.iter_unpack(value)]
    assert len(ints) == 40
    parser = _parsers[key]
    return parser(ints)
