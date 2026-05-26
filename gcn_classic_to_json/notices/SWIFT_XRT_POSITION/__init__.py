import numpy as np

from ... import utils


def parse(bin):
    bin[10]  # Spare. According to Docs: "4 bytes for the future".
    bin[22:39]  # Spare. According to Docs: "68 bytes for the future".
    bin[11]  # Intentionally Omitted. Same as bin[16] but less precise.

    amp_wave_bits = np.unpackbits(bin[17:18].view(dtype="u1"), bitorder='little')
    wave = np.packbits(amp_wave_bits[:8], bitorder='little')
    amp = np.packbits(amp_wave_bits[8:16], bitorder='little')

    soln_status_bits = np.unpackbits(bin[18:19].view(dtype=np.uint8), bitorder='little')

    misc_bits = np.unpackbits(bin[19:20].view(dtype=np.uint8), bitorder='little')

    return {
        # Fixed string constant identifying the mission. Listed explicitly as a schema field
        # in swift.xrt.thresholded_pixels with the value "Swift".
        "mission": "SWIFT",

        # Fixed string constant identifying the instrument. Listed explicitly as a schema field
        # in swift.xrt.thresholded_pixels with the value "XRT".
        "instrument": "XRT",

        # bin[4] = trig_obs_num: lower 24 bits = Trigger number, upper 8 bits = Observation number.
        # Assigned by the on-board BAT flight software to uniquely identify each trigger.
        "id": bin[4],

        # soln_status bit 5 (def_not_grb): ground-assigned flag indicating the event is
        # definitively NOT a GRB — i.e. this is a retraction notice.
        "alert_type": "retraction" if soln_status_bits[5] else "initial",

        # soln_status bit 30: when set, this notice was ground-generated (test);
        # when unset, the notice was flight-generated (current/real).
        "alert_tense": "test" if soln_status_bits[30] else "current",

        # bin[5] = data_tjd: Truncated Julian Day of the start of the CCD image from which
        #   this position was extracted.
        # bin[6] = data_sod: UT seconds-of-day of the same image start time, in centi-seconds
        #   (i.e. fl.pt. seconds * 100, then integerized).
        # Combined and converted to ISO 8601 datetime string.
        "observation_start": utils.datetime_to_iso8601(bin[5], bin[6]),

        # bin[7] = burst_ra: RA of the burst/afterglow as determined by the XRT flight software
        # (J2000 epoch). Stored as an integer in units of 0.0001-deg (fl.pt. degrees * 10000).
        # Divide by 10000 to recover degrees.
        "ra": bin[7] * 1e-4,

        # bin[8] = burst_dec: Dec of the burst/afterglow (J2000 epoch), same encoding as burst_ra.
        # Divide by 10000 to recover degrees.
        "dec": bin[8] * 1e-4,

        # bin[16] = hi_prec_err: high-precision position error radius (90% containment),
        # including both statistical and systematic contributions. Stored in units of
        # centi-arcsec (fl.pt. arcsec * 100). Divide by 100 to get arcsec, then by 3600
        # to convert to degrees.
        # Note: systematic error is always included; systematic_included is always True.
        "ra_dec_error": bin[16] / 3600 * 1e-2,
        # "systematic_included": True,  # systematic contributions always included in hi_prec_err

        # bin[9] = burst_flux: approximate energy flux of the afterglow in CGS units.
        # After 14 Nov 2005, stored as fl.pt. [erg/cm^2/s] * 1e14, then integerized.
        # Multiply by 1e-14 to recover flux in erg/cm^2/s.
        "energy_flux": bin[9] * 1e-14,

        # bin[21] = image_snr: signal-to-noise ratio of the source detection in the XRT image.
        # Stored as centi-sigma (fl.pt. SNR * 100). Divide by 100 to recover SNR.
        "image_snr": bin[21] * 1e-2,

        # bin[20] = xrt_bat_distance: angular distance between the XRT-derived position and
        # the BAT-derived position. Stored in units of 0.0001-deg. Divide by 10000 to get degrees.
        "xrt_bat_distance": bin[20] * 1e-4,

        # bin[12-15] = tam_x/y_1/2: positions of the Telescope Alignment Monitor (TAM)
        # stars in the 1st and 2nd XRT images. Used to verify XRT tube stability.
        # Stored in centi-tam_pixels (fl.pt. pixels * 100); typical range 200.00–400.00.
        # Divide by 100 to recover pixel coordinates.
        # Structured as a 2x2 array: [[x1, y1], [x2, y2]].
        "tam_values": [
            [bin[12] * 1e-2, bin[13] * 1e-2],  # TAM position from 1st image [x1, y1]
            [bin[14] * 1e-2, bin[15] * 1e-2],  # TAM position from 2nd image [x2, y2]
        ],

        # bin[17] = amp_wave: upper 16 bits = readout amplifier ID; lower 16 bits = waveform ID.
        # amp[0] is the decoded amplifier identifier.
        "readout_amplifier": amp[0],

        # bin[17] = amp_wave: upper 16 bits = readout amplifier ID; lower 16 bits = waveform ID.
        # wave[0] is the decoded waveform identifier (typically 50 or 60).
        "readout_waveform": wave[0],

        # soln_status bit 0 (point_src): flight-assigned flag set if the detected event is
        # possibly a cosmic ray rather than a real astrophysical source.
        "possible_cosmic_ray": bool(soln_status_bits[0]),

        # --- Fields present in the raw XRT_POS packet but NOT in the swift.xrt.position schema ---

        # misc bit 20 (was_subthresh): set if this event was originally a SubThreshold BAT trigger
        # that has since been promoted to a real XRT_POS notice.
        # "was_subthresh": bool(misc_bits[20]),

        # misc bit 21 (st_loss_lock): set if this is an image trigger AND it occurred during a
        # StarTracker Loss-of-Lock event, meaning the position may be less reliable.
        # Note: the swift.xrt.position schema exposes this inversely as 'star_tracker_locked'.
        # "star_tracker_locked": not bool(misc_bits[21]),

        # misc bit 22 (uploaded_too): set if this notice was generated as a result of an uploaded
        # Target-of-Opportunity (TOO) sequence — i.e. Swift was commanded to observe this location.
        # "uploaded_too_sequence": bool(misc_bits[22]),

        # misc bit 25 (updated_pos): set if this is an updated position notice that
        # changes/improves the position from the original XRT_Position notice for this trigger.
        # "updated_position": bool(misc_bits[25]),

        # misc bit 11 (pos_out_of_range): set if one or more of the RA/Dec values were outside
        # the valid range (e.g. RA > 360 deg), indicating a potentially invalid position solution.
        # "pos_out_of_range": bool(misc_bits[11]),

        # misc bit 13 (near_brt_star): set if the XRT position is within 0.3 degrees of a bright
        # star (magnitude < 6.5), which may contaminate or confuse the afterglow detection.
        # "bright_star_nearby": bool(misc_bits[13]),

        # misc bit 16 (low_xrt_bat_theta): set if the BAT–XRT angular separation (theta) is less
        # than 10 arcmin, indicating Swift was already pointed very close to this source.
        # "low_xrt_bat_theta": bool(misc_bits[16]),

        # misc bit 10 (not_real_peak): set if the detected peak in the XRT image is flagged as
        # not being a real astrophysical source peak (e.g. a readout artifact or hot pixel).
        # "not_real_astrophysical_peak": bool(misc_bits[10]),

        # NOTE: soln_status bits 28 and 29 ('spatial_coincidence' and 'temporal_coincidence')
        # do not exist in the SWIFT_XRT_POS (type=67) packet definition. These bits are defined
        # only in BAT-related packet types and were incorrectly included in the original code.
        # "spatial_coincidence":  bool(soln_status_bits[28]),  # not defined in XRT_POS packet
        # "temporal_coincidence": bool(soln_status_bits[29]),  # not defined in XRT_POS packet
    }