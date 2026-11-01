# 2. Environment and official firmware

The repository **does not contain Sony firmware** (`firmware/`, `*.bin`, `*.elf` are in `.gitignore`). You download the official one and unpack it.

```sh
git clone https://github.com/nicolvus/a6000-fw-decomp.git sony-a6000-electronic-shutter
cd sony-a6000-electronic-shutter
scripts/agent/bootstrap.sh --dry-run   # shows the steps without touching anything
scripts/agent/bootstrap.sh             # idempotent; can be re-run after a failure
```

The script downloads the official `Update_ILCE6000V321.dmg` from Sony's server, creates `.venv` and `.venv-fwtool`, extracts it with `7z`
and unpacks it with `fwtool.py`. For this guide, what it leaves in `firmware/extracted/fw321/` is enough. (It also downloads Ghidra and a JDK, ~800 MB, which
are only useful for research; you can stop it after step 3 "Desempaquetado con fwtool" if you only want to build the packages.)

## Checks

```sh
sha256sum firmware/original/Update_ILCE6000V321.dmg
# 844349ff7edddc294c0fddd90a454848eeda8987b6bf043c9757982b3a42ba3e
sha256sum firmware/extracted/fw321/firmware.fdat
# 603b42ec9d2dd66b91e38c15a6a23e860fb8af46a072050903506672036f0f90
sha256sum firmware/extracted/fw321/firmware.tar
# 970246492293e9175ef67b1ad587d5289ae886d47dbd10e77637d9bee458d5a8
```

If the `.dmg` hash does not match (Sony changed or removed the file), **stop**: do not continue with a different firmware.

## If it fails

- `fwtool` fails on the nested WBI section → alternative procedure in `docs/firmware-analysis.md`.
- If a script asks for a missing package: `.venv/bin/pip install -r requirements.txt` (or `.venv/bin/pip install <package>`).
- Bootstrap dependencies: `git curl 7z node npm unzip tar python3`.
