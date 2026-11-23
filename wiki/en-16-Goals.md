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
- ⬜ Bulb Timer — _Origin: Canon EOS 7D Mark II_. Partial: BULB is already timed by the host in frame slices and `T = 0` means unlimited; a 4-byte hook (`0x438c74f6`) replaces T with the "Bulb Timer" menu setting (Backup id `0x1070210`; 0 = stock), tested in Unicorn (5 s = 152 slices); the menu entry (Off…15 min) shows in the harness, but its write to Backup does not work yet (CFWAJ-F1); S2 still starts the exposure ([g55](../docs/gui/g55-bulb-timer.md), [g56](../docs/gui/g56-ajustes-propios-cfw.md)).
- ⬜ Focus Shift Shooting / Focus Stacking — _Origin: Nikon D850; Panasonic GH5, G9; Olympus E-M1 II, E-M1X_. Partial: the focus-step command is located (lens command `0x1D`, signed s16; primitive `0x43adb5e6`, the one used by the stock AF bracketing `lc_BracketAF`); «Focus Bracket» (Off/3…30) and «Focus Br. paso» settings in the «CFW» folder (harness: id `0x1070212`=02, `0x1070213`=02); cave tested in Unicorn (N = 5 ⇒ 4 moves). Missing: the end-of-capture hook and measuring step direction/scale. The factory `SequenceBracketAF` only moves focus one step (it does not shoot), so it does not replace the cave (g57 §6; API step = s8, range ±127). CFW not built. See [g57](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g57-focus-bracket.md). g61 update: the `libObj` hook `0x66df4e` now exists (intervalometer) but Focus Bracket is not attached to it: from `libObj` the step needs message `0x765a` through `ModelScalarCameraPatch` and the lens motor cannot be awaited (`FOCUSSHIFT-HOOK`, [g61](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g61-intervalometro-libobj.md) §6).
- ✔ Smile Shutter — _Origin: Sony α5100_. Already present in stock A6000 firmware: «Smile/Face Detect.» offers Smile Shutter (model type 29 → `Default` list); detector in av-cam, sequence in `libObj`; seen in the harness, no patch ([g58](../docs/gui/g58-smile-shutter.md)). Only the in-camera shot remains (SMILE-CAM).
- ⬜ Internal intervalometer — _Origin: ≈Sony α9_. Partial, implemented without a camera: «Intervalo» (Off/2 s…5 min) and «N. disparos» (10…999/no limit) settings in the «CFW» folder plus a `libObj` 3.21 cave on the continuous self-timer (the setting replaces the 10/2/5 s wait, with a shot counter that stops at N); Unicorn on the real bytes: 5 s and N = 10 ⇒ 5 s wait and stop after 10 shots; settings verified in the harness. CFW not built or installed; not measured on a camera. See [g61](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g61-intervalometro-libobj.md) and [g60](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g60-autodisparador-continuo.md).
- ⬜ Interval AE Tracking Sensitivity / Exposure Smoothing — _Origin: ≈Sony α7R III; Nikon D850_. Partial, implemented without a camera (level 1): «Seguim. AE» (Normal/Locked) setting in the «CFW» folder; with «Locked» and the intervalometer on, the `libObj` 3.21 cave sends `MSGID_SET_AEL_CMD` (`0x75be`, `PARAMID_AEL` `0x96e6` = `0x1d5`) after shot 1 and releases it (`0x1d6`) when the series ends; tested in Unicorn on the real bytes, setting verified in the harness. Smoothing Low/Medium/High (level 2) not implemented: the measured EV is not readable (`libObj` only receives already-decided Tv/Av/ISO); compensation is possible through `0x759e`/`PARAMID_EXPOSURE_BIAS` `0x9652`. CFW not built or installed; not measured on the camera. See [g62](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g62-seguimiento-ae-intervalo.md).
- ◐ Anti-Flicker Shooting / Flicker Reduction / Flicker Scan — _Origin: Canon EOS 7D Mark II; Nikon D500, D850; Fujifilm X-T3; Olympus E-M1 II, E-M1X_. **Flicker Scan: implemented without a camera** (CFW not built): a «Flicker Scan» Off/50 Hz/60 Hz setting in the «CFW» folder that, in Silent, rounds the exposure to the nearest flicker-period multiple (584/486 lines of 17.135 µs); Unicorn + harness ([g63](../docs/gui/g63-flicker-scan.md)). **Synchronised anti-flicker: pending by phases** (the A6000 has no flicker detector; phase and shutter latency unmeasured).
- 🔶 Keystone Compensation — _Origin: Olympus E-M1 II, E-M1X_ — the distortion engine builds an 11x11 int16 displacement grid (av-cam); still to confirm the engine applies it ([g64](gui/g64-keystone-motor-geometrico.md), KEYSTONE-1)
- 🔶 Live ND — _Origin: Olympus E-M1X_ — partial: useful only with per-frame exposure ≥ 1/20 s (gap ≤ 25 %); YC hook point before JPEG found (`0x438c6f68`), counter cave tested in Unicorn; accumulator still missing ([g65](gui/g65-live-nd-acumulador-f1.md))
- ⬜ In-camera photo rating — _Origin: ≈Sony α9_ — partial, no code: no latent Rating in 3.21/α6300/A7S; Rotate (`libmpr` `0x373ae0`) only overwrites Orientation, tags 0x4746/0x4749 must be inserted ([g66](gui/g66-rating-en-camara.md), RATING-1…3)

