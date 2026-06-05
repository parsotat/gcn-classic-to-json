import numpy as np

from ... import utils
from ..SWIFT_UVOT_FCHART_PROC import filters


pixel_binning_values = {0: "1x1", 1: "2x2", 2: "4x4", 6: "64x64"}

grb_position_sources = ["Window Position", "XRT Position"]


def parse_uvot_image(bin):
    x_pos, y_pos = bin[16:17].view(dtype="<i2")

    misc_bits = np.unpackbits(bin[19:20].view(np.uint8), bitorder='little')

    pixel_binning = np.packbits(misc_bits[:4], bitorder="little")

    return {
        # Fixed string constant identifying the mission. Listed explicitly as a schema field
        # in swift.uvot.image with the value "Swift".
        "mission": "SWIFT",

        # Fixed string constant identifying the instrument. Listed explicitly as a schema field
        # in swift.uvot.image with the value "UVOT".
        "instrument": "UVOT",

        # bin[4] = trig_obs_num: lower 24 bits = Trigger number, upper 8 bits = Observation number.
        # Assigned by the on-board BAT flight software to uniquely identify each trigger.
        "id": str(bin[4]),

        # misc bit 30 (ground_generated): set if this notice was ground-generated (type=79);
        # always 0 for the raw flight form (type=72).
        # "initial" for the raw flight notice (type=72); "update" for the ground-processed
        # notice (type=79), which refines/replaces the original raw image.
        "alert_type": "update" if misc_bits[30] else "initial",

        # bin[5] = ExpStart_tjd: Truncated Julian Day of the start of the UVOT CCD
        #   integration.
        # bin[6] = ExpStart_sod: UT seconds-of-day of the start of the CCD integration,
        #   in centi-seconds (fl.pt. seconds * 100, then integerized).
        # Combined and converted to an ISO 8601 datetime string.
        "observation_start": utils.datetime_to_iso8601(bin[5], bin[6]),

        # bin[7] = point_ra: RA of the spacecraft pointing direction at the start/stop of
        # the integration interval for the image (J2000 epoch).
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

        # bin[11] = expo_id: exposure ID expressed in spacecraft seconds.
        "exposure_id": bin[11],

        # bin[12] = X0: X coordinate of pixel_zero (origin) in the Image subarray.
        # Units are detector coordinates (range 0–2095).
        # bin[13] = Y0: Y coordinate of pixel_zero (origin) in the Image subarray.
        # Units are detector coordinates (range 0–2095).
        # Together they define the image_offset as [X0, Y0].
        "image_offset": [bin[12], bin[13]],

        # bin[14] = width: width of the Image subarray in detector coordinates (0–2095).
        # bin[15] = height: height of the Image subarray in detector coordinates (0–2095).
        # Together they define the image_size as [width, height].
        "image_size": [bin[14], bin[15]],

        # bin[16] = xy_grb: position of the GRB/transient in unbinned detector coordinates,
        # packed as two integers in the range 0–2095.
        # The source of this position is determined by misc bit 2^28:
        #   2^28 = 1: position came from an XRT Position command
        #   2^28 = 0: position came from the Window Position in the Mode command
        "grb_position": [x_pos, y_pos],

        # misc bit 28 (grb_position_source): indicates the source of the GRB position
        # stored in bin[16] (xy_grb).
        #   1 = position came from an XRT Position command
        #   0 = position came from the Window Position in the Mode command
        "grb_position_source": grb_position_sources[misc_bits[28]],

        # bin[17] = n_frames: total number of read-out frames that went into compiling
        # this image.
        "n_frames": bin[17],

        # misc bits 2^0-3: four-bit value encoding the pixel binning of the image.
        # Decoded via the pixel_binning_values lookup dictionary.
        #   0 = 1×1 binning (no binning)
        #   1 = 2×2 binning
        #   2 = 4×4 binning
        #   3 = 8×8 binning
        #   4 = 16×16 binning
        #   5 = 32×32 binning
        #   6 = 64×64 binning
        # Values outside the defined range default to 64×64 binning.
        "pixel_binning": pixel_binning_values[pixel_binning[0]] if pixel_binning[0] in pixel_binning_values.keys() else
        pixel_binning_values[6],

        # misc bit 29 (watchdog_timeout): set if this UVOT_IMAGE notice was forced out
        # early via the watchdog timeout mechanism rather than completing normally.
        "watchdog_timeout": bool(misc_bits[29]),

        # bin[22-38] = url: filename portion of the URL pointing to the raw UVOT image
        # FITS file. The full URL is formed by prepending
        # "http://gcn.gsfc.nasa.gov/gcn/notices_s/".
        # Spans 17 longwords (68 bytes), up to 67 ASCII characters, always null-terminated.
        # In the swift.uvot.image schema this field will contain the base64-encoded
        # FITS file rather than a URL string.
        # Only populated for the raw flight notice (type=72, misc bit 2^30 = 0).
        # Set to None for the ground-processed notice (type=79, misc bit 2^30 = 1).
        #"raw_image_fits_file": f"http://gcn.gsfc.nasa.gov/gcn/notices_s/{''.join([i.decode('utf-8') for i in bin[22:39].view('c')])}" if not misc_bits[30] else None,

        # bin[22-38] = url: filename portion of the URL pointing to the ground-processed
        # UVOT image FITS file. Same URL field and encoding as raw_image_fits_file above,
        # but populated only for the ground-processed notice (type=79, misc bit 2^30 = 1).
        # Set to None for the raw flight notice (type=72, misc bit 2^30 = 0).
        #"processed_image_fits_file": f"http://gcn.gsfc.nasa.gov/gcn/notices_s/{''.join([i.decode('utf-8') for i in bin[22:39].view('c')])}" if misc_bits[30] else None,

        # just have 1 key in the dict for the image fits files regardless of raw or processed, at a higher level we
        # tell the user if this is initial or updated
        "image_fits_files": f"http://gcn.gsfc.nasa.gov/gcn/notices_s/{''.join([i.decode('utf-8') for i in bin[22:39].view('c')])}"

        # --- Fields present in the UVOT_IMAGE packet but NOT in the
        # swift.uvot.image schema ---

        # misc bits 2^4-10: height of the Detector Window used in the Blue Processing
        # Electronics. A 7-bit value packed into bits 4–10 of the misc field.
        # "detector_window_height": (bin[19] >> 4) & 0x7F,

        # misc bit 11 (pos_out_of_range): set if one or more of the RA/Dec/Roll/Theta/Phi
        # values were outside the valid range (e.g. RA > 360 deg).
        # "pos_out_of_range": bool(misc_bits[11]),

        # misc bit 12 (blk_cat_src): set if the position is in the catalog of sources
        # to be blocked (internal use only).
        # "blocked_catalog_source": bool(misc_bits[12]),

        # misc bit 13 (near_brt_star): set if the position is near a bright star
        # (magnitude < 6.5).
        # "bright_star_nearby": bool(misc_bits[13]),

        # misc bit 20 (was_subthresh): set if this was originally a SubThreshold trigger,
        # now converted to a real UVOT_IMAGE (type=72) or UVOT_PROC_IMAGE (type=79) notice.
        # "was_subthresh": bool(misc_bits[20]),

        # misc bit 21 (st_loss_lock): set if this is an image trigger AND it occurred
        # during a StarTracker Loss-of-Lock event.
        # "star_tracker_loss_of_lock": bool(misc_bits[21]),

        # misc bit 22 (uploaded_too): set if this notice was generated as a result of an
        # uploaded TOO (Target-of-Opportunity) sequence.
        # "too_sequence_uploaded": bool(misc_bits[22]),

        # misc bit 24 (sky_image_error): set if the uvot_sky_image.ps file had an error
        # during processing and does not exist.
        # NOTE: only defined for type=79 (ground-processed).
        # "sky_image_error": bool(misc_bits[24]),

        # misc bit 25 (sources_fits_error): set if the uvot_sources_image.fits file had
        # an error during processing and does not exist.
        # NOTE: only defined for type=79 (ground-processed).
        # "sources_fits_error": bool(misc_bits[25]),

        # misc bit 26 (catalog_fits_error): set if the uvot_catalog_image.fits file had
        # an error during processing and does not exist.
        # NOTE: only defined for type=79 (ground-processed).
        # "catalog_fits_error": bool(misc_bits[26]),

        # misc bit 27 (field_image_error): set if the uvot_field_image.ps file had an
        # error during processing and does not exist.
        # NOTE: only defined for type=79 (ground-processed).
        # "field_image_error": bool(misc_bits[27]),
    }

def parse(bin):
    bin[18]  # Unused. According to Docs: 'useless by the time it reaches GCN distribution'
    bin[20:22]  # Spare. According to Docs: '8 bytes for the future'

    return {**parse_uvot_image(bin)}
