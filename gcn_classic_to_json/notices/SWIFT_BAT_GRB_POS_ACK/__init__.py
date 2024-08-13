import numpy as np

from ... import utils

flag_descriptions = {
    0: "A point source was found.",
    1: "It is a GRB.",
    2: "It is an interesting src.",
    3: "It is in the flight catalog.",
    5: "It is definitely not a GRB.",
    6: "It is probably not a GRB or Transient(hi bkg level).",
    7: "It is probably not a GRB or Transient(low image significance; < 7).",
    8: "It is in the ground catalog.",
    9: "It is probably not a GRB or Transient(negative bkg slop).",
    10: "StraTracker not locked so trigger porbably bogus.",
    11: "It is probably not a GRB or Transient(very low image significance; < 6.5).",
    12: "It is the catalog of sources to be blocked.",
    13: "There is a bright star nearby.",
    14: "This was orginally a SubTresh, but it is now converted to a real BAT_POS.",
    15: "This is a source that has purposefully been removed from on-board catalog.",
    16: "This matched a Nearby_Galaxy in the on-board catalog.",
    28: "There was a temporal coincidence with another event.",
    29: "There was a spatial coincidence with another event.",
    30: "This is a test submission",
}

energy_ranges = [[15, 25], [15, 50], [25, 100], [50, 350]]


def parse(bin):
    bin[15]  # Unused. According to docs: '4 bytes for the future'
    bin[19]  # Unused. Flags are either internal or equivalent to bin[18]
    bin[26:36]  # Unused. According to docs: '40 bytes for the future'
    bin[36]  # Unused. Flags Equivalent to bin[18]
    bin[38]  # Intentionally omitted. Sun/Moon parameters

    integ_time = bin[14] * 16 / 1000

    lat, lon = bin[16:17].view(">i2")

    soln_status_bits = np.flip(np.unpackbits(bin[18:19].view(dtype="u1")))

    comments = "\n".join(
        [val for (key, val) in flag_descriptions.items() if (soln_status_bits[key])]
    )

    calalog_num = bin[25]

    energy_range_idx = np.flip(bin[37:38].view(dtype="i1"))[0]
    energy_range = energy_ranges[energy_range_idx]

    return {
        "mission": "SWIFT",
        "instrument": "BAT",
        "id": [bin[4]],
        "trigger_time": utils.datetime_to_iso8601(bin[5], bin[6]),
        "trigger_type": "image" if soln_status_bits[4] else "rate",
        "image_duration": integ_time if soln_status_bits[4] else None,
        "image_energy_range": energy_range if soln_status_bits[4] else None,
        "rate_duration": integ_time if not soln_status_bits[4] else None,
        "rate_energy_range": integ_time if not soln_status_bits[4] else None,
        "ra": 1e-4 * bin[7],
        "dec": 1e-4 * bin[8],
        "ra_dec_error": 1e-4 * bin[11],
        "instrument_phi": 1e-2 * bin[12],
        "instrument_theta": 1e-2 * bin[13],
        "latitude": lat * 1e-2,
        "longitude": lon * 1e-2,
        "rate_snr": bin[21] * 1e-2,
        "image_snr": bin[20] * 1e-2,
        "n_events": bin[9],
        "image_peak": bin[10],
        "background_events": bin[22],
        "background_start_time": utils.datetime_to_iso8601(bin[5], bin[23]),
        "backgroun_duration": bin[24] * 1e-2,
        "trigger_index": bin[17],
        "catalog_number": calalog_num if soln_status_bits[3] else None,
        "additional_info": comments if comments else None,
    }
