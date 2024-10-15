import numpy as np

from ... import utils

start_tracker_status = ["locked", "not locked"]


def parse_fom(bin):
    id_record_number_bits = np.flip(np.unpackbits(bin[4:5].view(dtype="u1")))
    record_number = np.packbits(np.flip(id_record_number_bits[24:]))
    id = id_record_number_bits[:24].dot(2 ** np.arange(24))

    lat, lon = bin[10:11].view(dtype=">i2")

    integ_time = bin[15] * 4 / 1000

    soln_status_bits = np.flip(np.unpackbits(bin[16:17].view(dtype="u1")))
    soln_status_bits[8]  # Unused. According to docs: 'ground_catalog_source'.
    soln_status_bits[12]  # Unused. According to docs: 'blocked_catalog_source'.
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

    at_slew_flags = np.flip(np.unpackbits(bin[18:19].view(dtype="u1")))

    image_snr = bin[20]

    return {
        "mission": "SWIFT",
        "id": [id],
        "record_number": record_number[0],
        "alert_type": "retraction" if soln_status_bits[5] else "initial",
        "trigger_time": utils.datetime_to_iso8601(bin[5], bin[6]),
        "ra": bin[7] * 1e-4,
        "dec": bin[8] * 1e-4,
        "roll": bin[9] * 1e-4,
        "latitude": lat * 1e-2,
        "longitude": lon * 1e-2,
        "merit_value": bin[38] * 1e-2,
        "grb_status": grb_status,
        "point_source": bool(soln_status_bits[0]),
        "flaring_known_source": bool(soln_status_bits[2]),
        "star_tracker_status": start_tracker_status[soln_status_bits[10]],
        "bright_star_nearby": bool(soln_status_bits[13]),
        "removed_from_catalog": bool(soln_status_bits[15]),
        "galaxy_nearby": bool(soln_status_bits[16]),
        "trigger_index": bin[17],
        "trigger_type": "image" if soln_status_bits[4] else "rate",
        "image_duration": integ_time if soln_status_bits[4] else None,
        "rate_duration": integ_time if not soln_status_bits[4] else None,
        "rate_snr": bin[21] * 1e-2,
        "image_snr": image_snr if soln_status_bits[4] else None,
        "new_automated_target": bool(at_slew_flags[0]),
        "sufficient_merit": bool(at_slew_flags[1]),
    }


def parse(bin):
    bin[11:15]  # Spare. According to Docs: '16 bytes for the future'
    bin[22:38]  # Spare. According to Docs: '64 bytes for the future'
    bin[19]  # Unused. Flags are either internal or equivalent to bin[16]

    return {**parse_fom(bin)}
