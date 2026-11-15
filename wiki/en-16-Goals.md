# 16. Goals

Features wanted on the A6000, inherited from other Sony models and other brands, with their source model. ✅ = done and verified on the camera. Similar features are grouped with «/».

≈ = Sony model from memory, unverified (web search only confirmed Silent Shooting → α7S, FTP → α9 and AF Track Sens → α99 II); may not be the first.

## Under research and in progress

- ⬜ Silent Shooting ([state](en-14-Current-state)) — _Origin: Sony α7S_
- ⬜ Picture Profiles PP1–PP10 — _Origin: ≈Sony α7R III_
- ⬜ JPEG Extra Fine quality — _Origin: Sony α6300_

## Pending

### Photo

- ⬜ Maximum shutter speed 1/8000 — _Origin: ≈Sony α7_
- ⬜ Expanded ISO up to 409600 — _Origin: Sony α7S_
- ⬜ Pixel Shift Multi Shooting / High Res Shot / Handheld High Res Shot — _Origin: ≈Sony α7R III; Olympus E-M1 II, E-M1X; Panasonic G9_
- ⬜ Pre Capture photo / Pro Capture / Pre-Burst 4K/6K — _Origin: Olympus E-M1 II; Panasonic GH5, G9_. Full-resolution Pro Capture: feasible in phases, not implemented (the S1/S2 predicate and the burst queue are still unlocated; ring of N×24 MB). The 4K/6K part is ruled out (g50). See [g51](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g51-pro-capture.md).
- ⬜ Multiple Exposure — _Origin: Canon EOS 7D Mark II; Nikon D850; Olympus E-M1 II_. Partial (static): the Apollo/HME engine behind MFNR/Twilight is motion estimation only, with no add/max/min operation nor switchable alignment; a custom accumulator is needed. Pending `MULTIEXP-ACC` ([g53](../docs/gui/g53-multiple-exposure-motor-fusion.md)).
- ⬜ Live Composite — _Origin: Olympus E-M1 II_. Partial (static): = `MULTIEXP-ACC` in max mode; automatic repeat and review already exist in the firmware (`STILL_INTERVAL_REC` model, continuous self-timer parameters, `Stage_RchRcv_Resize_AutoReview`) but their tables and buffers are not located yet. Open items `LIVECOMP-F1..F3` ([g54](../docs/gui/g54-live-composite-live-bulb.md)).
- ⬜ Live Bulb / Live Time — _Origin: Olympus E-M1 II_. Discarded in its original form (mechanical shutter reads out only at the end; no documented non-destructive read on the IMX210); folded into Live Composite in sum mode ([g54](../docs/gui/g54-live-composite-live-bulb.md)).
- ⬜ Bulb Timer — _Origin: Canon EOS 7D Mark II_. Partial: BULB is already timed by the host in frame slices and `T = 0` means unlimited; a 4-byte hook (`0x438c74f6`) replaces T with a seconds cell (0 = stock), tested in Unicorn (5 s = 152 slices). No menu or camera measurement yet; S2 still starts the exposure ([g55](../docs/gui/g55-bulb-timer.md)).
- ⬜ Focus Shift Shooting / Focus Stacking — _Origin: Nikon D850; Panasonic GH5, G9; Olympus E-M1 II, E-M1X_
- ⬜ Smile Shutter — _Origin: Sony α5100_
- ⬜ Internal intervalometer — _Origin: ≈Sony α9_
- ⬜ Interval AE Tracking Sensitivity / Exposure Smoothing — _Origin: ≈Sony α7R III; Nikon D850_
- ⬜ Anti-Flicker Shooting / Flicker Reduction / Flicker Scan — _Origin: Canon EOS 7D Mark II; Nikon D500, D850; Fujifilm X-T3; Olympus E-M1 II, E-M1X_
- ⬜ Keystone Compensation — _Origin: Olympus E-M1 II, E-M1X_
- ⬜ Live ND — _Origin: Olympus E-M1X_
- ⬜ In-camera photo rating — _Origin: ≈Sony α9_

### Image and color

