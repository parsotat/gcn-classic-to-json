import numpy as np

from ..SWIFT_BAT_GRB_POS_ACK import parse_swift_bat


def parse(bin):
    bin[12:17]  # Unused. According to docs: '20 bytes for the future'
    bin[19]  # Intentionally Omitted. According to docs: 'miscellaneous bits'
    bin[20]  # Unused. According to docs: '4 bytes for the future'
    bin[22:38]  # Unused. According to docs: '64 bytes for the future'

    lat, lon = bin[10:11].view(">i2")

    at_slew_bits = np.flip(np.unpackbits(bin[18:19].view(dtype="u1")))

    at_slew_flag_descriptions = {
        0: "This burst is worthy of becoming the new Automated target.",
        1: "This burst is of sufficient merit to request a s/c slew.",
    }

    comments = "".join(
        [val for (key, val) in at_slew_flag_descriptions.items() if (at_slew_bits[key])]
    )

    return {
        **parse_swift_bat(bin),
        "latitude": lat * 1e-2,
        "longitude": lon * 1e-2,
        "ra_dec_error": 1e-4 * bin[11],
        "roll": bin[9] * 1e-4,
        "trigger_index": bin[17],
        "merit_value": bin[38] * 1e-2,
        "additional_info": comments if comments else None,
    }
