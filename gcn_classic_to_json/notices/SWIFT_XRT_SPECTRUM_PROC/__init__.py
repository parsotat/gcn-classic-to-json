import numpy as np

from ... import utils
from ..SWIFT_XRT_LC import termination_condition_dict
from ..SWIFT_XRT_IMAGE import mode_dict

termination_conditions_dict = {
    **termination_condition_dict,
    4: "Spectrum generated at the LRPD-to-WT transition",
    5: "Spectrum generated at the WT-to-LRorPC transition",
}

def parse(bin):
    bin[15:19]  # Spare. According to Docs: "16 bytes for the future"
    bin[20]  # Spare. According to Docs: "4 bytes for the future"

    misc_bits = np.unpackbits(bin[19:20].view(np.uint8), bitorder='little')

    return {
        **parse_swift_xrt_spec(bin),
        "fits_file_does_not_exist": bool(misc_bits[24]),
    }


def parse_swift_xrt_spec(bin):
    misc_bits = np.unpackbits(bin[19:20].view(np.uint8), bitorder='little')

    #extract the lower 4 bits, can also do bin[21] & 0x7
    termination_condition = np.packbits(np.unpackbits(bin[21:22].view(dtype="u1"), bitorder="little")[:4], bitorder="little")[0]

    return {
        # Fixed string constant identifying the mission. Listed explicitly as a schema field
        # in swift.xrt.spectrum with the value "Swift".
        "mission": "SWIFT",

        # Fixed string constant identifying the instrument. Listed explicitly as a schema field
        # in swift.xrt.spectrum with the value "XRT".
        "instrument": "XRT",

        # bin[4] = trig_obs_num: lower 24 bits = Trigger number, upper 8 bits = Observation number.
        # Assigned by the on-board BAT flight software to uniquely identify each trigger.
        "id": [bin[4]],

        # bin[5] = SpecStart_tjd: Truncated Julian Day of the start of the first CCD integration
        #   in the spectrum accumulation.
        # bin[6] = SpecStart_sod: UT seconds-of-day of the same start time, in centi-seconds
        #   (i.e. fl.pt. seconds * 100, then integerized).
        # Combined and converted to an ISO 8601 datetime string.
        "observation_start": utils.datetime_to_iso8601(bin[5], bin[6]),

        # bin[7] = bore_ra: RA of the XRT boresight (center of the XRT FOV), J2000 epoch.
        # Stored as an integer in units of 0.0001-deg (fl.pt. degrees * 10000).
        # Divide by 10000 to recover degrees.
        "ra_pointing": bin[7] * 1e-4,

        # bin[8] = bore_dec: Dec of the XRT boresight (center of the XRT FOV), J2000 epoch.
        # Same encoding as bore_ra. Divide by 10000 to recover degrees.
        "dec_pointing": bin[8] * 1e-4,

        # bin[9] = live_time: total exposure time duration of the spectrum integration.
        # Stored in centi-seconds (fl.pt. seconds * 100, then integerized).
        # Divide by 100 to recover seconds.
        "observation_livetime": bin[9] * 1e-2,

        # bin[10] = SpecStop_tjd: Truncated Julian Day of the last CCD integration
        #   in the spectrum accumulation.
        # bin[11] = SpecStop_sod: UT seconds-of-day of the same stop time, in centi-seconds
        #   (i.e. fl.pt. seconds * 100, then integerized).
        # Combined and converted to an ISO 8601 datetime string.
        "observation_stop": utils.datetime_to_iso8601(bin[10], bin[11]),

        # bin[12] = mode: CCD readout mode identifier. Integer values map as follows:
        #   1 = Null, 2 = Short image, 3 = Long image, 4 = Piled-up Photodiode,
        #   5 = Low Rate Photodiode, 6 = Windowed Timing, 7 = Photo-counting,
        #   8 = Raw data, 9 = Bias map, 10 = Stop.
        # Mapped to a human-readable string via mode_dict.
        # there are only 2 types spectra given by the readout mode: LRPD or WT
        "ccd_readout_mode": mode_dict[bin[12]],

        # bin[13] = waveform: CCD waveform ID. Values are either 50 or 60.
        "ccd_waveform_id": bin[13],

        # bin[14] = bias: bias value of the last LRPD (Low Rate Photodiode) frame, in ADU.
        # Only meaningful when mode == 5 (Low Rate Photodiode); should be ignored for
        # Windowed Timing (WT) spectra. Set to None for all non-LRPD modes.
        "bias": bin[14] if bin[12] == 5 else None,

        # bin[21] = term_code: integer code describing why spectrum accumulation stopped.
        # Values are:
        #   0 = Normal
        #   1 = Terminated by time
        #   2 = Terminated by snapshot
        #   3 = Terminated by entering SAA
        #   4 = Spectrum generated at the LRPD-to-WT transition
        #   5 = Spectrum generated at the WT-to-LRorPC transition
        # Mapped to a human-readable string via termination_conditions_dict.
        "termination_condition": termination_conditions_dict[termination_condition],

        # misc bit 29 (watchdog_timeout): set if this XRT_SPECTRUM notice was forced out
        # early via the watchdog timeout mechanism rather than completing normally.
        "watchdog_timeout": bool(misc_bits[29]),

        # bin[22-38] = url: filename portion of the URL pointing to the spectrum FITS file.
        # The full URL is formed by prepending "http://gcn.gsfc.nasa.gov/gcn/notices_s/".
        # Spans 17 longwords (68 bytes), up to 67 ASCII characters, always null-terminated.
        # In the swift.xrt.spectrum schema this field will contain the base64-encoded
        # FITS file rather than a URL string.
        "spectrum_fits_file": f"http://gcn.gsfc.nasa.gov/gcn/notices_s/{''.join([i.decode('utf-8') for i in bin[22:39].view('c')])}",

        # --- Fields present in the raw XRT_SPEC packet but NOT in the swift.xrt.spectrum schema ---

        # misc bit 11 (pos_out_of_range): set if one or more of the RA/Dec/Roll/Theta/Phi
        # values were outside the valid range (e.g. RA > 360 deg), indicating a potentially
        # invalid pointing solution.
        # "pos_out_of_range": bool(misc_bits[11]),

        # misc bit 13 (near_brt_star): set if the XRT boresight position is near (< 0.3 deg)
        # a bright star (magnitude < 6.5), which may affect the spectrum data quality.
        # "bright_star_nearby": bool(misc_bits[13]),

        # misc bit 20 (was_subthresh): set if this event was originally a SubThreshold BAT
        # trigger that has since been promoted to a real XRT_SPEC notice.
        # "was_subthresh": bool(misc_bits[20]),

        # misc bit 21 (st_loss_lock): set if this is an image trigger AND it occurred during
        # a StarTracker Loss-of-Lock event, meaning the pointing solution may be less reliable.
        # "star_tracker_loss_of_lock": bool(misc_bits[21]),

        # misc bit 22 (uploaded_too): set if this notice was generated as a result of an
        # uploaded Target-of-Opportunity (TOO) sequence — i.e. Swift was commanded to
        # observe this location and this notice is a direct result of that observation.
        # "too_sequence_uploaded": bool(misc_bits[22]),

        # misc bit 25 (pkt3_missing): set if this notice was generated with the 3rd of 3
        # telemetry packets missing, meaning the spectrum data may be incomplete.
        # "packet_3_missing": bool(misc_bits[25]),

        # misc bit 26 (pkt2_missing): set if this notice was generated with the 2nd of 3
        # telemetry packets missing, meaning the spectrum data may be incomplete.
        # "packet_2_missing": bool(misc_bits[26]),

        # misc bit 27 (pkt1_missing): set if this notice was generated with the 1st of 3
        # telemetry packets missing, meaning the spectrum data may be incomplete.
        # "packet_1_missing": bool(misc_bits[27]),

        # misc bit 30 (ground_generated): set if this notice was ground-generated (type=77);
        # always 0 for the raw flight form of this notice (type=68).
        # "ground_generated": bool(misc_bits[30]),

        # misc bit 31 (crc_error): set if a CRC error was detected in one or more of the
        # telemetry packets used to construct this notice.
        # "crc_error": bool(misc_bits[31]),
    }

