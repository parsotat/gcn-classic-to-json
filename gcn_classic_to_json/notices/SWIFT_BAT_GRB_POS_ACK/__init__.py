import numpy as np

from ... import utils

energy_ranges = [[15, 25], [15, 50], [25, 100], [50, 350]]
star_tracker_status = ["locked", "not locked"]


def parse_swift_bat(bin):
    return {
        # Fixed string constant identifying the mission. Listed explicitly as a schema field
        # in swift.bat.position with the value "Swift".
        "mission": "SWIFT",

        # Fixed string constant identifying the instrument. Listed explicitly as a schema field
        # in swift.bat.position with the value "BAT".
        "instrument": "BAT",

        # bin[4] = trig_obs_num: lower 24 bits = Trigger number, upper 8 bits = Observation number.
        # Assigned by the on-board BAT flight software to uniquely identify each trigger.
        "id": bin[4],

        # bin[5] = burst_tjd: Truncated Julian Day of the Swift-BAT burst trigger.
        # bin[6] = burst_sod: UT seconds-of-day of the same trigger time, in centi-seconds
        #   (i.e. fl.pt. seconds * 100, then integerized).
        # Combined and converted to an ISO 8601 datetime string.
        "trigger_time": utils.datetime_to_iso8601(bin[5], bin[6]),

        # bin[7] = burst_ra: RA of the burst/transient as determined by the BAT flight
        # software (J2000 epoch). Stored in units of 0.0001-deg (fl.pt. degrees * 10000).
        # Divide by 10000 to recover degrees.
        "ra": 1e-4 * bin[7],

        # bin[8] = burst_dec: Dec of the burst/transient (J2000 epoch).
        # Same encoding as burst_ra. Divide by 10000 to recover degrees.
        "dec": 1e-4 * bin[8],

        # bin[21] = rate_signif: signal-to-noise ratio of the rate-trigger detection.
        # Stored in centi-sigma (fl.pt. SNR * 100). Divide by 100 to recover sigma.
        "rate_snr": bin[21] * 1e-2,
    }


