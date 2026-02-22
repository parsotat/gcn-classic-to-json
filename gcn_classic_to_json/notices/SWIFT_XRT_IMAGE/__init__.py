import numpy as np

from ... import utils

mode_dict = {
    1: "Null",
    2: "Short Image",
    3: "Long Image",
    4: "Piled-up Photodiode",
    5: "Low Rate Photodiode",
    6: "Windowed Timing",
    7: "Photo-counting",
    8: "Raw Data",
    9: "Bias Map",
    10: "Stop",
}

def parse(bin):
    bin[10]  # Spare. 4 bytes for the future.

    return {**parse_swift_xrt_image(bin)}


def parse_swift_xrt_image(bin):
    gain_wave_mode_bits = np.unpackbits(bin[17:18].view(dtype="u1"), bitorder='little')
    waveform_id = np.packbits(gain_wave_mode_bits[:8], bitorder='little')
    mode = np.packbits(gain_wave_mode_bits[8:16], bitorder='little')
    gain = np.packbits(gain_wave_mode_bits[16:24], bitorder='little')

    misc_bits =  np.unpackbits(bin[19:20].view(np.uint8), bitorder='little')

    return {
        # Fixed string constant identifying the mission. Listed explicitly as a schema field
        # in swift.xrt.image with the value "Swift".
        "mission": "SWIFT",

        # Fixed string constant identifying the instrument. Listed explicitly as a schema field
        # in swift.xrt.image with the value "XRT".
        "instrument": "XRT",

        # bin[4] = trig_obs_num: lower 24 bits = Trigger number, upper 8 bits = Observation number.
        # Assigned by the on-board BAT flight software to uniquely identify each trigger.
        "id": [bin[4]],

        # bin[5] = ImgStart_tjd: Truncated Julian Day of the start of the CCD image integration.
        # bin[6] = ImgStart_sod: UT seconds-of-day of the same start time, in centi-seconds
        #   (i.e. fl.pt. seconds * 100, then integerized).
        # Combined and converted to an ISO 8601 datetime string.
        "observation_start": utils.datetime_to_iso8601(bin[5], bin[6]),

        # bin[7] = burst_ra: RA of the centroid of the source found in the XRT image
        # (J2000 epoch). Stored as an integer in units of 0.0001-deg (fl.pt. degrees * 10000).
        # Divide by 10000 to recover degrees.
        "ra": bin[7] * 1e-4,

        # bin[8] = burst_dec: Dec of the centroid of the source found in the XRT image
        # (J2000 epoch). Same encoding as burst_ra. Divide by 10000 to recover degrees.
        "dec": bin[8] * 1e-4,

        # bin[9] = n_bright_pix: number of pixels above the detection threshold in the
        # XRT image. The detection significance ("det_signif") is the square root of this value.
        # Note: saturation effects in pixel intensities can cause this to underestimate
        # significance for bright sources.
        "bright_pixels": bin[9],

        # bin[11] = centroid_std_dev: standard deviation of the centroid position.
        # Stored in units of 0.0001-deg (fl.pt. value * 10000, then integerized).
        # Divide by 10000 to recover the value in degrees.
        "centroid_std_dev": bin[11] * 1e-4,

        # bin[12] = cent_x: x-coordinate of the source centroid position in the XRT image.
        # Stored in centi-pixels (fl.pt. pixels * 100). Divide by 100 to recover pixels.
        # bin[13] = cent_y: y-coordinate of the source centroid position in the XRT image.
        # Same encoding as cent_x.
        # Schema field: centroid_position [x, y].
        "centroid_position": [bin[12] * 1e-2, bin[13] * 1e-2],

        # bin[14] = iraw_x: x-coordinate of the center of the 51x51 pixel postage stamp image
        # in raw CCD coordinates. Stored in centi-pixels; divide by 100 to recover pixels.
        # bin[15] = iraw_y: y-coordinate of the postage stamp center. Same encoding as iraw_x.
        # Schema field: centroid_ccd_position [x, y].
        "centroid_ccd_position": [bin[14] * 1e-2, bin[15] * 1e-2],

        # bin[16] = roll: roll angle of the spacecraft at the time of the image.
        # Stored in units of 0.0001-deg (fl.pt. degrees * 10000, range -180 to +180).
        # Divide by 10000 to recover degrees.
        # Schema field: pointing_roll.
        "pointing_roll": bin[16] * 1e-4,

        # bin[17] = gain/mod/wav: packed 32-bit word containing amplifier gain, CCD readout
        # mode, and waveform ID. Decoded externally into separate variables.
        # gain[0]: amplifier gain identifier. Values: 1, 2, 4, 8, 16.
        # Schema field: amplifier_gain.
        "amplifier_gain": gain[0],

        # bin[17] = gain/mod/wav (see above).
        # mode[0]: CCD readout mode identifier. Values:
        #   1 = Null, 2 = Short image, 3 = Long image, 4 = Piled-up Photodiode,
        #   5 = Low Rate Photodiode, 6 = Windowed Timing, 7 = Photo-counting,
        #   8 = Raw data, 9 = Bias map, 10 = Stop.
        # Mapped to a human-readable string via mode_dict.
        # Schema field: ccd_readout_mode.
        "ccd_readout_mode": mode_dict[mode[0]],

        # bin[17] = gain/mod/wav (see above).
        # waveform_id[0]: CCD waveform ID. Values are either 50 or 60.
        # Schema field: ccd_waveform_id.
        "ccd_waveform_id": waveform_id[0],

        # bin[18] = expo_time: CCD integration (exposure) time for this image.
        # Stored in centi-seconds (fl.pt. seconds * 100, then integerized).
        # Divide by 100 to recover seconds.
        # Schema field: observation_livetime.
        "observation_livetime": bin[18] * 1e-2,

        # misc bit 29 (watchdog_timeout): set if this XRT_IMAGE notice was forced out
        # early via the watchdog timeout mechanism rather than completing normally.
        "watchdog_timeout": bool(misc_bits[29]),

        # bin[20] = grb_in_xrt_y: y-coordinate (row) of the GRB X-ray afterglow position
        #   in XRT CCD coordinates. Stored in centi-pixels; divide by 100 to recover pixels.
        #   (The centi-pixel encoding is overkill as the intrinsic values are integer pixels.)
        # bin[21] = grb_in_xrt_z: z-coordinate (column) of the same afterglow position.
        #   Same encoding as grb_in_xrt_y.
        # Schema field: grb_xrt_coordinates [y, z].
        "grb_xrt_coordinates": [bin[20] * 1e-2, bin[21] * 1e-2],

        # bin[22-38] = url: filename portion of the URL pointing to the image FITS file.
        # The full URL is formed by prepending "http://gcn.gsfc.nasa.gov/gcn/notices_s/".
        # Spans 17 longwords (68 bytes), up to 67 ASCII characters, always null-terminated.
        # In the swift.xrt.image schema this field will contain the base64-encoded
        # FITS file rather than a URL string.
        "image_fits_file": f"http://gcn.gsfc.nasa.gov/gcn/notices_s/{''.join([i.decode('utf-8') for i in bin[22:39].view('c')])}",

        # --- Fields present in the raw XRT_IMAGE packet but NOT in the swift.xrt.image schema ---

        # misc bit 10 (not_real_peak): set if the detected peak in the XRT image is flagged
        # as not being a real astrophysical source peak (e.g. readout artifact or hot pixel).
        # "not_real_astrophysical_peak": bool(misc_bits[10]),

        # misc bit 11 (pos_out_of_range): set if one or more of the RA/Dec/Roll/Theta/Phi
        # values were outside the valid range (e.g. RA > 360 deg), indicating a potentially
        # invalid pointing solution.
        # "pos_out_of_range": bool(misc_bits[11]),

        # misc bit 13 (near_brt_star): set if the XRT boresight position is near (< 0.3 deg)
        # a bright star (magnitude < 6.5), which may affect the image data quality.
        # "bright_star_nearby": bool(misc_bits[13]),

        # misc bit 20 (was_subthresh): set if this event was originally a SubThreshold BAT
        # trigger that has since been promoted to a real XRT_IMAGE notice.
        # "was_subthresh": bool(misc_bits[20]),

        # misc bit 21 (st_loss_lock): set if this is an image trigger AND it occurred during
        # a StarTracker Loss-of-Lock event, meaning the pointing solution may be less reliable.
        # "star_tracker_loss_of_lock": bool(misc_bits[21]),

        # misc bit 22 (uploaded_too): set if this notice was generated as a result of an
        # uploaded Target-of-Opportunity (TOO) sequence — i.e. Swift was commanded to
        # observe this location and this notice is a direct result of that observation.
        # "too_sequence_uploaded": bool(misc_bits[22]),

        # misc bit 25 (pkt3_missing): set if this notice was generated with the 3rd of 3
        # telemetry packets missing, meaning the image data may be incomplete.
        # "packet_3_missing": bool(misc_bits[25]),

        # misc bit 26 (pkt2_missing): set if this notice was generated with the 2nd of 3
        # telemetry packets missing, meaning the image data may be incomplete.
        # "packet_2_missing": bool(misc_bits[26]),

        # misc bit 27 (pkt1_missing): set if this notice was generated with the 1st of 3
        # telemetry packets missing, meaning the image data may be incomplete.
        # "packet_1_missing": bool(misc_bits[27]),

        # misc bit 30 (ground_generated): set if this notice was ground-generated (type=78);
        # always 0 for the raw flight form of this notice (type=69).
        # "ground_generated": bool(misc_bits[30]),

        # misc bit 31 (crc_error): set if a CRC error was detected in one or more of the
        # telemetry packets used to construct this notice.
        # "crc_error": bool(misc_bits[31]),
    }

