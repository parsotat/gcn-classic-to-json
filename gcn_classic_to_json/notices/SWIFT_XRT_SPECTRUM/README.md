# SWIFT_XRT_SPEC / SWIFT_XRT_SPEC_PROC — GCN Socket Packet Definition

**Packet Types:**
- `68` = `SWIFT_XRT_SPEC` — raw flight spectrum
- `77` = `SWIFT_XRT_SPEC_PROC` — ground-processed spectrum

**Related types:** `67` = `SWIFT_XRT_POS`, `69` = `SWIFT_XRT_IMAGE`, `70` = `SWIFT_XRT_LC`, `71` = `SWIFT_XRT_NACK_POS`
**GCN Schema:** `swift.xrt.spectrum` (covers both raw and processed subtypes)

> **Note:** Types `68` and `77` share an **identical packet word layout**. The only structural
> differences are the `pkt_type` value in `bin[0]`, the state of `misc` bit $$2^{30}$$,
> which is always `0` for the raw flight form (type=68) and always `1` for the
> ground-processed form (type=77), and `misc` bit $$2^{24}$$, which is not assigned
> for type=68 but indicates a processing error in the ground-processed spectrum FITS
> file for type=77.

---

## Packet Word Layout

The packet consists of 40 four-byte (`long`) words, indexed `bin[0]`–`bin[39]`.
This layout applies to **both** type=68 and type=77.

