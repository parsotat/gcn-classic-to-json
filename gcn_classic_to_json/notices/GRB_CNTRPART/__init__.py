import numpy as np

from ... import utils


def parse(bin):
    bin[5:7]  # Intentionally Omitted. Datetime of original trigger
    bin[
        12
    ]  # Intentionally Omitted. According to Docs: 'filter if optical or exponent of band if radio or other'
    # However in practise these notices seem to be created only for Swift-XRT and the energy is 0.3-10 keV for all text notices.
    bin[13]  # Intentionally Omitted. According to Docs: 'Seeing during the observation'

    misc_bits = np.unpackbits(bin[19:20].view(np.uint8), bitorder='little')



    spectrum = None
    unit = None
    if (misc_bits[5] == 1) and (misc_bits[6] == 0):
        spectrum = "wavelength"
        unit = "nm"
    elif (misc_bits[5] == 0) and (misc_bits[6] == 1):
        spectrum = "frequency"
        unit = "Hz"
    elif (misc_bits[5] == 1) and (misc_bits[6] == 1):
        spectrum = "energy"
        unit = "keV"

    expo_factor = np.float_power(
        10, np.packbits(np.flip(misc_bits[24:])).view(dtype="i1")
    )[0]

    trig_id = np.unpackbits(bin[18:19].view(np.uint8), bitorder='little')

    return {
        "ref_ID": [bin[4]],
        "messenger": "EM",
        "ref_type": "GRB",
        "trigger_time": utils.datetime_to_iso8601(bin[14], bin[15]),
        "ra": bin[7] * 1e-4,
        "dec": bin[8] * 1e-4,
        "ra_dec_error": bin[11] * 1e-4,
        "systematic_included": True,
        "spectrum": spectrum,
        "units": unit,
        "energy_flux": bin[9] * 1e-2 * expo_factor,
        "energy_flux_error": bin[10] * 1e-2 * expo_factor,
        "flux_energy_range": [0.3, 10] if spectrum == "energy" else None,
        "duration": bin[16] * 1e-2,
        "confidence_level": bin[17] * 1e-4,
        "ref_instrument": f"{''.join([i.decode('utf-8') for i in  bin[20:24].view('c')])}",
        "submitter_name": f"{''.join([i.decode('utf-8') for i in  bin[24:39].view('c')])}" ,
        "additional_info": "We cannot confirm whether this is the GRB or serendipitous"
        if trig_id[1]
        else "This is definitely related to GRB",
    }
