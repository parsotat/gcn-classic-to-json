import numpy as np

from ..SWIFT_BAT_GRB_POS_ACK import parse_swift_bat


def parse(bin):
    bin[12:17]  # Unused. According to docs: '20 bytes for the future'
    bin[19]  # Intentionally Omitted. According to docs: 'miscellaneous bits'
    bin[20]  # Unused. According to docs: '4 bytes for the future'
    bin[22:38]  # Unused. According to docs: '64 bytes for the future'

    lat, lon = bin[10:11].view("<i2")

    at_slew_bits = [(bin[18:19] >> 1) &1, bin[18:19] & 1]

    at_slew_flag_descriptions = {
        0: "This burst is of sufficient merit to request a s/c slew.",
        1: "This burst is worthy of becoming the new Automated target.",
    }

    comments = "\n".join(
        [val for (key, val) in at_slew_flag_descriptions.items() if (at_slew_bits[key])]
    )

    return {
        **parse_swift_bat(bin),
        # bin[16] high-order short = lat: spacecraft latitude at the time of the BAT trigger.
        # Stored as a 2-byte integer in centi-degrees (fl.pt. degrees * 100).
        # Divide by 100 to recover degrees.
        "latitude": lat * 1e-2,

        # bin[16] low-order short = lon: spacecraft longitude at the time of the BAT trigger.
        # Same encoding as lat. Divide by 100 to recover degrees.
        "longitude": lon * 1e-2,

        # bin[11] = burst_error: radius of the position error circle (90% containment).
        # Stored in units of 0.0001-deg (fl.pt. degrees * 10000, then integerized).
        # Initially hardwired at 4 arcmin (0.067 deg); later made flux-dependent.
        # Divide by 10000 to recover degrees.
        "ra_dec_error": 1e-4 * bin[11],

        "roll": bin[9] * 1e-4,

        # bin[17] = trig_index: index value (row number in the BAT on-board flight software
        # table) of the trigger criterion that was the highest-significance successful trigger.
        "trigger_index": bin[17],

        "merit_value": bin[38] * 1e-2,
        "additional_info": comments if comments else None,
    }