| Index | Item Name       | Units             | Description |
|-------|-----------------|-------------------|-------------|
| 0     | `pkt_type`      | integer           | Packet type number (`68` = raw, `77` = processed) |
| 1     | `pkt_sernum`    | integer           | Serial number for this packet type; starts at 1 |
| 2     | `pkt_hop_cnt`   | integer           | Incremented by each network node the packet passes through |
| 3     | `pkt_sod`       | centi-sec         | UT seconds-of-day when the packet was sent from GCN; `int(sssss.sss × 100)` |
| 4     | `trig_obs_num`  | integers (packed) | Lower 24 bits = Trigger number; upper 8 bits = Observation number |
| 5     | `SpecStart_tjd` | days              | Truncated Julian Day of the first CCD integration in the spectrum |
| 6     | `SpecStart_sod` | centi-sec         | UT seconds-of-day of the spectrum start; `int(sssss.sss × 100)` |
| 7     | `bore_ra`       | 0.0001-deg        | RA of XRT boresight (J2000); `int(0.0–359.9999 × 10000)` |
| 8     | `bore_dec`      | 0.0001-deg        | Dec of XRT boresight (J2000); `int(−90.0–+90.0 × 10000)` |
| 9     | `live_time`     | centi-sec         | Total exposure time of the spectrum integration; `int(sssss.sss × 100)` |
| 10    | `SpecStop_tjd`  | days              | Truncated Julian Day of the last CCD integration in the spectrum |
| 11    | `SpecStop_sod`  | centi-sec         | UT seconds-of-day of the spectrum stop; `int(sssss.sss × 100)` |
| 12    | `mode`          | integer           | CCD readout mode (see [CCD readout modes](#ccd-readout-modes)) |
| 13    | `waveform`      | integer           | CCD waveform ID; values are `50` or `60` |
| 14    | `bias`          | ADU               | Bias value of the last LRPD frame; only meaningful when `mode = 5` (LRPD) |
| 15–18 | *(spare)*      | —                 | Reserved |
| 19    | `misc`          | bits              | Miscellaneous flag bits (see [misc bits](#misc-bits)) |
| 20    | *(spare)*       | —                 | Reserved |
| 21    | `term_code`     | integer           | Termination condition code (see [termination conditions](#termination-conditions)) |
| 22–38 | `url[17]`      | chars             | Filename portion of the spectrum FITS file URL (up to 67 chars, null-terminated) |
| 39    | `pkt_term`      | integer           | Packet termination character (ASCII newline, decimal 10) |

---

## CCD Readout Modes

Stored in `bin[12]` as an integer code.

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

## Termination Conditions

Stored in `bin[21]` as an integer code.

| Value | Description |
|-------|-------------|
| `0`   | Normal |
| `1`   | Terminated by time |
| `2`   | Terminated by snapshot |
| `3`   | Terminated by entering SAA |
| `4`   | Spectrum generated at the LRPD-to-WT transition |
| `5`   | Spectrum generated at the WT-to-LRorPC transition |

---

## misc Bits

Stored in `bin[19]`. Contains additional flag bits describing properties of the spectrum notice.
All bit definitions apply equally to both type=68 and type=77, with the exception of $$2^{24}$$
and $$2^{30}$$ which are only meaningful for the ground-processed form (type=77).

| Bit | Type=68 | Type=77 | Description |
|-----|---------|---------|-------------|
| $$2^{0}$$–$$2^{10}$$ | Not assigned | Not assigned | Spare |
| $$2^{11}$$ | ✓ | ✓ | `1` = one or more of the RA/Dec/Roll/Theta/Phi values were out of valid range (e.g. RA = 361°) |
| $$2^{12}$$ | ✓ | ✓ | `1` = source is in the catalog of sources to be blocked (internal use only) |
| $$2^{13}$$ | ✓ | ✓ | `1` = there is a nearby bright star (magnitude < 6.5) |
| $$2^{14}$$–$$2^{19}$$ | Not assigned | Not assigned | Spare |
| $$2^{20}$$ | ✓ | ✓ | `1` = this was originally a SubThreshold trigger, now promoted to a real `XRT_SPEC` |
| $$2^{21}$$ | ✓ | ✓ | `1` = image trigger occurred during a StarTracker Loss-of-Lock event |
| $$2^{22}$$ | ✓ | ✓ | `1` = notice generated as a result of an uploaded TOO (Target-of-Opportunity) sequence |
| $$2^{23}$$ | Not assigned | Not assigned | Spare |
| $$2^{24}$$ | Not assigned | ✓ | `1` = the `xrt_proc_sp{1,2}.fits` file had an error in processing and does not exist *(type=77 only)* |
| $$2^{25}$$ | ✓ | ✓ | `1` = notice was generated with the 3rd of 3 telemetry packets missing |
| $$2^{26}$$ | ✓ | ✓ | `1` = notice was generated with the 2nd of 3 telemetry packets missing |
| $$2^{27}$$ | ✓ | ✓ | `1` = notice was generated with the 1st of 3 telemetry packets missing |
| $$2^{28}$$ | Not assigned | Not assigned | Spare |
| $$2^{29}$$ | ✓ | ✓ | `1` = this `XRT_SPECTRUM` notice was forced out via the watchdog timeout |
| $$2^{30}$$ | Always `0` | Always `1` | `0` = flight-generated (type=68); `1` = ground-generated (type=77) |
| $$2^{31}$$ | ✓ | ✓ | `1` = CRC error detected in one or more telemetry packets used to build this notice |

---

## Differences Between Type=68 and Type=77

| Property | `SWIFT_XRT_SPEC` (type=68) | `SWIFT_XRT_SPEC_PROC` (type=77) |
|----------|----------------------------|----------------------------------|
| `bin[0]` `pkt_type` | `68` | `77` |
| `misc` $$2^{24}$$ | Not assigned | `1` = `xrt_proc_sp{1,2}.fits` had a processing error and does not exist |
| `misc` $$2^{30}$$ | Always `0` | Always `1` |
| Origin | Raw flight telemetry | Ground-reprocessed spectrum |
| Packet word layout | Identical | Identical |
| `term_code` values | 0–5 | 0–5 |

---

## Value Conversions

| Field           | Raw Unit   | Conversion | Output Unit |
|-----------------|------------|------------|-------------|
| `bore_ra`       | 0.0001-deg | `× 1e-4`   | degrees     |
| `bore_dec`      | 0.0001-deg | `× 1e-4`   | degrees     |
| `live_time`     | centi-sec  | `× 1e-2`   | seconds     |
| `SpecStart_sod` | centi-sec  | passed to `datetime_to_iso8601` | ISO 8601 |
| `SpecStop_sod`  | centi-sec  | passed to `datetime_to_iso8601` | ISO 8601 |
| `bias`          | ADU        | none (raw integer); `None` if `mode ≠ 5` | ADU |

---

## swift.xrt.spectrum JSON Schema Fields

Defined in the GCN JSON schema document for `swift.xrt.spectrum` (covers both raw and processed subtypes):

| Field                   | Type / Example                                                                                                                                                          | Source |
|-------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|
| `alert_datetime`        | ISO 8601 string                                                                                                                                                         | GCN metadata |
| `alert_tense`           | `"current"` or `"test"`                                                                                                                                                 | GCN metadata |
| `alert_type`            | `"initial"` or `"update"`                                                                                                                                               | GCN metadata |
| `mission`               | `"Swift"`                                                                                                                                                               | Fixed constant |
| `instrument`            | `"XRT"`                                                                                                                                                                 | Fixed constant |
| `id`                    | integer trigger ID                                                                                                                                                      | `bin[4]` lower 24 bits |
| `pointing_ra`           | float (degrees)                                                                                                                                                         | `bin[7] × 1e-4` |
| `pointing_dec`          | float (degrees)                                                                                                                                                         | `bin[8] × 1e-4` |
| `observation_start`     | ISO 8601 datetime string                                                                                                                                                | `bin[5]`, `bin[6]` |
| `observation_stop`      | ISO 8601 datetime string                                                                                                                                                | `bin[10]`, `bin[11]` |
| `observation_livetime`  | float (seconds)                                                                                                                                                         | `bin[9] × 1e-2` |
| `ccd_readout_mode`      | `"Null"`, `"Short image"`, `"Long image"`, `"Piled-up Photodiode"`, `"Low Rate Photodiode"`, `"Windowed Timing"`, `"Photo-counting"`, `"Raw data"`, `"Bias map"`, `"Stop"` | `bin[12]` |
| `ccd_waveform_id`       | integer (`50` or `60`)                                                                                                                                                  | `bin[13]` |
| `bias`                  | integer (ADU), or `None` if `mode ≠ 5`                                                                                                                                 | `bin[14]` |
| `termination_condition` | `"Normal"`, `"Terminated by time"`, `"Terminated by snapshot"`, `"Terminated by entering SAA"`, `"LRPD-to-WT transition"`, `"WT-to-LRorPC transition"`                 | `bin[21]` |
| `spectrum_fits_file`    | base64-encoded FITS file                                                                                                                                                | `bin[22–38]` URL string |