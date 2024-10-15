import numpy as np

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
    "Unknown",
]


def parse(bin):
    bin[11]  # Unused. According to Docs: 'ra_dec_error, but less precise'
    bin[12:16]  # Spare. According to Docs: '16 bytes for the future'
    bin[17]  # Spare. According to Docs: '4 bytes for the future'
    bin[
        21
    ]  # Unused. According to Docs : 'angular distance between XRT and UVOT but set to 0'
    bin[22:39]  # Spare. According to Docs: '68 bytes for the future'

    soln_status = np.flip(np.unpackbits(bin[18:19].view(dtype="u1")))

    misc_status = np.flip(np.unpackbits(bin[19:20].view(dtype="u1")))

    return {
        "id": [bin[4]],
        "alert_tense": "test" if soln_status[30] else "current",
        "alert_type": "retraction" if soln_status[5] else "initial",
        "trigger_time": utils.datetime_to_iso8601(bin[5], bin[6]),
        "ra": bin[7] * 1e-4,
        "dec": bin[8] * 1e-4,
        "ra_dec_error": bin[16] * 1e-4 / 36,
        "systematic_included": True,
        "filter": [filters[bin[10]]],
        "magnitide": bin[9] * 1e-2,
        "magnitude_error": bin[20] * 1e-2,
        "point_source": bool(soln_status[0]),
        "catalog_source": bool(soln_status[3]),
        "ground_catalog_source": bool(soln_status[8]),
        "spatial_coincidence": bool(soln_status[28]),
        "temporal_coincidence": bool(soln_status[29]),
        "bright_star_nearby": bool(misc_status[13]),
        "updated_position": bool(misc_status[25]),
        "ground_generated": bool(misc_status[30]),
    }
