# 15. SWD recovery (EXPERIMENTAL)

Linked reports are in Spanish.

> **EXPERIMENTAL.** Only the read-only phases (1 to 7) have been run on a camera, on 2026-11-03 ([R47](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r47-primer-contacto-swd-lectura-ram.md)); no write has been tried. It is a plan derived from static analysis and emulation. It can damage the board or lose calibration data. There is no guarantee it works. Every phase needs your own authorization and judgment.

Applies only to an A6000 bricked after installing 3.25 (LED 3 slow + 2 fast; Loader3 error −302, **inferred**, not measured). Cause and status: [Current state](en-14-Current-state). Full technical detail (Spanish): [R46](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r46-procedimiento-fisico-swd.md).

## Idea

An SWD debugger on the BIONZ could write the NAND without the BootROM key (which we do not know). Then the factory updater is brought back and official firmware is installed over USB. Rationale: [R37](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r37-cierre-estatico-recuperacion.md), [R38](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r38-guard-y-entrada-updater.md), [R40](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r40-jtag-swd-bionz.md).

## What is known and what is not

| Item | Status |
|---|---|
| SWCLK = ball W25 and SWDIO = ball W26 of IC6000 (BIONZ), to CN4906 pins 11/12 via R4911/R4912 | Schematic |
| R4911, R4912, R4915, R4916 and CN4906 **not populated** (footprints only) | User-confirmed (2026-11-02) |
| No bootloader touches the CoreSight DAP | Binary (R40) |
| Real SWCLK/SWDIO voltage (assumed ≈ 3.15 V) | **Not measured** |
| Whether an eFuse blocks debugging | **Unknown**; if it does, this route is dropped |
| OpenOCD/pyOCD support for the CXD90014 | **Not demonstrated** |
| NAND writes from the BIONZ (MuMin logical layer) | Static analysis and emulation only ([R39](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r39-estatico-profundo.md)) |

## Materials

- SWD probe with target-voltage reference: J-Link EDU Mini, or a Raspberry Pi Pico with `debugprobe` (fixed 3.3 V; do not use it if the line reads 1.8 V).
- Multimeter with continuity. No oscilloscope needed.
- Fine-tip soldering iron and thin solder with flux; 30–38 AWG enameled wire; magnifier or microscope; desoldering braid.
- Precision screwdrivers, ESD gear, Kapton tape.
- Regulated 3.8–4.2 V supply limited to 1 A, or a charged NP-FW50 battery.
- Optional: 0 Ω resistors (0402/0603, only for variant 5b) and an 8-channel logic analyzer.

## Before starting

1. Make the **external R1 backup** and verify it (still pending).
2. Install OpenOCD or pyOCD and check the probe is detected **without** connecting it to the camera.
3. Decide in advance what will be written (phase 8).

## Phases

Each phase has a stop criterion. If it is not met, stop and document.

1. **Open and photograph.** Battery out, wait 5 min. Open per the service manual, bag screws by zone, and photograph both sides of the SY-1028 board. Locate CN4906, R4911, R4912 and IC6000.
2. **Identify.** Compare against the schematic. Confirm R4915 and R4916 are empty (so Darwin does not fight the probe). Mark the R4911/R4912 pads and the nearest ground.
3. **Continuity (camera off).** Check which pad of each resistor goes to the BIONZ and which to CN4906; that board ground is common; and no shorts between SWCLK/SWDIO and ground or supplies. A low reading or a short stops the procedure.
4. **Voltage (camera powered, no probe).** Measure D_3.15V_MSS and the SWCLK/SWDIO pads to ground. 3.0–3.3 V: continue. 1.8 V or anything else: do not connect a 3.3 V probe.
5. **Connect the wires (camera off).**
   - **5a (recommended):** a wire straight to the BIONZ-side pad of R4911 and of R4912, plus a ground wire. Secure with Kapton.
   - **5b:** fit 0 Ω resistors (or 22 Ω, max 47 Ω) in R4911/R4912 and solder to CN4906 pads 11/12. Harder: fine pitch.
   - Length ≤ 15 cm. Check continuity and shorts before going on.
6. **First contact with the DAP (read only).** Connect GND first, then SWCLK/SWDIO. With the camera powered, run an SWD scan at 100 kHz (`dap info`); drop to 10–50 kHz if there is no answer. Success: valid IDCODE. Abort: no answer after checking voltage, wiring and speed, or debugging disabled by an eFuse.
7. **Read.** Halt the core and read `0xc0001200` (key table), `[0xc006000c]` and the log buffer at `0xc006001c…`. Confirm the real error code and dump the useful RAM with a SHA-256.
8. **Choose the write, with a prior backup of whatever is readable from `nflasha2` and `nflasha3`:**
   - **A.** Create `\updater\mode` in `nflasha2` (R37/R38): the factory updater in `nflasha1` boots and accepts firmware over USB.
   - **B.** Rewrite `nflasha3` with the good 20-10 image ([R30](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r30-updater-done-boundary.md)).
   - Both must respect ECC, geometry and bad blocks. Neither has been run.
9. **Close.** Remove the probe and wires, reassemble, check boot, and install the official **3.26** package over USB (prepared in R37). 3.25c ([R45](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r45-firmware-325c-experimental.md)) is also experimental and not recommended.

## Stop conditions

- A short, an abnormal reading or unexpected voltage.
- Smell, heat or current above 1 A.
- The DAP reports debugging disabled.
- Any doubt about what is written or where: do not write.

## Risks

- Soldering 0402 pads is irreversible and can lift traces; secure the wires so they do not pull.
- A wrong voltage on SWCLK/SWDIO can damage the BIONZ.
- A bad write to `nflasha2` can lose calibration data.
- If an eFuse blocks the DAP this route is useless; what remains is an external NAND read (no NAND identified), Sony service or a board swap.
