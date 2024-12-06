import numpy as np

from ... import utils

mode_dict = {
    1: "Null",
    2: "Short Image",
    3: "Long Image",
    4: "Piled-up Photodiode",
    5: "Low Rate Photodiode",
    6: "Windowed Timing",
    7: "Photo-counting",
    8: "Raw Data",
    9: "Bias Map",
    10: "Stop",
}


def parse_swift_xrt_image(bin):
    gain_wave_mode_bits = np.unpackbits(bin[17:18].view(dtype="u1"))
    waveform_id = np.packbits(gain_wave_mode_bits[-8:])
    mode = np.packbits(gain_wave_mode_bits[-16:-8])
    gain = np.packbits(gain_wave_mode_bits[-24:-16])

    misc_bits = np.flip(np.unpackbits(bin[19:20].view(dtype="u1")))

    return {
        "mission": "SWIFT",
        "instrument": "XRT",
        "id": [bin[4]],
        "observation_start": utils.datetime_to_iso8601(bin[5], bin[6]),
        "observation_livetime": bin[18] * 1e-2,
        "ra": bin[7] * 1e-4,
        "dec": bin[8] * 1e-4,
        "num_bright_pixels": bin[9],
        "centroid_std_dev": bin[11] * 1e-4,
        "centroid_pos": [bin[12] * 1e-2, bin[13] * 1e-2],
        "image_pos": [bin[14] * 1e-2, bin[15] * 1e-2],
        "roll": bin[16] * 1e-4,
        "gain": gain[0],
        "mode": mode_dict[mode[0]],
        "waveform_id": waveform_id[0],
        "not_real_astrophysical_peak": bool(misc_bits[10]),
        "pos_out_of_range": bool(misc_bits[11]),
        "bright_star_nearby": bool(misc_bits[13]),
        "originally_subtresh": bool(misc_bits[20]),
        "too_sequence_uploaded": bool(misc_bits[22]),
        "first_packet_missing": bool(misc_bits[27]),
        "second_packet_missing": bool(misc_bits[26]),
        "third_packet_missing": bool(misc_bits[25]),
        "watchdog_time": bool(misc_bits[29]),
        "grb_pos": [bin[20] * 1e-2, bin[21] * 1e-2],
        "url": f"http://gcn.gsfc.nasa.gov/gcn/notices_s/{utils.binary_to_string(bin[22:39])}",
    }


def parse(bin):
    bin[10]  # Spare. 4 bytes for the future.

    return {**parse_swift_xrt_image(bin)}
