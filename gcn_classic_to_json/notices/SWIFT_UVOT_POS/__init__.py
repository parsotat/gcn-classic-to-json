import numpy as np

from ... import utils

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
    "Unknown",
]


def parse(bin):
    bin[11]  # Unused. According to Docs: 'ra_dec_error, but less precise'
    bin[12:16]  # Spare. According to Docs: '16 bytes for the future'
    bin[17]  # Spare. According to Docs: '4 bytes for the future'
    bin[
        21
    ]  # Unused. According to Docs : 'angular distance between XRT and UVOT but set to 0'
    bin[22:39]  # Spare. According to Docs: '68 bytes for the future'

    soln_status = np.unpackbits(bin[18:19].view(np.uint8), bitorder='little')


    misc_status = np.unpackbits(bin[19:20].view(np.uint8), bitorder='little')

    return {
        # Fixed string constant identifying the mission. Listed explicitly as a schema field
        # in swift.uvot.position with the value "Swift".
        "mission": "SWIFT",

        # Fixed string constant identifying the instrument. Listed explicitly as a schema field
        # in swift.uvot.position with the value "UVOT".
        "instrument": "UVOT",

        # bin[4] = trig_obs_num: lower 24 bits = Trigger number, upper 8 bits = Observation number.
        # Assigned by the on-board BAT flight software to uniquely identify each trigger.
        "id": [bin[4]],

        # soln_status bit 30 (test_submit): set if this is a test submission;
        # unset for real current notices.
        "alert_tense": "test" if soln_status[30] else "current",

        # soln_status bit 5 (def_not_grb): ground-assigned flag indicating the event is
        # definitively NOT a GRB — i.e. this is a retraction notice.
        # NOTE: the swift.uvot.position schema lists ["initial", "update"] as possible
        # values, but def_not_grb is a retraction flag so "retraction" is used here
        # for consistency with other BAT/XRT schema implementations.
        "alert_type": "retraction" if soln_status[5] else "initial",

        # bin[5] = burst_tjd: Truncated Julian Day of the Swift-UVOT data.
        # bin[6] = burst_sod: UT seconds-of-day of the Swift-UVOT data, in centi-seconds
        #   (fl.pt. seconds * 100, then integerized).
        # Combined and converted to an ISO 8601 datetime string.
        # Used as observation_start since it represents the time of the UVOT observation.
        "observation_start": utils.datetime_to_iso8601(bin[5], bin[6]),

        # bin[7] = burst_ra: RA of the burst/afterglow as determined by the UVOT ground
        # software (J2000 epoch). Stored in units of 0.0001-deg (fl.pt. degrees * 10000).
        # Divide by 10000 to recover degrees.
        "ra": bin[7] * 1e-4,

        # bin[8] = burst_dec: Dec of the burst/afterglow (J2000 epoch).
        # Same encoding as burst_ra. Divide by 10000 to recover degrees.
        "dec": bin[8] * 1e-4,

        # bin[16] = hi_prec_err: high-precision 90%-containment position error radius.
        # Stored in units of centi-arcsec to remove the 0.36 arcsec quantization error
        # introduced by the regular burst_error (bin[11]) field.
        # Includes both statistical and systematic contributions.
        # Conversion: centi-arcsec → degrees = value / 360000 = value * 1e-4 / 36.
        # NOTE: the swift.uvot.position schema example shows systematic_included: False,
        # but the hi_prec_err field explicitly includes systematic contributions.
        # systematic_included is set to True here to reflect the packet definition.
        "ra_dec_error": bin[16] * 1e-4 / 36,
        "systematic_included": True,

        # bin[9] = burst_mag: magnitude of the burst/afterglow in the specified filter.
        # Stored in centi-mag (fl.pt. magnitude * 100, then integerized).
        # Divide by 100 to recover magnitude.
        "mag": bin[9] * 1e-2,

        # bin[20] = mag_error: uncertainty in the magnitude value (in the specified filter).
        # Stored in centi-mag (fl.pt. mag_error * 100, then integerized).
        # Divide by 100 to recover magnitude error.
        "mag_error": bin[20] * 1e-2,

        #added system info to the json
        "mag_system": "Vega"

        # bin[10] = filter: integer identifier of the UVOT filter used for the observation.
        # Decoded via the filters lookup dictionary.
        # Filter values:
        #   0=Blocked, 1=UV_Grism, 2=UVW2, 3=V, 4=UVM2, 5=Vis_Grism,
        #   6=UVW1, 7=U, 8=Magnifier, 9=B, 10=White, 11=unknown
        "filter": [filters[bin[10]]],

        # bin[21] = uvot-xrt: angular distance between the UVOT position and the XRT
        # position. Stored in units of 0.0001-deg (fl.pt. degrees * 10000, then integerized).
        # Divide by 10000 to recover degrees.
        "uvot_xrt_distance": bin[21] * 1e-4,

        # --- Fields present in the SWIFT_UVOT_POS packet but NOT in the
        # swift.uvot.position schema ---

        # soln_status bit 0 (point_src): set if a point source was found;
        # unset if it is an extended source.
        # "point_source": bool(soln_status[0]),

        # soln_status bit 1 (grb): set if the source is classified as a GRB.
        # "grb": bool(soln_status[1]),

        # soln_status bit 3 (catalog_src): set if the source is in the on-board catalog.
        # "catalog_source": bool(soln_status[3]),

        # soln_status bit 8 (gnd_cat_src): ground-assigned flag; set if the BAT position
        # is in the BAT ground catalog.
        # "ground_catalog_source": bool(soln_status[8]),

        # soln_status bit 28 (spatial_coinc): ground-assigned flag; set if there was a
        # spatial coincidence with another event.
        # "spatial_coincidence": bool(soln_status[28]),

        # soln_status bit 29 (temporal_coinc): ground-assigned flag; set if there was a
        # temporal coincidence with another event.
        # "temporal_coincidence": bool(soln_status[29]),

        # misc bit 13 (near_brt_star): set if the UVOT position is near a bright star
        # (magnitude < 6.5).
        # "bright_star_nearby": bool(misc_status[13]),

        # misc bit 25 (updated_position): set if this notice changes/improves the position
        # specified in the original UVOT_Position notice.
        # "updated_position": bool(misc_status[25]),

        # misc bit 30 (ground_generated): set if this notice was ground-generated;
        # unset if flight-generated.
        # "ground_generated": bool(misc_status[30]),
    }