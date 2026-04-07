# SWIFT_UVOT_SRCLIST / SWIFT_UVOT_SRCLIST_PROC — GCN Socket Packet Definition

**Packet Types:**
- `73` = `SWIFT_UVOT_SRCLIST` — raw flight UVOT source list
- `80` = `SWIFT_UVOT_SRCLIST_PROC` — ground-processed UVOT source list

**Related types:** `72` = `SWIFT_UVOT_IMAGE`, `79` = `SWIFT_UVOT_IMAGE_PROC`, `81` = `SWIFT_UVOT_POSITION`
**GCN Schema:** `swift.uvot.source_list` (covers both raw and processed subtypes)

> **Note:** Types `73` and `80` share an **identical packet word layout**. The only structural
> differences are the `pkt_type` value in `bin[0]` and the state of `misc` bit $$2^{30}$$,
> which is always `0` for the raw flight form (type=73) and always `1` for the
> ground-processed form (type=80). The `bin[22–38]` URL field points to the raw source list
> FITS file in type=73 packets and to the ground-processed source list FITS file in type=80
> packets. Several `misc` bits ($$2^{20}$$, $$2^{24}$$–$$2^{27}$$) are only assigned for
> the ground-processed form (type=80).

---

## Packet Word Layout

The packet consists of 40 four-byte (`long`) words, indexed `bin[0]`–`bin[39]`.
This layout applies to **both** type=73 and type=80.

