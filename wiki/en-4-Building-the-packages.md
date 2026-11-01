# 4. Building the 3.23 and 3.24 packages

Two options: use the prebuilt `.dat` files from the [`fw-3.23-3.24` release](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.23-3.24)
or build them yourself (so you can check what they contain). Both paths are verified with the same hashes.

## Expected hashes

| File | SHA-256 |
|---|---|
| `a6000-custom-fw-3.23-b1a-silent-shutter.dat` | `4c21353d…ccf474542` (full hash in the release) |
| `a6000-custom-fw-3.24-recovery-stock-darwin.dat` | `e1345aff…8f22` (full hash in the release) |

```sh
sha256sum -c SHA256SUMS.txt   # in the folder with the release .dat files and SHA256SUMS.txt
```

## Building from the official firmware

```sh
source .venv/bin/activate
python scripts/replicar/generar_nucleos.py        # 1. patches the OFFICIAL darwin_core.bin (type 0 and B1a) and checks their SHA-256
python scripts/e25_05/build_packages.py           # 2. builds and verifies the packages (≈ 85 s, 69 checks)
python -m pytest -q tests/test_e25_05_paquetes.py # 3. package tests
```

Outputs (ignored by git, they derive from Sony firmware):
`analysis/darwin-patch/fdat/experimental-323/firmware_packed.dat` (3.23) and `analysis/darwin-patch/fdat/recuperacion-324/firmware_packed.dat` (3.24).

Step 1 only changes bytes in `darwin_core.bin` (2–9 bytes, see [How it works](https://github.com/nicolvus/a6000-fw-decomp/wiki/en-8-How-the-patch-works)); `build_packages.py` puts them back into the official
`firmware.tar`, recomputes the CRC and the Darwin checksum, encrypts with `CXD90014` and packs the `.dat`.

## Building 3.25c (experimental)

```sh
python scripts/e25_27/build.py --out analysis/e25-27/artifacts-325c --package   # ≈ 45 s, deterministic
python scripts/e25_27/verify_325c.py                                              # 30 checks + bootloader emulation
```

Expected `.dat` SHA-256: `d64ad6e3d203dfafae020fc777ae8e9fe4a77c49f1f469cf5b907a1a6a477752`. The checker needs the 3.25 package that bricked
the camera as a negative control and `bootloader.bin` from the author's dumps; without them only the versioned evidence can be checked
(`tests/test_e25_27_325c.py`).

## Inspecting what you built

```sh
python references/fwtool/fwtool.py unpack -f analysis/darwin-patch/fdat/experimental-323/firmware_packed.dat -o /tmp/exp323
```

## Probing the guard without flashing

With the camera in MTP/mass storage mode (it changes nothing on the camera):

```sh
python scripts/fdat_guard_probe.py        # must reject the installed version and accept 3.23 and 3.24
```

## Verified reproducibility

On 2026-11-01 these steps were run from scratch on the official firmware and the two resulting `.dat` files have **exactly** the release SHA-256
(`4c21353d…` and `e1345aff…`), with 69/69 checks.
