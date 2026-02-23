# SWIFT_BAT_SCALED_MAP — GCN Socket Packet Definition

**Packet Type:** `64` = `SWIFT_BAT_SCALED_MAP` (NOT PUBLIC, Swift team only)
**Related types:** `61` = `SWIFT_BAT_GRB_POS_ACK`, `63` = `SWIFT_BAT_GRB_LC`, `97` = `SWIFT_BAT_QUICKLOOK_POSITION`
**GCN Schema:** `swift.bat.scaled_map`

> **Important:** Unlike other BAT packet types, `bin[5–6]` in this packet contain the
> **map generation time** (`map_tjd`/`map_sod`), not the BAT burst trigger time.
> Similarly, `bin[7–8]` contain the **spacecraft pointing direction** (`point_ra`/`point_dec`),
> not the burst position. The burst RA/Dec and position error are not present in this packet
> (`bin[9–13]` are spare).

---

## Packet Word Layout

The packet consists of 40 four-byte (`long`) words, indexed `bin[0]`–`bin[39]`.

| Index | Item Name       | Units             | Description |
|-------|-----------------|-------------------|-------------|
| 0     | `pkt_type`      | integer           | Packet type number (`= 64`) |
| 1     | `pkt_sernum`    | integer           | Serial number for this packet type; starts at 1 |
| 2     | `pkt_hop_cnt`   | integer           | Incremented by each network node the packet passes through |
| 3     | `pkt_sod`       | centi-sec         | UT seconds-of-day when the packet was sent from GCN; `int(sssss.sss × 100)` |
| 4     | `trig_obs_num`  | integers (packed) | Lower 24 bits = Trigger number; upper 8 bits = Observation number |
| 5     | `map_tjd`       | days              | Truncated Julian Day when the scaled map was generated |
| 6     | `map_sod`       | centi-sec         | UT seconds-of-day when the scaled map was generated; `int(sssss.sss × 100)` |
| 7     | `point_ra`      | 0.0001-deg        | RA of the spacecraft pointing direction at the start/stop of the map integration interval (J2000); `int(0.0–359.9999 × 10000)` |
| 8     | `point_dec`     | 0.0001-deg        | Dec of the spacecraft pointing direction (J2000); `int(−90.0–+90.0 × 10000)` |
| 9–13  | *(spare)*       | —                 | Reserved; burst RA, Dec, and position error are not present in this packet |
| 14    | `foregnd_dur`   | milliseconds      | Duration of the foreground (source) sampling interval, native to the ScaledMap notice (not copied from `BAT_POS`) |
| 15    | `integ_time`    | 4msec ticks       | Duration of the trigger sampling interval, copied from `BAT_POS`; e.g. value of `16` = 64 msec. Only valid if `misc` $$2^{24}$$ is set |
| 16    | `lon_lat`       | 2 shorts (packed) | High-order short = spacecraft latitude × 100; low-order short = spacecraft longitude × 100 |
| 17    | `trig_index`    | integer           | Row number in BAT on-board trigger table; **not yet assigned** |
| 18    | `soln_status`   | bits              | Solution/trigger classification flags copied from `BAT_POS_ACK`; **only valid if `misc` $$2^{24}$$ is set** (see [soln_status bits](#soln_status-bits)) |
| 19    | `misc`          | bits              | Miscellaneous flag bits (see [misc bits](#misc-bits)) |
| 20    | `image_signif`  | centi-sigma       | SNR of the image-trigger detection, copied from `BAT_Position`; `int(SNR × 100)` |
| 21    | `rate_signif`   | centi-sigma       | SNR of the rate-trigger detection, copied from `BAT_Position`; `int(SNR × 100)` |
| 22–38 | `url[17]`      | chars             | Filename portion of the scaled map FITS file URL (up to 67 chars, null-terminated) |
| 39    | `pkt_term`      | integer           | Packet termination character (ASCII newline, decimal 10) |

---

## soln_status Bits

Stored in `bin[18]`. **Only valid when `misc` bit $$2^{24}$$ is set**, indicating the field
was copied from the associated `BAT_POS_ACK` packet.

| Bit | Assigned | Name | Description |
|-----|----------|------|-------------|
| $$2^{0}$$ | Flight* | `point_src` | `1` = a point source was found |
| $$2^{1}$$ | Flight* | `grb` | `1` = it is a GRB |
| $$2^{2}$$ | Flight* | `interesting` | `1` = interesting known source (e.g. a flaring catalogued source) |
| $$2^{3}$$ | Flight* | `flt_cat_src` | `1` = source is in the flight on-board catalog |
| $$2^{4}$$ | Flight* | `image_trig` | `1` = image trigger; `0` = rate trigger |
| $$2^{5}$$ | Ground* | `def_not_grb` | `1` = definitively NOT a GRB — **this is a retraction** |
| $$2^{6}$$ | Ground* | `uncert_grb` | `1` = probably not a GRB or transient (high background level, i.e. near SAA) |
| $$2^{7}$$ | Ground* | `uncert_grb` | `1` = probably not a GRB or transient (low image significance; < 7.0 sigma) |
| $$2^{8}$$ | Ground* | `gnd_cat_src` | `1` = source is in the BAT ground catalog |
| $$2^{9}$$ | Ground* | `uncert_grb` | `1` = probably not a GRB or transient (negative background slope; exiting SAA) |
| $$2^{10}$$ | Ground* | `st_loss_lock` | `1` = StarTracker not locked; trigger is probably bogus |
| $$2^{11}$$ | Ground* | `uncert_grb` | `1` = very probably not a GRB or transient (VERY low image significance; < 6.5 sigma) |
| $$2^{12}$$ | Ground* | `blk_cat_src` | `1` = source is in the catalog of sources to be blocked (internal use only) |
| $$2^{13}$$ | Ground* | `near_brt_star` | `1` = there is a nearby bright star (magnitude < 6.5) |
| $$2^{14}$$ | — | *(spare)* | Reserved |
| $$2^{15}$$ | Ground* | `onboard_rmvd` | `1` = source has been purposefully removed from the on-board catalog |
| $$2^{16}$$ | Ground* | `nearby_gal` | `1` = matched a nearby galaxy in the on-board catalog |
| $$2^{17}$$–$$2^{31}$$ | — | *(spare)* | Reserved |

> \* These bits are only valid if `misc` bit $$2^{24}$$ is set, indicating `soln_status`
> was copied from the associated `BAT_POS_ACK` packet.

---

## misc Bits

Stored in `bin[19]`.

| Bit | Description |
|-----|-------------|
| $$2^{0}$$ | `1` = the `BAT_Pos` TDRSS message was not received for this trigger number |
| $$2^{1}$$–$$2^{10}$$ | Not assigned |
| $$2^{11}$$ | `1` = one or more of the RA/Dec/Roll/Theta/Phi values were out of valid range (e.g. RA = 361°) |
| $$2^{12}$$ | Not assigned |
| $$2^{13}$$ | `1` = position is near a bright star (magnitude < 6.5) |
| $$2^{14}$$ | `1` = position is inside the (circularized) NGC galaxy: distance between the BAT_Pos position and the galaxy center is less than the sum of the position error radius and galaxy radius, AND the position error radius is smaller than the galaxy radius |
| $$2^{15}$$ | `1` = an NGC galaxy is inside the position error circle: distance between the BAT_Pos position and the galaxy center is less than the sum of the position error radius and galaxy radius, AND the galaxy radius is smaller than the position error radius |
| $$2^{16}$$–$$2^{19}$$ | Not assigned |
| $$2^{20}$$ | `1` = this was originally a SubThreshold trigger, now converted to a real `BAT_SM` notice |
| $$2^{21}$$ | `1` = this is an image trigger AND it occurred during a StarTracker Loss-of-Lock event |
| $$2^{22}$$ | `1` = notice generated as a result of an uploaded TOO (Target-of-Opportunity) sequence |
| $$2^{23}$$ | Not assigned |
| $$2^{24}$$ | `1` = the `soln_status` field (`bin[18]`) was copied from the associated `BAT_POS_ACK` packet and is valid |
| $$2^{25}$$–$$2^{28}$$ | Not assigned |
| $$2^{29}$$ | `1` = this `BAT_SCALED_MAP` notice was forced out via the watchdog timeout |
| $$2^{30}$$ | `1` = ground-generated; `0` = flight-generated |
| $$2^{31}$$ | `1` = CRC error detected in one or more telemetry packets |

---

## Value Conversions

| Field               | Raw Unit     | Conversion | Output Unit |
|---------------------|--------------|------------|-------------|
| `point_ra`          | 0.0001-deg   | `× 1e-4`   | degrees     |
| `point_dec`         | 0.0001-deg   | `× 1e-4`   | degrees     |
| `foregnd_dur`       | milliseconds | `× 1e-3`   | seconds     |
| `lat`               | centi-deg    | `× 1e-2`   | degrees     |
| `lon`               | centi-deg    | `× 1e-2`   | degrees     |
| `image_signif`      | centi-sigma  | `× 1e-2`   | sigma       |
| `rate_signif`       | centi-sigma  | `× 1e-2`   | sigma       |
| `map_sod`           | centi-sec    | passed to `datetime_to_iso8601` | ISO 8601 |

---

## swift.bat.scaled_map JSON Schema Fields

| Field                  | Type / Example                    | Source | Notes |
|------------------------|-----------------------------------|--------|-------|
| `alert_datetime`       | ISO 8601 string                   | GCN metadata | |
| `alert_tense`          | `"current"` or `"test"`           | GCN metadata | |
| `alert_type`           | `"initial"` or `"retraction"`     | `soln_status` $$2^{5}$$* | |
| `mission`              | `"Swift"`                         | Fixed constant (`parse_swift_bat`) | |
| `instrument`           | `"BAT"`                           | Fixed constant (`parse_swift_bat`) | |
| `id`                   | integer trigger ID                | `bin[4]` lower 24 bits (`parse_swift_bat`) | |
| `trigger_time`         | ISO 8601 datetime string          | `bin[5]` (`map_tjd`), `bin[6]` (`map_sod`) | Map generation time, not BAT burst trigger time |
| `ra`                   | float (degrees)                   | — | `None`; burst RA not in packet (`bin[9–13]` spare) |
| `dec`                  | float (degrees)                   | — | `None`; burst Dec not in packet (`bin[9–13]` spare) |
| `ra_dec_error`         | float (degrees), e.g. 3 arcmin   | — | `None`; not in packet |
| `systematic_included`  | bool                              | — | `None`; not meaningful without `ra_dec_error` |
| `ra_pointing`          | float (degrees)                   | `bin[7] × 1e-4` | Spacecraft pointing direction RA |
| `dec_pointing`         | float (degrees)                   | `bin[8] × 1e-4` | Spacecraft pointing direction Dec |
| `latitude`             | float (degrees)                   | `lat × 1e-2` (high-order short of `bin[16]`) | |
| `longitude`            | float (degrees)                   | `lon × 1e-2` (low-order short of `bin[16]`) | |
| `trigger_type`         | `"image"` or `"rate"`             | `soln_status` $$2^{4}$$