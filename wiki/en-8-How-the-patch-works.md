# 8. How the patch works

The shutter is driven by **Darwin**, a separate microcontroller (`darwin_core`) that moves the mechanical curtains and re-cocks them after each shot.
3.23 only modifies `darwin_core.bin` of the official 3.21 firmware (157,276 B, load address `0x4200`), in two stacked steps:

| Step | Change in `darwin_core.bin` | Effect |
|---|---|---|
| **Type 0** | `0x20c78..0x20c7f` → `b 0x20c8e; nop; nop; nop` (`09e000bf00bf00bf`) | The mechanism-type function `0x20c74` always returns 0 (an existing "no coils" branch): P4D/P4E are not energized |
| **B1a** | `0x1fe6a: 28 46 → 0a e0` (2 bytes) | The gate `0x1fe66` always returns 0; the starters pick the list `[0,7,8,9,10]`, which does not use the shutter motor on capture or re-cocking |

Capture and re-cocking never reach the primitives that drive P40/P41; the exposure is set by the sensor (row-by-row reset and readout).
Then `darwin.sum` (CRC-32 and size) is updated and the FDAT is repacked: it is decrypted with `CXD90014`, the header and `DEND` CRCs are recomputed and the `.dat` is written.

## Why only Darwin is touched

Changing only Darwin leaves the compressed partitions (`nflasha3`) untouched, which is the part that bricked the camera with 3.25.
3.23 went through the same updater and the same Loader3 with Sony's own `nflasha3`.

## More detail (Spanish)

- [E25 mechanical shutter disabling](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e25-desactivacion-mecanica.md)
- [Independent audit E25-06](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e25-06-auditoria-independiente-paquetes.md)
- [Package preparation E25-05](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e25-05-preparacion-paquetes-323-324.md)
