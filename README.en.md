# Sony A6000 — electronic shutter and CFW

[![Versión en español](https://img.shields.io/badge/🇪🇸_Versión_en_español-blue?style=for-the-badge)](README.md)

[![modules](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-modulos.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![sessions](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-sesiones.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![tests](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-pruebas.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![CI](https://github.com/nicolvus/a6000-fw-decomp/actions/workflows/tests.yml/badge.svg)](https://github.com/nicolvus/a6000-fw-decomp/actions/workflows/tests.yml)
[![Featured in Awesome REA](https://img.shields.io/badge/Featured%20in-Awesome%20REA-f0b429)](https://github.com/AIshihzong/awesome-reverse-engineer-anything)

Reverse engineering of the Sony A6000 (ILCE-6000: BIONZ + Darwin microcontroller) **3.21** firmware to get
**electronic shutter** operation and to add features the camera never had. The repository holds analysis, patches,
scripts and documentation; Sony's firmware is not versioned here (`scripts/agent/bootstrap.sh` downloads it from
Sony's server).

## Current state (2026-11-25)

| Area | Status | Evidence |
|---|---|---|
| **Electronic shutter** | **Works** on the author's camera from CFW **3.30** (inline `pkt[0x0e]` + Darwin gate). **3.23** was the first milestone: a 2-byte patch to Darwin and the camera shoots without moving motor or coils | [R54](docs/capture/e26-r54-paquete-330-envio-pkt0e.md), [T040](docs/capture/registro-pruebas-camara.md) |
| **Calibrated Silent** | Uniform row exposure; CFW **3.77** levels it from 1/1250 to 1/50 (E = 17.135 µs·n + 564 µs) | [R87](docs/capture/e26-r87-disparo-remoto-y-recalibracion.md) |
| **EFCS** | EFCS/Electronic selector in the menu. With EFCS on, ≈1.27 ms are lost and the frame is **black from 1/1000**, also with stock Sony firmware: the cause is physical, not firmware | [R74](docs/capture/e26-r74-conclusion-final-efcs-negro.md), [R83](docs/capture/e26-r83-informe-final-efcs-negro.md) |
| **Author's camera** | CFW of the 3.93/4.0x series on top of the Silent base (`pp` is the last audited build); the stock 3.21 roll-back package is verified | [G105](docs/gui/g105-builds-por-funcion.md), [CFW audit](reports/film-pb-1-auditoria-cfw-20261127.md) |
| **Video (FILM-PB-1)** | **Open**: clips record fine and play on a PC, but the camera will not play them. Patched code was ruled out; the likely cause is the «PAL/NTSC selector» not matching the clip frame rate, and that setting is not exposed in this model's menu | [likely cause](reports/film-pb-1-causa-sistema-tv-20261127.md) |
| **GUI** | QEMU harness that boots `im.elf` 3.21 and draws menus, icons and settings without the camera; CFWs are built on top of it | [GUI lane](docs/gui/README.md), [G22](docs/gui/g22-arnes-ui-qemu.md) |
| **USB charging while on** | Under investigation: the command reaches Darwin but is not applied by a wall charger | [report](docs/capture/usb-carga-encendida.md) |
| **Recovery** | Closed: camera recovered on 2026-11-03 over SWD, forcing the factory updater without writing NAND | [R49](docs/capture/e26-r49-cierre-recuperacion-326.md) |

## Firmware series

These numbers are **internal builds**, not Sony versions: each one is a `.dat` built from stock 3.21 and verified
offline before installing. They are flashed with `pmca-console firmware --flash` (and `--reflash` to switch between
builds sharing a version number).

| Build | What it adds | Status |
|---|---|---|
| 3.23 / 3.24 | Darwin patch: shutter motor and coils never move / same payload numbered 3.24 | 3.23 installed and confirmed on the camera; 3.24 verified offline |
| 3.25 | EFCS/Electronic selector from the menu | **Left the camera unable to boot**: TPZL format of `nflasha3` (E26 incident, [R36](docs/capture/e26-r36-causa-fallo-325.md)) |
| 3.25c / 3.26 / 3.27 | 3.25 with `nflasha3` in Sony's shape, plus the roll-backs | 3.26 installed by the stock updater to recover the camera; 3.27 = 3.25c installed |
| 3.30 – 3.38 | Real electronic shutter (inline `pkt[0x0e]`) and calibration | Installed and tested on the camera |
| 3.76 / 3.77 | Silent calibrated in `av-cam` (ShutMode 0 + `r5`) | Validated in RAM; base of the following CFWs |
| 3.93 (`base`/`film`/`pp`/`exfine`/`iso`) | One build per feature on the Silent base: Film Simulation, Picture Profile, Extra Fine, ISO | Installed and tested one by one; `iso` leaves the camera in a boot loop |
| 4.01 – 4.02 | Film recipe driven from the GUI + Fn icons; video bisection (Silent only) | Installed; FILM-PB-1 is detected at this point |
| 4.03 / 4.04 | 4.02 core with Sony's `/usr` / stock 3.21 minus `nflasha5` (control) | Built and audited, not installed |

## Limits and risks

> **⚠️ Installing modified firmware can brick the camera.** BIONZ recovery over SWD is proven
> ([R48](docs/capture/e26-r48-plan-recuperacion-actualizador-swd.md),
> [R49](docs/capture/e26-r49-cierre-recuperacion-326.md)), but **no independent recovery of the Darwin firmware has
> been demonstrated** and everything has been tried on **one camera** only. Read
> [Current state and limits](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-14-Current-state) before touching
> anything.

- The electronic shutter is measured on one camera and one sensor unit; with EFCS on, black frames from 1/1000.
- With the current CFW the camera **cannot play video** (FILM-PB-1); recording and playing on a PC do work.
- The dashboard figures (modules, sessions, tests) measure documentation and verifiers, not camera behaviour.

## Documentation

| Where | What |
|---|---|
| **[Wiki](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-Home)** ([source](wiki/en-Home.md), EN/ES) | Requirements and risks, end-to-end reproduction, how the patch works, results, current state, tools, glossary and repository map |
| [Progress board](https://nicolvus.github.io/a6000-fw-decomp/progress/) · [site home](https://nicolvus.github.io/a6000-fw-decomp/) | Status, coverage and tests generated from the repository |
| [knowledge/CURRENT.md](knowledge/CURRENT.md) | Minimal context for agents |
| [docs/STATE.md](docs/STATE.md) | Standing conclusions and limits |
| [docs/PENDIENTES.md](docs/PENDIENTES.md) | Open, blocked and closed tasks (single source) |
| [docs/INDEX.md](docs/INDEX.md) | Reports by subsystem; the reports live in [`docs/capture/`](docs/capture/) and [`reports/`](reports/) |
| [FUNCIONES.md](FUNCIONES.md) | Full list of target features |

Research reports and code comments are in **Spanish**; the wiki and this README come in Spanish and English.

## Target features

**On the camera:** Silent base, Picture Profiles PP1–PP10 (menu, lists and selector), Film Simulation, Extra Fine
(with the open «no space on card» bug) and the GUI's own icons and texts. **Built and audited, boot loop still to
solve:** expanded ISO. **Under research:** LUTs, HLG, 1/8000 and the rest of the list. Per-feature status and origin
model in [FUNCIONES.md](FUNCIONES.md) and [Goals](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-16-Goals).

**Ruled out for now:** digital level (the orientation sensor is optical and binary,
[R88](docs/capture/e26-r88-sensor-inclinacion-swd.md)), anamorphic desqueeze (`av-cam` 3.21's parameter table does
not define it) and open gate recording at 6000×4000 (the sensor delivers 14.98 Hz; the only firmware path would be
1440×960, [G112](docs/gui/g112-opengate-video-3-2.md)).

## Build and install

1. `scripts/agent/bootstrap.sh` downloads stock 3.21 from Sony (the repository holds **no** firmware).
2. Packages are built with the repository scripts: see
   [Building the packages](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-4-Building-the-packages) and
   [Installing 3.23](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-5-Installing-3.23). `.dat` files are not
   published in the repository or in a release.
3. Before any camera test: NVRAM backup and the owner's explicit authorisation; the IP comes from `A6000_HOST`.

## Repository layout

```
docs/        reports (capture/), state, pending tasks, index, GUI lane (gui/)
knowledge/   minimal context, history and knowledge graphs
scripts/     bootstrap, package builds, GUI harness, analysis tools
tests/       verifiers for every conclusion (pytest; firmware tests are skipped)
analysis/    reproducible evidence and results
wiki/        wiki source (Spanish pages and en-* English counterparts)
src/, tools/, references/, projects/   analysis code, utilities and third-party references
```

## Quality and contributing

`CI=1 python -m pytest tests -q`, plus `ruff` and `mypy` with no new warnings; CI never uses firmware. Full rules in
[CONTRIBUTING.en.md](CONTRIBUTING.en.md).

## Copyright and use

**Copyright.** The `.dat` files built with these scripts are Sony's stock firmware with a minimal, documented binary
change in `darwin_core.bin` and `av-cam.bin` (see
[How the patch works](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-8-How-the-patch-works)). The original
firmware is © Sony Corporation, which keeps all rights to it; the author holds no Sony licence and this repository
claims no ownership over it. The project's openness covers only what the author wrote (scripts, analysis,
documentation), not Sony's part. It is published for research and interoperability (reverse engineering of hardware
the author owns), without Sony source code. This note states the author's position; it is not a legal warranty.

**Use.** Everything is provided «as is», without warranty of any kind; using it is at your own risk and can brick the
camera. Meant for research, learning and personal use on a camera you own. The author's code, scripts, analysis and
documentation are under the [MIT](LICENSE) licence, which does **not** cover Sony's firmware or the third-party
material below.

**Sony and third-party material:**

- **Source code published by Sony** (Linux and other open packages): used to understand boot, drivers and the
  console. Keeps its original licence.
- **Level 3 service manual** for the ILCE-6000/6000L/6000Y (Rev. 1.1), publicly available: source of schematics and
  board sheets. The PDF is not versioned; `references/manuals/` only holds the manifest with hash, origin and a few
  sample pages.
- **Stock 3.21 firmware**: downloaded by each user from Sony's server.
- **Third-party tools** under their own licences: [Sony-PMCA-RE](https://github.com/ma1co/Sony-PMCA-RE),
  [fwtool.py](https://github.com/ma1co/fwtool.py) and
  [OpenMemories-Tweak](https://github.com/ma1co/OpenMemories-Tweak).