| Index | Item Name        | Units             | Description |
|-------|------------------|-------------------|-------------|
| 0     | `pkt_type`       | integer           | Packet type number (`73` = raw, `80` = processed) |
| 1     | `pkt_sernum`     | integer           | Serial number for this packet type; starts at 1 |
| 2     | `pkt_hop_cnt`    | integer           | Incremented by each network node the packet passes through |
| 3     | `pkt_sod`        | centi-sec         | UT seconds-of-day when the packet was sent from GCN; `int(sssss.sss × 100)` |
| 4     | `trig_obs_num`   | integers (packed) | Lower 24 bits = Trigger number; upper 8 bits = Observation number |
| 5     | `expo_start_tjd` | days              | Truncated Julian Day of the start of the UVOT CCD exposure integration |
| 6     | `expo_start_sod` | centi-sec         | UT seconds-of-day of the exposure start; `int(sssss.sss × 100)` |
| 7     | `point_ra`       | 0.0001-deg        | RA of the spacecraft pointing direction at the start/stop of the integration interval (J2000); `int(0.0–359.9999 × 10000)` |
| 8     | `point_dec`      | 0.0001-deg        | Dec of the spacecraft pointing direction (J2000); `int(−90.0–+90.0 × 10000)` |
| 9     | `image_roll`     | 0.0001-deg        | Roll angle of the target; `int(0.0–359.9999 × 10000)` |
| 10    | `filter`         | integer           | Filter identifier (see [filter values](#filter-values)) |
| 11    | `bkg_mean`       | 0.001 units       | Mean value of the background level in the exposure; `int(value × 1000)` |
| 12    | `x_max`          | det-coords        | Maximum extent of the image window in X direction (0–2095) |
| 13    | `y_max`          | det-coords        | Maximum extent of the image window in Y direction (0–2095) |
| 14    | `n_stars`        | integer           | Total number of stars (sources) found in the source list |
| 15    | `x_offset`       | det-coords        | X offset of the image window origin in detector coordinates (0–2095) |
| 16    | `y_offset`       | det-coords        | Y offset of the image window origin in detector coordinates (0–2095) |
| 17    | `det_thresh`     | DN                | Detection threshold used in this exposure (digital number units) |
| 18    | `photo_thresh`   | DN                | Photometry threshold used in this exposure (digital number units) |
| 19    | `misc`           | bits              | Miscellaneous flag bits (see [misc bits](#misc-bits)) |
| 20–21 | *(spare)*       | —                 | Reserved |
| 22–38 | `url[17]`       | chars             | Filename portion of the source list FITS file URL (up to 67 chars, null-terminated). Points to the **raw** source list FITS file for type=73 and the **ground-processed** source list FITS file for type=80 |
| 39    | `pkt_term`       | integer           | Packet termination character (ASCII newline, decimal 10) |

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

## misc Bits

Stored in `bin[19]`. All bit definitions apply equally to both type=73 and type=80 unless
otherwise noted.

| Bit | Type=73 | Type=80 | Description |
|-----|---------|---------|-------------|
| $$2^{0}$$–$$2^{10}$$ | Not assigned | Not assigned | Spare |
| $$2^{11}$$ | ✓ | ✓ | `1` = one or more of the RA/Dec/Roll/Theta/Phi values were out of valid range (e.g. RA = 361°) |
| $$2^{12}$$ | ✓ | ✓ | `1` = position is in the catalog of sources to be blocked (internal use only) |
| $$2^{13}$$ | ✓ | ✓ | `1` = position is near a bright star (magnitude < 6.5) |
| $$2^{14}$$–$$2^{19}$$ | Not assigned | Not assigned | Spare |
| $$2^{20}$$ | Not assigned | ✓ | `1` = this was originally a SubThreshold trigger, now converted to a real `UVOT_PROC_SL` notice (type=80 only) |
| $$2^{21}$$ | ✓ | ✓ | `1` = image trigger occurred during a StarTracker Loss-of-Lock event |
| $$2^{22}$$ | ✓ | ✓ | `1` = notice generated as a result of an uploaded TOO (Target-of-Opportunity) sequence |
| $$2^{23}$$ | Not assigned | Not assigned | Spare |
| $$2^{24}$$ | Not assigned | ✓ | `1` = the `uvot_sky_srclist.ps` file had a processing error and does not exist (type=80 only) |
| $$2^{25}$$ | Not assigned | ✓ | `1` = the `uvot_sources_srclist.fits` file had a processing error and does not exist (type=80 only) |
| $$2^{26}$$ | Not assigned | ✓ | `1` = the `uvot_catalog_srclist.fits` file had a processing error and does not exist (type=80 only) |
| $$2^{27}$$ | Not assigned | ✓ | `1` = the `uvot_field_srclist.ps` file had a processing error and does not exist (type=80 only) |
| $$2^{28}$$ | Not assigned | Not assigned | Spare |
| $$2^{29}$$ | ✓ | ✓ | `1` = this `UVOT_SRCLIST` notice was forced out via the watchdog timeout |
| $$2^{30}$$ | Always `0` | Always `1` | `0` = flight-generated (type=73); `1` = ground-generated (type=80) |
| $$2^{31}$$ | ✓ | ✓ | `1` = CRC error detected in one or more telemetry packets |

---

## Differences Between Type=73 and Type=80

| Property | `SWIFT_UVOT_SRCLIST` (type=73) | `SWIFT_UVOT_SRCLIST_PROC` (type=80) |
|----------|--------------------------------|--------------------------------------|
| `bin[0]` `pkt_type` | `73` | `80` |
| `misc` $$2^{30}$$ | Always `0` | Always `1` |
| `misc` $$2^{20}$$ | Not assigned | SubThreshold conversion flag |
| `misc` $$2^{24}$$–$$2^{27}$$ | Not assigned | Processing error flags for output files |
| `bin[22–38]` URL | Raw source list FITS file | Ground-processed source list FITS file |
| `alert_type` | `"initial"` | `"update"` |
| `raw_source_list_fits_file` | Populated from `bin[22–38]` | `None` |
| `processed_source_list_fits_files` | `None` | Populated from `bin[22–38]` |
| Origin | Raw flight telemetry | Ground-reprocessed source list |
| Packet word layout | Identical | Identical |

---

## Value Conversions

| Field              | Raw Unit    | Conversion | Output Unit |
|--------------------|-------------|------------|-------------|
| `point_ra`         | 0.0001-deg  | `× 1e-4`   | degrees     |
| `point_dec`        | 0.0001-deg  | `× 1e-4`   | degrees     |
| `image_roll`       | 0.0001-deg  | `× 1e-4`   | degrees     |
| `bkg_mean`         | 0.001 units | `× 1e-3`   | float       |
| `expo_start_sod`   | centi-sec   | passed to `datetime_to_iso8601` | ISO 8601 |

---

## swift.uvot.source_list JSON Schema Fields

| Field                    | Type / Example                    | Source                                                                  | Notes |
|--------------------------|-----------------------------------|-------------------------------------------------------------------------|-------|
| `alert_datetime`         | ISO 8601 string                   | GCN metadata                                                            | |
| `alert_tense`            | `"current"` or `"test"`           | GCN metadata                                                            | |
| `alert_type`             | `"initial"` or `"update"`         | `misc` $$2^{30}$$: `"initial"` for type=73; `"update"` for type=80      | |
| `mission`                | `"Swift"`                         | Fixed constant                                                          | |
| `instrument`             | `"UVOT"`                          | Fixed constant                                                          | |
| `id`                     | integer trigger ID                | `bin[4]` lower 24 bits                                                  | |
| `ra_pointing`            | float (degrees)                   | `bin[7] × 1e-4`                                                         | Spacecraft pointing direction RA (J2000) |
| `dec_pointing`           | float (degrees)                   | `bin[8] × 1e-4`                                                         | Spacecraft pointing direction Dec (J2000) |
| `roll`                   | float (degrees)                   | `bin[9] × 1e-4`                                                         | |
| `observation_start`      | ISO 8601 datetime string          | `bin[5]` (`expo_start_tjd`), `bin[6]` (`expo_start_sod`)                | |
| `filter`                 | string, e.g. `"White"`            | `filters[bin[10]]`                                                      | |
| `background_mean`        | float                             | `bin[11] × 1e-3`                                                        | |
| `image_extent`           | `[x_max, y_max]` (det-coords)     | `[bin[12], bin[13]]`                                                    | Maximum extent of image window |
| `image_offset`           | `[x_offset, y_offset]` (det-coords) | `[bin[15], bin[16]]`                                                    | Image window origin in detector coordinates |
| `n_stars`                | integer                           | `bin[14]`                                                               | Total number of sources in source list |
| `detection_threshold`    | integer (DN)                      | `bin[17]`                                                               | |
| `photometry_threshold`   | integer (DN)                      | `bin[18]`                                                               | |
| `watchdog_timeout`       | bool                              | `misc` $$2^{29}$$                                                       | |
| `source_list_fits_files` | base64-encoded FITS file or `None` | `bin[22–38]` URL string for both raw and processed files                | |