- ⬜ S-Log2 — _Origin: ≈Sony α7S_
- ⬜ S-Log3 — _Origin: ≈Sony α7S II_
- ⬜ HLG 1-3 — _Origin: ≈Sony α7R III_
- ⬜ D Range Priority — _Origin: Fujifilm X-T3_
- ⬜ Color Chrome Effect — _Origin: Fujifilm X-T3_
- ⬜ LUT import — _Origin: Sony ZV-E1_
- ⬜ Direct film simulation — _Origin: Fujifilm X-T5_

### Video

- ⬜ Full HD / HD 120 fps — _Origin: ≈Sony α6300_
- ⬜ Variable Frame Rate — _Origin: Panasonic GH5_
- ⬜ Internal 4K — _Origin: ≈Sony α7R II_
- ⬜ Dual Video Recording — _Origin: ≈Sony α7R III_
- ⬜ 4K HDMI output — _Origin: Sony α7S_
- ⬜ Timecode / User Bit — _Origin: ≈Sony α7S II_
- ⬜ Loop Recording — _Origin: Panasonic GH5_
- ⬜ Movie Silent Control / Silent Multi Controller — _Origin: Fujifilm X-T3; Sony α99 II_
- ⬜ Anamorphic Desqueeze — _Origin: Panasonic GH5_
- ⬜ Synchro Scan — _Origin: Panasonic GH5_
- ⬜ Auto Object Framing — _Origin: ≈Sony ZV-E1_
- ⬜ Voice Memo — _Origin: ≈Sony α9_

### Monitoring

- ⬜ Zebra 0–109 % — _Origin: ≈Sony α6400_
- ⬜ Waveform Monitor — _Origin: Panasonic GH5_
- ⬜ Vectorscope — _Origin: Panasonic GH5_
- ⬜ Gamma Display Assist — _Origin: ≈Sony α7R III_
- ⬜ Sports Finder Mode — _Origin: Fujifilm X-T3_

### Focus

- ⬜ Real-time Eye AF — _Origin: ≈Sony α9_
- ⬜ Real-time AF tracking (3D Tracking / EOS iTR AF) — _Origin: ≈Sony α6400; Nikon D500, D850; Canon EOS 7D Mark II_
- ⬜ AF tracking sensitivity settings (AF-C Custom Settings / AF-C Cases) — _Origin: Sony α99 II; Fujifilm X-T3; Panasonic GH5; Olympus E-M1 II; Canon EOS 7D Mark II_
- ⬜ AF Acceleration/Deceleration Tracking — _Origin: Canon EOS 7D Mark II_
- ⬜ AF Range Control — _Origin: ≈Sony α99 II_
- ⬜ AF Micro Adjustment — _Origin: ≈Sony α99_
- ⬜ Pre-AF — _Origin: Fujifilm X-T3_
- ⬜ AF Point Auto Switching / Zone Area Switching — _Origin: Canon EOS 7D Mark II; Fujifilm X-T3_
- ⬜ Starry Sky AF — _Origin: Olympus E-M1 II_
- ⬜ Intelligent Subject Detection AF — _Origin: Olympus E-M1X_

### System and connectivity

- ⬜ USB charging while powered on — _Origin: ≈Sony α7 II_
- ⬜ FTP Background Transfer — _Origin: Sony α9_

## Discarded

- ❌ Post Focus — _Origin: Panasonic GH5, G9_. Depends on 4K/6K Photo (discarded in g50: no readout mode of 3840+ columns, encoder too weak) and the A6000 has no touchscreen (no panel in the service manual; the firmware «Touch» strings belong to face detection). Variants: focus sweep in FHD video → `G50-FHDPHOTO`; full-resolution burst sweep → Focus Shift Shooting. See [g52](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g52-post-focus.md).
- ❌ 4K/6K Photo (incl. 4K Photo Burst S/S) — _Origin: Panasonic GH5, G9_. The A6000's IMX210 only reads 6000×4000 at 15 fps or 1996×1124 at 60 Hz (no mode of 3840+ columns), the encoder tops out at 1080p60 (about 135 Mpx/s vs 249 for 4K30) and the firmware lacks the A6300's Photo Capture view. See [g50](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g50-4k-6k-photo.md).
- ❌ Digital level (virtual horizon) — _Origin: ≈Sony α6300_. The A6000 has no accelerometer: its orientation sensor (SE7750) is optical and each of its two channels is only high or low, so it tells four 90° positions apart and nothing in between. Measured over SWD while rotating the camera ([R88](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r88-sensor-inclinacion-swd.md)).
