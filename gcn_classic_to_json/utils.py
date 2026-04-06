import numpy as np
from astropy.time import Time
import logging

log = logging.getLogger(__name__)

def datetime_to_iso8601(date, time):
    """Converts time to ISO 8601 format.

    The function converts input into the ISO 8601 format from
    Truncated Julian Date by first converting it to Julian Date.

    Parameters
    ----------
    date : int
        Date must be in Truncated Julian Date format.
    time : int
        Time of day must in Seconds of Day format.

    Returns
    -------
    string
        returns datetime in ISO8601 format.

    Notes
    -----
    The zero point for Truncated Julian Day is given in https://en.wikipedia.org/wiki/Julian_day.
    """
    TJD0 = (2440000, 0.5)
    return Time(date + TJD0[0], time / 8640000 + TJD0[1], format="jd").isot + "Z"


def binary_to_string(binary):
    """Converts a binary array to a ASCII-string.

    The function converts `binary` into a C-style string,
    flips the position of every 4 bytes, strips excess null characters
    and then converts the result into ASCII characters.

    Parameters
    ----------
    binary : array-like
        A array for binary values encoded as 4-byte integers.

    Returns
    -------
    string:
        returns the corresponding ASCII string.

    Notes:
    ------
    The strings in the binary packets look like they were accidentally byte-swapped.
    """
    return (
        np.fliplr(binary.view("c").reshape(-1, 4))
        .ravel()
        .tobytes()
        .strip(b"\0")
        .decode()
    )

def breakdown_obsnum(binary_value):
    """
    This function takes the obsnum part of a binary packet and converts it into the target ID and the segment number
    """
    target_id = None
    segment = None

    try:
        target_id=(binary_value & 0xFFFFFF).view(dtype="u4")
        if len(target_id)==1:
            target_id=target_id[0]
        else:
            logging.debug(f'There were more than 1 target IDs obtained from the binary packet obsnum')
    except Exception as e:
        logging.debug(f'{e}')
        logging.debug(f'Error obtaining the target ID from the binary packet obsnum')

    try:
        segment=(binary_value >> 24 & 0xFF).view(dtype="u4")
        if len(segment)==1:
            segment=segment[0]
        else:
            logging.debug(f'There were more than 1 segments obtained from the binary packet obsnum')
    except Exception as e:
        logging.debug(f'{e}')
        logging.debug(f'Error obtaining the segment number from the binary packet obsnum')


    return target_id, segment

def get_timenow():
    return f"{Time.now().isot}Z"