### Image and color

- ◐ S-Log2 — _Origin: ≈Sony α7S_. Firmware patches done (curve `0x14`, Gamma menu, Color Mode/S-Gamut; [g25](../docs/gui/g25-gamma-slog2-itu709-800.md)), built into CFW 3.81 (not installed); camera verification pending.
- ◐ S-Log3 — _Origin: ≈Sony α7S II_. Firmware patches done (curve `0x17`, core [g32c](../docs/gui/g32c-slog3-nucleo.md), [g26](../docs/gui/g26-slog3-color-mode-a6300.md)), built into CFW 3.81 (not installed); camera verification pending.
- ◐ HLG 1-3 — _Origin: ≈Sony α7R III_. Not in stock firmware; HLG1/2/3 tables (ARIB STD-B67, approximate 87/95/100 % levels) plus menu and `libObj` patches tested offline, no CFW or camera; a safe spot for the curves and a harness screenshot are missing ([g67](../docs/gui/g67-hlg-gamma.md)).
- ◐ D Range Priority — _Origin: Fujifilm X-T3_. **Implemented without a camera** (CFW not built, not installed): a «DR Prioridad» Off/Weak/Strong setting in the «CFW» folder that, on half-press, sets DRO Lv3/Lv5 and an AE bias of −1/−2 EV (messages `0x755a` and `0x759e` to ObjCamera); Unicorn on `libObj` + harness. Limits: not Fujifilm's sensor-level DR200/400 (no extra analog gain), no knee, in RAW only the bias applies, DRO Lv5 gain (~2 EV) and the bias encoding are unmeasured. [g68](../docs/gui/g68-dr-prioridad.md) · DRP-F1…F3.
- ◐ Color Chrome Effect — _Origin: Fujifilm X-T3_. **Implemented without a camera** (CFW not built, not installed): a «Color Chrome» Weak/Strong setting that adds Color Depth (+2/+4) to the 6 sectors of the `av-cam` colorimetry packet; Unicorn + harness. Limit: per-hue approximation, not saturation-dependent luminance (that needs the 5×9×9 3D LUT found). [g69](../docs/gui/g69-color-chrome-film-lut.md) · CCH-F1…F3.
- ◐ LUT import — _Origin: Sony ZV-E1_. **Phase A implemented without a camera** (CFW not built, not installed): a «LUT» Off/LUT1/LUT2/LUT3 setting that replaces the hardware 5×9×9 3D LUT with `.dat` tables generated from a `.cube` (`scripts/lut/cube_a6000.py`, mean ΔE2000 0.3–0.7 on synthetic LUTs); format resolved (Y×Cb×Cr, signed 7-bit deltas), [g71](../docs/gui/g71-lut3d-formato-y-cube.md). Phase B (exact `.cube` of any size, 17³/33³/65³): **done without a camera by another route** (G91, 2026-11-22): `lutjpg` applies the full `.cube` to the JPEGs on the SD from Linux on the camera (stills only; video/live view stay at 5×9×9), [g91](../docs/gui/g91-lut-completa-por-software.md) · LUT-SW-2. General route (video and live view): own 1D curve after the gamma in a free firmware slot + 5×9×9 LUT, verified in Unicorn, not yet integrated ([g92](../docs/gui/g92-auditoria-cadena-color-lut-general.md) · LUT-T-1). Before: **Literal version ruled out**: the hardware 3D LUT is 5×9×9 (405 7-bit nodes, `0x654` B), not 17³/33³. Alternative: resample a `.cube` to that grid; loading from the SD is unchecked. [g69](../docs/gui/g69-color-chrome-film-lut.md) · CCH-F3, CCH-F5.
- ◐ Direct film simulation — _Origin: Fujifilm X-T5_. **Partial, no camera**: Classic/Vivid/Soft options of the same «Color Chrome» setting (Sat + per-sector Color Depth; estimated weights, not Fujifilm colour science); splitting the setting needs new Backup ids (exhausted). [g69](../docs/gui/g69-color-chrome-film-lut.md) · CCH-F4.
- ⬜ Direct film simulation — _Origin: Fujifilm X-T5_

