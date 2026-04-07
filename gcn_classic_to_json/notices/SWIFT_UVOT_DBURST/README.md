# SWIFT_UVOT_IMAGE / SWIFT_UVOT_IMAGE_PROC — GCN Socket Packet Definition

**Packet Types:**
- `72` = `SWIFT_UVOT_IMAGE` — raw flight UVOT image (aka DarkBurst, aka Genie)
- `79` = `SWIFT_UVOT_IMAGE_PROC` — ground-processed UVOT image

**Related types:** `73` = `SWIFT_UVOT_SRCLIST`, `80` = `SWIFT_UVOT_SRCLIST_PROC`, `81` = `SWIFT_UVOT_POSITION`
**GCN Schema:** `swift.uvot.image` (covers both raw and processed subtypes)

> **Note:** Types `72` and `79` share an **identical packet word layout**. The only structural
> differences are the `pkt_type` value in `bin[0]` and the state of `misc` bit $$2^{30}$$,
> which is always `0` for the raw flight form (type=72) and always `1` for the
> ground-processed form (type=79). The `bin[22–38]` URL field points to the raw image FITS
> file in type=72 packets and to the ground-processed image FITS file in type=79 packets.
> Several `misc` bits ($$2^{20}$$, $$2^{24}$$–$$2^{27}$$) have subtly different meanings
> between the two packet types.

---

## Packet Word Layout

The packet consists of 40 four-byte (`long`) words, indexed `bin[0]`–`bin[39]`.
This layout applies to **both** type=72 and type=79.

