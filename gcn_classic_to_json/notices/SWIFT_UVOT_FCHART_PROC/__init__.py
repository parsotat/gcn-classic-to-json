from ... import utils
import numpy as np

filters = [
    "Blocked",
    "UV_Grism",
    "UVW2",
    "V",
    "UVM2",
    "Vis_Grism",
    "UVW1",
    "U",
    "Magnifier",
    "B",
    "White",
    "unknown",
]



def parse_uvot_srclist(bin):
    misc_status = np.unpackbits(bin[19:20].view(np.uint8), bitorder='little')

    return {
        # Fixed string constant identifying the mission. Listed explicitly as a schema field
        # in swift.uvot.source_list with the value "Swift".
        "mission": "SWIFT",

        # Fixed string constant identifying the instrument. Listed explicitly as a schema field
        # in swift.uvot.source_list with the value "UVOT".
        "instrument": "UVOT",

        # bin[4] = trig_obs_num: lower 24 bits = Trigger number, upper 8 bits = Observation number.
        # Assigned by the on-board BAT flight software to uniquely identify each trigger.
        "id": bin[4],

        # misc bit 30 (ground_generated): set if this notice was ground-generated (type=80);
        # always 0 for the raw flight form (type=73).
        # "initial" for the raw flight notice (type=73); "update" for the ground-processed
        # notice (type=80), which refines/replaces the original raw source list.
        "alert_type": "update" if misc_status[30] else "initial",

        # bin[5] = expo_start_tjd: Truncated Julian Day of the start of the UVOT CCD
        #   exposure integration.
        # bin[6] = expo_start_sod: UT seconds-of-day of the start of the exposure, in
        #   centi-seconds (fl.pt. seconds * 100, then integerized).
        # Combined and converted to an ISO 8601 datetime string.
        "observation_start": utils.datetime_to_iso8601(bin[5], bin[6]),

        # bin[7] = point_ra: RA of the spacecraft pointing direction at the start/stop of
        # the integration interval for the source list (J2000 epoch).
        # Stored in units of 0.0001-deg (fl.pt. degrees * 10000, then integerized).
        # Divide by 10000 to recover degrees.
        "ra_pointing": bin[7] * 1e-4,

        # bin[8] = point_dec: Dec of the spacecraft pointing direction (J2000 epoch).
        # Same encoding as point_ra. Divide by 10000 to recover degrees.
        "dec_pointing": bin[8] * 1e-4,

        # bin[9] = image_roll: Roll angle of the target.
        # Stored in units of 0.0001-deg (fl.pt. degrees * 10000, then integerized).
        # Divide by 10000 to recover degrees.
        "roll": bin[9] * 1e-4,

        # bin[10] = filter: integer identifier of the UVOT filter used for the observation.
        # Decoded via the filters lookup dictionary.
        # Filter values:
        #   0=Blocked, 1=UV_Grism, 2=UVW2, 3=V, 4=UVM2, 5=Vis_Grism,
        #   6=UVW1, 7=U, 8=Magnifier, 9=B, 10=White, 11=unknown
        "filter": filters[bin[10]],

        # bin[11] = bkg_mean: mean value of the background level in the exposure.
        # Stored as a floating point quantity multiplied by 1000 and then integerized
        # (units of 0.001). Divide by 1000 to recover the background mean value.
        "background_mean": bin[11] * 1e-3,

        # bin[12] = x_max: maximum extent of the image window in the X direction,
        # expressed in detector coordinates (range 0–2095).
        # bin[13] = y_max: maximum extent of the image window in the Y direction,
        # expressed in detector coordinates (range 0–2095).
        # Together they define the image_extent as [x_max, y_max].
        "image_extent": [bin[12], bin[13]],

        # bin[15] = x_offset: X offset of the image window origin in detector coordinates
        # (range 0–2095).
        # bin[16] = y_offset: Y offset of the image window origin in detector coordinates
        # (range 0–2095).
        # Together they define the image_offset as [x_offset, y_offset].
        "image_offset": [bin[15], bin[16]],

        # bin[14] = n_stars: total number of stars (sources) found in the source list.
        "n_stars": bin[14],

        # bin[17] = det_thresh: detection threshold used in this exposure.
        # Units are DN (digital number), range 0 to ???.
        "detection_threshold": bin[17],

        # bin[18] = photo_thresh: photometry threshold used in this exposure.
        # Units are DN (digital number), range 0 to ???.
        "photometry_threshold": bin[18],

        # misc bit 29 (watchdog_timeout): set if this UVOT_SRCLIST notice was forced out
        # early via the watchdog timeout mechanism rather than completing normally.
        "watchdog_timeout": bool(misc_status[29]),

        # bin[22-38] = url: filename portion of the URL pointing to the raw source list
        # FITS file. The full URL is formed by prepending
        # "http://gcn.gsfc.nasa.gov/gcn/notices_s/".
        # Spans 17 longwords (68 bytes), up to 67 ASCII characters, always null-terminated.
        # In the swift.uvot.source_list schema this field will contain the base64-encoded
        # FITS file rather than a URL string.
        # Only populated for the raw flight notice (type=73, misc bit 2^30 = 0).
        # Set to None for the ground-processed notice (type=80, misc bit 2^30 = 1).
        #"raw_source_list_fits_file": f"http://gcn.gsfc.nasa.gov/gcn/notices_s/{''.join([i.decode('utf-8') for i in bin[22:39].view('c')])}" if not misc_status[30] else None,

        # bin[22-38] = url: filename portion of the URL pointing to the ground-processed
        # source list FITS file. Same URL field and encoding as raw_source_list_fits_file
        # above, but populated only for the ground-processed notice (type=80,
        # misc bit 2^30 = 1).
        # Set to None for the raw flight notice (type=73, misc bit 2^30 = 0).
        #"processed_source_list_fits_files": f"http://gcn.gsfc.nasa.gov/gcn/notices_s/{''.join([i.decode('utf-8') for i in bin[22:39].view('c')])}" if misc_status[30] else None,

        #just have 1 key in the dict for the source list fits files regardless of raw or processed, at a higher level we
        # tell the user if this is initial or updated
        "source_list_fits_files": f"http://gcn.gsfc.nasa.gov/gcn/notices_s/{''.join([i.decode('utf-8') for i in bin[22:39].view('c')])}"

        # --- Fields present in the UVOT_SRCLIST packet but NOT in the
        # misc_status.uvot.source_list schema ---

        # misc bit 11 (pos_out_of_range): set if one or more of the RA/Dec/Roll/Theta/Phi
        # values were outside the valid range (e.g. RA > 360 deg).
        # "pos_out_of_range": bool(misc_bits[11]),

        # misc bit 12 (blk_cat_src): set if the position is in the catalog of sources to
        # be blocked (internal use only).
        # "blocked_catalog_source": bool(misc_bits[12]),

        # misc bit 13 (near_brt_star): set if the position is near a bright star
        # (magnitude < 6.5).
        # "bright_star_nearby": bool(misc_bits[13]),

        # misc bit 20 (was_subthresh): set if this was originally a SubThreshold trigger,
        # now converted to a real UVOT_PROC_SL notice.
        # NOTE: this bit is only defined for type=80 (ground-processed).
        # "was_subthresh": bool(misc_bits[20]),

        # misc bit 21 (st_loss_lock): set if this is an image trigger AND it occurred
        # during a StarTracker Loss-of-Lock event.
        # "star_tracker_loss_of_lock": bool(misc_bits[21]),

        # misc bit 22 (uploaded_too): set if this notice was generated as a result of an
        # uploaded TOO (Target-of-Opportunity) sequence.
        # "too_sequence_uploaded": bool(misc_bits[22]),

        # misc bit 24 (sky_srclist_error): set if the uvot_sky_srclist.ps file had an
        # error during processing and does not exist.
        # NOTE: this bit is only defined for type=80 (ground-processed).
        # "sky_srclist_error": bool(misc_bits[24]),

        # misc bit 25 (sources_fits_error): set if the uvot_sources_srclist.fits file had
        # an error during processing and does not exist.
        # NOTE: this bit is only defined for type=80 (ground-processed).
        # "sources_fits_error": bool(misc_bits[25]),

        # misc bit 26 (catalog_fits_error): set if the uvot_catalog_srclist.fits file had
        # an error during processing and does not exist.
        # NOTE: this bit is only defined for type=80 (ground-processed).
        # "catalog_fits_error": bool(misc_bits[26]),

        # misc bit 27 (field_srclist_error): set if the uvot_field_srclist.ps file had an
        # error during processing and does not exist.
        # NOTE: this bit is only defined for type=80 (ground-processed).
        # "field_srclist_error": bool(misc_bits[27]),
    }

def parse(bin):
    bin[19]  # Intentionally Omitted. Bits seemed to be used for internal messages
    bin[20:22]  # Spare. According to Docs: '8 bytes for future use'

    return {**parse_uvot_srclist(bin)}
