import numpy as np

from ..SWIFT_XRT_THRESHPIX_PROC import parse_swift_xrt_thresh


def parse(bin):
    bin[13:19]  # Spare. According to Docs: "24 bytes for the future".
    bin[20:22]  # Spare. According to Docs: "8 bytes for the future".
    bin[12]  # Intentionally Omitted. seq_num but unused

    misc_bits = np.flip(np.unpackbits(bin[19:20].view(dtype="u1")))

    return {
        **parse_swift_xrt_thresh(bin),
        "pos_out_of_range": bool(misc_bits[11]),
        "originally_subtresh": bool(misc_bits[20]),
        "too_sequence_uploaded": bool(misc_bits[22]),
        "watchdog_timeout": bool(misc_bits[29]),
    }
