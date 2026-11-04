# 7. Rollback and recovery

## Back to stock Darwin (3.24)

```sh
pmca-console firmware -f a6000-custom-fw-3.24-recovery-stock-darwin.dat
```

- It is only accepted if the camera is on **3.23** and still has access to the updater.
- Restores Sony's official 3.21 Darwin with version number 3.24.
- **Verified offline only (69/69, byte for byte); never installed on a real camera.**
- It is not an independent recovery of the microcontroller: if the camera does not boot, 3.24 cannot be installed.

## Corrupted NVRAM or odd settings

Service mode + `scripts/senser_backup_restore.py FILE SHA256` with your backup ([step 3](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-3-NVRAM-backup)). Tested on hardware on 2026-10-20.

## The 3.25 incident and 3.25c

3.25 integrated an EFCS/Electronic selector into the firmware by modifying `av-cam.bin` inside `nflasha3`. After installing it, the author's camera does not boot
(LED 3 slow + 2 fast, Loader3 error code −302). Cause identified offline ([R36](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r36-causa-fallo-325.md), Spanish):
the recompressed `nflasha3` did not follow the format the hardware decompressor reads (blocks starting mid-sector and a single 64 KiB record
instead of 16 × 4 KiB). Physical confirmation is missing. The original 3.25 is not published.

**3.25c** ([release](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.25c-experimental), [R45](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r45-firmware-325c-experimental.md))
has the same features with `nflasha3` in Sony's format: 0 decompressor violations, 366/369 blocks identical to Sony's and 0 failures in the emulation
of the real bootloader (3.25 fails on 361). **It should boot, but it has never been installed**, and its new BIONZ/Darwin code has only run in emulation.
Requirements: official firmware 3.21 (or 3.23/3.24), charged battery and an NVRAM backup; it does **not** help a camera that already installed the original 3.25.
To go back to Sony firmware after 3.25c use **3.26** from the same release (3.24 is no longer accepted after a 3.25).
If you prefer the tested path: **3.23 + layer 2 in RAM, without touching `nflasha3`.**

**That camera was recovered (2026-11-03, [R49](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r49-cierre-recuperacion-326.md), Spanish).** Over SWD, Loader3 was made to boot the factory updater by forcing a single CPU register, with no NAND write; the updater then installed stock **3.26** over USB. Method and limits: [15. SWD recovery](en-15-SWD-recovery-experimental). It requires opening the camera and soldering; this is a single case, not a guarantee. Other paths studied and not used: restoring `nflasha3` from a copy, or writing `\updater\mode` into `nflasha2` (Loader3 ignores block writes, R48 §2.1).

## If your camera does not boot

Stop. Do not try to flash anything else. Open an *issue* in the repository with the LED pattern and the last step, and keep your NVRAM backup. If nothing works, the last resort is replacing the mainboard.
