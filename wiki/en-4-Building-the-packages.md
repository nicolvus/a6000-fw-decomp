# 4. Building the packages

**No `.dat` files are published:** neither in the git tree nor as GitHub Releases. The packages are built here from the official
3.21 firmware, which is what lets you check what they contain.

## 3.23 and 3.24 packages (minimal Darwin patch)

```sh
source .venv/bin/activate
python scripts/replicar/generar_nucleos.py        # 1. patches the OFFICIAL darwin_core.bin (type 0 and B1a) and checks its SHA-256
python scripts/e25_05/build_packages.py           # 2. builds and verifies the packages (≈ 85 s, 69 checks)
python -m pytest -q tests/test_e25_05_paquetes.py # 3. package tests
```

| File | Reference SHA-256 |
|---|---|
| `analysis/darwin-patch/fdat/experimental-323/firmware_packed.dat` (3.23) | `4c21353dc742bde86d66de6d3d6bdd8dc18f4c445c436399e768731ccf474542` |
| `analysis/darwin-patch/fdat/recuperacion-324/firmware_packed.dat` (3.24) | `e1345aff44270270fec8ae15014f3696cf98c06a07b9eaeb89ff6346e77c8f22` |

Source of the hashes: [E25-06](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e25-06-auditoria-independiente-paquetes.md).
Step 1 only changes bytes in `darwin_core.bin` (2–9 bytes, see [How the patch works](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-8-How-the-patch-works));
`build_packages.py` puts them back into Sony's `firmware.tar`, recomputes the Darwin CRC and checksum, encrypts with `CXD90014` and packs the `.dat`.
The outputs are git-ignored because they derive from Sony firmware.

## CFW of the 3.93 series (one build per feature)

Builds with new features are built on the **Silent base** by a single script; `--funciones` lets you install one feature at a time to
isolate a fault ([G105](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g105-builds-por-funcion.md)).

```sh
python scripts/gui/build_cfw_film.py build/cfw_func393/pp --version 3.93 --funciones pp
python scripts/gui/build_cfw_film.py build/cfw_func393/base --version 3.93 --funciones ''   # Silent only
python scripts/gui/build_cfw_film.py build/cfw_func393/film --version 3.93 --pp              # full Film CFW
python scripts/gui/audit_package_nflasha15.py --darwin-v3 --sin-wbi --bionz-g22 build/cfw_func393/pp
```

- Features available through `--funciones`: `base`, `film`, `pp`, `exfine`, `iso` (the script lists them if given an invalid value).
- `--iconos` / `--iconos-nativos`: own icons for the Fn menu or Sony's (CAM-394).
- Before installing, test the build in the UI harness: `scripts/gui/harness/setup.sh`
  ([G22](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/gui/g22-arnes-ui-qemu.md)).
- CFWs ship **without `nflasha5`** (cold boot) and with Darwin v3: that is the difference FILM-PB-1 investigates
  ([Current state](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-14-Current-state)).

## 3.25c (historical)

```sh
python scripts/e25_27/build.py --out analysis/e25-27/artifacts-325c --package   # ≈ 45 s, deterministic
python scripts/e25_27/verify_325c.py                                            # 30 checks + bootloader emulation
```

Expected `.dat` SHA-256: `d64ad6e3d203dfafae020fc777ae8e9fe4a77c49f1f469cf5b907a1a6a477752`. The verifier needs the 3.25 package that
bricked the camera as a negative control plus the author's `bootloader.bin` dumps; without them only the versioned evidence is checked
(`tests/test_e25_27_325c.py`). 3.25c was installed as 3.27 ([page 7](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-7-Rollback-and-recovery)).

## Inspecting what you built

```sh
python references/fwtool/fwtool.py unpack -f analysis/darwin-patch/fdat/experimental-323/firmware_packed.dat -o /tmp/exp323
```

## Measuring the guard without flashing

With the camera in MTP/mass-storage mode (nothing on it changes):

```sh
python scripts/fdat_guard_probe.py        # must reject the installed version and accept 3.23 and 3.24
```

## Reproducibility checked

On 2026-11-01 these steps were run from scratch on the official firmware and both resulting `.dat` files have **exactly** the SHA-256
in the table, with 69/69 checks.
