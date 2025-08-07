import numpy as np

from ... import utils

termination_condition_dict = {
    0: "Normal",
    1: "Terminated by time",
    2: "Terminated by snapshot",
    3: "Terminated by entering SAA",
}


def parse(bin):
    bin[12:19]  # Spare. According to Docs: "28 bytes for the future".

    misc_bits = np.unpackbits(bin[19:20].view(np.uint8), bitorder='little')

    return {
        "mission": "SWIFT",
        "instrument": "XRT",
        "id": [bin[4]],
        "observation_start": utils.datetime_to_iso8601(bin[5], bin[6]),
        "observation_end": utils.datetime_to_iso8601(bin[10], bin[11]),
        "observation_livetime": bin[9] * 1e-2,
        "ra": bin[7] * 1e-4,
        "dec": bin[8] * 1e-4,
        "bins": bin[20],
        "termination_condition": termination_condition_dict[bin[21]],
        "pos_out_of_range": bool(misc_bits[11]),
        "bright_star_nearby": bool(misc_bits[13]),
        "was_subthresh": bool(misc_bits[20]),
        "too_sequence_uploaded": bool(misc_bits[22]),
        "url": f"http://gcn.gsfc.nasa.gov/gcn/notices_s/{''.join([i.decode('utf-8') for i in  bin[22:39].view('c')])}",
    }
