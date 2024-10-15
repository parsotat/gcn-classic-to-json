import numpy as np

from ... import utils


def parse_pointdir(bin):
    id_record_number_bits = np.flip(np.unpackbits(bin[4:5].view(dtype="u1")))
    record_number = np.packbits(np.flip(id_record_number_bits[24:]))
    id = id_record_number_bits[:24].dot(2 ** np.arange(24))

    lat, lon = bin[16:17].view(dtype=">i2")

    soln_status_bits = np.flip(np.unpackbits(bin[19:20].view(dtype="u1")))
    return {
        "mission": "SWIFT",
        "id": [id],
        "record_number": record_number,
        "trigger_time": utils.datetime_to_iso8601(bin[5], bin[6]),
        "ra_pointing": bin[7] * 1e-4,
        "dec_pointing": bin[8] * 1e-4,
        "roll": bin[9] * 1e-4,
        "latitude": lat * 1e-2,
        "longitude": lon * 1e-2,
        "bright_star_nearby": bool(soln_status_bits[13]),
    }


def parse(bin):
    bin[10:16]  # Spare. According to Docs: '24 bytes for the future'
    bin[17:19]  # Spare. According to Docs: '8 bytes for the future'
    bin[20:22]  # Spare. According to Docs: '8 bytes for the future'
    bin[22:39]  # Unused. According to Docs: 'tgtname; might get added late'

    return {**parse_pointdir(bin)}