### Video

- 🔧 Full HD / HD 120 fps — _Origin: ≈Sony α6300_. Partial: 1080p120 ruled out (readout ~69 fps max, 249 Mpx/s > 135); 720p120 has its pieces in the firmware (sensor mode 0x12 at 120 Hz, MP4 720p100 encoder, "120p 50M" menu node absent from the A6000 list), chain not closed, no CFW ([G70](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g70-hd-120fps.md)).
- ⬜ Variable Frame Rate — _Origin: Panasonic GH5_
- ⬜ Internal 4K — _Origin: ≈Sony α7R II_
- ⬜ Dual Video Recording — _Origin: ≈Sony α7R III_
- ⬜ 4K HDMI output — _Origin: Sony α7S_
- ⬜ Timecode / User Bit — _Origin: ≈Sony α7S II_
- ⬜ Loop Recording — _Origin: Panasonic GH5_. Not in the factory firmware; design in [g82](../docs/gui/g82-loop-recording.md), blocked by E2E-15 (harness cannot record yet), no code.
- ⬜ Movie Silent Control / Silent Multi Controller — _Origin: Fujifilm X-T3; Sony α99 II_ Static sweep in [g83](../docs/gui/g83-barrido-objetivos-restantes.md).
- ⬜ Anamorphic Desqueeze — _Origin: Panasonic GH5_ Static sweep in [g83](../docs/gui/g83-barrido-objetivos-restantes.md).
- ⬜ Synchro Scan — _Origin: Panasonic GH5_ Static sweep in [g83](../docs/gui/g83-barrido-objetivos-restantes.md).
- ⬜ Auto Object Framing — _Origin: ≈Sony ZV-E1_ Static sweep in [g83](../docs/gui/g83-barrido-objetivos-restantes.md).
- ⬜ Voice Memo — _Origin: ≈Sony α9_ Static sweep in [g83](../docs/gui/g83-barrido-objetivos-restantes.md).

### Monitoring

- ◐ Zebra 0–109 % — _Origin: ≈Sony α6400_ Static sweep in [g83](../docs/gui/g83-barrido-objetivos-restantes.md). **Implemented without a camera (G84):** CFW setting "Zebra Nivel" Off/10…60 % (band centre ±5), tested in the harness up to the VDF order; CFW not built.
- ⬜ Waveform Monitor — _Origin: Panasonic GH5_ Static sweep in [g83](../docs/gui/g83-barrido-objetivos-restantes.md).
- ⬜ Vectorscope — _Origin: Panasonic GH5_ Static sweep in [g83](../docs/gui/g83-barrido-objetivos-restantes.md).
- ⬜ Gamma Display Assist — _Origin: ≈Sony α7R III_ Static sweep in [g83](../docs/gui/g83-barrido-objetivos-restantes.md).
- ⬜ Sports Finder Mode — _Origin: Fujifilm X-T3_ Static sweep in [g83](../docs/gui/g83-barrido-objetivos-restantes.md).

