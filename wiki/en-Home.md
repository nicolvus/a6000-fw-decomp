# Sony a6000 CFW Wiki — Silent Shutter

[🇪🇸 Versión en español](https://github.com/nicolvus/a6000-fw-decomp/wiki/Home)

An end-to-end guide to reproducing the **completely silent** shutter on the Sony A6000 (ILCE-6000), obtained by reverse engineering
firmware 3.21: the Darwin microcontroller stops moving the mechanical curtains and the sensor controls the exposure.

> ⚠️ **Installing modified firmware can brick the camera.** There is no proven independent recovery: a later firmware
> (3.25, not published) left the author's camera unable to boot. Its fixed version,
> [3.25c](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.25c-experimental), should work but is **experimental and has
> never been installed** ([page 7](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-7-Rollback-and-recovery)). Read [Requirements and risks](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-1-Requirements-and-risks) before you start.

The wiki is available in English and Spanish. The research reports linked from it (`docs/capture/`, `knowledge/`, `docs/STATE.md`) are in **Spanish** only.

## Reproduction path

| Step | What you get | Page |
|---|---|---|
| 1 | Understand what you need and what can go wrong | [Requirements and risks](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-1-Requirements-and-risks) |
| 2 | Repository, Python environment and unpacked official 3.21 firmware | [Environment and official firmware](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-2-Environment-and-official-firmware) |
| 3 | A backup of **your** camera's NVRAM | [NVRAM backup](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-3-NVRAM-backup) |
| 4 | The 3.23 and 3.24 `.dat` files built by you (or the release ones) and verified | [Building the packages](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-4-Building-the-packages) |
| 5 | Camera on 3.23: mechanical shutter inactive | [Installing 3.23](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-5-Installing-3.23) |
| 6 | Optional: uniform row-by-row exposure (RAM patch) | [Layer 2](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-6-Layer-2-uniform-exposure) |
| 7 | What to do if something fails | [Rollback and recovery](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-7-Rollback-and-recovery) |

All scripts and apps, with their usage: [Tools](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-12-Tools).

To understand the why: [How the patch works](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-8-How-the-patch-works), [Results and limits](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-9-Results-and-limits) and the
[repository map](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-10-Repository-map). Legal notice: [Copyright and use](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-11-Copyright-and-use).

## What is verified and what is not

| Step | Verification |
|---|---|
| Building the 3.23 and 3.24 `.dat` files from the official firmware | **Reproduced on 2026-11-01**: same SHA-256 as the release, 69/69 checks |
| Probing the guard without flashing | Tested offline and with the camera in MTP mode |
| NVRAM backup and restore | Tested on hardware (2026-10-20) |
| Installing 3.23 | **Confirmed on a real camera** (T040/T041, 2026-10-27), from an intermediate 3.22 |
| Installing 3.23 directly from 3.21 | Verified offline only (the guard accepts it); not installed that way |
| Installing 3.24 | **Never installed on a real camera** |
| Installing 3.25c | **Never installed on a real camera**; verified offline (30/30 checks, bootloader emulation with no failures) |
| Layer 2 (RAM patch) | Tested in T050; absolute scale with ±25 % uncertainty |
| Installing Tweak and RemoteShutter with the instructions in this wiki | The author already had them installed; the steps written here come from the documentation and **have not been re-run from scratch** |
| Layer 2 without a PC (from the camera) | Idea only, not implemented |

Glossary of terms and labels: [Glossary](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-13-Glossary).

## Status in one line

3.23 installed and confirmed on a real camera (2026-10-27): it shoots silently and without errors. 3.24 (back to stock Darwin) is only
verified offline and was never installed on a real camera. 3.25c is published as experimental and has never been installed.
