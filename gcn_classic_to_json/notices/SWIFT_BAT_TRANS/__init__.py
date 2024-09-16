import numpy as np

from ... import utils
from ..SWIFT_BAT_GRB_POS_ACK import parse_swift_bat

energy_ranges = [[15, 25], [15, 50], [25, 100], [50, 350]]
start_tracker_status = ["locked", "not locked"]


def parse(bin):
    bin[15]  # Unused. According to docs: '4 bytes for the future'
    bin[19]  # Unused. Flags are either internal or equivalent to bin[18]
    bin[26:36]  # Unused. According to docs: '40 bytes for the future'
    bin[36]  # Unused. Flags Equivalent to bin[18]
    bin[38]  # Intentionally omitted. Sun/Moon parameters

    integ_time = bin[14] * 4 / 1000

    lat, lon = bin[16:17].view(">i2")

    soln_status_bits = np.flip(np.unpackbits(bin[18:19].view(dtype="u1")))

    soln_status_bits[8]  # Unused. According to docs: 'ground_catalog_source'.
    soln_status_bits[12]  # Unused. According to docs: 'blocked_catalog_source'.
    # These seems to be cross-referenced with a ground catalog with the name of the source printed in the text notices.
    # But since the name of this source isn't stored in the these packets, I don't see a reason to include it.
    if soln_status_bits[11]:
        grb_status = (
            "It is probably not a GRB or transient due to very low image significance"
        )
    elif soln_status_bits[7]:
        grb_status = (
            "It is probably not a GRB or transient due to low image significance"
        )
    elif soln_status_bits[9]:
        grb_status = (
            "It is probably not a GRB or transient due to negative background slope"
        )
    elif soln_status_bits[6]:
        grb_status = (
            "It is probably not a GRB or transient due to high background level"
        )
    elif soln_status_bits[1]:
        grb_status = "It is a GRB"
    else:
        grb_status = "It is not a GRB"

    calalog_num = bin[25]

    energy_range_idx = np.flip(bin[37:38].view(dtype="i1"))[0]
    energy_range = energy_ranges[energy_range_idx]

    return {
        **parse_swift_bat(bin),
        "ra_dec_error": bin[11] * 1e-4,
        "instrument_phi": bin[12] * 1e-4,
        "instrument_theta": bin[13] * 1e-4,
        "latitude": lat * 1e-2,
        "longitude": lon * 1e-2,
        "trigger_type": "image" if soln_status_bits[4] else "rate",
        "image_duration": integ_time if soln_status_bits[4] else None,
        "image_energy_range": energy_range if soln_status_bits[4] else None,
        "rate_duration": integ_time if not soln_status_bits[4] else None,
        "rate_energy_range": energy_range if not soln_status_bits[4] else None,
        "rate_snr": bin[21] * 1e-2,
        "image_snr": bin[20] * 1e-2,
        "n_events": bin[9],
        "image_peak": bin[10],
        "background_events": bin[22],
        "background_start_time": utils.datetime_to_iso8601(bin[5], bin[23]),
        "backgroun_duration": bin[24] * 1e-2,
        "trigger_index": bin[17],
        "catalog_number": calalog_num if soln_status_bits[3] else None,
        "grb_status": grb_status,
        "point_source": bool(soln_status_bits[0]),
        "flaring_known_source": bool(soln_status_bits[2]),
        "star_tracker_status": start_tracker_status[soln_status_bits[10]],
        "bright_star_nearby": bool(soln_status_bits[13]),
        "temporal_coincidence": bool(soln_status_bits[28]),
        "spatial_coincidence": bool(soln_status_bits[29]),
    }
