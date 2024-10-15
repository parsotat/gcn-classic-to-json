from ... import utils
from ..SWIFT_ACTUAL_POINTDIR import parse_pointdir


def parse(bin):
    bin[10]  # Spare. According to Docs: '4 bytes for the future'
    bin[17:19]  # Spare. According to Docs: '8 bytes for the future'
    bin[20:22]  # Spare. According to Docs: '8 bytes for the future'

    _, bat_mode = bin[11:12].view(dtype=">i2")
    _, xrt_mode = bin[12:13].view(dtype=">i2")
    _, uvot_mode = bin[13:14].view(dtype=">i2")

    return {
        **parse_pointdir(bin),
        "bat_mode": hex(bat_mode),
        "xrt_mode": hex(xrt_mode),
        "uvot_mode": hex(uvot_mode),
        "observation_time": bin[14] * 1e-2,
        "merit_value": bin[15] * 1e-2,
        "target_name": utils.binary_to_string(bin[22:39]),
    }
