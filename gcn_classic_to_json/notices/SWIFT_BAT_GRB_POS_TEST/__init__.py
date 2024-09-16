import numpy as np

from ... import utils
from ..SWIFT_BAT_GRB_POS_ACK import parse_swift_bat

grb_status = ["It is not a GRB", "It is a GRB"]


def parse(bin):
    bin[15]  # Unused. According to docs: '4 bytes for the future'
    bin[16]  # Unused. According to docs: 'always be 0.00,0.00 for this notice'
    bin[19]  # Unused. Flags are either internal or equivalent to bin[18]
    bin[25:36]  # Unused. According to docs: '44 bytes for the future'
    bin[36:38]  # Intentionally Omitted. Flags are redundant with rest of notice
    bin[38]  # Intentionally omitted. Sun/Moon parameters

    integ_time = bin[14] * 4 / 1000

    soln_status_bits = np.flip(np.unpackbits(bin[18:19].view(dtype="u1")))
    soln_status_bits[8]  # Unused. According to docs: 'ground_catalog_source'.
    soln_status_bits[12]  # Unused. According to docs: 'blocked_catalog_source'.
    # These seems to be cross-referenced with a ground catalog with the name of the source printed in the text notices.
    # But since the name of this source isn't stored in the these packets, I don't see a reason to include it.

    return {
        **parse_swift_bat(bin),
        "alert_tense": "test",
        "ra_dec_error": 1e-4 * bin[11],
        "instrument_phi": 1e-2 * bin[12],
        "instrument_theta": 1e-2 * bin[13],
        "image_duration": integ_time if soln_status_bits[4] else None,
        "rate_duration": integ_time if not soln_status_bits[4] else None,
        "image_snr": bin[20] * 1e-2,
        "n_events": bin[9],
        "image_peak": bin[10],
        "background_events": bin[22],
        "background_start_time": utils.datetime_to_iso8601(bin[5], bin[23]),
        "backgroun_duration": bin[24] * 1e-2,
        "trigger_index": bin[17],
        "grb_status": grb_status[soln_status_bits[1]],
        "point_source": bool(soln_status_bits[0]),
        "flaring_known_source": bool(soln_status_bits[2]),
        "bright_star_nearby": bool(soln_status_bits[13]),
    }
