# SWIFT_BAT_GRB_POS / SWIFT_BAT_QUICKLOOK_POSITION — GCN Socket Packet Definition

**Packet Types:**
- `61` = `SWIFT_BAT_GRB_POS_ACK` — standard BAT GRB position
- `97` = `SWIFT_BAT_QUICKLOOK_POSITION` — quick-look BAT GRB position

**Related types:** `62` = `SWIFT_BAT_GRB_POS_NACK`, `63` = `SWIFT_BAT_GRB_POS_UPD`, `82` = `SWIFT_BAT_GRB_POS_TEST`, `98` = `SWIFT_BAT_SUBTHRESHOLD_POSITION`
**GCN Schema:** `swift.bat.position`

> **Note:** Types `61` and `97` share an **identical packet word layout**. Type `97`
> (`SWIFT_BAT_QUICKLOOK_POSITION`) is identical in format and content to type `61`
> (`SWIFT_BAT_GRB_POS_ACK`) — the only difference is the `pkt_type` value in `bin[0]`.
> The quick-look notice is issued earlier in the pipeline with potentially less refined
> position information.

---

## Packet Word Layout

The packet consists of 40 four-byte (`long`) words, indexed `bin[0]`–`bin[39]`.
This layout applies to **both** type=61 and type=97.

