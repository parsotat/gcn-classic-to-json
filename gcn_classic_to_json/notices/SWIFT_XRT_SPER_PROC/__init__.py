import numpy as np

from ... import utils


def parse_swift_xrt_sper(bin):
    misc_bits = np.unpackbits(bin[19:20].view(np.uint8), bitorder='little')

    return {
        "mission": "SWIFT",
        "instrument": "XRT",
        "id": [bin[4]],
        "observation_start": utils.datetime_to_iso8601(bin[5], bin[6]),
        "ra": bin[7] * 1e-4,
        "dec": bin[8] * 1e-4,
        "observation_livetime": bin[9] * 1e-3,
        "observation_end": utils.datetime_to_iso8601(bin[10], bin[11]),
        "num_packets": bin[12],
        "num_events": bin[20],
        "url": f"http://gcn.gsfc.nasa.gov/gcn/notices_s/{''.join([i.decode('utf-8') for i in  bin[22:39].view('c')])}",
        "too_sequence_uploaded": bool(misc_bits[22]),
        "watchdog_timeout": bool(misc_bits[29]),
    }


def parse(bin):
    bin[13:19]  # Spare. According to Docs: "24 bytes for the future".
    bin[21]  # Spare. According to Docs: "4 bytes for the future".
    return {**parse_swift_xrt_sper(bin)}
