# 14. Current state and limits

Linked reports are in Spanish.

| Aspect | State (2026-11-01) |
|---|---|
| Camera | **Bricked** after installing 3.25 (updater at 100 % and Done; user's account, no UART capture or NAND read) |
| Cause | **Identified offline** ([R36](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r36-causa-fallo-325.md)): 3.25's recompressed `nflasha3` does not follow the format the hardware decompressor reads (359/369 blocks start mid-sector and Loader3 does not pass that offset on; 3 blocks are a single 64 KiB record instead of 16 × 4 KiB). The first read of the partition fails and Loader3 returns −302 (3 slow + 2 fast). 3.23 did not touch `nflasha3`. Physical confirmation is missing (LED video; the UART is silenced, R37) |
| Recovery | Only `nflasha3` needs restoring, and a good copy exists ([R30](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r30-updater-done-boundary.md)). The BootROM serial path opens on every boot but requires a key stored in `nflasha0`, which was never dumped ([R32](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r32-moderreg-valor-real.md), [R33](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r33-veracidad-clave-nflasha0.md)). Minimal physical step identified ([R37](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r37-cierre-estatico-recuperacion.md)): an empty `\updater\mode` file in `nflasha2` makes Loader3 start the factory updater in `nflasha1` (intact) and accept firmware over USB; the **3.26** package (stock content) is ready. In the last `nflasha2` dump **1 logical byte** is enough (restoring a deleted `MODE` entry, [R38](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r38-guard-y-entrada-updater.md)), and the updater guard accepts 3.26. That byte cannot be reprogrammed in place with an external reader (MuMin + ECC, [R39](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r39-estatico-profundo.md)): it has to be written from the BIONZ itself. Next step: repair the camera or replace the mainboard |
| Silent shutter | Achieved with 3.23 (T040, confirmed by the user); row-by-row exposure measured in the RAW ([E25-10](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e25-10-exposicion-por-fila.md)) |
| EFCS / Electronic selector (3.25) | Implemented and verified **offline only** (emulation); never validated on the camera ([E25-24b](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e25-24b-implementacion-selector.md), [E25-27](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e25-27-construccion-firmware-integrado.md)) |
| 3.25c (fixed 3.25) | **Experimental and theoretical**, published as the *pre-release* [`fw-3.25c-experimental`](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.25c-experimental): fixes the `nflasha3` defects that bricked the camera (30/30 checks, emulation 0/369 failures vs 361 for 3.25). **Never installed**; the new BIONZ/Darwin code has never run on hardware ([R45](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r45-firmware-325c-experimental.md)) |
| Verification | 4,427 local tests (those that read firmware are skipped in CI); label census 133/372; 295 S sessions with a report (numbered in parallel up to S630; they are not 630) + 85 E phase reports; 12/24 physical plans with a test; log T001–T056 |

**Last milestone:** E26 R45 (2026-11-01) — 3.25c (fixed 3.25) built, verified offline on the final `.dat` and published as an experimental,
theoretical *pre-release*; never installed on a camera. Per-report detail in [knowledge/CURRENT.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/knowledge/CURRENT.md).

## Limits and risks

- **No independent recovery** ([E24-04](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e24-04-dictamen-seguridad.md), [E25-04](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e25-04-recuperabilidad-y-decision.md)): Darwin also controls power. The real case is 3.25.
- **Offline does not guarantee booting:** 3.25 passed every offline check and bricked the camera ([R36](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-r36-causa-fallo-325.md)).
- **Untested scenarios with 3.23:** Darwin operation 5 (P40/P41=3) and P4B/P4C are still active; their physical effect was not measured.
- **Backup:** the external copy of the backup (R1) is still unverified.

See also the [step-by-step verification](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-Home) and [Requirements and risks](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-1-Requirements-and-risks).

Progress board (documentation coverage, sessions and tests): <https://nicolvus.github.io/a6000-fw-decomp/progress/>.
