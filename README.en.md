# Sony A6000 — Silent Shutter

[![Versión en español](https://img.shields.io/badge/🇪🇸_Versión_en_español-blue?style=for-the-badge)](README.md)

[![modules](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-modulos.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![sessions](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-sesiones.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![tests](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-pruebas.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![CI](https://github.com/nicolvus/a6000-fw-decomp/actions/workflows/tests.yml/badge.svg)](https://github.com/nicolvus/a6000-fw-decomp/actions/workflows/tests.yml)

Reverse engineering of the Sony A6000 firmware 3.21 (ILCE-6000: BIONZ + Darwin microcontroller) to shoot with a fully
electronic shutter. **Milestone:** with the modified firmware **3.23** (a 2-byte patch to Darwin) the real camera shot
silently and without errors. **Later**, the integrated firmware **3.25** left the camera unable to boot because of a format error
in the `nflasha3` partition, now identified and fixed in **3.25c**. That camera was **recovered on 2026-11-03 over SWD** and now boots stock firmware 3.26 ([R49](docs/capture/e26-r49-cierre-recuperacion-326.md)).

> **⚠️ 3.25c: experimental.** [3.25c](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.25c-experimental) fixes the errors
> that bricked 3.25 (30/30 checks, and an emulation of the real bootloader with no failures) and **should** boot, but it **has never been
> installed on a camera**. The original 3.25 is not published. Installing any modified firmware can leave the camera unusable and **there is
> no proven independent recovery**. Read [Current state and limits](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-14-Current-state).

## Documentation

All the detail lives in the **[Sony a6000 CFW Wiki](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-Home)** (source in [`wiki/`](wiki/en-Home.md)): requirements and risks, how to reproduce it end to end, how the patch works,
results, current state and limits, tools, glossary and repository map. The wiki is available in English and Spanish; the research reports and code comments are in **Spanish**.
Prebuilt packages are in the [`fw-3.23-3.24` release](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.23-3.24) and, as an
experimental *pre-release*, in [`fw-3.25c-experimental`](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.25c-experimental) (3.25c and a 3.26 to roll back).
[Progress board](https://nicolvus.github.io/a6000-fw-decomp/progress/) (current state, coverage and tests) · [site home](https://nicolvus.github.io/a6000-fw-decomp/).

| Version | What it does | Status |
|---|---|---|
| 3.23 | Darwin patch: the shutter motor and coils never move | **Installed and confirmed** on a real camera: silent, no errors |
| 3.24 | Stock Darwin with version number 3.24 (roll back from 3.23) | Verified offline, never installed |
| 3.25 | EFCS / Electronic selector from the menu | **Bricked the author's camera** (not published) |
| 3.25c | 3.25 with `nflasha3` in Sony's exact format | Published as experimental; verified offline, **never installed** |
| 3.26 | Stock Sony content with version number 3.26 (roll back from 3.25c) | Verified offline; installed once on the author's camera to recover it ([R49](docs/capture/e26-r49-cierre-recuperacion-326.md)) |

**Status:** firmware 3.23 (T040) makes the camera shoot silently and without errors; 3.25 (E26) left the author's camera unable to boot;
its cause is fixed in 3.25c (experimental, untested on a camera, [R45](docs/capture/e26-r45-firmware-325c-experimental.md)) and that camera was recovered over SWD with the stock updater and 3.26 ([R49](docs/capture/e26-r49-cierre-recuperacion-326.md)).
Details in [Current state and limits](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-14-Current-state). Contributing: [CONTRIBUTING.en.md](CONTRIBUTING.en.md).

## Target features

Details in [Goals](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-16-Goals) (✅ = verified on the camera). ≈ = Sony model from memory, unverified (web search only confirmed Silent Shooting → α7S, FTP → α9 and AF Track Sens → α99 II); may not be the first.

| Feature | Category | Origin | Status |
|---|---|---|---|
| Silent Shooting | In progress | Sony α7S | ⬜ |
| Picture Profiles PP1–PP10 | In progress | ≈Sony α7R III | ⬜ |
| Maximum shutter speed 1/8000 | Photo | ≈Sony α7 | ⬜ |
| Expanded ISO up to 409600 | Photo | Sony α7S | ⬜ |
| Pixel Shift Multi Shooting / High Res Shot / Handheld High Res Shot | Photo | ≈Sony α7R III; Olympus E-M1 II, E-M1X; Panasonic G9 | ⬜ |
| 4K/6K Photo (incl. 4K Photo Burst S/S) | Photo | Panasonic GH5, G9 | ⬜ |
| Pre Capture photo / Pro Capture / Pre-Burst 4K/6K | Photo | Olympus E-M1 II; Panasonic GH5, G9 | ⬜ |
| Post Focus | Photo | Panasonic GH5, G9 | ⬜ |
| Multiple Exposure | Photo | Canon EOS 7D Mark II; Nikon D850; Olympus E-M1 II | ⬜ |
| Live Composite | Photo | Olympus E-M1 II | ⬜ |
| Live Bulb / Live Time | Photo | Olympus E-M1 II | ⬜ |
| Bulb Timer | Photo | Canon EOS 7D Mark II | ⬜ |
| Focus Shift Shooting / Focus Stacking | Photo | Nikon D850; Panasonic GH5, G9; Olympus E-M1 II, E-M1X | ⬜ |
| Smile Shutter | Photo | Sony α5100 | ⬜ |
| Internal intervalometer | Photo | ≈Sony α9 | ⬜ |
| Interval AE Tracking Sensitivity / Exposure Smoothing | Photo | ≈Sony α7R III; Nikon D850 | ⬜ |
| Anti-Flicker Shooting / Flicker Reduction / Flicker Scan | Photo | Canon EOS 7D Mark II; Nikon D500, D850; Fujifilm X-T3; Olympus E-M1 II, E-M1X | ⬜ |
| Keystone Compensation | Photo | Olympus E-M1 II, E-M1X | ⬜ |
| Live ND | Photo | Olympus E-M1X | ⬜ |
| In-camera photo rating | Photo | ≈Sony α9 | ⬜ |
| S-Log2 | Image and color | ≈Sony α7S | ⬜ |
| S-Log3 | Image and color | ≈Sony α7S II | ⬜ |
| HLG 1-3 | Image and color | ≈Sony α7R III | ⬜ |
| D Range Priority | Image and color | Fujifilm X-T3 | ⬜ |
| Color Chrome Effect | Image and color | Fujifilm X-T3 | ⬜ |
| LUT import | Image and color | Sony ZV-E1 | ⬜ |
| Direct film simulation | Image and color | Fujifilm X-T5 | ⬜ |
| Full HD / HD 120 fps | Video | ≈Sony α6300 | ⬜ |
| Variable Frame Rate | Video | Panasonic GH5 | ⬜ |
| Internal 4K | Video | ≈Sony α7R II | ⬜ |
| Dual Video Recording | Video | ≈Sony α7R III | ⬜ |
| 4K HDMI output | Video | Sony α7S | ⬜ |
| Timecode / User Bit | Video | ≈Sony α7S II | ⬜ |
| Loop Recording | Video | Panasonic GH5 | ⬜ |
| Movie Silent Control / Silent Multi Controller | Video | Fujifilm X-T3; Sony α99 II | ⬜ |
| Anamorphic Desqueeze | Video | Panasonic GH5 | ⬜ |
| Synchro Scan | Video | Panasonic GH5 | ⬜ |
| Auto Object Framing | Video | ≈Sony ZV-E1 | ⬜ |
| Voice Memo | Video | ≈Sony α9 | ⬜ |
| Zebra 0–109 % | Monitoring | ≈Sony α6400 | ⬜ |
| Waveform Monitor | Monitoring | Panasonic GH5 | ⬜ |
| Vectorscope | Monitoring | Panasonic GH5 | ⬜ |
| Gamma Display Assist | Monitoring | ≈Sony α7R III | ⬜ |
| Sports Finder Mode | Monitoring | Fujifilm X-T3 | ⬜ |
| Real-time Eye AF | Focus | ≈Sony α9 | ⬜ |
| Real-time AF tracking (3D Tracking / EOS iTR AF) | Focus | ≈Sony α6400; Nikon D500, D850; Canon EOS 7D Mark II | ⬜ |
| AF tracking sensitivity settings (AF-C Custom Settings / AF-C Cases) | Focus | Sony α99 II; Fujifilm X-T3; Panasonic GH5; Olympus E-M1 II; Canon EOS 7D Mark II | ⬜ |
| AF Acceleration/Deceleration Tracking | Focus | Canon EOS 7D Mark II | ⬜ |
| AF Range Control | Focus | ≈Sony α99 II | ⬜ |
| AF Micro Adjustment | Focus | ≈Sony α99 | ⬜ |
| Pre-AF | Focus | Fujifilm X-T3 | ⬜ |
| AF Point Auto Switching / Zone Area Switching | Focus | Canon EOS 7D Mark II; Fujifilm X-T3 | ⬜ |
| Starry Sky AF | Focus | Olympus E-M1 II | ⬜ |
| Intelligent Subject Detection AF | Focus | Olympus E-M1X | ⬜ |
| USB charging while powered on | System and connectivity | ≈Sony α7 II | ⬜ |
| FTP Background Transfer | System and connectivity | Sony α9 | ⬜ |

## Copyright and use

**Copyright.** The two `.dat` files in the [`fw-3.23-3.24` release](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.23-3.24) are
Sony's official 3.21 firmware with a minimal, documented binary change to `darwin_core.bin` (2–9 bytes; see
[How the patch works](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-8-How-the-patch-works) and [E25-05](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e25-05-preparacion-paquetes-323-324.md)).
The ones in the [`fw-3.25c-experimental` release](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.25c-experimental) are the same firmware
with 22 bytes changed in `darwin_core.bin` and 89 in `av-cam.bin` (3.25c), or unchanged except for the version number (3.26)
([R45](docs/capture/e26-r45-firmware-325c-experimental.md)).
The original firmware is © Sony Corporation, which keeps all rights to it. The author **holds no license from Sony** for that
firmware and this repository claims no ownership of it. The project being open does not change that: the openness covers only what
the author wrote (scripts, analysis, documentation), not the Sony part contained in the `.dat` files.
They are published for research and interoperability purposes (reverse engineering to change the behavior of hardware the author
owns), without any Sony source code. This note states the author's position, it is not a legal guarantee, and the files will be
removed if Sony asks.

**Use.**
- Everything is provided "as is", without warranty of any kind; use it at your own risk, it can render the camera unusable (see [Current state and limits](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-14-Current-state)).
- Meant for research, learning and personal use on a camera you own. Do not use it to bypass protections for unlawful purposes or to redistribute Sony firmware on your own.
- The author's code, scripts, analysis and documentation are released under the [MIT](LICENSE) license. That license does **not** cover Sony's firmware, the release `.dat` files, or the third-party material below.

**Sony and third-party material used by the project**
- **Source code published by Sony** for this camera (Linux and other open-source packages). Used to understand the boot process, the drivers and the Loader2/Loader3 console. It keeps its original license (GPL and others); the extracted copies are in `analysis/session18/`.
- **Level 3 service manual** for the ILCE-6000/6000L/6000Y (Rev. 1.1), publicly available online. Used as a source of schematics and board sheets. The PDF is **not** versioned (it is in `.gitignore`); `references/manuals/` only holds the manifest with its hash and origin, plus a few sample pages.
- **Official firmware 3.21**: each person downloads it from Sony's server with `scripts/agent/bootstrap.sh`; it is not included in the repository.
- **Third-party tools** with their own licenses: [Sony-PMCA-RE](https://github.com/ma1co/Sony-PMCA-RE), [fwtool.py](https://github.com/ma1co/fwtool.py) and [OpenMemories-Tweak](https://github.com/ma1co/OpenMemories-Tweak) in `references/`.