| Index | Item Name      | Units             | Description |
|-------|----------------|-------------------|-------------|
| 0     | `pkt_type`     | integer           | Packet type number (`61` = standard, `97` = quick-look) |
| 1     | `pkt_sernum`   | integer           | Serial number for this packet type; starts at 1 |
| 2     | `pkt_hop_cnt`  | integer           | Incremented by each network node the packet passes through |
| 3     | `pkt_sod`      | centi-sec         | UT seconds-of-day when the packet was sent from GCN; `int(sssss.sss × 100)` |
| 4     | `trig_obs_num` | integers (packed) | Lower 24 bits = Trigger number; upper 8 bits = Observation number |
| 5     | `burst_tjd`    | days              | Truncated Julian Day of the Swift-BAT burst trigger |
| 6     | `burst_sod`    | centi-sec         | UT seconds-of-day of the trigger; `int(sssss.sss × 100)` |
| 7     | `burst_ra`     | 0.0001-deg        | RA of burst/transient (J2000); `int(0.0–359.9999 × 10000)` |
| 8     | `burst_dec`    | 0.0001-deg        | Dec of burst/transient (J2000); `int(−90.0–+90.0 × 10000)` |
| 9     | `burst_flue`   | counts            | Net (background-subtracted) counts during the trigger interval |
| 10    | `burst_ipeak`  | counts            | Height of the peak in the sky-image plane (FFT/MaskConvolution/InvFFT result); multiplicative factor of ~0.5–0.7 |
| 11    | `burst_error`  | 0.0001-deg        | 90%-containment position error radius; `int(degrees × 10000)`. Initially hardwired at 4 arcmin |
| 12    | `phi`          | centi-deg         | BAT instrument phi coordinate; measured from +Y-axis towards -Z axis; `int(degrees × 100)` |
| 13    | `theta`        | centi-deg         | BAT instrument theta coordinate; measured from BAT boresight; `int(degrees × 100)` |
| 14    | `integ_time`   | 4msec ticks       | Duration of the trigger sampling interval; e.g. value of `16` = 64 msec |
| 15    | *(spare)*      | —                 | Reserved |
| 16    | `lon_lat`      | 2 shorts (packed) | High-order short = spacecraft latitude × 100; low-order short = spacecraft longitude × 100 |
| 17    | `trig_index`   | integer           | Row number in the BAT on-board trigger table of the highest-significance trigger criterion |
| 18    | `soln_status`  | bits              | Solution/trigger classification flags (see [soln_status bits](#soln_status-bits)) |
| 19    | `misc`         | bits              | Miscellaneous flag bits (see [misc bits](#misc-bits)) |
| 20    | `image_signif` | centi-sigma       | SNR of the image-trigger detection; `int(SNR × 100)`. By definition never exceeds 6.50 sigma for type=61 |
| 21    | `rate_signif`  | centi-sigma       | SNR of the rate-trigger detection; `int(SNR × 100)` |
| 22    | `bkg_flue`     | counts            | Number of events during the background interval |
| 23    | `bkg_start`    | centi-sec         | UT seconds-of-day of the background interval start; `int(sssss.sss × 100)`; may be 0 if not specified |
| 24    | `bkg_dur`      | centi-sec         | Duration of the background interval; `int(seconds × 100)` |
| 25    | `cat_num`      | integer           | On-board catalog match ID number; only valid when `soln_status` bit $$2^{3}$$ is set |
| 26–35 | *(spare)*     | —                 | Reserved |
| 36    | `merit_0-3`    | integers          | Merit parameters 0–3 (range −127 to +127), packed 4 per long (see [merit parameters](#merit-parameters)) |
| 37    | `merit_4-7`    | integers          | Merit parameters 4–7 (range −127 to +127), packed 4 per long (see [merit parameters](#merit-parameters)) |
| 38    | `merit_8-9`    | integers          | Merit parameters 8–9 (range −127 to +127), packed 2 per long (see [merit parameters](#merit-parameters)) |
| 39    | `pkt_term`     | integer           | Packet termination character (ASCII newline, decimal 10) |

---

## soln_status Bits

Stored in `bin[18]`. Contains flight- and ground-assigned flags characterising the trigger solution.

| Bit | Assigned | Name | Description |
|-----|----------|------|-------------|
| $$2^{0}$$ | Flight | `point_src` | `1` = a point source was found |
| $$2^{1}$$ | Flight | `grb` | `1` = it is a GRB |
| $$2^{2}$$ | Flight | `interesting` | `1` = interesting known source (e.g. a flaring catalogued source) |
| $$2^{3}$$ | Flight | `flt_cat_src` | `1` = source is in the flight on-board catalog |
| $$2^{4}$$ | Flight | `image_trig` | `1` = image trigger; `0` = rate trigger |
| $$2^{5}$$ | Ground | `def_not_grb` | `1` = definitively NOT a GRB — **this is a retraction** |
| $$2^{6}$$ | Ground | `uncert_grb` | `1` = probably not a GRB or transient (high background level, i.e. near SAA) |
| $$2^{7}$$ | Ground | `uncert_grb` | `1` = probably not a GRB or transient (low image significance; < 7.0 sigma) |
| $$2^{8}$$ | Ground | `gnd_cat_src` | `1` = source is in the BAT ground catalog |
| $$2^{9}$$ | Ground | `uncert_grb` | `1` = probably not a GRB or transient (negative background slope; exiting SAA) |
| $$2^{10}$$ | Ground | `st_loss_lock` | `1` = StarTracker not locked; trigger is probably bogus |
| $$2^{11}$$ | Ground | `uncert_grb` | `1` = very probably not a GRB or transient (VERY low image significance; < 6.5 sigma) |
| $$2^{12}$$ | Ground | `blk_cat_src` | `1` = source is in the catalog of sources to be blocked (internal use only) |
| $$2^{13}$$ | Ground | `near_brt_star` | `1` = there is a nearby bright star (duplicate of `misc` $$2^{13}$$) |
| $$2^{14}$$–$$2^{31}$$ | — | *(spare)* | Reserved |

> **Note:** The `star_tracker_locked` schema field is derived from `soln_status` bit $$2^{10}$$
> (`st_loss_lock`): `True` if the StarTracker was locked, `False` if not locked.

---

## misc Bits

Stored in `bin[19]`.

| Bit | Description |
|-----|-------------|
| $$2^{0}$$–$$2^{10}$$ | Not assigned (spare) |
| $$2^{11}$$ | `1` = one or more of the RA/Dec/Roll/Theta/Phi values were out of valid range (e.g. RA = 361°) |
| $$2^{12}$$ | `1` = the theta value was less than 10 arcmin — Swift was already pointed at this source (`within_10arcmin`) |
| $$2^{13}$$ | `1` = position is near (< 0.3 deg) a bright star (magnitude < 6.5) |
| $$2^{14}$$ | `1` = position is inside the (circularized) NGC galaxy: distance between position and galaxy center is less than the sum of the position error radius and galaxy radius, AND the position error radius is smaller than the galaxy radius |
| $$2^{15}$$ | `1` = an NGC galaxy is inside the position error circle: distance between position and galaxy center is less than the sum of the position error radius and galaxy radius, AND the galaxy radius is smaller than the position error radius |
| $$2^{16}$$–$$2^{19}$$ | Not assigned |
| $$2^{20}$$ | `1` = this was originally a SubThreshold trigger, now converted to a real `BAT_POS` notice |
| $$2^{21}$$ | `1` = this is an image trigger AND it occurred during a StarTracker Loss-of-Lock event |
| $$2^{22}$$ | `1` = notice generated as a result of an uploaded TOO (Target-of-Opportunity) sequence |
| $$2^{23}$$ | `1` = the trigger time was zero; the spacecraft system clock from the TDRSS Message Secondary Header was used to fill the `Burst_TJD` and `Burst_SOD` fields (occurs during a ground-commanded GRB TOO) |
| $$2^{24}$$ | `1` = the TDRSS message was received on the ground more than 60 sec after the BAT trigger time (most likely caused by BAT triggering during a Malindi downlink pass, where TDRSS messages are buffered on-board until the pass ends) |
| $$2^{25}$$ | `1` = this is an updated position notice that changes/improves the position specified in the original `BAT_Position` notice |
| $$2^{26}$$–$$2^{27}$$ | Not assigned |
| $$2^{28}$$ | `1` = this notice was derived from a SERS (Malindi playback) message rather than a real-time TDRSS message; some fields may be undefined |
| $$2^{29}$$ | `1` = this notice was reconstituted from a `BAT_LC` message received before a `BAT_POS` was received; some fields may be undefined |
| $$2^{30}$$ | `1` = ground-generated notice; `0` = flight-generated |
| $$2^{31}$$ | `1` = CRC error detected in one or more telemetry packets |

---

## Merit Parameters

Stored in `bin[36–38]` as three packed 32-bit words. Each word contains multiple 1-byte signed
integers (range −127 to +127), packed with parameter `0` in the lowest address byte, `1` in the
next lowest, etc. There are 10 merit parameters in total.

> **Note:** These merit parameters are distinct from the `merit_value` field in the
> `SWIFT_FOM_OBS` and `SWIFT_SC_SLEW` messages.

| Parameter | `bin` | Description |
|-----------|-------|-------------|
| `merit[0]` | 36 (byte 0) | Flag bit: `1` = GRB, `0` = not GRB |
| `merit[1]` | 36 (byte 1) | Flag bit: `1` = Transient (unknown source with trigger duration > 64 sec), `0` = not |
| `merit[2]` | 36 (byte 2) | Flag bit: `1` = Known source (matches something in on-board catalog), `0` = not |
| `merit[3]` | 36 (byte 3) | Trigger duration: $$\log_{2}(t_\mathrm{trig} / 1024\,\mathrm{msec})$$ |
| `merit[4]` | 37 (byte 0) | Trigger energy range: `0` = 15–25 keV, `1` = 15–50 keV, `2` = 25–100 keV, `3` = 50–350 keV |
| `merit[5]` | 37 (byte 1) | Image significance (sigma) |
| `merit[6]` | 37 (byte 2) | Observability: `−1` if within 30° of Moon; `−5` if within 20° of Moon; `−100` if within 45° of Sun |
| `merit[7]` | 37 (byte 3) | Flag bit: `1` = source is in a confused or obscured region (e.g. Galactic Centre or Plane) |
| `merit[8]` | 38 (byte 0) | Sun distance: `−100 × cos(sun_angular_dist)` |
| `merit[9]` | 38 (byte 1) | Offset parameter to bias for/against PPTs and TOOs with respect to Automated Targets |

---

## Differences Between Type=61 and Type=97

| Property | `SWIFT_BAT_GRB_POS_ACK` (type=61) | `SWIFT_BAT_QUICKLOOK_POSITION` (type=97) |
|----------|------------------------------------|------------------------------------------|
| `bin[0]` `pkt_type` | `61` | `97` |
| Pipeline stage | Standard pipeline position | Early quick-look position |
| Packet word layout | Identical | Identical |
| Position refinement | Fully processed | Potentially less refined |

---

## Value Conversions

| Field          | Raw Unit      | Conversion | Output Unit |
|----------------|---------------|------------|-------------|
| `burst_ra`     | 0.0001-deg    | `× 1e-4`   | degrees     |
| `burst_dec`    | 0.0001-deg    | `× 1e-4`   | degrees     |
| `burst_error`  | 0.0001-deg    | `× 1e-4`   | degrees     |
| `phi`          | centi-deg     | `× 1e-2`   | degrees     |
| `theta`        | centi-deg     | `× 1e-2`   | degrees     |
| `lat`          | centi-deg     | `× 1e-2`   | degrees     |
| `lon`          | centi-deg     | `× 1e-2`   | degrees     |
| `image_signif` | centi-sigma   | `× 1e-2`   | sigma       |
| `rate_signif`  | centi-sigma   | `× 1e-2`   | sigma       |
| `bkg_dur`      | centi-sec     | `× 1e-2`   | seconds     |
| `burst_sod`    | centi-sec     | passed to `datetime_to_iso8601` | ISO 8601 |
| `bkg_start`    | centi-sec     | passed to `datetime_to_iso8601` | ISO 8601 |

---

## swift.bat.position JSON Schema Fields

| Field                    | Type / Example                                                    | Source | Notes |
|--------------------------|-------------------------------------------------------------------|--------|-------|
| `alert_datetime`         | ISO 8601 string                                                   | GCN metadata | |
| `alert_tense`            | `"current"` or `"test"`                                           | `soln_status` $$2^{30}$$ | |
| `alert_type`             | `"initial"` or `"retraction"`                                     | `soln_status` $$2^{5}$$ | |
| `mission`                | `"Swift"`                                                         | Fixed constant (`parse_swift_bat`) | |
| `instrument`             | `"BAT"`                                                           | Fixed constant (`parse_swift_bat`) | |
| `id`                     | integer trigger ID                                                | `bin[4]` lower 24 bits (`parse_swift_bat`) | |
| `trigger_time`           | ISO 8601 datetime string                                          | `bin[5]`, `bin[6]` (`parse_swift_bat`) | |
| `ra`                     | float (degrees)                                                   | `bin[7] × 1e-4` (`parse_swift_bat`) | |
| `dec`                    | float (degrees)                                                   | `bin[8] × 1e-4` (`parse_swift_bat`) | |
| `ra_dec_error`           | float (degrees), e.g. 4 arcmin                                    | `bin[11] × 1e-4` | |
| `systematic_included`    | `False` (always)                                                  | Fixed constant | |
| `latitude`               | float (degrees)                                                   | `lat × 1e-2` (high-order short of `bin[16]`) | |
| `longitude`              | float (degrees)                                                   | `lon × 1e-2` (low-order short of `bin[16]`) | |
| `instrument_phi`         | float (degrees)                                                   | `bin[12] × 1e-2` | |
| `instrument_theta`       | float (degrees)                                                   | `bin[13] × 1e-2` | |
| `trigger_type`           | `"image"` or `"rate"`                                             | `soln_status` $$2^{4}$$ | |
| `trigger_index`          | integer                                                           | `bin[17]` | |
| `net_count_rate`         | counts                                                            | `bin[9]` | |
| `background_count_rate`  | counts                                                            | `bin[22]` | |
| `rate_snr`               | float (sigma)                                                     | `bin[21] × 1e-2` (`parse_swift_bat`) | |
| `rate_duration`          | float (sec) or `None`                                             | `bin[14]` × 4msec; `None` for image triggers | |
| `rate_energy_range`      | energy band or `None`                                             | decoded from trigger criterion; `None` for image triggers | |
| `image_snr`              | float (sigma)                                                     | `bin[20] × 1e-2` | |
| `image_duration`         | float (sec) or `None`                                             | `bin[14]` × 4msec; `None` for rate triggers | |
| `image_energy_range`     | energy band or `None`                                             | decoded from trigger criterion; `None` for rate triggers | |
| `classification`         | e.g. `{'known': 0.0, 'unknown': 1.0}`                            | — | `None`; not in binary packet |
| `properties`             | e.g. `{'NAME': 1.0, 'LGRB': 0.0, 'SGRB': 0.0}`                  | — | `None`; not in binary packet |
| `T90`                    | float (seconds)                                                   | — | `None`; not in binary packet |
| `hardness_ratio`         | float                                                             | — | `None`; not in binary packet |
| `spectral_lag`           | float                                                             | — | `None`; not