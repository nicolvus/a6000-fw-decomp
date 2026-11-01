# 1. Requirements and risks

## What you need

| Item | Detail |
|---|---|
| Camera | Sony A6000 (ILCE-6000) on **official firmware 3.21** (version from `pmca info`) |
| Battery and cable | Charged battery and a USB data cable |
| PC | Linux (tested on Arch/CachyOS), Python 3, `git`, `curl`, `7z`, `unzip`, `tar` |
| `pmca-console` | [Sony-PMCA-RE](https://github.com/ma1co/Sony-PMCA-RE) (also included in `references/pmca/`) |
| Layer 2 only | Camera Wi-Fi on your network, OpenMemories Tweak (telnet/ADB) and the RemoteShutter app ([page 6](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-6-Layer-2-uniform-exposure)) |

3.22 is **not** required: it was an intermediate package by the author (coils off only) and 3.23 already includes that change.

## Risks (read them)

- **No independent recovery.** Darwin also controls power; a Darwin or BIONZ that does not boot has no proven way back over USB.
- **3.24 was never installed on a real camera.** It only works if the camera still has access to the updater and is on 3.23.
- **Offline verification does not guarantee booting.** 3.25 passed every offline check and still bricked the author's camera.
  3.25c adds the checks that would have caught that failure (decompressor format and emulation of the real bootloader), but it is still untested on a camera.
- **Untested scenarios with 3.23:** Darwin operation 5 (P40/P41=3) and P4B/P4C are still active; their physical effect was not measured. Neither were flash, video and Live View with the patches active.
- The updater only accepts versions **strictly higher** than the installed one: you cannot "downgrade".

## Project safety rules

1. NVRAM backup before touching anything ([page 3](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-3-NVRAM-backup)).
2. Verify the SHA-256 of every `.dat` before flashing.
3. Probe the updater guard without flashing (`fdat_guard_probe.py`).
4. Log every camera test in `docs/capture/registro-pruebas-camara.md`.
5. **This project gives you no warranty at all.** Do it at your own risk ([Copyright and use](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-11-Copyright-and-use)).
