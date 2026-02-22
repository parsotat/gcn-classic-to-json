# SWIFT_XRT_IMAGE / SWIFT_XRT_IMAGE_PROC — GCN Socket Packet Definition

**Packet Types:**
- `69` = `SWIFT_XRT_IMAGE` — raw flight image
- `78` = `SWIFT_XRT_IMAGE_PROC` — ground-processed image

**Related types:** `67` = `SWIFT_XRT_POS`, `68` = `SWIFT_XRT_SPEC`, `70` = `SWIFT_XRT_LC`, `71` = `SWIFT_XRT_NACK_POS`
**GCN Schema:** `swift.xrt.image` (covers both raw and processed subtypes)

> **Note:** Types `69` and `78` share an **identical packet word layout**. The only structural
> differences are the `pkt_type` value in `bin[0]`, the state of `misc` bit $$2^{30}$$,
> which is always `0` for the raw flight form (type=69) and always `1` for the
> ground-processed form (type=78), and `misc` bit $$2^{24}$$, which is not assigned
> for type=69 but indicates a processing error in the ground-processed image FITS
> file for type=78.

---

## Packet Word Layout

The packet consists of 40 four-byte (`long`) words, indexed `bin[0]`–`bin[39]`.
This layout applies to **both** type=69 and type=78.

