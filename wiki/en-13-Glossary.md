# 13. Glossary

## Hardware and firmware

| Term | Meaning |
|---|---|
| **A6000 / ILCE-6000** | The camera. FDAT model `0x41030035`, region 0 |
| **BIONZ (CXD90014)** | The main image processor/SoC (ARM) that runs Linux and the camera app |
| **Darwin** | Separate microcontroller that moves the mechanical curtains, re-cocks and controls power. Its firmware is `darwin_core.bin` |
| **Mechanical shutter / EFCS / electronic** | EFCS = electronic front curtain (the rear one is still mechanical). Electronic = no mechanical curtain at all; the sensor controls the exposure row by row |
| **IMX210 / IMX235** | Image sensors. Row-by-row readout takes ≈ 61 ms |
| **P4D/P4E coils, P40/P41 motor** | Darwin outputs that drive the curtain magnets and the re-cocking motor |
| **FDAT / `.dat`** | Firmware package format consumed by the updater; encrypted with `CXD90014` |
| **`nflasha0..3`** | NAND partitions. `nflasha3` is the compressed one that holds `av-cam.bin` |
| **`av-cam.bin`** | Main binary of the camera application on BIONZ |
| **Loader2 / Loader3 / BootROM** | Boot chain. Loader3 produces the −302 error seen with 3.25 (LED 3 slow + 2 fast) |
| **TPZL / LDEC** | Block compression format of `nflasha3` and the hardware decompressor that reads it |
| **NVRAM / backup** | Memory with each camera's settings and calibration; copied through service mode |
| **Service mode / updater** | USB camera modes used by `pmca` to dump the NVRAM and flash |

## Patches

| Term | Meaning |
|---|---|
| **Type 0** | Darwin patch: function `0x20c74` always returns 0, so the P4D/P4E coils are never energized (firmware 3.22) |
| **B1a** | 2-byte patch at `0x1fe6a`: Darwin does not drive the shutter motor on capture or re-cocking (3.23 = type 0 + B1a) |
| **Layer 1 / Layer 2** | Layer 1 = firmware 3.23; layer 2 = RAM patch (`ShutMode 0` + `r5`) for uniform exposure |
| **`ShutMode`** | BIONZ register (`0x836d6fb6`) that selects the shutter mode; the patch sets it to 0 |
| **`r5`** | Sensor exposure parameter (`0x836d7000`); (4219 − `r5`) × 15.2 µs is the exposure |
| **Watchdog** | `sh` process on the camera that reverts the RAM patch if the PC does not answer within 25 s |
| **3.25c** | 3.25 rebuilt with `nflasha3` in Sony's exact format; experimental, never installed |

## Report labels

| Label | Meaning |
|---|---|
| **Sxx** | Static/offline analysis session |
| **Exx / E25-nn** | Research phase with a report in `docs/capture/` (E25 = mechanical disabling; E26 = 3.25 incident and recovery) |
| **Rnn / E26-Rnn** | Recovery reports for the bricked camera (R36 = cause of the 3.25 failure; R45 = 3.25c) |
| **Tnnn** | Physical camera test, logged in `docs/capture/registro-pruebas-camara.md` (T040 = first silent shot with 3.23) |
| **VERIFICADO / PARCIAL / NO_VERIFICADO** | Evidence level of a conclusion (verified / partial / not verified) |
| **REA / Ghidra** | Reverse engineering tools: REA via MCP and the historical read-only Ghidra project |
