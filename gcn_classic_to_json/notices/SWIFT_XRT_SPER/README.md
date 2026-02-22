# SWIFT_XRT_SPER / SWIFT_XRT_SPER_PROC — GCN Socket Packet Definition

**Packet Types:**
- `87` = `SWIFT_XRT_SPER` — raw flight SPER (NOT PUBLIC, Swift team only)
- `88` = `SWIFT_XRT_SPER_PROC` — ground-processed SPER (NOT PUBLIC, Swift team only)

**Related types:** `67` = `SWIFT_XRT_POS`, `68` = `SWIFT_XRT_SPEC`, `69` = `SWIFT_XRT_IMAGE`, `70` = `SWIFT_XRT_LC`
**GCN Schema:** `swift.xrt.sper` (covers both raw and processed subtypes)

> **Note:** Types `87` and `88` share the same packet word layout with one exception:
> `bin[12]` has a different meaning between the two types (see [packet word layout](#packet-word-layout)).
> The state of `misc` bit $$2^{30}$$ also distinguishes the two subtypes, being always `0`
> for the raw flight form (type=87) and always `1` for the ground-processed form (type=88).

---

## Packet Word Layout

The packet consists of 40 four-byte (`long`) words, indexed `bin[0]`–`bin[39]`.

| Index | Item Name              | Units             | Description |
|-------|------------------------|-------------------|-------------|
| 0     | `pkt_type`             | integer           | Packet type number (`87` = raw, `88` = processed) |
| 1     | `pkt_sernum`           | integer           | Serial number for this packet type; starts at 1 |
| 2     | `pkt_hop_cnt`          | integer           | Incremented by each network node the packet passes through |
| 3     | `pkt_sod`              | centi-sec         | UT seconds-of-day when the packet was sent from GCN; `int(sssss.sss × 100)` |
| 4     | `trig_obs_num`         | integers (packed) | Lower 24 bits = Trigger number; upper 8 bits = Observation number |
| 5     | `burst_tjd`            | days              | Truncated Julian Day of the Swift-BAT transient trigger |
| 6     | `burst_sod`            | centi-sec         | UT seconds-of-day of the trigger time; `int(sssss.sss × 100)` |
| 7     | `point_ra`             | 0.0001-deg        | RA of XRT pointing direction (J2000); `int(0.0–359.9999 × 10000)` |
| 8     | `point_dec`            | 0.0001-deg        | Dec of XRT pointing direction (J2000); `int(−90.0–+90.0 × 10000)` |
| 9     | `expo_time`            | 0.001-sec         | Total exposure time of the SPER integration; `int(time × 1000)` |
| 10    | `stop_date`            | days              | Truncated Julian Day of the end of the SPER integration |
| 11    | `stop_time`            | centi-sec         | UT seconds-of-day of the integration stop; `int(sssss.sss × 100)` |
| 12    | `num_pkt` / `seq_num`  | integer           | **type=87:** number of telemetry packets used in this integration; **type=88:** serial number of this message (1–3) |
| 13–18 | *(spare)*             | —                 | Reserved |
| 19    | `misc`                 | bits              | Miscellaneous flag bits (see [misc bits](#misc-bits)) |
| 20    | `num_evt`              | integer           | Total number of XRT events (photons) collected during the SPER integration |
| 21    | *(spare)*              | —                 | Reserved |
| 22–38 | `url[17]`             | chars             | Filename portion of the SPER FITS file URL (up to 67 chars, null-terminated) |
| 39    | `pkt_term`             | integer           | Packet termination character (ASCII newline, decimal 10) |

---

## misc Bits

Stored in `bin[19]`. All bit definitions apply equally to both type=87 and type=88, with the
exception of $$2^{30}$$ which distinguishes the two subtypes.

| Bit | Type=87 | Type=88 | Description |
|-----|---------|---------|-------------|
| $$2^{0}$$–$$2^{9}$$ | Not assigned | Not assigned | Spare |
| $$2^{10}$$ | ✓ | ✓ | `1` = StarTracker was NOT locked during this SPER integration *(added 26 Apr 2016)* |
| $$2^{11}$$ | ✓ | ✓ | `1` = one or more of the RA/Dec/Roll/Theta/Phi values were out of valid range (e.g. RA = 361°) |
| $$2^{12}$$–$$2^{21}$$ | Not assigned | Not assigned | Spare |
| $$2^{22}$$ | ✓ | ✓ | `1` = notice generated as a result of an uploaded TOO (Target-of-Opportunity) sequence |
| $$2^{23}$$–$$2^{28}$$ | Not assigned | Not assigned | Spare |
| $$2^{29}$$ | ✓ | ✓ | `1` = this `XRT_SPER` notice was forced out via the watchdog timeout |
| $$2^{30}$$ | Always `0` | Always `1` | `0` = flight-generated (type=87); `1` = ground-generated (type=88) |
| $$2^{31}$$ | ✓ | ✓ | `1` = CRC error detected in one or more telemetry packets used to build this notice |

---

## Differences Between Type=87 and Type=88

| Property | `SWIFT_XRT_SPER` (type=87) | `SWIFT_XRT_SPER_PROC` (type=88) |
|----------|----------------------------|---------------------------------|
| `bin[0]` `pkt_type` | `87` | `88` |
| `bin[12]` | `num_pkt`: number of telemetry packets in integration | `seq_num`: serial number of this message (1–3) |
| `misc` $$2^{30}$$ | Always `0` | Always `1` |
| Origin | Raw flight telemetry | Ground-reprocessed SPER |

---

## Value Conversions

| Field        | Raw Unit   | Conversion | Output Unit |
|--------------|------------|------------|-------------|
| `point_ra`   | 0.0001-deg | `× 1e-4`   | degrees     |
| `point_dec`  | 0.0001-deg | `× 1e-4`   | degrees     |
| `expo_time`  | 0.001-sec  | `× 1e-3`   | seconds     |
| `burst_sod`  | centi-sec  | passed to `datetime_to_iso8601` | ISO 8601 |
| `stop_time`  | centi-sec  | passed to `datetime_to_iso8601` | ISO 8601 |

---

## swift.xrt.sper JSON Schema Fields

Defined in the GCN JSON schema document for `swift.xrt.sper` (covers both raw and processed
subtypes). Note: no example packets are available for this schema type.

| Field                  | Type / Example                | Source |
|------------------------|-------------------------------|--------|
| `alert_datetime`       | ISO 8601 string               | GCN metadata |
| `alert_tense`          | `"current"` or `"test"`       | GCN metadata |
| `alert_type`           | `"initial"` or `"update"`     | GCN metadata |
| `mission`              | `"Swift"`                     | Fixed constant |
| `instrument`           | `"XRT"`                       | Fixed constant |
| `id`                   | integer trigger ID            | `bin[4]` lower 24 bits |
| `pointing_ra`          | float (degrees)               | `bin[7] × 1e-4` |
| `pointing_dec`         | float (degrees)               | `bin[8] × 1e-4` |
| `observation_start`    | ISO 8601 datetime string      | `bin[5]`, `bin[6]` |
| `observation_stop`     | ISO 8601 datetime string      | `bin[10]`, `bin[11]` |
| `observation_livetime` | float (seconds)               | `bin[9] × 1e-3` |
| `num_packets`          | integer                       | `bin[12]` (type=87 only) |
| `num_events`           | integer                       | `bin[20]` |
| `watchdog_timeout`     | bool                          | `misc` $$2^{29}$$ |
| `sper_fits_file`       | base64-encoded FITS file      | `bin[22–38]` URL string |