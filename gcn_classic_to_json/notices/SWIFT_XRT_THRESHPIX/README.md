# SWIFT_XRT_THRESHPIX / SWIFT_XRT_THRESHPIX_PROC — GCN Socket Packet Definition

**Packet Types:**
- `85` = `SWIFT_XRT_THRESHPIX` — raw flight thresholded pixels (NOT PUBLIC, Swift team only)
- `86` = `SWIFT_XRT_THRESHPIX_PROC` — ground-processed thresholded pixels (NOT PUBLIC, Swift team only)

**Related types:** `67` = `SWIFT_XRT_POS`, `68` = `SWIFT_XRT_SPEC`, `69` = `SWIFT_XRT_IMAGE`, `70` = `SWIFT_XRT_LC`
**GCN Schema:** `swift.xrt.thresholded_pixels` (covers both raw and processed subtypes)

> **Note:** Types `85` and `86` share an **identical packet word layout**. The only structural
> differences are the `pkt_type` value in `bin[0]` and the state of `misc` bit $$2^{30}$$,
> which is always `0` for the raw flight form (type=85) and always `1` for the
> ground-processed form (type=86).

---

## Packet Word Layout

The packet consists of 40 four-byte (`long`) words, indexed `bin[0]`–`bin[39]`.
This layout applies to **both** type=85 and type=86.

| Index | Item Name      | Units             | Description |
|-------|----------------|-------------------|-------------|
| 0     | `pkt_type`     | integer           | Packet type number (`85` = raw, `86` = processed) |
| 1     | `pkt_sernum`   | integer           | Serial number for this packet type; starts at 1 |
| 2     | `pkt_hop_cnt`  | integer           | Incremented by each network node the packet passes through |
| 3     | `pkt_sod`      | centi-sec         | UT seconds-of-day when the packet was sent from GCN; `int(sssss.sss × 100)` |
| 4     | `trig_obs_num` | integers (packed) | Lower 24 bits = Trigger number; upper 8 bits = Observation number |
| 5     | `Start_tjd`    | days              | Truncated Julian Day of the first CCD integration in the accumulation |
| 6     | `Start_sod`    | centi-sec         | UT seconds-of-day of the accumulation start; `int(sssss.sss × 100)` |
| 7     | `bore_ra`      | 0.0001-deg        | RA of XRT boresight (J2000); `int(0.0–359.9999 × 10000)` |
| 8     | `bore_dec`     | 0.0001-deg        | Dec of XRT boresight (J2000); `int(−90.0–+90.0 × 10000)` |
| 9     | `live_time`    | 0.001-sec         | Total exposure time of the thresholded pixels accumulation; `int(sssss.sss × 1000)` |
| 10    | `Stop_tjd`     | days              | Truncated Julian Day of the last CCD integration in the accumulation |
| 11    | `Stop_sod`     | centi-sec         | UT seconds-of-day of the accumulation stop; `int(sssss.sss × 100)` |
| 12–18 | *(spare)*     | —                 | Reserved |
| 19    | `misc`         | bits              | Miscellaneous flag bits (see [misc bits](#misc-bits)) |
| 20–21 | *(spare)*     | —                 | Reserved |
| 22–38 | `url[17]`     | chars             | Filename portion of the thresholded pixels FITS file URL (up to 67 chars, null-terminated) |
| 39    | `pkt_term`     | integer           | Packet termination character (ASCII newline, decimal 10) |

---

## misc Bits

Stored in `bin[19]`. All bit definitions apply equally to both type=85 and type=86, with the
exception of $$2^{30}$$ which distinguishes the two subtypes.

| Bit | Type=85 | Type=86 | Description |
|-----|---------|---------|-------------|
| $$2^{0}$$–$$2^{10}$$ | Not assigned | Not assigned | Spare |
| $$2^{11}$$ | ✓ | ✓ | `1` = one or more of the RA/Dec/Roll/Theta/Phi values were out of valid range (e.g. RA = 361°) |
| $$2^{12}$$ | ✓ | ✓ | `1` = source is in the catalog of sources to be blocked (internal use only) |
| $$2^{13}$$ | ✓ | ✓ | `1` = there is a nearby bright star (magnitude < 6.5) |
| $$2^{14}$$–$$2^{19}$$ | Not assigned | Not assigned | Spare |
| $$2^{20}$$ | ✓ | ✓ | `1` = this was originally a SubThreshold trigger, now promoted to a real `XRT_THRESHPIX` |
| $$2^{21}$$ | ✓ | ✓ | `1` = image trigger occurred during a StarTracker Loss-of-Lock event |
| $$2^{22}$$ | ✓ | ✓ | `1` = notice generated as a result of an uploaded TOO (Target-of-Opportunity) sequence |
| $$2^{23}$$–$$2^{28}$$ | Not assigned | Not assigned | Spare |
| $$2^{29}$$ | ✓ | ✓ | `1` = this `XRT_THRESHPIX` notice was forced out via the watchdog timeout |
| $$2^{30}$$ | Always `0` | Always `1` | `0` = flight-generated (type=85); `1` = ground-generated (type=86) |
| $$2^{31}$$ | ✓ | ✓ | `1` = CRC error detected in one or more telemetry packets used to build this notice |

---

## Differences Between Type=85 and Type=86

| Property | `SWIFT_XRT_THRESHPIX` (type=85) | `SWIFT_XRT_THRESHPIX_PROC` (type=86) |
|----------|---------------------------------|---------------------------------------|
| `bin[0]` `pkt_type` | `85` | `86` |
| `misc` $$2^{30}$$ | Always `0` | Always `1` |
| Origin | Raw flight telemetry | Ground-reprocessed thresholded pixels |
| Packet word layout | Identical | Identical |

---

## Value Conversions

| Field        | Raw Unit   | Conversion | Output Unit |
|--------------|------------|------------|-------------|
| `bore_ra`    | 0.0001-deg | `× 1e-4`   | degrees     |
| `bore_dec`   | 0.0001-deg | `× 1e-4`   | degrees     |
| `live_time`  | 0.001-sec  | `× 1e-3`   | seconds     |
| `Start_sod`  | centi-sec  | passed to `datetime_to_iso8601` | ISO 8601 |
| `Stop_sod`   | centi-sec  | passed to `datetime_to_iso8601` | ISO 8601 |

---

## swift.xrt.thresholded_pixels JSON Schema Fields

Defined in the GCN JSON schema document for `swift.xrt.thresholded_pixels` (covers both raw
and processed subtypes):

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
| `watchdog_timeout`     | bool                          | `misc` $$2^{29}$$ |
| `subtype`              | `"FLIGHT"` or `"PROCESSED"`   | `misc` $$2^{30}$$ |