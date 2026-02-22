import numpy as np

from ... import utils


def parse_swift_xrt_thresh(bin):
    return {
        # Fixed string constant identifying the mission. Listed explicitly as a schema field
        # in swift.xrt.thresholded_pixels with the value "Swift".
        "mission": "SWIFT",

        # Fixed string constant identifying the instrument. Listed explicitly as a schema field
        # in swift.xrt.thresholded_pixels with the value "XRT".
        "instrument": "XRT",

        # bin[4] = trig_obs_num: lower 24 bits = Trigger number, upper 8 bits = Observation number.
        # Assigned by the on-board BAT flight software to uniquely identify each trigger.
        "id": [bin[4]],

        # bin[5] = Start_tjd: Truncated Julian Day of the start of the first CCD integration
        #   in the thresholded pixels accumulation.
        # bin[6] = Start_sod: UT seconds-of-day of the same start time, in centi-seconds
        #   (i.e. fl.pt. seconds * 100, then integerized).
        # Combined and converted to an ISO 8601 datetime string.
        "observation_start": utils.datetime_to_iso8601(bin[5], bin[6]),

        # bin[7] = bore_ra: RA of the XRT boresight (center of the XRT FOV), J2000 epoch.
        # Stored as an integer in units of 0.0001-deg (fl.pt. degrees * 10000).
        # Divide by 10000 to recover degrees.
        "pointing_ra": bin[7] * 1e-4,

        # bin[8] = bore_dec: Dec of the XRT boresight (center of the XRT FOV), J2000 epoch.
        # Same encoding as bore_ra. Divide by 10000 to recover degrees.
        "pointing_dec": bin[8] * 1e-4,

        # bin[9] = live_time: total exposure time duration of the thresholded pixels
        # accumulation. Stored in units of 0.001-sec (fl.pt. seconds * 1000, then
        # integerized). Multiply by 1e-3 to recover seconds.
        "observation_livetime": bin[9] * 1e-3,

        # bin[10] = Stop_tjd: Truncated Julian Day of the last CCD integration in the
        #   thresholded pixels accumulation.
        # bin[11] = Stop_sod: UT seconds-of-day of the same stop time, in centi-seconds
        #   (i.e. fl.pt. seconds * 100, then integerized).
        # Combined and converted to an ISO 8601 datetime string.
        "observation_stop": utils.datetime_to_iso8601(bin[10], bin[11]),

        # misc bit 29 (watchdog_timeout): set if this XRT_THRESHPIX notice was forced out
        # early via the watchdog timeout mechanism rather than completing normally.
        "watchdog_timeout": bool(misc_bits[29]),

        # bin[22-38] = url: filename portion of the URL pointing to the thresholded pixels
        # FITS file. The full URL is formed by prepending
        # "http://gcn.gsfc.nasa.gov/gcn/notices_s/".
        # Spans 17 longwords (68 bytes), up to 67 ASCII characters, always null-terminated.
        # In the swift.xrt.thresholded_pixels schema this field will contain the
        # base64-encoded FITS file rather than a URL string.
        "thresholded_pixels_fits_file": f"http://gcn.gsfc.nasa.gov/gcn/notices_s/{''.join([i.decode('utf-8') for i in bin[22:39].view('c')])}",

        # --- Fields present in the raw XRT_THRESHPIX packet but NOT in the
        # swift.xrt.thresholded_pixels schema ---

        # misc bit 11 (pos_out_of_range): set if one or more of the RA/Dec/Roll/Theta/Phi
        # values were outside the valid range (e.g. RA > 360 deg), indicating a potentially
        # invalid pointing solution.
        # "pos_out_of_range": bool(misc_bits[11]),

        # misc bit 20 (was_subthresh): set if this event was originally a SubThreshold BAT
        # trigger that has since been promoted to a real XRT_THRESHPIX notice.
        # "was_subthresh": bool(misc_bits[20]),

        # misc bit 21 (st_loss_lock): set if this is an image trigger AND it occurred during
        # a StarTracker Loss-of-Lock event, meaning the pointing solution may be less reliable.
        # "star_tracker_loss_of_lock": bool(misc_bits[21]),

        # misc bit 22 (uploaded_too): set if this notice was generated as a result of an
        # uploaded Target-of-Opportunity (TOO) sequence — i.e. Swift was commanded to
        # observe this location and this notice is a direct result of that observation.
        # "too_sequence_uploaded": bool(misc_bits[22]),

        # misc bit 30 (ground_generated): set if this notice was ground-generated (type=86);
        # always 0 for the raw flight form of this notice (type=85).
        # "ground_generated": bool(misc_bits[30]),

        # misc bit 31 (crc_error): set if a CRC error was detected in one or more of the
        # telemetry packets used to construct this notice.
        # "crc_error": bool(misc_bits[31]),
    }


def parse(bin):
    bin[13:19]  # Spare. According to Docs: "24 bytes for the future".
    bin[20:22]  # Spare. According to Docs: "8 bytes for the future".
    bin[12]  # Intentionally Omitted. seq_num but unused

    misc_bits = np.unpackbits(bin[19:20].view(np.uint8), bitorder='little')

    return {
        **parse_swift_xrt_thresh(bin),
        #"pos_out_of_range": bool(misc_bits[11]),
        #"was_subthresh": bool(misc_bits[20]),
        #"too_sequence_uploaded": bool(misc_bits[22]),
        #"watchdog_timeout": bool(misc_bits[29]),
    }
