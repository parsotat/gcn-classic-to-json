import numpy as np

from ... import utils

mode_dict = {
    1: "Null",
    2: "Short image",
    3: "long image",
    4: "Piled-up Photodiode",
    5: "Low Rate Photodiode",
    6: "Windowed Timing",
    7: "Photo-counting",
    8: "Raw data",
    9: "Bias map",
    10: "Stop",
}

termination_conditions_dict = {
    0: "Normal",
    1: "Terminated by time",
    2: "Terminated by snapshot",
    3: "Terminated by entering SAA",
    4: "Spectrum generated at the LRPD-to-WT transition",
    5: "Spectrum generated at the WT-to-LRorPC transition",
}


def parse_swift_xrt_spec(bin):
    misc_bits = np.unpackbits(bin[19:20].view(dtype="u1"))

    termination_conditions_bits = np.unpackbits(bin[21:22].view(dtype="u1"))

    return {
        "id": [bin[4]],
        "observation_start": utils.datetime_to_iso8601(bin[5], bin[6]),
        "ra": bin[7] * 1e-4,
        "dec": bin[8] * 1e-4,
        "observation_livetime": bin[9] * 1e-2,
        "observation_end": utils.datetime_to_iso8601(bin[10], bin[11]),
        "mode": mode_dict[bin[12]],
        "waveform": bin[13],
        "bias": bin[14],
        "termination_condition": termination_conditions_dict[
            np.packbits(np.pad(termination_conditions_bits[-4:], pad_width=[4, 0]))[0]
        ],
        "url": f"http://gcn.gsfc.nasa.gov/gcn/notices_s/{utils.binary_to_string(bin[22:39])}",
        "pos_out_of_range": bool(misc_bits[11]),
        "bright_star_nearby": bool(misc_bits[13]),
        "originally_subtresh": bool(misc_bits[20]),
        "too_sequence_uploaded": bool(misc_bits[22]),
        "watchdog_timeout": bool(misc_bits[29]),
    }


def parse(bin):
    bin[15:19]  # Spare. According to Docs: "16 bytes for the future"
    bin[20]  # Spare. According to Docs: "4 bytes for the future"

    misc_bits = np.unpackbits(bin[19:20].view(dtype="u1"))

    return {
        **parse_swift_xrt_spec(bin),
        "fits_file_does_not_exist": bool(misc_bits[24]),
    }