### Focus

- ⬜ Real-time Eye AF — _Origin: ≈Sony α9_ Static sweep in [g83](../docs/gui/g83-barrido-objetivos-restantes.md).
- ⬜ Real-time AF tracking (3D Tracking / EOS iTR AF) — _Origin: ≈Sony α6400; Nikon D500, D850; Canon EOS 7D Mark II_
- ⬜ AF tracking sensitivity settings (AF-C Custom Settings / AF-C Cases) — _Origin: Sony α99 II; Fujifilm X-T3; Panasonic GH5; Olympus E-M1 II; Canon EOS 7D Mark II_
- ⬜ AF Acceleration/Deceleration Tracking — _Origin: Canon EOS 7D Mark II_ Static sweep in [g83](../docs/gui/g83-barrido-objetivos-restantes.md).
- ⬜ AF Range Control — _Origin: ≈Sony α99 II_ Static sweep in [g83](../docs/gui/g83-barrido-objetivos-restantes.md).
- ⬜ AF Micro Adjustment — _Origin: ≈Sony α99_ Static sweep in [g83](../docs/gui/g83-barrido-objetivos-restantes.md).
- ⬜ Pre-AF — _Origin: Fujifilm X-T3_ Static sweep in [g83](../docs/gui/g83-barrido-objetivos-restantes.md).
- ⬜ AF Point Auto Switching / Zone Area Switching — _Origin: Canon EOS 7D Mark II; Fujifilm X-T3_ Static sweep in [g83](../docs/gui/g83-barrido-objetivos-restantes.md).
- ⬜ Starry Sky AF — _Origin: Olympus E-M1 II_ Static sweep in [g83](../docs/gui/g83-barrido-objetivos-restantes.md).
- ⬜ Intelligent Subject Detection AF — _Origin: Olympus E-M1X_ Static sweep in [g83](../docs/gui/g83-barrido-objetivos-restantes.md).

### System and connectivity

- ⬜ USB charging while powered on — _Origin: ≈Sony α7 II_ Static sweep in [g83](../docs/gui/g83-barrido-objetivos-restantes.md).
- ⬜ FTP Background Transfer — _Origin: Sony α9_ Static sweep in [g83](../docs/gui/g83-barrido-objetivos-restantes.md).

## Discarded

- ❌ Post Focus — _Origin: Panasonic GH5, G9_. Depends on 4K/6K Photo (discarded in g50: no readout mode of 3840+ columns, encoder too weak) and the A6000 has no touchscreen (no panel in the service manual; the firmware «Touch» strings belong to face detection). Variants: focus sweep in FHD video → `G50-FHDPHOTO`; full-resolution burst sweep → Focus Shift Shooting. See [g52](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g52-post-focus.md).
- ❌ 4K/6K Photo (incl. 4K Photo Burst S/S) — _Origin: Panasonic GH5, G9_. The A6000's IMX210 only reads 6000×4000 at 15 fps or 1996×1124 at 60 Hz (no mode of 3840+ columns), the encoder tops out at 1080p60 (about 135 Mpx/s vs 249 for 4K30) and the firmware lacks the A6300's Photo Capture view. See [g50](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g50-4k-6k-photo.md).
- ❌ Digital level (virtual horizon) — _Origin: ≈Sony α6300_. The A6000 has no accelerometer: its orientation sensor (SE7750) is optical and each of its two channels is only high or low, so it tells four 90° positions apart and nothing in between. Measured over SWD while rotating the camera ([R88](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r88-sensor-inclinacion-swd.md)).