def parse(bin):
    bin[15]  # Unused. According to docs: '4 bytes for the future'
    bin[19]  # Unused. Flags are either internal or equivalent to bin[18]
    bin[26:36]  # Unused. According to docs: '40 bytes for the future'
    bin[36]  # Unused. Flags Equivalent to bin[18]
    bin[38]  # Intentionally omitted. Sun/Moon parameters

    integ_time = bin[14] * 4 / 1000

    lat, lon = bin[16:17].view("<i2")

    misc_bits = np.unpackbits(bin[19:20].view(dtype=np.uint8), bitorder='little')

    soln_status_bits = np.unpackbits(bin[18:19].view(np.uint8), bitorder='little')
    soln_status_bits[8]  # Unused. According to docs: 'ground_catalog_source'.
    soln_status_bits[12]  # Unused. According to docs: 'blocked_catalog_source'.
    # These seems to be cross-referenced with a ground catalog with the name of the source printed in the text notices.
    # But since the name of this source isn't stored in the these packets, I don't see a reason to include it.
    if soln_status_bits[11]:
        grb_status = (
            "It is probably not a GRB or transient due to very low image significance"
        )
    elif soln_status_bits[7]:
        grb_status = (
            "It is probably not a GRB or transient due to low image significance"
        )
    elif soln_status_bits[9]:
        grb_status = (
            "It is probably not a GRB or transient due to negative background slope"
        )
    elif soln_status_bits[6]:
        grb_status = (
            "It is probably not a GRB or transient due to high background level"
        )
    elif soln_status_bits[1]:
        grb_status = "It is a GRB"
    else:
        grb_status = "It is not a GRB"

    catalog_num = bin[25]

    #bins 36 onwards are assigned on a byte, by byte basis, and there are 9 bytes that are assigned via s_t_r
    merit_bytes = bin[36:].view(dtype="i1")

    #the energyrange is given by the 4th index of the extracted bytes
    energy_range_idx = merit_bytes[4]
    energy_range = energy_ranges[energy_range_idx]

    return {
        # Fields inherited from parse_swift_bat(bin):
        #   mission, instrument, id, trigger_time, ra, dec, rate_snr
        # See parse_swift_bat() definition for field-level comments on these.
        **parse_swift_bat(bin),

        # bin[11] = burst_error: radius of the position error circle (90% containment).
        # Stored in units of 0.0001-deg (fl.pt. degrees * 10000, then integerized).
        # Initially hardwired at 4 arcmin (0.067 deg); later made flux-dependent.
        # Divide by 10000 to recover degrees.
        "ra_dec_error": 1e-4 * bin[11],

        # Systematic error is never included in the BAT position error. Always False.
        "systematic_included": False,

        # bin[16] high-order short = lat: spacecraft latitude at the time of the BAT trigger.
        # Stored as a 2-byte integer in centi-degrees (fl.pt. degrees * 100).
        # Divide by 100 to recover degrees.
        "latitude": lat * 1e-2,

        # bin[16] low-order short = lon: spacecraft longitude at the time of the BAT trigger.
        # Same encoding as lat. Divide by 100 to recover degrees.
        "longitude": lon * 1e-2,

        # bin[12] = phi: BAT instrument phi coordinate of the trigger, measured from the
        # +Y-axis of the spacecraft increasing towards the -Z axis.
        # Stored in centi-degrees (fl.pt. degrees * 100). Divide by 100 to recover degrees.
        "instrument_phi": 1e-2 * bin[12],

        # bin[13] = theta: BAT instrument theta coordinate of the trigger, measured from
        # the BAT boresight. Stored in centi-degrees (fl.pt. degrees * 100).
        # Divide by 100 to recover degrees.
        "instrument_theta": 1e-2 * bin[13],

        # soln_status bit 4 (image_trig): set if this was an image trigger;
        # unset if this was a rate trigger.
        "trigger_type": "image" if soln_status_bits[4] else "rate",

        # bin[17] = trig_index: index value (row number in the BAT on-board flight software
        # table) of the trigger criterion that was the highest-significance successful trigger.
        "trigger_index": bin[17],

        # bin[9] = burst_flue: net (background-subtracted) count rate during the trigger
        # interval. Units are counts accumulated during the integ_time interval.
        "net_count_rate": bin[9],

        # bin[22] = bkg_flue: number of events during the background interval.
        # Units are counts.
        "background_count_rate": bin[22],

        # bin[14] = integ_time: duration of the trigger sampling interval in units of
        # 4msec ticks (e.g. a value of 16 = 64 msec trigger criterion).
        # rate_duration is set to the integration time for rate triggers; None for image
        # triggers. energy_range is the decoded energy band of the trigger criterion.
        "rate_duration": integ_time if not soln_status_bits[4] else None,
        "rate_energy_range": energy_range if not soln_status_bits[4] else None,

        # bin[20] = image_signif: signal-to-noise ratio of the image-trigger detection.
        # Stored in centi-sigma (fl.pt. SNR * 100). Divide by 100 to recover sigma.
        "image_snr": bin[20] * 1e-2,

        # image_duration and image_energy_range are set for image triggers; None for rate
        # triggers.
        "image_duration": integ_time if soln_status_bits[4] else None,
        "image_energy_range": energy_range if soln_status_bits[4] else None,

        # classification, properties, T90, hardness_ratio, and spectral_lag are schema
        # fields that are not derivable from the BAT_GRB_POS binary packet.
        "classification": None,
        "properties": None,
        "T90": None,
        "hardness_ratio": None,
        "spectral_lag": None,

        # bin[5/23] = background_start_time: start time of the background interval.
        # Uses the burst TJD (bin[5]) combined with the background start SOD (bin[23]),
        # which is stored in centi-seconds. Note: bin[23] may be zero if the trigger
        # criterion does not have a specified background interval.
        "background_start_time": utils.datetime_to_iso8601(bin[5], bin[23]),

        # bin[24] = bkg_dur: duration of the background interval.
        # Stored in centi-seconds (fl.pt. seconds * 100). Divide by 100 to recover seconds.
        "background_duration": bin[24] * 1e-2,

        # bin[25] = cat_num: on-board catalog match ID number, present only when the source
        # is matched to a known source in the flight catalog (soln_status bit 3 = 1).
        # Set to None if this is not a catalog source.
        "catalog_number": catalog_num if soln_status_bits[3] else None,

        # misc bit 12: set if the theta value (angle between Swift pointing direction and
        # the trigger position) was less than 10 arcmin — i.e. Swift was already pointed
        # at this source at the time of the trigger.
        "within_10arcmin": bool(misc_bits[12]),

        # soln_status bit 10 (st_loss_lock): indicates whether the StarTracker was NOT
        # locked at the time of the trigger. Decoded via star_tracker_status lookup dict.
        # True = StarTracker was locked; False = StarTracker was NOT locked.
        "star_tracker_locked": False if "not" in star_tracker_status[soln_status_bits[10]] else True,

        # soln_status bit 30 (test_submit): set if this is a test submission;
        # unset for real current notices.
        "alert_tense": "test" if soln_status_bits[30] else "current",

        # soln_status bit 5 (def_not_grb): ground-assigned flag indicating the event is
        # definitively NOT a GRB — i.e. this is a retraction notice.
        "alert_type": "retraction" if soln_status_bits[5] else "initial",

        # --- Fields present in the BAT_GRB_POS packet but NOT in the swift.bat.position schema ---

        # bin[10] = burst_ipeak: height of the peak in the sky-image plane (result of
        # FFT/MaskConvolution/InvFFT). Units are counts with a multiplicative factor of ~0.5-0.7.
        # "image_peak": bin[10],

        # soln_status bit 0 (point_src): flight-assigned flag; set if a point source was found.
        # "point_source": bool(soln_status_bits[0]),

        # soln_status bit 1 (grb): flight-assigned flag; set if the source is classified as a GRB.
        # "grb_status": grb_status,

        # soln_status bit 2 (interesting): flight-assigned flag; set if the source is an
        # interesting known source (e.g. a flaring catalogued source).
        # "flaring_known_source": bool(soln_status_bits[2]),

        # soln_status bit 13 (near_brt_star): set if the BAT position is near a bright star
        # (magnitude < 6.5).
        # "bright_star_nearby": bool(soln_status_bits[13]),

        # soln_status bit 14 (was_subthresh): set if this was originally a SubThreshold
        # trigger that has since been promoted to a real BAT_GRB_POS notice.
        # "was_subthresh": bool(soln_status_bits[14]),

        # soln_status bit 15 (removed_from_catalog): set if the source has been removed
        # from the on-board catalog.
        # "removed_from_catalog": bool(soln_status_bits[15]),

        # soln_status bit 16 (galaxy_nearby): set if there is a nearby NGC galaxy within
        # the position error circle.
        # "galaxy_nearby": bool(soln_status_bits[16]),

        # soln_status bit 28 (spatial_coinc): ground-assigned flag; set if there was a
        # spatial coincidence with another event.
        # "spatial_coincidence": bool(soln_status_bits[28]),

        # soln_status bit 29 (temporal_coinc): ground-assigned flag; set if there was a
        # temporal coincidence with another event.
        # "temporal_coincidence": bool(soln_status_bits[29]),
    }