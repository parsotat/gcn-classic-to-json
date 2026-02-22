# SWIFT_BAT_GRB_LC / SWIFT_BAT_GRB_LC_PROC — GCN Socket Packet Definition

**Packet Types:**
- `63` = `SWIFT_BAT_GRB_LC` — raw flight BAT lightcurve
- `76` = `SWIFT_BAT_GRB_LC_PROC` — ground-processed BAT lightcurve

**Related types:** `61` = `SWIFT_BAT_GRB_POS_ACK`, `62` = `SWIFT_BAT_GRB_POS_NACK`, `97` = `SWIFT_BAT_QUICKLOOK_POSITION`
**GCN Schema:** `swift.bat.lightcurve`

> **Note:** Types `63` and `76` share an **identical packet word layout**. The only structural
> differences are the `pkt_type` value in `bin[0]` and the state of `misc` bit $$2^{30}$$,
> which is always `0` for the raw flight form (type=63) and always `1` for the
> ground-processed form (type=76).

---

## Packet Word Layout

The packet consists of 40 four-byte (`long`) words, indexed `bin[0]`–`bin[39]`.
This layout applies to **both** type=63 and type=76.

| Index | Item Name      | Units             | Description |
|-------|----------------|-------------------|-------------|
| 0     | `pkt_type`     | integer           | Packet type number (`63` = raw, `76` = processed) |
| 1     | `pkt_sernum`   | integer           | Serial number for this packet type; starts at 1 |
| 2     | `pkt_hop_cnt`  | integer           | Incremented by each network node the packet passes through |
| 3     | `pkt_sod`      | centi-sec         | UT seconds-of-day when the packet was sent from GCN; `int(sssss.sss × 100)` |
| 4     | `trig_obs_num` | integers (packed) | Lower 24 bits = Trigger number; upper 8 bits = Observation number |
| 5     | `burst_tjd`    | days              | Truncated Julian Day of the Swift-BAT burst trigger |
| 6     | `burst_sod`    | centi-sec         | UT seconds-of-day of the trigger; `int(sssss.sss × 100)` |
| 7     | `burst_ra`     | 0.0001-deg        | RA of burst/transient (J2000); `int(0.0–359.9999 × 10000)` |
| 8     | `burst_dec`    | 0.0001-deg        | Dec of burst/transient (J2000); `int(−90.0–+90.0 × 10000)` |
| 9–11  | *(spare)*      | —                 | Reserved; `ra_dec_error`, `net_count_rate`, and `background_count_rate` schema fields are not available from this packet |
| 12    | `phi`          | centi-deg         | BAT instrument phi coordinate; measured from +Y-axis towards -Z axis; `int(degrees × 100)` |
| 13    | `theta`        | centi-deg         | BAT instrument theta coordinate; measured from BAT boresight; `int(degrees × 100)` |
| 14    | `delta_time`   | centi-sec         | Start of the lightcurve relative to the trigger time (T0 − T_lc); `int(seconds × 100)` |
| 15    | `integ_time`   | 4msec ticks       | Duration of trigger sampling interval; e.g. value of `16` = 64 msec. Copied from `BAT_POS`; only valid if `misc` $$2^{24}$$ is set |
| 16    | `lon_lat`      | 2 shorts (packed) | High-order short = spacecraft latitude × 100; low-order short = spacecraft longitude × 100 |
| 17    | `trig_index`   | integer           | Row number in BAT on-board trigger table of the highest-significance trigger criterion |
| 18    | `soln_status`  | bits              | Solution/trigger classification flags copied from `BAT_POS_ACK`; **only valid if `misc` $$2^{24}$$ is set** (see [soln_status bits](#soln_status-bits)) |
| 19    | `misc`         | bits              | Miscellaneous flag bits (see [misc bits](#misc-bits)) |
| 20    | `image_signif` | centi-sigma       | SNR of the image-trigger detection, copied from `BAT_POS`; `int(SNR × 100)` |
| 21    | `rate_signif`  | centi-sigma       | SNR of the rate-trigger detection; `int(SNR × 100)` |
| 22–38 | `url[17]`     | chars             | Filename portion of the lightcurve FITS file URL (up to 67 chars, null-terminated) |
| 39    | `pkt_term`     | integer           | Packet termination character (ASCII newline, decimal 10) |

---

## soln_status Bits

Stored in `bin[18]`. In the `SWIFT_BAT_GRB_LC` packet, **all `soln_status` bits are only valid
when `misc` bit $$2^{24}$$ is set**, indicating the field was copied from the corresponding
`BAT_POS_ACK` packet. Bits $$2^{0}$$–$$2^{28}$$ and $$2^{31}$$ are spare in the lightcurve
packet's native form.

| Bit | Assigned | Name | Description |
|-----|----------|------|-------------|
| $$2^{0}$$ | Flight* | `point_src` | `1` = a point source was found |
| $$2^{1}$$ | Flight* | `grb` | `1` = it is a GRB |
| $$2^{2}$$ | Flight* | `interesting` | `1` = interesting known source (e.g. a flaring catalogued source) |
| $$2^{3}$$ | Flight* | `flt_cat_src` | `1` = source is in the flight on-board catalog |
| $$2^{4}$$ | Flight* | `image_trig` | `1` = image trigger; `0` = rate trigger |
| $$2^{5}$$ | Ground* | `def_not_grb` | `1` = definitively NOT a GRB — **retraction** |
| $$2^{6}$$–$$2^{9}$$ | — | *(spare)* | Reserved |
| $$2^{10}$$ | Flight* | `star_tracker` | StarTracker lock status; decoded via lookup table |
| $$2^{11}$$–$$2^{12}$$ | — | *(spare)* | Reserved |
| $$2^{13}$$ | Ground* | `bright_star` | `1` = position is near a bright star (magnitude < 6.5) |
| $$2^{14}$$ | Ground* | `was_subthresh` | `1` = originally a SubThreshold trigger |
| $$2^{15}$$ | Ground* | `removed_from_catalog` | `1` = source removed from on-board catalog |
| $$2^{16}$$ | Ground* | `galaxy_nearby` | `1` = a nearby NGC galaxy is within the position error circle |
| $$2^{17}$$–$$2^{28}$$ | — | *(spare)* | Reserved |
| $$2^{29}$$ | Ground | `temporal_coinc` | `1` = temporal coincidence with another event |
| $$2^{30}$$ | Ground | `test_submit` | `1` = test submission; `0` = real current notice |
| $$2^{31}$$ | — | *(spare)* | Reserved |

> \* These bits are only valid if `misc` bit $$2^{24}$$ is set, indicating `soln_status`
> was copied from the associated `BAT_POS_ACK` packet.

---

## misc Bits

Stored in `bin[19]`.

| Bit | Type=63 | Type=76 | Description |
|-----|---------|---------|-------------|
| $$2^{0}$$–$$2^{21}$$ | Not assigned | Not assigned | Spare |
| $$2^{22}$$ | ✓ | ✓ | `1` = notice generated as a result of an uploaded TOO (Target-of-Opportunity) sequence |
| $$2^{23}$$ | ✓ | ✓ | `1` = notice includes "extended" data packets |
| $$2^{24}$$ | ✓ | ✓ | `1` = `soln_status` field (bin[18]) was copied from the associated `BAT_POS_ACK` packet and is valid |
| $$2^{25}$$ | ✓ | ✓ | `1` = notice was generated with the 3rd of 3 telemetry packets missing |
| $$2^{26}$$ | ✓ | ✓ | `1` = notice was generated with the 2nd of 3 telemetry packets missing |
| $$2^{27}$$ | ✓ | ✓ | `1` = notice was generated with the 1st of 3 telemetry packets missing |
| $$2^{28}$$ | Not assigned | Not assigned | Spare |
| $$2^{29}$$ | ✓ | ✓ | `1` = this `BAT_GRB_LC` notice was forced out via the watchdog timeout |
| $$2^{30}$$ | Always `0` | Always `1` | `0` = flight-generated (type=63); `1` = ground-generated (type=76) |
| $$2^{31}$$ | ✓ | ✓ | `1` = CRC error detected in one or more telemetry packets |

---

## Differences Between Type=63 and Type=76

| Property | `SWIFT_BAT_GRB_LC` (type=63) | `SWIFT_BAT_GRB_LC_PROC` (type=76) |
|----------|-------------------------------|-----------------------------------|
| `bin[0]` `pkt_type` | `63` | `76` |
| `misc` $$2^{30}$$ | Always `0` | Always `1` |
| Origin | Raw flight telemetry | Ground-reprocessed lightcurve |
| Packet word layout | Identical | Identical |

---

## Value Conversions

| Field          | Raw Unit    | Conversion | Output Unit |
|----------------|-------------|------------|-------------|
| `burst_ra`     | 0.0001-deg  | `× 1e-4`   | degrees     |
| `burst_dec`    | 0.0001-deg  | `× 1e-4`   | degrees     |
| `phi`          | centi-deg   | `× 1e-2`   | degrees     |
| `theta`        | centi-deg   | `× 1e-2`   | degrees     |
| `delta_time`   | centi-sec   | `× 1e-2`   | seconds     |
| `lat`          | centi-deg   | `× 1e-2`   | degrees     |
| `lon`          | centi-deg   | `× 1e-2`   | degrees     |
| `image_signif` | centi-sigma | `× 1e-2`   | sigma       |
| `rate_signif`  | centi-sigma | `× 1e-2`   | sigma       |
| `burst_sod`    | centi-sec   | passed to `datetime_to_iso8601` | ISO 8601 |

---

## swift.bat.lightcurve JSON Schema Fields

Defined in the GCN JSON schema document for `swift.bat.lightcurve` (covers both raw and
processed subtypes):

| Field                  | Type / Example                           | Source | Notes |
|------------------------|------------------------------------------|--------|-------|
| `alert_datetime`       | ISO 8601 string                          | GCN metadata | |
| `alert_tense`          | `"current"` or `"test"`                  | `soln_status` $$2^{30}$$* | |
| `alert_type`           | `"initial"` or `"retraction"`            | `soln_status` $$2^{5}$$* | |
| `mission`              | `"Swift"`                                | Fixed constant (`parse_swift_bat`) | |
| `instrument`           | `"BAT"`                                  | Fixed constant (`parse_swift_bat`) | |
| `id`                   | integer trigger ID                       | `bin[4]` lower 24 bits (`parse_swift_bat`) | |
| `trigger_time`         | ISO 8601 datetime string                 | `bin[5]`, `bin[6]` (`parse_swift_bat`) | |
| `ra`                   | float (degrees)                          | `bin[7] × 1e-4` (`parse_swift_bat`) | |
| `dec`                  | float (degrees)                          | `bin[8] × 1e-4` (`parse_swift_bat`) | |
| `ra_dec_error`         | float (degrees), e.g. 3 arcmin          | — | `None`; `bin[11]` is spare in type=63/76 |
| `systematic_included`  | bool                                     | — | `None`; not meaningful without `ra_dec_error` |
| `latitude`             | float (degrees)                          | `lat × 1e-2` (high-order short of `bin[16]`) | |
| `longitude`            | float (degrees)                          | `lon × 1e-2` (low-order short of `bin[16]`) | |
| `instrument_phi`       | float (degrees)                          | `bin[12] × 1e-2` | |
| `instrument_theta`     | float (degrees)                          | `bin[13] × 1e-2` | |
| `trigger_type`         | `"image"` or `"rate"`                    | `soln_status` $$2^{4}$$* | |
| `trigger_index`        | integer                                  | `bin[17]` | |
| `net_count_rate`       | counts                                   | — | `None`; `bin[9]` is spare in type=63/76 |
| `background_count_rate`| counts                                   | — | `None`; `bin[22-38]` is the URL in the LC packet |
| `rate_snr`             | float (sigma)                            | `bin[21] × 1e-2` (`parse_swift_bat`) | |
| `rate_duration`        | float (sec) or `None`                    | `bin[15]` × 4msec; `None` for image triggers | Only valid if `misc` $$2^{24}$$ is set |
| `rate_energy_range`    | energy band or `None`                    | — | `None`; no energy range field in binary packet |
| `image_snr`            | float (sigma)                            | `bin[20] × 1e-2` | |
| `image_duration`       | float (sec) or `None`                    | `bin[15]` × 4msec; `None` for rate triggers | Only valid if `misc` $$2^{24}$$ is set |
| `image_energy_range`   | energy band or `None`                    | — | `None`; no energy range field in binary packet |
| `classification`       | e.g. `{'known': 0.0, 'unknown': 1.0}`   | — | `None`; not in binary packet |
| `properties`           | e.g. `{'NAME': 1.0, 'LGRB': 0.0, ...}` | — | `None`; not in binary packet |
| `T90`                  | float (seconds)                          | — | `None`; not in binary packet |
| `hardness_ratio`       | float                                    | — | `None`; not in binary packet |
| `spectral_lag`         | float                                    | — | `None`; not in binary packet |
| `observation_start`    | ISO 8601 datetime string                 | — | `None`; not in binary packet |
| `lightcurve_fits_file` | base64-encoded FITS file                 | `bin[22–38]` URL string | |
| `watchdog_timeout`     | bool                                     | `misc` $$2^{29}$$ | |
| `star_tracker_locked`  | bool                                     | `soln_status` $$2^{10}$$* via lookup | |

> \* Only valid if `misc` bit $$2^{24}$$ is set, indicating `soln_status` was copied from
> the associated `BAT_POS_ACK` packet.