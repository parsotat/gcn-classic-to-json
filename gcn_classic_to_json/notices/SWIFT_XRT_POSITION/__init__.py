import numpy as np

from ... import utils


def parse(bin):
    bin[10]  # Spare. According to Docs: "4 bytes for the future".
    bin[22:39]  # Spare. According to Docs: "68 bytes for the future".
    bin[11]  # Intentionally Omitted. Same as bin[16] but less precise.

    amp_wave_bits = np.unpackbits(bin[17:18].view(dtype="u1"))
    wave = np.packbits(amp_wave_bits[-8:])
    amp = np.packbits(amp_wave_bits[-16:-8])

    soln_status_bits = np.flip(np.unpackbits(bin[18:19].view(dtype="u1")))

    misc_bits = np.flip(np.unpackbits(bin[19:20].view(dtype="u1")))

    return {
        "id": [bin[4]],
        "alert_type": "retraction" if soln_status_bits[5] else "initial",
        "alert_tense": "test" if soln_status_bits[30] else "current",
        "observation_start": utils.datetime_to_iso8601(bin[5], bin[6]),
        "ra": bin[7] * 1e-4,
        "dec": bin[8] * 1e-4,
        "ra_dec_error": bin[16] / 3600 * 1e-2,
        "systematic_included": True,
        "trigger_type": "image",
        "energy_flux": bin[9] * 1e-14,
        "image_snr": bin[21] * 1e-2,
        "tam_pos_1": [bin[12] * 1e-2, bin[13] * 1e-2],
        "tam_pos_2": [bin[14] * 1e-2, bin[15] * 1e-2],
        "amplifier": amp[0],
        "waveform": wave[0],
        "xrt_bat_theta": bin[20] * 1e-4,
        "cosmic_ray_possibility": bool(soln_status_bits[0]),
        "originally_subtresh": bool(soln_status_bits[14]),
        "spatial_coincidence": bool(soln_status_bits[28]),
        "temporal_coincidence": bool(soln_status_bits[29]),
        "not_real_astrophysical_peak": bool(misc_bits[10]),
        "pos_out_of_range": bool(misc_bits[11]),
        "bright_star_nearby": bool(misc_bits[13]),
        "low_xrt_bat_theta": bool(misc_bits[16]),
        "uploaded_too_sequence": bool(misc_bits[22]),
        "updated_position": bool(misc_bits[25]),
    }
