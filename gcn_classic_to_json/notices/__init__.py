import importlib
import pkgutil

import numpy as np
from gcn import NoticeType
import logging

_parsers = {
    module: importlib.import_module(f".{module}", __package__).parse
    for _, module, _ in pkgutil.iter_modules(__path__)
}

keys = tuple(_parsers.keys())


def _frombuffer(value):
    return np.frombuffer(value, dtype="<i4")


def parse(value):
    ints = _frombuffer(value)
    assert len(ints) == 40
    
    #get the actual notice type if we dont know it
    key=[i for i in NoticeType if i.value==ints[0] ]

    assert key != None, f"There is no associated notice type for packet type {ints[0]}"
    assert len(key) == 1, f"There are multiple or No associated notice type for packet type {ints[0]}"
    
    key=key[0]
    
    assert ints[0] == NoticeType[key.name], "Field 0 must equal the notice type"
    ints[1]  # Unused. According to docs: 'Generally set to 1.'
    ints[2]  # Unused. According to docs: 'hopcount item is defunct'.
    ints[3]  # Unused. According to docs: 'seconds of day when packet was created'.
    assert ints[-1] == np.asarray("\0\0\0\n", dtype="c").view(">i4")[0], (
        "Field 39 must be a newline"
    )

    logging.info(f'Identified packet as a {key.name} type notice.')


    parser = _parsers[key.name]
    return parser(ints)
