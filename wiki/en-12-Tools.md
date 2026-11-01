# 12. Tools

All paths are relative to the repository root. Activate the environment first: `source .venv/bin/activate`.

## On the PC (no camera)

| Tool | Purpose | Usage |
|---|---|---|
| `scripts/agent/bootstrap.sh` | Downloads official firmware 3.21, creates the environments and unpacks it | `scripts/agent/bootstrap.sh [--dry-run]` ([step 2](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-2-Environment-and-official-firmware)) |
| `references/fwtool/fwtool.py` | Unpacks/inspects `.dat` and FDAT | `python references/fwtool/fwtool.py unpack -f X.dat -o out/` |
| `scripts/replicar/generar_nucleos.py` | Patches the official `darwin_core.bin` (type 0 and B1a) and checks their SHA-256 | no arguments |
| `scripts/e25_05/build_packages.py` | Builds and verifies the 3.23 and 3.24 packages (69 checks, ≈ 85 s) | no arguments |
| `scripts/e25_27/build.py` / `verify_325c.py` | Builds 3.25c and runs its 30 checks and the bootloader emulation | `build.py --out DIR --package`, then `verify_325c.py` |
| `scripts/recovery/r1_manifest.py` | Inventory and hash verification of the backup and the packages | `verify` |
| `scripts/audit/repo_audit.py` | Audits links, cited paths, figures and SHA-256 | no arguments |
| REA / Ghidra | Firmware reverse engineering ([map](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-10-Repository-map)) | `docs/agent/bootstrap-desde-cero.md` §4 |

## With the camera over USB

| Tool | Purpose | Usage |
|---|---|---|
| `pmca-console` ([Sony-PMCA-RE](https://github.com/ma1co/Sony-PMCA-RE)) | Info, firmware flashing and app installation | `pmca-console info`, `pmca-console firmware -f X.dat` |
| `scripts/senser_backup_dump.py` | NVRAM backup, **read only** ([step 3](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-3-NVRAM-backup)) | `python scripts/senser_backup_dump.py DIR` |
| `scripts/senser_backup_restore.py` | Restores the NVRAM from your copy | `python scripts/senser_backup_restore.py FILE SHA256` |
| `scripts/fdat_guard_probe.py` | Probes the updater guard **without flashing** | `python scripts/fdat_guard_probe.py [VERSION ...]` |

## With the camera over Wi-Fi (telnet / ADB / HTTP)

Requirements: [layer 2](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-6-Layer-2-uniform-exposure) (Tweak with telnet and ADB enabled, RemoteShutter open). Set your camera's IP
with the `A6000_HOST` variable or `--host` (default `192.168.1.29`).

| Tool | Purpose | Usage |
|---|---|---|
| `scripts/camera_telnet.py` | Runs commands on the camera's `telnetd` (root, no login) | `python scripts/camera_telnet.py --host IP 'uname -a'` |
| `scripts/camera_install_apk.py` | Installs an APK over ADB (port 5555) | `python scripts/camera_install_apk.py APK [IP]` |
| `tools/remote-shutter/` | RemoteShutter app: HTTP server on port 8080 (`/shoot`, `/ss`, `/status`, `/info`, `/log`, `/jpg`) | `tools/remote-shutter/build.sh` (JDK 17 and build-tools in `~/.local/android-build`) |
| `scripts/camera_silent.py` | Layer 2 RAM patch with a 25 s watchdog: checks, patches, reverts and verifies | imported by the test scripts |
| `scripts/camera_silent_test.py` | T050 test pattern: watchdog, references, shots from 1/4000 to 1/30 and a burst of 4 | `python scripts/camera_silent_test.py OUT/` (fixed scene, hands off the camera) |
| `scripts/camera_suite.py` | Image verification suite: latency, EXIF, luminance, banding and re-cocking | `python scripts/camera_suite.py OUT/ [--host IP] [--quick]` |

## Rules when using them

- The read scripts write nothing; the RAM patch scripts first check the original bytes and do nothing if they do not match.
- Never test on the camera without an NVRAM backup.
- Log every test in `docs/capture/registro-pruebas-camara.md`.
