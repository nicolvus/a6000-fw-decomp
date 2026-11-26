# Sony a6000 CFW Wiki — Silent Shutter

[🇪🇸 Versión en español](https://github.com/nicolvus/a6000-fw-decomp/wiki/Home)

An end-to-end guide to reproducing the **completely silent** shutter on the Sony A6000 (ILCE-6000), obtained by reverse engineering
firmware 3.21: the Darwin microcontroller stops moving the mechanical curtains and the sensor controls the exposure.

> ⚠️ **Installing modified firmware can brick the camera.** There is no proven independent recovery: 3.25 (not published) left the
> author's camera unable to boot and it was only recovered over SWD
> ([page 15](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-15-SWD-recovery-experimental)). The fixed 3.25 was installed as **3.27**
> and from **3.30** on the camera shoots with the electronic shutter. Read [Requirements and risks](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-1-Requirements-and-risks) before you start.

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

### After 3.23

3.23 is the **minimal patch** that leaves the mechanical shutter idle, and this guide uses it as the replication path. The line went on
like this (state and links in [14. Current state](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-14-Current-state)):

| Build | What it added |
|---|---|
| 3.25 / 3.25c / 3.27 | EFCS/Electronic selector in the firmware. 3.25 bricked the camera; the fixed build was installed as 3.27 |
| 3.30 – 3.35 | Real **electronic** shutter (inline `pkt[0x0e]` + Darwin gate) and calibrated exposure |
| 3.77 | Silent calibrated inside the firmware: the [layer 2](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-6-Layer-2-uniform-exposure) RAM patch is no longer needed |
| 3.93 | One build per feature on the Silent base (Film Simulation, Picture Profile, Extra Fine, ISO) plus the UI harness |

Standing limits: with **EFCS on** the frame is black from 1/1000 (physical cause, also with Sony firmware) and CFWs **do not play video**
(FILM-PB-1). `.dat` files are not published as releases: they are built with the repository scripts
([page 4](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-4-Building-the-packages)).

All scripts and apps, with their usage: [Tools](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-12-Tools).

To understand the why: [How the patch works](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-8-How-the-patch-works), [Results and limits](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-9-Results-and-limits) and the
[repository map](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-10-Repository-map). Legal notice: [Copyright and use](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-11-Copyright-and-use).

## What is verified and what is not

| Step | Verification |
|---|---|
| Building the 3.23 and 3.24 `.dat` files from the official firmware | **Reproduced on 2026-11-01**: same SHA-256 as the reference files, 69/69 checks |
| Probing the guard without flashing | Tested offline and with the camera in MTP mode |
| NVRAM backup and restore | Tested on hardware (2026-10-20) |
| Installing 3.23 | **Confirmed on a real camera** (T040/T041, 2026-10-27), from an intermediate 3.22 |
| Installing 3.23 directly from 3.21 | Verified offline only (the guard accepts it); not installed that way |
| Installing 3.24 | **Never installed on a real camera** |
| Installing 3.25c | **Installed as 3.27** (2026-11-03): it boots; the selector was never seen as 1 in the packet sent to Darwin ([R52](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r52-prueba-fisica-selector-327.md)) |
| Layer 2 (RAM patch) | Tested in T050; absolute scale with ±25 % uncertainty |
| Installing Tweak and RemoteShutter with the instructions in this wiki | The author already had them installed; the steps written here come from the documentation and **have not been re-run from scratch** |
| Layer 2 without a PC (from the camera) | Idea only, not implemented |

Glossary of terms and labels: [Glossary](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-13-Glossary).

## Status in one line

**Electronic** shutter working since **3.30** and Silent calibrated in the firmware since **3.77**; 3.23 remains the minimal patch
confirmed on a real camera (2026-10-27). The author's camera runs a CFW of the **3.93/4.0x** series and with it the camera **does not play
video** (FILM-PB-1); the likely cause is the PAL/NTSC setting against the clip frame rate. 3.24 (back to stock Darwin) is only verified
offline.
