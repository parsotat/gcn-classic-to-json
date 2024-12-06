import numpy as np

from ... import utils

error_flag_dict = {
    1: "No source found in image",
    2: "Algorithm did not converge",
    3: "Standard deviation too large",
    255: "General Error",
}


def parse(bin):
    bin[13:16]  # Spare. According to Docs: '12 bytes for the future'
    bin[20:39]  # Spare. According to Docs: '76 bytes for the future'

    error_flag_val = bin[18]

    misc_bits = np.flip(np.unpackbits(bin[19:20].view(dtype="u1")))

    return {
        "mission": "SWIFT",
        "instrument": "XRT",
        "id": [bin[4]],
        "alert_type": "retraction" if misc_bits[5] else "initial",
        "trigger_time": utils.datetime_to_iso8601(bin[5], bin[6]),
        "ra_pointing": bin[7] * 1e-4,
        "dec_pointing": bin[8] * 1e-4,
        "centroid_counts": bin[9],
        "min_counts": bin[10],
        "centroid_std": bin[11] * 1e-4,
        "sig_max": bin[12] * 1e-4,
        "phase2_iter": bin[16],
        "max_iter": bin[17],
        "error_flag": error_flag_dict[error_flag_val],
        "pos_out_of_range": bool(misc_bits[11]),
        "bright_star_nearby": bool(misc_bits[13]),
        "sper_data_used": bool(misc_bits[14]),
        "originally_subtresh": bool(misc_bits[20]),
        "too_sequence_uploaded": bool(misc_bits[22]),
    }
