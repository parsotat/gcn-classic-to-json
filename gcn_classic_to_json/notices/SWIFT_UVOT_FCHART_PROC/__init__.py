from ... import utils

filters = [
    "Blocked",
    "UV_Grism",
    "UVW2",
    "V",
    "UVM2",
    "Vis_Grism",
    "UVW1",
    "U",
    "Magnifier",
    "B",
    "White",
    "unknown",
]


def parse_uvot_srclist(bin):
    return {
        "id": [bin[4]],
        "trigger_time": utils.datetime_to_iso8601(bin[5], bin[6]),
        "ra_pointing": bin[7] * 1e-4,
        "dec_pointing": bin[8] * 1e-4,
        "roll": bin[9] * 1e-4,
        "filter": [filters[bin[10]]],
        "background_mean": bin[11] * 1e-4,
        "image_max": [bin[12], bin[13]],
        "n_stars": bin[14],
        "image_offset": [bin[15], bin[16]],
        "detector_threshold": bin[17],
        "photometry_threshold": bin[18],
        "fits_file_url": f"http://gcn.gsfc.nasa.gov/gcn/notices_s/{utils.binary_to_string(bin[22:39])}",
    }


def parse(bin):
    bin[19]  # Intentionally Omitted. Bits seemed to be used for internal messages
    bin[20:22]  # Spare. According to Docs: '8 bytes for future use'

    return {**parse_uvot_srclist(bin)}
