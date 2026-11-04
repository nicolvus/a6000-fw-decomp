# 9. Results and limits

## What was measured with 3.23

- **Full images** (JPEG 6000×4000 and ARW 6024×4024) without the mechanical shutter.
- **Shooting and re-cocking:** 36/36 shots in bursts of 6 and 10/10 single shots; re-cocking in 0.7–1.0 s; 2.6–2.9 s latency at fast speeds.
- **Exposure** (E25-10): without a rear curtain row `i` integrates T + ≈7 ms + 15.2 µs·i (readout ≈ 61 ms), so from 1/4000 to 1/500 the shutter speed barely scales.
  With [layer 2](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-6-Layer-2-uniform-exposure) the exposure is uniform.

## Weak points

- With layer 1 (3.23) alone the exposure is not uniform.
- Measured range 1/4000 to 1/30; from 1/15 normal shooting comes back; 1/8000 emulated only; long electronic exposure not implemented.
- Rolling effect due to the ≈ 61 ms readout.
- Layer 2 needs telnet and RemoteShutter, and is applied on every shot or burst.
- Not measured: flash, video, Live View with the patches, Darwin operation 5 (P40/P41=3) and P4B/P4C.
- Absolute scale with ±25 % uncertainty.
- Baseline risk: flashing modified firmware with no proven independent recovery.

## Versions

| Version | What it does | Result |
|---|---|---|
| 3.21 | Sony official | Normal mechanical shutter |
| 3.22 | Darwin "type 0" (coils off); intermediate package by the author | Installed (T024); boots. Effect deduced from the code |
| 3.23 | 3.22 + B1a | Installed (T040); shoots silently and without errors |
| 3.24 | Stock Darwin with version number 3.24 | Prepared, not installed |
| 3.25 | Integrated with the EFCS/Electronic selector | **The camera does not boot** (not published) |
| 3.25c | 3.25 with `nflasha3` in Sony's format | Published as experimental; verified offline (30/30, emulation with no failures); **never installed** |
| 3.26 | Recovery with stock 3.21 content | Published with 3.25c to roll back; verified offline; the 3.26 recovery package was installed once to recover the author's camera ([R49](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r49-cierre-recuperacion-326.md)) |
