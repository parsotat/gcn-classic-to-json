# SWIFT_UVOT_POSITION — GCN Socket Packet Definition

**Packet Type:** `81` = `SWIFT_UVOT_POSITION`
**Related types:** `89` = `SWIFT_UVOT_NACK_POSITION`
**GCN Schema:** `swift.uvot.position`

---

## Packet Word Layout

The packet consists of 40 four-byte (`long`) words, indexed `bin[0]`–`bin[39]`.

| Index | Item Name      | Units             | Description |
|-------|----------------|-------------------|-------------|
| 0     | `pkt_type`     | integer           | Packet type number (`= 81`) |
| 1     | `pkt_sernum`   | integer           | Serial number for this packet type; starts at 1 |
| 2     | `pkt_hop_cnt`  | integer           | Incremented by each network node the packet passes through |
| 3     | `pkt_sod`      | centi-sec         | UT seconds-of-day when the packet was sent from GCN; `int(sssss.sss × 100)` |
| 4     | `trig_obs_num` | integers (packed) | Lower 24 bits = Trigger number; upper 8 bits = Observation number |
| 5     | `burst_tjd`    | days              | Truncated Julian Day of the Swift-UVOT data |
| 6     | `burst_sod`    | centi-sec         | UT seconds-of-day of the Swift-UVOT data; `int(sssss.sss × 100)` |
| 7     | `burst_ra`     | 0.0001-deg        | RA of the burst/afterglow as determined by UVOT ground software (J2000); `int(0.0–359.9999 × 10000)` |
| 8     | `burst_dec`    | 0.0001-deg        | Dec of the burst/afterglow (J2000); `int(−90.0–+90.0 × 10000)` |
| 9     | `burst_mag`    | centi-mag         | Magnitude of the burst/afterglow in the specified filter; `int(mag × 100)` |
| 10    | `filter`       | integer           | Filter identifier (see [filter values](#filter-values)) |
| 11    | `burst_error`  | 0.0001-deg        | 90%-containment position error radius (low-precision); `int(degrees × 10000)`. See `hi_prec_err` for the preferred high-precision value |
| 12–15 | *(spare)*     | —                 | Reserved |
| 16    | `hi_prec_err`  | centi-arcsec      | High-precision 90%-containment position error radius, including both statistical and systematic contributions. Uses centi-arcsec units to avoid the 0.36 arcsec quantization error of `burst_error` |
| 17    | *(spare)*      | —                 | Reserved |
| 18    | `soln_status`  | bits              | Solution/source classification flags (see [soln_status bits](#soln_status-bits)) |
| 19    | `misc`         | bits              | Miscellaneous flag bits (see [misc bits](#misc-bits)) |
| 20    | `mag_error`    | centi-mag         | Uncertainty in the magnitude value; `int(mag_error × 100)` |
| 21    | `uvot-xrt`     | 0.0001-deg        | Angular distance between the UVOT position and the XRT position; `int(degrees × 10000)` |
| 22–38 | *(spare)*     | —                 | Reserved |
| 39    | `pkt_term`     | integer           | Packet termination character (ASCII newline, decimal 10) |

---

## Filter Values

Decoded from `bin[10]`.

| Value | Filter |
|-------|--------|
| `0`   | Blocked |
| `1`   | UV_Grism |
| `2`   | UVW2 |
| `3`   | V |
| `4`   | UVM2 |
| `5`   | Vis_Grism |
| `6`   | UVW1 |
| `7`   | U |
| `8`   | Magnifier |
| `9`   | B |
| `10`  | White |
| `11`  | unknown |

---

## soln_status Bits

Stored in `bin[18]`.

| Bit | Assigned | Name | Description |
|-----|----------|------|-------------|
| $$2^{0}$$ | Flight | `point_src` | `1` = a point source was found; `0` = extended source |
| $$2^{1}$$ | Flight | `grb` | `1` = it is a GRB |
| $$2^{2}$$ | — | *(undef)* | Not yet defined |
| $$2^{3}$$ | Flight | `catalog_src` | `1` = source is in the on-board catalog |
| $$2^{4}$$ | — | *(undef)* | Not yet defined |
| $$2^{5}$$ | Ground | `def_not_grb` | `1` = definitively NOT a GRB — **this is a retraction** |
| $$2^{6}$$–$$2^{7}$$ | — | *(undef)* | Not yet defined |
| $$2^{8}$$ | Ground | `gnd_cat_src` | `1` = BAT position is in the BAT ground catalog |
| $$2^{9}$$–$$2^{27}$$ | — | *(undef)* | Not yet defined |
| $$2^{28}$$ | Ground | `spatial_coinc` | `1` = spatial coincidence with another event |
| $$2^{29}$$ | Ground | `temporal_coinc` | `1` = temporal coincidence with another event |
| $$2^{30}$$ | Ground | `test_submit` | `1` = test submission; `0` = real current notice |
| $$2^{31}$$ | — | *(undef)* | Not yet defined |

---

## misc Bits

Stored in `bin[19]`.

| Bit | Description |
|-----|-------------|
| $$2^{0}$$–$$2^{11}$$ | Not assigned |
| $$2^{12}$$ | `1` = position is in the catalog of sources to be blocked (internal use only) |
| $$2^{13}$$ | `1` = position is near a bright star (magnitude < 6.5) |
| $$2^{14}$$–$$2^{21}$$ | Not assigned |
| $$2^{22}$$ | `1` = notice generated as a result of an uploaded TOO (Target-of-Opportunity) sequence |
| $$2^{23}$$–$$2^{24}$$ | Not assigned |
| $$2^{25}$$ | `1` = this is an updated position that changes/improves the position in the original `UVOT_Position` notice |
| $$2^{26}$$–$$2^{29}$$ | Not assigned |
| $$2^{30}$$ | `1` = ground-generated; `0` = flight-generated |
| $$2^{31}$$ | `1` = CRC error detected in one or more telemetry packets |

---

## Value Conversions

| Field          | Raw Unit      | Conversion    | Output Unit |
|----------------|---------------|---------------|-------------|
| `burst_ra`     | 0.0001-deg    | `× 1e-4`      | degrees     |
| `burst_dec`    | 0.0001-deg    | `× 1e-4`      | degrees     |
| `burst_error`  | 0.0001-deg    | `× 1e-4`      | degrees     |
| `hi_prec_err`  | centi-arcsec  | `× 1e-4 / 36` | degrees     |
| `burst_mag`    | centi-mag     | `× 1e-2`      | magnitude   |
| `mag_error`    | centi-mag     | `× 1e-2`      | magnitude   |
| `uvot-xrt`     | 0.0001-deg    | `× 1e-4`      | degrees     |
| `burst_sod`    | centi-sec     | passed to `datetime_to_iso8601` | ISO 8601 |

---

## swift.uvot.position JSON Schema Fields

| Field                | Type / Example          | Source | Notes |
|----------------------|-------------------------|--------|-------|
| `alert_datetime`     | ISO 8601 string         | GCN metadata | |
| `alert_tense`        | `"current"` or `"test"` | `soln_status` $$2^{30}$$ | |
| `alert_type`         | `"initial"` or `"retraction"` | `soln_status` $$2^{5}$$ | Schema lists `["initial", "update"]`; `"retraction"` used here per `def_not_grb` flag meaning |
| `mission`            | `"Swift"`               | Fixed constant | |
| `instrument`         | `"UVOT"`                | Fixed constant | |
| `id`                 | integer trigger ID      | `bin[4]` lower 24 bits | |
| `observation_start`  | ISO 8601 datetime string | `bin[5]` (`burst_tjd`), `bin[6]` (`burst_sod`) | Time of the Swift-UVOT data |
| `ra`                 | float (degrees)         | `bin[7] × 1e-4` | UVOT ground software position (J2000) |
| `dec`                | float (degrees)         | `bin[8] × 1e-4` | UVOT ground software position (J2000) |
| `ra_dec_error`       | float (degrees), e.g. 0.77 arcsec | `bin[16] × 1e-4 / 36` | High-precision error (`hi_prec_err`) in centi-arcsec converted to degrees |
| `systematic_included` | `True`                 | Fixed constant | `hi_prec_err` explicitly includes both statistical and systematic contributions. Note: schema example shows `False` — this is believed to be a schema documentation error |
| `magnitude`          | float (magnitude)       | `bin[9] × 1e-2` | |
| `magnitude_error`    | float (magnitude)       | `bin[20] × 1e-2` | |
| `filter`             | string, e.g. `"White"`  | `filters[bin[10]]` | |
| `uvot_xrt_distance`  | float (degrees)         | `bin[21] × 1e-4` | Angular distance between UVOT and XRT positions |