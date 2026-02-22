# SWIFT_XRT_LC — GCN Socket Packet Definition

**Packet Type:** `70` (`SWIFT_XRT_LC`)
**Related types:** `67` = `SWIFT_XRT_POS`, `68` = `SWIFT_XRT_SPEC`, `69` = `SWIFT_XRT_IMAGE`, `71` = `SWIFT_XRT_NACK_POS`
**GCN Schema:** `swift.xrt.lightcurve`

---

## Packet Word Layout

The packet consists of 40 four-byte (`long`) words, indexed `bin[0]`–`bin[39]`.

| Index | Item Name      | Units             | Description |
|-------|----------------|-------------------|-------------|
| 0     | `pkt_type`     | integer           | Packet type number (`= 70`) |
| 1     | `pkt_sernum`   | integer           | Serial number for this packet type; starts at 1 |
| 2     | `pkt_hop_cnt`  | integer           | Incremented by each network node the packet passes through |
| 3     | `pkt_sod`      | centi-sec         | UT seconds-of-day when the packet was sent from GCN; `int(sssss.sss × 100)` |
| 4     | `trig_obs_num` | integers (packed) | Lower 24 bits = Trigger number; upper 8 bits = Observation number |
| 5     | `start_tjd`    | days              | Truncated Julian Day of the first CCD integration in the lightcurve |
| 6     | `start_sod`    | centi-sec         | UT seconds-of-day of the lightcurve start; `int(sssss.sss × 100)` |
| 7     | `bore_ra`      | 0.0001-deg        | RA of XRT boresight (J2000); `int(0.0–359.9999 × 10000)` |
| 8     | `bore_dec`     | 0.0001-deg        | Dec of XRT boresight (J2000); `int(−90.0–+90.0 × 10000)` |
| 9     | `live_time`    | centi-sec         | Total exposure time of the lightcurve integration; `int(sssss.sss × 100)` |
| 10    | `SpecStop_tjd` | days              | Truncated Julian Day of the last CCD integration in the lightcurve |
| 11    | `SpecStop_sod` | centi-sec         | UT seconds-of-day of the lightcurve stop; `int(sssss.sss × 100)` |
| 12–18 | *(spare)*     | —                 | Reserved |
| 19    | `misc`         | bits              | Miscellaneous flag bits (see [misc bits](#misc-bits)) |
| 20    | `n_bins`       | integer           | Number of valid bins in the collected lightcurve (0–100) |
| 21    | `term_cond`    | integer           | Termination condition code (see [termination conditions](#termination-conditions)) |
| 22–38 | `url[17]`     | chars             | Filename portion of the lightcurve FITS file URL (up to 67 chars, null-terminated) |
| 39    | `pkt_term`     | integer           | Packet termination character (ASCII newline, decimal 10) |

---

## Termination Conditions

Stored in `bin[21]` as an integer code.

| Value | Description |
|-------|-------------|
| `0`   | Normal — all 100 bins collected |
| `1`   | Terminated by time (1–99 bins collected) |
| `2`   | Terminated by snapshot (1–99 bins collected) |
| `3`   | Terminated by entering SAA (1–99 bins collected) |

---

## misc Bits

Stored in `bin[19]`. Contains additional flag bits describing properties of the lightcurve notice.

| Bit | Description |
|-----|-------------|
| $$2^{0}$$–$$2^{10}$$ | Not assigned (spare) |
| $$2^{11}$$ | `1` = one or more of the RA/Dec/Roll/Theta/Phi values were out of valid range (e.g. RA = 361°) |
| $$2^{12}$$ | `1` = source is in the catalog of sources to be blocked (internal use only) |
| $$2^{13}$$ | `1` = there is a nearby bright star (magnitude < 6.5) |
| $$2^{14}$$–$$2^{19}$$ | Not assigned |
| $$2^{20}$$ | `1` = this was originally a SubThreshold trigger, now promoted to a real `XRT_LC` |
| $$2^{21}$$ | `1` = image trigger occurred during a StarTracker Loss-of-Lock event |
| $$2^{22}$$ | `1` = notice generated as a result of an uploaded TOO (Target-of-Opportunity) sequence |
| $$2^{23}$$–$$2^{30}$$ | Not assigned |
| $$2^{31}$$ | `1` = CRC error detected in one or more of the packets used to build this notice |

---

## Value Conversions

| Field          | Raw Unit   | Conversion | Output Unit |
|----------------|------------|------------|-------------|
| `bore_ra`      | 0.0001-deg | `× 1e-4`   | degrees     |
| `bore_dec`     | 0.0001-deg | `× 1e-4`   | degrees     |
| `live_time`    | centi-sec  | `× 1e-2`   | seconds     |
| `start_sod`    | centi-sec  | passed to `datetime_to_iso8601` | ISO 8601 |
| `SpecStop_sod` | centi-sec  | passed to `datetime_to_iso8601` | ISO 8601 |

---

## swift.xrt.lightcurve JSON Schema Fields

Defined in the GCN JSON schema document for `swift.xrt.lightcurve`:

| Field                   | Type / Example                                                                                    | Source |
|-------------------------|---------------------------------------------------------------------------------------------------|--------|
| `alert_datetime`        | ISO 8601 string                                                                                   | GCN metadata |
| `alert_tense`           | `"current"` or `"test"`                                                                           | GCN metadata |
| `alert_type`            | `"initial"` or `"update"`                                                                         | GCN metadata |
| `mission`               | `"Swift"`                                                                                         | Fixed constant |
| `instrument`            | `"XRT"`                                                                                           | Fixed constant |
| `id`                    | integer trigger ID                                                                                | `bin[4]` lower 24 bits |
| `pointing_ra`           | float (degrees)                                                                                   | `bin[7] × 1e-4` |
| `pointing_dec`          | float (degrees)                                                                                   | `bin[8] × 1e-4` |
| `observation_start`     | ISO 8601 datetime string                                                                          | `bin[5]`, `bin[6]` |
| `observation_stop`      | ISO 8601 datetime string                                                                          | `bin[10]`, `bin[11]` |
| `observation_livetime`  | float (seconds)                                                                                   | `bin[9] × 1e-2` |
| `collected_bins`        | integer, e.g. `27`                                                                                | `bin[20]` |
| `termination_condition` | `"Normal"`, `"Terminated by time"`, `"Terminated by snapshot"`, `"Terminated by entering SAA"`   | `bin[21]` |
| `lightcurve_fits_file`  | base64-encoded FITS file                                                                          | `bin[22–38]` URL string |