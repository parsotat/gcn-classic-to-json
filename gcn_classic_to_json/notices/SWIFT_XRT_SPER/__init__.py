import numpy as np

from ..SWIFT_XRT_SPER_PROC import parse_swift_xrt_sper


def parse(bin):
    bin[13:19]  # Spare. According to Docs: "24 bytes for the future".
    bin[21]  # Spare. According to Docs: "4 bytes for the future".
    misc_bits = np.flip(np.unpackbits(bin[19:20].view(dtype="u1")))

    return {
        **parse_swift_xrt_sper(bin),
        "star_tracker_not_locked": bool(misc_bits[10]),
        "pos_out_of_range": bool(misc_bits[11]),
    }
