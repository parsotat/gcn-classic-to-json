import numpy as np

from ... import utils

termination_condition_dict = {
    0: "Normal",
    1: "Terminated by time",
    2: "Terminated by snapshot",
    3: "Terminated by entering SAA",
}


def parse(bin):
    bin[12:19]  # Spare. According to Docs: "28 bytes for the future".

    misc_bits = np.unpackbits(bin[19:20].view(np.uint8), bitorder='little')

    return {
        # Fixed string constant identifying the mission. Listed explicitly as a schema field
        # in swift.xrt.lightcurve with the value "Swift".
        "mission": "SWIFT",

        # Fixed string constant identifying the instrument. Listed explicitly as a schema field
        # in swift.xrt.lightcurve with the value "XRT".
        "instrument": "XRT",

        # bin[4] = trig_obs_num: lower 24 bits = Trigger number, upper 8 bits = Observation number.
        # Assigned by the on-board BAT flight software to uniquely identify each trigger.
        "id": [bin[4]],

        # bin[5] = start_tjd: Truncated Julian Day of the start of the first CCD integration
        #   in the lightcurve accumulation.
        # bin[6] = start_sod: UT seconds-of-day of the same start time, in centi-seconds
        #   (i.e. fl.pt. seconds * 100, then integerized).
        # Combined and converted to an ISO 8601 datetime string.
        "observation_start": utils.datetime_to_iso8601(bin[5], bin[6]),

        # bin[10] = SpecStop_tjd: Truncated Julian Day of the last CCD integration
        #   in the lightcurve accumulation.
        # bin[11] = SpecStop_sod: UT seconds-of-day of the same stop time, in centi-seconds
        #   (i.e. fl.pt. seconds * 100, then integerized).
        # Combined and converted to an ISO 8601 datetime string.
        "observation_stop": utils.datetime_to_iso8601(bin[10], bin[11]),

        # bin[9] = live_time: total exposure time duration of the lightcurve integration.
        # Stored in centi-seconds (fl.pt. seconds * 100, then integerized).
        # Divide by 100 to recover seconds.
        "observation_livetime": bin[9] * 1e-2,

        # bin[7] = bore_ra: RA of the XRT boresight (center of the XRT FOV), J2000 epoch.
        # Stored as an integer in units of 0.0001-deg (fl.pt. degrees * 10000).
        # Divide by 10000 to recover degrees.
        "pointing_ra": bin[7] * 1e-4,

        # bin[8] = bore_dec: Dec of the XRT boresight (center of the XRT FOV), J2000 epoch.
        # Same encoding as bore_ra. Divide by 10000 to recover degrees.
        "pointing_dec": bin[8] * 1e-4,

        # bin[20] = n_bins: number of valid bins collected in the lightcurve (range: 0–100).
        "collected_bins": bin[20],

        # bin[21] = term_cond: integer code describing why lightcurve collection stopped.
        # Values are:
        #   0 = Normal (100 bins collected)
        #   1 = Terminated by time (1–99 bins)
        #   2 = Terminated by snapshot (1–99 bins)
        #   3 = Terminated by entering SAA (1–99 bins)
        # Mapped to a human-readable string via termination_condition_dict.
        "termination_condition": termination_condition_dict[bin[21]],

        # bin[22-38] = url: filename portion of the URL pointing to the lightcurve FITS file.
        # The full URL is formed by prepending "http://gcn.gsfc.nasa.gov/gcn/notices_s/".
        # Spans 17 longwords (68 bytes), up to 67 ASCII characters, always null-terminated.
        # In the swift.xrt.lightcurve schema this field is named 'lightcurve_fits_file' and
        # will contain the base64-encoded FITS file rather than a URL string.
        "lightcurve_fits_file": f"http://gcn.gsfc.nasa.gov/gcn/notices_s/{''.join([i.decode('utf-8') for i in bin[22:39].view('c')])}",

        # --- Fields present in the raw XRT_LC packet but NOT in the swift.xrt.lightcurve schema ---

        # misc bit 11 (pos_out_of_range): set if one or more of the RA/Dec/Roll/Theta/Phi
        # values were outside the valid range (e.g. RA > 360 deg), indicating a potentially
        # invalid pointing solution.
        # "pos_out_of_range": bool(misc_bits[11]),

        # misc bit 13 (near_brt_star): set if the XRT boresight position is near (< 0.3 deg)
        # a bright star (magnitude < 6.5), which may affect the lightcurve data quality.
        # "bright_star_nearby": bool(misc_bits[13]),

        # misc bit 20 (was_subthresh): set if this event was originally a SubThreshold BAT
        # trigger that has since been promoted to a real XRT_LC notice.
        # "was_subthresh": bool(misc_bits[20]),

        # misc bit 22 (uploaded_too): set if this notice was generated as a result of an
        # uploaded Target-of-Opportunity (TOO) sequence — i.e. Swift was commanded to
        # observe this location and this notice is a direct result of that observation.
        # "too_sequence_uploaded": bool(misc_bits[22]),
    }