import numpy as np

from ... import utils


def parse_swift_xrt_sper(bin):
    misc_bits = np.unpackbits(bin[19:20].view(np.uint8), bitorder='little')

    return {
        # Fixed string constant identifying the mission. Listed explicitly as a schema field
        # in swift.xrt.sper with the value "Swift".
        "mission": "SWIFT",

        # Fixed string constant identifying the instrument. Listed explicitly as a schema field
        # in swift.xrt.sper with the value "XRT".
        "instrument": "XRT",

        # bin[4] = trig_obs_num: lower 24 bits = Trigger number, upper 8 bits = Observation number.
        # Assigned by the on-board BAT flight software to uniquely identify each trigger.
        "id": str(bin[4]),

        # bin[5] = burst_tjd: Truncated Julian Day of the Swift-BAT transient trigger.
        # bin[6] = burst_sod: UT seconds-of-day of the same trigger time, in centi-seconds
        #   (i.e. fl.pt. seconds * 100, then integerized).
        # Combined and converted to an ISO 8601 datetime string.
        "observation_start": utils.datetime_to_iso8601(bin[5], bin[6]),

        # bin[7] = point_ra: RA of the XRT pointing direction (J2000 epoch).
        # Stored as an integer in units of 0.0001-deg (fl.pt. degrees * 10000).
        # Divide by 10000 to recover degrees.
        "ra_pointing": bin[7] * 1e-4,

        # bin[8] = point_dec: Dec of the XRT pointing direction (J2000 epoch).
        # Same encoding as point_ra. Divide by 10000 to recover degrees.
        "dec_pointing": bin[8] * 1e-4,

        # bin[9] = expo_time: total exposure time of the SPER integration.
        # Stored in units of 0.001-sec (fl.pt. seconds * 1000, then integerized).
        # Multiply by 1e-3 to recover seconds.
        "observation_livetime": bin[9] * 1e-3,

        # bin[10] = stop_date: Truncated Julian Day of the end of the SPER integration.
        # bin[11] = stop_time: UT seconds-of-day of the same stop time, in centi-seconds
        #   (i.e. fl.pt. seconds * 100, then integerized).
        # Combined and converted to an ISO 8601 datetime string.
        "observation_stop": utils.datetime_to_iso8601(bin[10], bin[11]),

        # bin[12] = num_pkt (type=87) / seq_num (type=88):
        #   type=87 (SWIFT_XRT_SPER): number of telemetry packets used in this integration.
        #   type=88 (SWIFT_XRT_SPER_PROC): serial number of this message (1–3), as the
        #     ground-processed SPER notice is split into a sequence of up to 3 messages.
        "num_packets": bin[12],

        # bin[20] = num_evt: total number of XRT events (photons) collected during the
        # SPER integration period.
        "num_events": bin[20],

        # misc bit 29 (watchdog_timeout): set if this XRT_SPER notice was forced out
        # early via the watchdog timeout mechanism rather than completing normally.
        "watchdog_timeout": bool(misc_bits[29]),

        # bin[22-38] = url: filename portion of the URL pointing to the SPER FITS file.
        # The full URL is formed by prepending "http://gcn.gsfc.nasa.gov/gcn/notices_s/".
        # Spans 17 longwords (68 bytes), up to 67 ASCII characters, always null-terminated.
        # In the swift.xrt.sper schema this field will contain the base64-encoded
        # FITS file rather than a URL string.
        "sper_fits_file": f"http://gcn.gsfc.nasa.gov/gcn/notices_s/{''.join([i.decode('utf-8') for i in bin[22:39].view('c')])}",

        # --- Fields present in the raw XRT_SPER packet but NOT in the swift.xrt.sper schema ---

        # misc bit 10 (st_loss_lock): set if the StarTracker was NOT locked during this
        # SPER integration, meaning the pointing solution may be less reliable.
        # Note: this bit was added to the SPER notice on 26 Apr 2016.
        # "star_tracker_not_locked": bool(misc_bits[10]),

        # misc bit 11 (pos_out_of_range): set if one or more of the RA/Dec/Roll/Theta/Phi
        # values were outside the valid range (e.g. RA > 360 deg), indicating a potentially
        # invalid pointing solution.
        # "pos_out_of_range": bool(misc_bits[11]),

        # misc bit 22 (uploaded_too): set if this notice was generated as a result of an
        # uploaded Target-of-Opportunity (TOO) sequence — i.e. Swift was commanded to
        # observe this location and this notice is a direct result of that observation.
        # "too_sequence_uploaded": bool(misc_bits[22]),

        # misc bit 30 (ground_generated): set if this notice was ground-generated (type=88);
        # always 0 for the raw flight form of this notice (type=87).
        # "ground_generated": bool(misc_bits[30]),

        # misc bit 31 (crc_error): set if a CRC error was detected in one or more of the
        # telemetry packets used to construct this notice.
        # "crc_error": bool(misc_bits[31]),
    }

def parse(bin):
    bin[13:19]  # Spare. According to Docs: "24 bytes for the future".
    bin[21]  # Spare. According to Docs: "4 bytes for the future".
    return {**parse_swift_xrt_sper(bin)}
