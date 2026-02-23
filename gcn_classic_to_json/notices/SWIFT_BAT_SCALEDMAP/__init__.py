import numpy as np

from ... import utils
from ..SWIFT_BAT_GRB_POS_ACK import parse_swift_bat

star_tracker_status = ["locked", "not locked"]


def parse(bin):
    bin[9:14]  # Unused. According to docs: '20 bytes for the future'
    bin[17]  # Unused. According to docs: 'trig_index. This field is not yet (if ever) assigned.'
    bin[19]  # Unused. Flags are either internal or equivalent to bin[18]

    integ_time = bin[15] * 4 / 1000  # misc_bit has to be defined

    lat, lon = bin[16:17].view("<i2")

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

    return {
        # Fields inherited from parse_swift_bat(bin):
        #   mission, instrument, id, rate_snr
        # NOTE: For the SWIFT_BAT_SCALED_MAP packet (type=64), the following fields
        # from parse_swift_bat() have NON-STANDARD meanings and must be remapped:
        #
        #   "trigger_time": bin[5]/bin[6] = map_tjd/map_sod — the time when the
        #     scaled map was generated, NOT the BAT burst trigger time.
        #
        #   "ra": bin[7] * 1e-4 = point_ra — the RA of the spacecraft pointing
        #     direction, NOT the burst position RA.
        #
        #   "dec": bin[8] * 1e-4 = point_dec — the Dec of the spacecraft pointing
        #     direction, NOT the burst position Dec.
        #
        # These are remapped below to their correct schema field names.
        **{k: v for k, v in parse_swift_bat(bin).items()
           if k not in ("trigger_time", "ra", "dec")},

        # bin[5] = map_tjd: Truncated Julian Day when the scaled map was generated.
        # bin[6] = map_sod: UT seconds-of-day when the scaled map was generated,
        #   in centi-seconds (fl.pt. seconds * 100, then integerized).
        # Note: this is the map generation time, not the BAT burst trigger time.
        # Combined and converted to an ISO 8601 datetime string.
        "trigger_time": utils.datetime_to_iso8601(bin[5], bin[6]),

        # bin[9-13] are SPARE in the BAT_SCALED_MAP packet — the burst RA, Dec, and
        # position error are not present. The schema fields ra, dec, and ra_dec_error
        # are therefore not derivable from this packet.
        "ra": None,
        "dec": None,
        "ra_dec_error": None,

        # Systematic error is never included in the BAT position error. Always False.
        # NOTE: ra_dec_error is not available in this packet so systematic_included
        # is also not meaningful here.
        "systematic_included": None,

        # bin[7] = point_ra: RA of the spacecraft pointing direction at the
        # start/stop of the integration interval for this map (J2000 epoch).
        # Stored in units of 0.0001-deg (fl.pt. degrees * 10000, then integerized).
        # Divide by 10000 to recover degrees.
        "ra_pointing": bin[7] * 1e-4,

        # bin[8] = point_dec: Dec of the spacecraft pointing direction at the
        # start/stop of the integration interval for this map (J2000 epoch).
        # Same encoding as point_ra. Divide by 10000 to recover degrees.
        "dec_pointing": bin[8] * 1e-4,

        # bin[16] high-order short = lat: spacecraft latitude at the time of the BAT trigger.
        # Stored as a 2-byte integer in centi-degrees (fl.pt. degrees * 100).
        # Divide by 100 to recover degrees.
        "latitude": lat * 1e-2,

        # bin[16] low-order short = lon: spacecraft longitude at the time of the BAT trigger.
        # Same encoding as lat. Divide by 100 to recover degrees.
        "longitude": lon * 1e-2,

        # soln_status bit 4 (image_trig): set if this was an image trigger;
        # unset if this was a rate trigger.
        # NOTE: soln_status (bin[18]) is only valid if misc bit 2^24 is set, indicating
        # it was copied from the associated BAT_POS_ACK packet.
        "trigger_type": "image" if soln_status_bits[4] else "rate",

        # bin[21] = rate_signif: SNR of the rate-trigger detection, copied from BAT_POS.
        # NOTE: rate_snr is already provided by parse_swift_bat() from bin[21].
        # The line below would produce a duplicate key and has been removed.
        # "rate_snr": bin[21] * 1e-2,

        # bin[20] = image_signif: signal-to-noise ratio of the image-trigger detection,
        # copied from BAT_Position notice. Stored in centi-sigma (fl.pt. SNR * 100).
        # Divide by 100 to recover sigma.
        "image_snr": bin[20] * 1e-2,

        # observation_start is a schema field that is not derivable from the
        # BAT_SCALED_MAP binary packet.
        # just using the original scaled map time here
        "observation_start": utils.datetime_to_iso8601(bin[5], bin[6]),

        # bin[22-38] = url: filename portion of the URL pointing to the scaled map FITS file.
        # The full URL is formed by prepending "http://gcn.gsfc.nasa.gov/gcn/notices_s/".
        # Spans 17 longwords (68 bytes), up to 67 ASCII characters, always null-terminated.
        # In the swift.bat.scaled_map schema this field will contain the base64-encoded
        # FITS file rather than a URL string.
        "scaled_map_fits_file": f"http://gcn.gsfc.nasa.gov/gcn/notices_s/{''.join([i.decode('utf-8') for i in bin[22:39].view('c')])}",

        # misc bit 29 (watchdog_timeout): set if this BAT_SCALED_MAP notice was forced out
        # early via the watchdog timeout mechanism rather than completing normally.
        "watchdog_timeout": bool(misc_bits[29]),

        # soln_status bit 10 (st_loss_lock): StarTracker lock status at trigger time.
        # Decoded via star_tracker_status lookup dict. Only valid if misc bit 2^24 is set.
        # True = StarTracker was locked; False = StarTracker was NOT locked.
        "star_tracker_locked": False if "not" in star_tracker_status[soln_status_bits[10]] else True,

        # soln_status bit 5 (def_not_grb): ground-assigned flag indicating the event is
        # definitively NOT a GRB — i.e. this is a retraction notice.
        # NOTE: only valid if misc bit 2^24 is set.
        "alert_type": "retraction" if soln_status_bits[5] else "initial",

        # --- Fields present in the BAT_SCALED_MAP packet but NOT in the
        # swift.bat.scaled_map schema ---

        # bin[14] = foregnd_dur: duration of the foreground (source) sampling interval
        # native to the ScaledMap notice (not copied from BAT_POS).
        # The units are milliseconds.
        # "foreground_duration": bin[14] * 1e-3,

        # bin[15] = integ_time: duration of the trigger sampling interval in units of
        # 4msec ticks (e.g. a value of 16 = 64 msec trigger criterion). Copied from the
        # BAT_POS notice. Only valid if misc bit 2^24 is set.
        # "trigger_duration": integ_time,

        # bin[17] = trig_index: row number in the BAT on-board trigger table of the
        # highest-significance trigger criterion. Not yet (if ever) assigned.
        # "trigger_index": bin[17],

        # soln_status bit 0 (point_src): flight-assigned flag; set if a point source was
        # found. Only valid if misc bit 2^24 is set.
        # "point_source": bool(soln_status_bits[0]),

        # soln_status bit 1 (grb): flight-assigned flag; set if the source is classified
        # as a GRB. Only valid if misc bit 2^24 is set.
        # "grb_status": grb_status,

        # soln_status bit 2 (interesting): flight-assigned flag; set if the source is an
        # interesting known source (e.g. a flaring catalogued source). Only valid if
        # misc bit 2^24 is set.
        # "flaring_known_source": bool(soln_status_bits[2]),

        # soln_status bit 13 (near_brt_star): set if the BAT position is near a bright star
        # (magnitude < 6.5). Only valid if misc bit 2^24 is set.
        # "bright_star_nearby": bool(soln_status_bits[13]),

        # soln_status bit 14 (was_subthresh): set if this was originally a SubThreshold
        # trigger. Only valid if misc bit 2^24 is set.
        # "was_subthresh": bool(soln_status_bits[14]),

        # soln_status bit 15 (onboard_rmvd): set if this source has been purposefully
        # removed from the on-board catalog. Only valid if misc bit 2^24 is set.
        # "removed_from_catalog": bool(soln_status_bits[15]),

        # soln_status bit 16 (nearby_gal): set if this matched a nearby galaxy in the
        # on-board catalog. Only valid if misc bit 2^24 is set.
        # "galaxy_nearby": bool(soln_status_bits[16]),
    }