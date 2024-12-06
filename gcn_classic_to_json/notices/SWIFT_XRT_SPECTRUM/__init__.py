import numpy as np

from ..SWIFT_XRT_SPECTRUM_PROC import parse_swift_xrt_spec


def parse(bin):
    bin[15:19]  # Spare. According to Docs: "16 bytes for the future"
    bin[20]  # Spare. According to Docs: "4 bytes for the future"
    misc_bits = np.unpackbits(bin[19:20].view(dtype="u1"))

    return {
        **parse_swift_xrt_spec(bin),
        "first_packet_missing": bool(misc_bits[27]),
        "second_packet_missing": bool(misc_bits[26]),
        "third_packet_missing": bool(misc_bits[25]),
    }
