"""
This is the documentation for this packet from GCN classic for ease of reference:

------Insert Documentation Here-------
"""

from astropy.time import Time

#set constants for ease of use

# Zero point for Truncated Julian Day according to
# https://en.wikipedia.org/wiki/Julian_day.
TJD0 = (2440000, 0.5)

mission="Swift"
instrument="UVOT" #insert instrument here for appropriate notice type


def parse(bin):
    packet_dict=dict(
        mission=mission,
        instrument=instrument,
        trigger_time=Time(
            bin[5] + TJD0[0],
            bin[6] / 8640000 + TJD0[1],
            format="jd",
        ).isot,
        ra=1e-4 * bin[7],
        dec=1e-4 * bin[8],
        ra_dec_error=1e-4 * bin[11],
    )
    return packet_dict
