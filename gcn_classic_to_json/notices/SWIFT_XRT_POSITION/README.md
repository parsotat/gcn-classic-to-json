# SWIFT_XRT_POS — GCN Socket Packet Definition

**Packet Type:** `67` (`SWIFT_XRT_POS`)
**Related types:** `68` = `SWIFT_XRT_SPEC`, `69` = `SWIFT_XRT_IMAGE`, `70` = `SWIFT_XRT_LC`, `71` = `SWIFT_XRT_NACK_POS`
**GCN Schema:** `swift.xrt.position`

---

## Packet Word Layout

The packet consists of 40 four-byte (`long`) words, indexed `bin[0]`–`bin[39]`.

| Index | Item Name      | Units            | Description |
|-------|----------------|------------------|-------------|
| 0     | `pkt_type`     | integer          | Packet type number (`= 67`) |
| 1     | `pkt_sernum`   | integer          | Serial number for this packet type; starts at 1 |
| 2     | `pkt_hop_cnt`  | integer          | Incremented by each network node the packet passes through |
| 3     | `pkt_sod`      | centi-sec        | UT seconds-of-day when the packet was sent from GCN; `int(sssss.sss × 100)` |
| 4     | `trig_obs_num` | integers (packed)| Lower 24 bits = Trigger number; upper 8 bits = Observation number |
| 5     | `data_tjd`     | days             | Truncated Julian Day of the CCD image start |
| 6     | `data_sod`     | centi-sec        | UT seconds-of-day of the CCD image start; `int(sssss.sss × 100)` |
| 7     | `burst_ra`     | 0.0001-deg       | RA of burst/afterglow (J2000); `int(0.0–359.9999 × 10000)` |
| 8     | `burst_dec`    | 0.0001-deg       | Dec of burst/afterglow (J2000); `int(−90.0–+90.0 × 10000)` |
| 9     | `burst_flux`   | 1e-14 erg/cm²/s  | Approximate energy flux; `int(flux × 1e14)` (after 14 Nov 2005) |
| 10    | *(spare)*      | —                | Reserved |
| 11    | `burst_error`  | 0.0001-deg       | 90%-containment position error radius (statistical + systematic); hardcoded to 6 arcsec early in mission |
| 12    | `tam_x_1`      | centi-pixels     | TAM x-position in 1st image; `int(pixels × 100)`, typical range 200–400 |
| 13    | `tam_y_1`      | centi-pixels     | TAM y-position in 1st image; `int(pixels × 100)`, typical range 200–400 |
| 14    | `tam_x_2`      | centi-pixels     | TAM x-position in 2nd image; `int(pixels × 100)`, typical range 200–400 |
| 15    | `tam_y_2`      | centi-pixels     | TAM y-position in 2nd image; `int(pixels × 100)`, typical range 200–400 |
| 16    | `hi_prec_err`  | centi-arcsec     | High-precision 90%-containment error radius (statistical + systematic); `int(arcsec × 100)` |
| 17    | `amp_wave`     | integer (packed) | Upper 16 bits = amplifier ID; lower 16 bits = waveform ID (50 or 60) |
| 18    | `soln_status`  | bits             | Solution/trigger classification flags (see [soln_status bits](#soln_status-bits)) |
| 19    | `misc`         | bits             | Miscellaneous flag bits (see [misc bits](#misc-bits)) |
| 20    | `xrt_bat_dist` | 0.0001-deg       | Angular distance between XRT and BAT positions; `int(degrees × 10000)` |
| 21    | `image_snr`    | centi-sigma      | Signal-to-noise ratio of XRT image detection; `int(SNR × 100)` |
| 22–38 | `url[17]`     | chars            | Filename portion of the notice URL (up to 67 chars, null-terminated) |
| 39    | `pkt_term`     | integer          | Packet termination character (ASCII newline, decimal 10) |

---

## soln_status Bits

Stored in `bin[18]`. Contains flight- and ground-assigned flags characterising the type of trigger solution found.

| Bit | Assigned | Name | Description |
|-----|----------|------|-------------|
| $$2^{0}$$  | Flight | `point_src`   | `1` = a point source was found |
| $$2^{1}$$  | Flight | `grb`         | `1` = it is a GRB |
| $$2^{2}$$  | Flight | `interesting` | `1` = interesting source (e.g. a flaring known source) |
| $$2^{3}$$  | Flight | `flt_cat_src` | `1` = source is in the flight on-board catalog |
| $$2^{4}$$  | Flight | `image_trig`  | `1` = image trigger; `0` = rate trigger |
| $$2^{5}$$  | Ground | `def_not_grb` | `1` = definitively NOT a GRB — **this is a retraction** |
| $$2^{6}$$–$$2^{9}$$ | — | *(spare)* | Reserved for future use |
| $$2^{10}$$ | Ground | `cosmic_ray`  | `1` = possibly a cosmic ray, not a real astrophysical source |
| $$2^{30}$$ | Ground | `test_notice` | `1` = ground-generated (test); `0` = flight-generated (current/real) |

> **Note:** Bits $$2^{28}$$ and $$2^{29}$$ (sometimes labelled `spatial_coincidence` and `temporal_coincidence`) are **not defined** in the `SWIFT_XRT_POS` (type=67) packet. These bits exist only in BAT-related packet types and should not be used when parsing XRT position notices.

---

## misc Bits

Stored in `bin[19]`. Contains additional flag bits describing properties of the position notice.

| Bit | Description |
|-----|-------------|
| $$2^{0}$$–$$2^{9}$$ | Not assigned (spare) |
| $$2^{10}$$ | `1` = the detected peak is not a real astrophysical source peak (e.g. readout artifact or hot pixel) |
| $$2^{11}$$ | `1` = one or more of the RA/Dec values were out of valid range (e.g. RA = 361°) |
| $$2^{12}$$ | Not assigned |
| $$2^{13}$$ | `1` = position is within 0.3° of a bright star (magnitude < 6.5) |
| $$2^{14}$$ | `1` = position is inside a catalogued NGC galaxy (position error radius < galaxy radius) |
| $$2^{15}$$ | `1` = an NGC galaxy is inside the position error circle (galaxy radius < position error radius) |
| $$2^{16}$$ | `1` = BAT–XRT theta < 10 arcmin (Swift was already pointed at this source) |
| $$2^{17}$$–$$2^{19}$$ | Not assigned |
| $$2^{20}$$ | `1` = this was originally a SubThreshold trigger, now promoted to a real `XRT_POS` |
| $$2^{21}$$ | `1` = image trigger occurred during a StarTracker Loss-of-Lock event |
| $$2^{22}$$ | `1` = notice generated as a result of an uploaded TOO (Target-of-Opportunity) sequence |
| $$2^{23}$$ | `1` = packet was briefly delayed to interrogate the XRT image for amplifier gain |
| $$2^{24}$$ | Not assigned |
| $$2^{25}$$ | `1` = this is an updated position, superseding the original `XRT_Position` notice |
| $$2^{26}$$–$$2^{31}$$ | Not assigned |

---

## Value Conversions

| Field         | Raw Unit       | Conversion          | Output Unit   |
|---------------|----------------|---------------------|---------------|
| `burst_ra`    | 0.0001-deg     | `× 1e-4`            | degrees       |
| `burst_dec`   | 0.0001-deg     | `× 1e-4`            | degrees       |
| `hi_prec_err` | centi-arcsec   | `× 1e-2 / 3600`     | degrees       |
| `burst_flux`  | `flux × 1e14`  | `× 1e-14`           | erg/cm²/s     |
| `image_snr`   | centi-sigma    | `× 1e-2`            | sigma         |
| `xrt_bat_dist`| 0.0001-deg     | `× 1e-4`            | degrees       |
| `tam_x/y_1/2` | centi-pixels   | `× 1e-2`            | TAM pixels    |
| `data_sod`    | centi-sec      | passed to `datetime_to_iso8601` | ISO 8601 |

---

## swift.xrt.position JSON Schema Fields

Defined in the GCN JSON schema document for `swift.xrt.position`:

| Field                  | Type / Example                     | Source |
|------------------------|------------------------------------|--------|
| `alert_datetime`       | ISO 8601 string                    | GCN metadata |
| `alert_tense`          | `"current"` or `"test"`            | `soln_status` $$2^{30}$$ |
| `alert_type`           | `"initial"` or `"retraction"`      | `soln_status` $$2^{5}$$ |
| `id`                   | integer trigger ID                 | `bin[4]` lower 24 bits |
| `ra`                   | float (degrees)                    | `bin[7] × 1e-4` |
| `dec`                  | float (degrees)                    | `bin[8] × 1e-4` |
| `ra_dec_error`         | float (arcsec), e.g. `0.77`        | `bin[16] × 1e-2` |
| `systematic_included`  | `True` (always)                    | always included in `hi_prec_err` |
| `observation_start`    | ISO 8601 datetime string           | `bin[5]`, `bin[6]` |
| `energy_flux`          | float (erg/cm²/s)                  | `bin[9] × 1e-14` |
| `image_snr`            | float (sigma)                      | `bin[21] × 1e-2` |
| `xrt_bat_distance`     | float (degrees)                    | `bin[20] × 1e-4` |
| `tam_values`           | `[[x1,y1], [x2,y2]]` (TAM pixels) | `bin[12–15] × 1e-2` |
| `readout_amplifier`    | integer                            | upper 16 bits of `bin[17]` |
| `readout_waveform`     | integer (`50` or `60`)             | lower 16 bits of `bin[17]` |
| `possible_cosmic_ray`  | bool                               | `soln_status` $$2^{0}$$ |
| `subtype`              | `"FLIGHT_POSITION"`                | GCN metadata |
| `star_tracker_locked`  | bool                               | `not misc` $$2^{21}$$ |