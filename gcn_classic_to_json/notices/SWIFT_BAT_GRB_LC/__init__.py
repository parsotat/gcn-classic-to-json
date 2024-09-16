import numpy as np

from ... import utils
from ..SWIFT_BAT_GRB_POS_ACK import parse_swift_bat

start_tracker_status = ["locked", "not locked"]


def parse(bin):
    bin[9:12]  # Unused. According to docs: '12 bytes for the future'
    bin[19]  # Unused. Flags are either internal or equivalent to bin[18]

    soln_status_bits = np.flip(np.unpackbits(bin[18:19].view(dtype="u1")))

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

    integ_time = bin[15] * 4 / 1000

    lat, lon = bin[16:17].view(">i2")

    return {
        **parse_swift_bat(bin),
        "latitude": lat * 1e-2,
        "longitude": lon * 1e-2,
        "trigger_type": "image" if soln_status_bits[4] else "rate",
        "rate_duration": integ_time if not soln_status_bits[4] else None,
        "rate_energy_range": integ_time if not soln_status_bits[4] else None,
        "instrument_phi": 1e-2 * bin[12],
        "instrument_theta": 1e-2 * bin[13],
        "rate_snr": bin[21] * 1e-2,
        "image_snr": bin[20] * 1e-2,
        "delta_time": bin[14] * 1e-2,
        "trigger_index": bin[17],
        "url": "http://gcn.gsfc.nasa.gov/gcn/notices_s/"
        + utils.binary_to_string(bin[22:39]),
        "grb_status": grb_status,
        "point_source": bool(soln_status_bits[0]),
        "flaring_known_source": bool(soln_status_bits[2]),
        "star_tracker_status": start_tracker_status[soln_status_bits[10]],
        "bright_star_nearby": bool(soln_status_bits[13]),
        "removed_from_catalog": bool(soln_status_bits[15]),
        "galaxy_nearby": bool(soln_status_bits[16]),
    }