| Index | Item Name       | Units             | Description |
|-------|-----------------|-------------------|-------------|
| 0     | `pkt_type`      | integer           | Packet type number (`72` = raw, `79` = processed) |
| 1     | `pkt_sernum`    | integer           | Serial number for this packet type; starts at 1 |
| 2     | `pkt_hop_cnt`   | integer           | Incremented by each network node the packet passes through |
| 3     | `pkt_sod`       | centi-sec         | UT seconds-of-day when the packet was sent from GCN; `int(sssss.sss × 100)` |
| 4     | `trig_obs_num`  | integers (packed) | Lower 24 bits = Trigger number; upper 8 bits = Observation number |
| 5     | `ExpStart_tjd`  | days              | Truncated Julian Day of the start of the UVOT CCD integration |
| 6     | `ExpStart_sod`  | centi-sec         | UT seconds-of-day of the start of the CCD integration; `int(sssss.sss × 100)` |
| 7     | `point_ra`      | 0.0001-deg        | RA of the spacecraft pointing direction at the start/stop of the integration interval (J2000); `int(0.0–359.9999 × 10000)` |
| 8     | `point_dec`     | 0.0001-deg        | Dec of the spacecraft pointing direction (J2000); `int(−90.0–+90.0 × 10000)` |
| 9     | `image_roll`    | 0.0001-deg        | Roll angle of the target; `int(0.0–359.9999 × 10000)` |
| 10    | `filter`        | integer           | Filter identifier (see [filter values](#filter-values)) |
| 11    | `expo_id`       | seconds           | Exposure ID expressed in spacecraft seconds |
| 12    | `X0`            | det-coords        | X coordinate of pixel_zero (origin) of the Image subarray (0–2095) |
| 13    | `Y0`            | det-coords        | Y coordinate of pixel_zero (origin) of the Image subarray (0–2095) |
| 14    | `width`         | det-coords        | Width of the Image subarray (0–2095) |
| 15    | `height`        | det-coords        | Height of the Image subarray (0–2095) |
| 16    | `xy_grb`        | det-coords (packed) | Position of the GRB/transient in unbinned detector coordinates (0–2095), packed as two integers. Source indicated by `misc` $$2^{28}$$ |
| 17    | `n_frames`      | integer           | Total number of read-out frames that went into compiling this image |
| 18    | `swl_lwl`       | integers (packed) | Short-word and long-word lengths used in compression of the as-transmitted image packet; no compression is applied in the GCN-distributed version — these values are essentially unused |
| 19    | `misc`          | bits              | Miscellaneous flag bits (see [misc bits](#misc-bits)) |
| 20–21 | *(spare)*      | —                 | Reserved |
| 22–38 | `url[17]`      | chars             | Filename portion of the UVOT image FITS file URL (up to 67 chars, null-terminated). Points to the **raw** image FITS file for type=72 and the **ground-processed** image FITS file for type=79 |
| 39    | `pkt_term`      | integer           | Packet termination character (ASCII newline, decimal 10) |

---

## Filter Values

Decoded from `bin[10]`.

| Value | Filter     |
|-------|------------|
| `0`   | Blocked    |
| `1`   | UV_Grism   |
| `2`   | UVW2       |
| `3`   | V          |
| `4`   | UVM2       |
| `5`   | Vis_Grism  |
| `6`   | UVW1       |
| `7`   | U          |
| `8`   | Magnifier  |
| `9`   | B          |
| `10`  | White      |
| `11`  | unknown    |

---

## Pixel Binning Values

Decoded from `misc` bits $$2^{0}$$–$$2^{3}$$ (4-bit value).

| Value | Binning |
|-------|---------|
| `0`   | 1×1 (no binning) |
| `1`   | 2×2 |
| `2`   | 4×4 |
| `3`   | 8×8 |
| `4`   | 16×16 |
| `5`   | 32×32 |
| `6`   | 64×64 |

---

## misc Bits

Stored in `bin[19]`. All bit definitions apply equally to both type=72 and type=79 unless
otherwise noted.

| Bit | Type=72 | Type=79 | Description |
|-----|---------|---------|-------------|
| $$2^{0}$$–$$2^{3}$$ | ✓ | ✓ | 4-bit value encoding the pixel binning (see [pixel binning values](#pixel-binning-values)) |
| $$2^{4}$$–$$2^{10}$$ | ✓ | ✓ | 7-bit value encoding the height of the Detector Window used in the Blue Processing Electronics |
| $$2^{11}$$ | ✓ | ✓ | `1` = one or more of the RA/Dec/Roll/Theta/Phi values were out of valid range (e.g. RA = 361°) |
| $$2^{12}$$ | ✓ | ✓ | `1` = position is in the catalog of sources to be blocked (internal use only) |
| $$2^{13}$$ | ✓ | ✓ | `1` = position is near a bright star (magnitude < 6.5) |
| $$2^{14}$$–$$2^{19}$$ | Not assigned | Not assigned | Spare |
| $$2^{20}$$ | ✓ | ✓ | `1` = this was originally a SubThreshold trigger, now converted to a real `UVOT_IMAGE` (type=72) or `UVOT_PROC_IMAGE` (type=79) notice |
| $$2^{21}$$ | ✓ | ✓ | `1` = image trigger occurred during a StarTracker Loss-of-Lock event |
| $$2^{22}$$ | ✓ | ✓ | `1` = notice generated as a result of an uploaded TOO (Target-of-Opportunity) sequence |
| $$2^{23}$$ | Not assigned | Not assigned | Spare |
| $$2^{24}$$ | Not assigned | ✓ | `1` = the `uvot_sky_image.ps` file had a processing error and does not exist (type=79 only) |
| $$2^{25}$$ | Not assigned | ✓ | `1` = the `uvot_sources_image.fits` file had a processing error and does not exist (type=79 only) |
| $$2^{26}$$ | Not assigned | ✓ | `1` = the `uvot_catalog_image.fits` file had a processing error and does not exist (type=79 only) |
| $$2^{27}$$ | Not assigned | ✓ | `1` = the `uvot_field_image.ps` file had a processing error and does not exist (type=79 only) |
| $$2^{28}$$ | ✓ | ✓ | GRB position source: `1` = position from XRT Position command; `0` = position from Window Position in the Mode command |
| $$2^{29}$$ | ✓ | ✓ | `1` = this `UVOT_IMAGE` notice was forced out via the watchdog timeout |
| $$2^{30}$$ | Always `0` | Always `1` | `0` = flight-generated (type=72); `1` = ground-generated (type=79) |
| $$2^{31}$$ | ✓ | ✓ | `1` = CRC error detected in one or more telemetry packets |

---

## Differences Between Type=72 and Type=79

| Property | `SWIFT_UVOT_IMAGE` (type=72) | `SWIFT_UVOT_IMAGE_PROC` (type=79) |
|----------|------------------------------|-----------------------------------|
| `bin[0]` `pkt_type` | `72` | `79` |
| `misc` $$2^{30}$$ | Always `0` | Always `1` |
| `misc` $$2^{24}$$–$$2^{27}$$ | Not assigned | Processing error flags for output files |
| `bin[22–38]` URL | Raw image FITS file | Ground-processed image FITS file |
| `alert_type` | `"initial"` | `"update"` |
| `raw_image_fits_file` | Populated from `bin[22–38]` | `None` |
| `processed_image_fits_file` | `None` | Populated from `bin[22–38]` |
| Origin | Raw flight telemetry | Ground-reprocessed image |
| Packet word layout | Identical | Identical |

---

## Value Conversions

| Field           | Raw Unit   | Conversion | Output Unit |
|-----------------|------------|------------|-------------|
| `point_ra`      | 0.0001-deg | `× 1e-4`   | degrees     |
| `point_dec`     | 0.0001-deg | `× 1e-4`   | degrees     |
| `image_roll`    | 0.0001-deg | `× 1e-4`   | degrees     |
| `ExpStart_sod`  | centi-sec  | passed to `datetime_to_iso8601` | ISO 8601 |

---

## swift.uvot.image JSON Schema Fields

> **Note:** A dedicated `swift.uvot.image` schema page is not returned by the schema document
> search. The fields below are inferred from the packet definition, the schema listing
> \ue202turn0file3, and by analogy with the closely related `swift.uvot.source_list` schema.

| Field                   | Type / Example                      | Source                                                             | Notes |
|-------------------------|-------------------------------------|--------------------------------------------------------------------|-------|
| `alert_datetime`        | ISO 8601 string                     | GCN metadata                                                       | |
| `alert_tense`           | `"current"` or `"test"`             | GCN metadata                                                       | |
| `alert_type`            | `"initial"` or `"update"`           | `misc` $$2^{30}$$: `"initial"` for type=72; `"update"` for type=79 | |
| `mission`               | `"Swift"`                           | Fixed constant                                                     | |
| `instrument`            | `"UVOT"`                            | Fixed constant                                                     | |
| `id`                    | integer trigger ID                  | `bin[4]` lower 24 bits                                             | |
| `observation_start`     | ISO 8601 datetime string            | `bin[5]` (`ExpStart_tjd`), `bin[6]` (`ExpStart_sod`)               | |
| `ra_pointing`           | float (degrees)                     | `bin[7] × 1e-4`                                                    | Spacecraft pointing direction RA (J2000) |
| `dec_pointing`          | float (degrees)                     | `bin[8] × 1e-4`                                                    | Spacecraft pointing direction Dec (J2000) |
| `roll`                  | float (degrees)                     | `bin[9] × 1e-4`                                                    | |
| `filter`                | string, e.g. `"White"`              | `filters[bin[10]]`                                                 | |
| `exposure_id`           | integer (spacecraft seconds)        | `bin[11]`                                                          | |
| `image_offset`          | `[X0, Y0]` (det-coords)             | `[bin[12], bin[13]]`                                               | Coordinates of pixel_zero in the Image subarray |
| `image_size`            | `[width, height]` (det-coords)      | `[bin[14], bin[15]]`                                               | Dimensions of the Image subarray |
| `grb_position`          | `[x_pos, y_pos]` (det-coords)       | decoded from `bin[16]` (`xy_grb`, two packed integers)             | Position in unbinned detector coordinates |
| `grb_position_source`   | string                              | `grb_position_sources[misc_bits[28]]`                              | `"XRT_position"` or `"window_position"` |
| `n_frames`              | integer                             | `bin[17]`                                                          | Total read-out frames in this image |
| `pixel_binning`         | string, e.g. `"2x2"`               | decoded from `misc` bits $$2^{0}$$–$$2^{3}$$                       | |
| `watchdog_timeout`      | bool                                | `misc` $$2^{29}$$                                                  | |
| `image_fits_file`       | base64-encoded FITS file or `None`  | `bin[22–38]` URL string for both the raw and processed fits files  | |