| Index | Item Name          | Units             | Description |
|-------|--------------------|-------------------|-------------|
| 0     | `pkt_type`         | integer           | Packet type number (`69` = raw, `78` = processed) |
| 1     | `pkt_sernum`       | integer           | Serial number for this packet type; starts at 1 |
| 2     | `pkt_hop_cnt`      | integer           | Incremented by each network node the packet passes through |
| 3     | `pkt_sod`          | centi-sec         | UT seconds-of-day when the packet was sent from GCN; `int(sssss.sss × 100)` |
| 4     | `trig_obs_num`     | integers (packed) | Lower 24 bits = Trigger number; upper 8 bits = Observation number |
| 5     | `ImgStart_tjd`     | days              | Truncated Julian Day of the start of the CCD image integration |
| 6     | `ImgStart_sod`     | centi-sec         | UT seconds-of-day of the image start; `int(sssss.sss × 100)` |
| 7     | `burst_ra`         | 0.0001-deg        | RA of the centroid of the source found in the image (J2000); `int(0.0–359.9999 × 10000)` |
| 8     | `burst_dec`        | 0.0001-deg        | Dec of the centroid of the source found in the image (J2000); `int(−90.0–+90.0 × 10000)` |
| 9     | `n_bright_pix`     | integer           | Number of pixels above the detection threshold in the XRT image |
| 10    | *(spare)*          | —                 | Reserved |
| 11    | `centroid_std_dev` | 0.0001-deg        | Standard deviation of the centroid position; `int(value × 10000)` |
| 12    | `cent_x`           | centi-pixels      | x-coordinate of source centroid in image; `int(pixels × 100)` |
| 13    | `cent_y`           | centi-pixels      | y-coordinate of source centroid in image; `int(pixels × 100)` |
| 14    | `iraw_x`           | centi-pixels      | x-coordinate of the center of the 51×51 pixel postage stamp in CCD coordinates; `int(pixels × 100)` |
| 15    | `iraw_y`           | centi-pixels      | y-coordinate of the postage stamp center; `int(pixels × 100)` |
| 16    | `roll`             | 0.0001-deg        | Spacecraft roll angle; `int(−180.0–+180.0 × 10000)` |
| 17    | `gain/mod/wav`     | integer (packed)  | Amplifier gain, CCD readout mode, and waveform ID packed into one word |
| 18    | `expo_time`        | centi-sec         | CCD integration (exposure) time; `int(sssss.sss × 100)` |
| 19    | `misc`             | bits              | Miscellaneous flag bits (see [misc bits](#misc-bits)) |
| 20    | `grb_in_xrt_y`     | centi-pixels      | GRB afterglow y-coordinate (row) in XRT CCD coordinates; `int(pixels × 100)` |
| 21    | `grb_in_xrt_z`     | centi-pixels      | GRB afterglow z-coordinate (column) in XRT CCD coordinates; `int(pixels × 100)` |
| 22–38 | `url[17]`         | chars             | Filename portion of the image FITS file URL (up to 67 chars, null-terminated) |
| 39    | `pkt_term`         | integer           | Packet termination character (ASCII newline, decimal 10) |

---

## gain/mod/wav Encoding

`bin[17]` is a packed 32-bit word containing three sub-fields decoded externally.

| Sub-field | Description | Values |
|-----------|-------------|--------|
| Amplifier gain | Multiplicative gain factor applied to the CCD readout | `1`, `2`, `4`, `8`, `16` |
| CCD readout mode | Operational mode of the XRT CCD (see [CCD readout modes](#ccd-readout-modes)) | `1`–`10` |
| Waveform ID | CCD waveform identifier | `50` or `60` |

---

## CCD Readout Modes

Decoded from `bin[17]` (`gain/mod/wav`).

| Value | Description |
|-------|-------------|
| `1`   | Null |
| `2`   | Short image |
| `3`   | Long image |
| `4`   | Piled-up Photodiode |
| `5`   | Low Rate Photodiode (LRPD) |
| `6`   | Windowed Timing (WT) |
| `7`   | Photo-counting (PC) |
| `8`   | Raw data |
| `9`   | Bias map |
| `10`  | Stop |

---

## misc Bits

Stored in `bin[19]`. All bit definitions apply equally to both type=69 and type=78, with the
exception of $$2^{24}$$ and $$2^{30}$$ which are only meaningful for the ground-processed
form (type=78).

| Bit | Type=69 | Type=78 | Description |
|-----|---------|---------|-------------|
| $$2^{0}$$–$$2^{9}$$ | Not assigned | Not assigned | Spare |
| $$2^{10}$$ | ✓ | ✓ | `1` = the detected peak is not a real astrophysical source peak (e.g. readout artifact or hot pixel) |
| $$2^{11}$$ | ✓ | ✓ | `1` = one or more of the RA/Dec/Roll/Theta/Phi values were out of valid range (e.g. RA = 361°) |
| $$2^{12}$$ | Not assigned | Not assigned | Spare |
| $$2^{13}$$ | ✓ | ✓ | `1` = there is a nearby bright star (magnitude < 6.5) |
| $$2^{14}$$–$$2^{19}$$ | Not assigned | Not assigned | Spare |
| $$2^{20}$$ | ✓ | ✓ | `1` = this was originally a SubThreshold trigger, now promoted to a real `XRT_IMAGE` |
| $$2^{21}$$ | ✓ | ✓ | `1` = image trigger occurred during a StarTracker Loss-of-Lock event |
| $$2^{22}$$ | ✓ | ✓ | `1` = notice generated as a result of an uploaded TOO (Target-of-Opportunity) sequence |
| $$2^{23}$$ | Not assigned | Not assigned | Spare |
| $$2^{24}$$ | Not assigned | ✓ | `1` = the `xrt_proc_image.fits` file had an error in processing and does not exist *(type=78 only)* |
| $$2^{25}$$ | ✓ | ✓ | `1` = notice was generated with the 3rd of 3 telemetry packets missing |
| $$2^{26}$$ | ✓ | ✓ | `1` = notice was generated with the 2nd of 3 telemetry packets missing |
| $$2^{27}$$ | ✓ | ✓ | `1` = notice was generated with the 1st of 3 telemetry packets missing |
| $$2^{28}$$ | Not assigned | Not assigned | Spare |
| $$2^{29}$$ | ✓ | ✓ | `1` = this `XRT_IMAGE` notice was forced out via the watchdog timeout |
| $$2^{30}$$ | Always `0` | Always `1` | `0` = flight-generated (type=69); `1` = ground-generated (type=78) |
| $$2^{31}$$ | ✓ | ✓ | `1` = CRC error detected in one or more telemetry packets used to build this notice |

---

## Differences Between Type=69 and Type=78

| Property | `SWIFT_XRT_IMAGE` (type=69) | `SWIFT_XRT_IMAGE_PROC` (type=78) |
|----------|-----------------------------|-----------------------------------|
| `bin[0]` `pkt_type` | `69` | `78` |
| `misc` $$2^{24}$$ | Not assigned | `1` = `xrt_proc_image.fits` had a processing error and does not exist |
| `misc` $$2^{30}$$ | Always `0` | Always `1` |
| Origin | Raw flight telemetry | Ground-reprocessed image |
| Packet word layout | Identical | Identical |

---

## Value Conversions

| Field              | Raw Unit     | Conversion | Output Unit |
|--------------------|--------------|------------|-------------|
| `burst_ra`         | 0.0001-deg   | `× 1e-4`   | degrees     |
| `burst_dec`        | 0.0001-deg   | `× 1e-4`   | degrees     |
| `roll`             | 0.0001-deg   | `× 1e-4`   | degrees     |
| `expo_time`        | centi-sec    | `× 1e-2`   | seconds     |
| `centroid_std_dev` | 0.0001-deg   | `× 1e-4`   | degrees     |
| `cent_x/y`         | centi-pixels | `× 1e-2`   | pixels      |
| `iraw_x/y`         | centi-pixels | `× 1e-2`   | pixels      |
| `grb_in_xrt_y/z`   | centi-pixels | `× 1e-2`   | pixels      |
| `ImgStart_sod`     | centi-sec    | passed to `datetime_to_iso8601` | ISO 8601 |

---

## swift.xrt.image JSON Schema Fields

Defined in the GCN JSON schema document for `swift.xrt.image` (covers both raw and processed subtypes):

| Field                   | Type / Example                                                                                                                                                              | Source |
|-------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|
| `alert_datetime`        | ISO 8601 string                                                                                                                                                             | GCN metadata |
| `alert_tense`           | `"current"` or `"test"`                                                                                                                                                     | GCN metadata |
| `alert_type`            | `"initial"` or `"update"`                                                                                                                                                   | GCN metadata |
| `mission`               | `"Swift"`                                                                                                                                                                   | Fixed constant |
| `instrument`            | `"XRT"`                                                                                                                                                                     | Fixed constant |
| `id`                    | integer trigger ID                                                                                                                                                          | `bin[4]` lower 24 bits |
| `ra`                    | float (degrees), source centroid                                                                                                                                            | `bin[7] × 1e-4` |
| `dec`                   | float (degrees), source centroid                                                                                                                                            | `bin[8] × 1e-4` |
| `pointing_roll`         | float (degrees)                                                                                                                                                             | `bin[16] × 1e-4` |
| `observation_start`     | ISO 8601 datetime string                                                                                                                                                    | `bin[5]`, `bin[6]` |
| `observation_livetime`  | float (seconds)                                                                                                                                                             | `bin[18] × 1e-2` |
| `ccd_readout_mode`      | `"Null"`, `"Short image"`, `"Long image"`, `"Piled-up Photodiode"`, `"Low Rate Photodiode"`, `"Windowed Timing"`, `"Photo-counting"`, `"Raw data"`, `"Bias map"`, `"Stop"` | `bin[17]` decoded |
| `ccd_waveform_id`       | integer (`50` or `60`)                                                                                                                                                      | `bin[17]` decoded |
| `amplifier_gain`        | integer (`1`, `2`, `4`, `8`, `16`)                                                                                                                                          | `bin[17]` decoded |
| `bright_pixels`         | integer, e.g. `51`                                                                                                                                                          | `bin[9]` |
| `centroid_std_dev`      | float (degrees)                                                                                                                                                             | `bin[11] × 1e-4` |
| `centroid_position`     | `[x, y]` (pixels)                                                                                                                                                          | `bin[12–13] × 1e-2` |
| `centroid_ccd_position` | `[x, y]` (pixels)                                                                                                                                                          | `bin[14–15] × 1e-2` |
| `grb_xrt_coordinates`   | `[y, z]` (pixels)                                                                                                                                                          | `bin[20–21] × 1e-2` |
| `watchdog_timeout`      | bool                                                                                                                                                                        | `misc` $$2^{29}$$ |
| `subtype`               | `"FLIGHT"` or `"PROCESSED"`                                                                                                                                                 | `misc` $$2^{30}$$ |
| `image_fits_file`       | base64-encoded FITS file                                                                                                                                                    | `bin[22–38]` URL string |