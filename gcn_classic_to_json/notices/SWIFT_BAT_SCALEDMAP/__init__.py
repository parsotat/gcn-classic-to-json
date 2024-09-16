import numpy as np

from ... import utils
from ..SWIFT_BAT_GRB_POS_ACK import parse_swift_bat

start_tracker_status = ["locked", "not locked"]


def parse(bin):
    bin[9:14]  # Unused. According to docs: '20 bytes for the future'
    bin[
        17
    ]  # Unused. According to docs: 'trig_index. This field is not yet (if ever) assigned.'
    bin[19]  # Unused. Flags are either internal or equivalent to bin[18]

    integ_time = bin[15] * 4 / 1000  # misc_bit has to be defined

    lat, lon = bin[16:17].view(">i2")

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

    return {
        **parse_swift_bat(bin),
        "alert_type": "retraction" if soln_status_bits[5] else "initial",
        "latitude": lat * 1e-2,
        "longitude": lon * 1e-2,
        "foreground_duration": bin[14] * 1e-3,
        "image_duration": integ_time if soln_status_bits[4] else None,
        "rate_duration": integ_time if not soln_status_bits[4] else None,
        "image_snr": bin[20] * 1e-2,
        "grb_status": grb_status,
        "point_source": bool(soln_status_bits[0]),
        "flaring_known_source": bool(soln_status_bits[2]),
        "star_tracker_status": start_tracker_status[soln_status_bits[10]],
        "bright_star_nearby": bool(soln_status_bits[13]),
        "originally_subtresh": bool(soln_status_bits[14]),
        "removed_from_catalog": bool(soln_status_bits[15]),
        "url": "http://gcn.gsfc.nasa.gov/gcn/notices_s/"
        + utils.binary_to_string(bin[22:39]),
    }
