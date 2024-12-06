import numpy as np

from ... import utils


def parse_swift_xrt_thresh(bin):
    return {
        "id": [bin[4]],
        "observation_start": utils.datetime_to_iso8601(bin[5], bin[6]),
        "ra": bin[7] * 1e-4,
        "dec": bin[8] * 1e-4,
        "observation_livetime": bin[9] * 1e-3,
        "observation_end": utils.datetime_to_iso8601(bin[10], bin[11]),
        "url": f"http://gcn.gsfc.nasa.gov/gcn/notices_s/{utils.binary_to_string(bin[22:39])}",
    }


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
