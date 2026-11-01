# 5. Installing 3.23

> Only do this with an NVRAM backup ([step 3](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-3-NVRAM-backup)), verified hashes ([step 4](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-4-Building-the-packages)), a charged battery and the camera on 3.21.

```sh
pmca-console firmware -f a6000-custom-fw-3.23-b1a-silent-shutter.dat
pmca-console info          # must show version 3.23
```

- Do not disconnect or turn off the camera during the update.
- Write down the result in `docs/capture/registro-pruebas-camara.md`.
- Tested by the author on 2026-10-27 (T040/T041) from an intermediate 3.22; from a direct 3.21 the guard accepts it (verified offline) but the author did not install it that way.

## What to expect

The mechanical shutter becomes **completely inactive**: it does not move on capture or re-cocking. The camera shoots silently and without errors.
Without [layer 2](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-6-Layer-2-uniform-exposure) the exposure is **not uniform** (the bottom of the image gets more light): see [Results and limits](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-9-Results-and-limits).

## Minimal test

Take a normal shot and check: no shutter noise, full image (JPEG 6000×4000 / ARW 6024×4024), no error message and re-cocking in ~0.7–1.0 s.
