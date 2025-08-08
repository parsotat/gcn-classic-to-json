import numpy as np

from ... import utils
from ..SWIFT_UVOT_FCHART_PROC import filters


pixel_binning_values = {0: "1x1", 1: "2x2", 2: "4x4", 6: "64x64"}

grb_position_sources = ["Window Position", "XRT Position"]


def parse_uvot_image(bin):
    x_pos, y_pos = bin[16:17].view(dtype="<i2")

    misc_bits = np.unpackbits(bin[19:20].view(np.uint8), bitorder='little')

    pixel_binning = np.packbits(np.pad(np.flip(misc_bits[:5]), (3, 0)))

    return {
        "mission": "SWIFT",
        "instrument": "UVOT",
        "id": [bin[4]],
        "img_start_time": utils.datetime_to_iso8601(bin[5], bin[6]),
        "ra_pointing": bin[7] * 1e-4,
        "dec_pointing": bin[8] * 1e-4,
        "roll": bin[9] * 1e-4,
        "filter": [filters[bin[10]]],
        "exposure_ID": bin[11],
        "image_offset": [bin[12], bin[13]],
        "image_size": [bin[14], bin[15]],
        "grb_position": [x_pos, y_pos],
        "n_frames": bin[17],
        "fits_file_url": f"http://gcn.gsfc.nasa.gov/gcn/notices_s/{''.join([i.decode('utf-8') for i in  bin[22:39].view('c')])}",
        "pixel_binning": pixel_binning_values[pixel_binning[0]],
        "bright_star_nearby": bool(misc_bits[13]),
        "was_subthresh": bool(misc_bits[20]),
        "grb_position_source": grb_position_sources[misc_bits[28]],
    }


def parse(bin):
    bin[18]  # Unused. According to Docs: 'useless by the time it reaches GCN distribution'
    bin[20:22]  # Spare. According to Docs: '8 bytes for the future'

    return {**parse_uvot_image(bin)}
