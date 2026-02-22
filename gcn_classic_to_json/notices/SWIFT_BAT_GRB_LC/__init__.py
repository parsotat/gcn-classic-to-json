import numpy as np

from ... import utils
from ..SWIFT_BAT_GRB_POS_ACK import parse_swift_bat

star_tracker_status = ["locked", "not locked"]


def parse(bin):
    bin[9:12]  # Unused. According to docs: '12 bytes for the future'
    bin[19]  # Unused. Flags are either internal or equivalent to bin[18]

    soln_status_bits = np.unpackbits(bin[18:19].view(np.uint8), bitorder='little')

    misc_bits = np.unpackbits(bin[19:20].view(dtype=np.uint8), bitorder='little')

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

    integ_time = bin[15] * 4 / 1000

    lat, lon = bin[16:17].view("<i2")

    return {
        # Fields inherited from parse_swift_bat(bin):
        #   mission, instrument, id, trigger_time, ra, dec, rate_snr
        # See parse_swift_bat() definition for field-level comments on these.
        **parse_swift_bat(bin),

        # bin[11] = burst_error: 90%-containment position error radius.
        # NOTE: bin[11] is SPARE in the BAT_GRB_LC (type=63/76) packet — this field
        # is not populated and cannot be derived from the lightcurve packet.
        "ra_dec_error": None,

        # Systematic error is never included in the BAT position error. Always False.
        # NOTE: ra_dec_error is not available in this packet (bin[11] is spare), so
        # systematic_included is also not meaningful here.
        "systematic_included": None,

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
        # NOTE: in the BAT_GRB_LC (type=63) packet, soln_status bits 0-28 are all spare
        # in the packet's native form. This bit is only valid if misc bit 2^24 is set,
        # indicating soln_status was copied from the associated BAT_POS_ACK packet.
        "trigger_type": "image" if soln_status_bits[4] else "rate",

        # bin[17] = trig_index: index value (row number in the BAT on-board flight software
        # table) of the trigger criterion that was the highest-significance successful trigger.
        "trigger_index": bin[17],

        # bin[9] = burst_flue: net (background-subtracted) count rate during the trigger
        # interval. NOTE: bin[9] is SPARE in the BAT_GRB_LC (type=63/76) packet — this
        # field is not populated and cannot be derived from the lightcurve packet.
        "net_count_rate": None,

        # bin[22-38] in the BAT_GRB_LC packet contains the URL, not background counts.
        # background_count_rate is not available in the lightcurve packet.
        "background_count_rate": None,

        # bin[15] = integ_time: duration of the trigger sampling interval in units of
        # 4msec ticks (e.g. a value of 16 = 64 msec trigger criterion). Copied from the
        # BAT_POS notice. Only valid if misc bit 2^24 is set.
        # rate_duration is set to the integration time for rate triggers; None for image
        # triggers.
        "rate_duration": integ_time if not soln_status_bits[4] else None,

        # There is no energy range field in the BAT_GRB_LC binary packet.
        "rate_energy_range": None,

        # bin[20] = image_signif: signal-to-noise ratio of the image-trigger detection.
        # Stored in centi-sigma (fl.pt. SNR * 100). Divide by 100 to recover sigma.
        "image_snr": bin[20] * 1e-2,

        # image_duration is set to the integration time for image triggers; None for rate
        # triggers.
        "image_duration": integ_time if soln_status_bits[4] else None,

        # There is no energy range field in the BAT_GRB_LC binary packet.
        "image_energy_range": None,

        # classification, properties, T90, hardness_ratio, spectral_lag, and
        # observation_start are schema fields that are not derivable from the
        # BAT_GRB_LC binary packet.
        "classification": None,
        "properties": None,
        "T90": None,
        "hardness_ratio": None,
        "spectral_lag": None,
        "observation_start": None,

        # bin[22-38] = url: filename portion of the URL pointing to the lightcurve FITS file.
        # The full URL is formed by prepending "http://gcn.gsfc.nasa.gov/gcn/notices_s/".
        # Spans 17 longwords (68 bytes), up to 67 ASCII characters, always null-terminated.
        # In the swift.bat.lightcurve schema this field will contain the base64-encoded
        # FITS file rather than a URL string.
        "lightcurve_fits_file": f"http://gcn.gsfc.nasa.gov/gcn/notices_s/{''.join([i.decode('utf-8') for i in bin[22:39].view('c')])}",

        # misc bit 29 (watchdog_timeout): set if this BAT_GRB_LC notice was forced out
        # early via the watchdog timeout mechanism rather than completing normally.
        "watchdog_timeout": bool(misc_bits[29]),

        # soln_status bit 10 (star_tracker): StarTracker lock status at trigger time.
        # Decoded via star_tracker_status lookup dict. Only valid if misc bit 2^24 is set.
        # True = StarTracker was locked; False = StarTracker was NOT locked.
        "star_tracker_locked": False if "not" in star_tracker_status[soln_status_bits[10]] else True,

        # --- Fields present in the BAT_GRB_LC packet but NOT in the
        # swift.bat.lightcurve schema ---

        # bin[14] = delta_time: start time of the lightcurve relative to the trigger time.
        # Stored in centi-seconds (fl.pt. seconds * 100). Divide by 100 to recover seconds.
        # Note: there is an implied negative sign — the lightcurve starts at T0 - delta_time
        # before the trigger.
        # "delta_time": bin[14] * 1e-2,

        # NOTE: rate_snr is already provided by parse_swift_bat() from bin[21].
        # The line below would produce a duplicate key and has been removed.
        # "rate_snr": bin[21] * 1e-2,

        # soln_status bit 1 (grb): flight-assigned flag; set if the source is classified
        # as a GRB. Decoded via grb_status lookup dict. Only valid if misc bit 2^24 is set.
        # "grb_status": grb_status,

        # soln_status bit 0 (point_src): flight-assigned flag; set if a point source was
        # found. Only valid if misc bit 2^24 is set.
        # "point_source": bool(soln_status_bits[0]),

        # soln_status bit 2 (interesting): flight-assigned flag; set if the source is an
        # interesting known source (e.g. a flaring catalogued source). Only valid if
        # misc bit 2^24 is set.
        # "flaring_known_source": bool(soln_status_bits[2]),

        # soln_status bit 13 (bright_star): set if the BAT position is near a bright star
        # (magnitude < 6.5). Only valid if misc bit 2^24 is set.
        # "bright_star_nearby": bool(soln_status_bits[13]),

        # soln_status bit 15 (removed_from_catalog): set if the source has been removed
        # from the on-board catalog. Only valid if misc bit 2^24 is set.
        # "removed_from_catalog": bool(soln_status_bits[15]),

        # soln_status bit 16 (galaxy_nearby): set if a nearby NGC galaxy is within the
        # position error circle. Only valid if misc bit 2^24 is set.
        # "galaxy_nearby": bool(soln_status_bits[16]),
    }