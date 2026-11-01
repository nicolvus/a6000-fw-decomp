# 2. Entorno y firmware oficial

El repositorio **no contiene firmware de Sony** (`firmware/`, `*.bin`, `*.elf` están en `.gitignore`). Se descarga el oficial y se desempaqueta.

```sh
git clone https://github.com/nicolvus/a6000-fw-decomp.git sony-a6000-electronic-shutter
cd sony-a6000-electronic-shutter
scripts/agent/bootstrap.sh --dry-run   # muestra los pasos sin tocar nada
scripts/agent/bootstrap.sh             # idempotente; puede relanzarse tras un fallo
```

El script descarga el `Update_ILCE6000V321.dmg` oficial desde el servidor de Sony, crea `.venv` y `.venv-fwtool`, lo descomprime con `7z`
y lo desempaqueta con `fwtool.py`. Para esta guía basta lo que deja en `firmware/extracted/fw321/`. (Además baja Ghidra y JDK, ~800 MB, útiles
solo para la investigación; puedes interrumpirlo tras el paso 3 «Desempaquetado con fwtool» si solo quieres construir los paquetes.)

## Comprobaciones

```sh
sha256sum firmware/original/Update_ILCE6000V321.dmg
# 844349ff7edddc294c0fddd90a454848eeda8987b6bf043c9757982b3a42ba3e
sha256sum firmware/extracted/fw321/firmware.fdat
# 603b42ec9d2dd66b91e38c15a6a23e860fb8af46a072050903506672036f0f90
sha256sum firmware/extracted/fw321/firmware.tar
# 970246492293e9175ef67b1ad587d5289ae886d47dbd10e77637d9bee458d5a8
```

Si el hash del `.dmg` no coincide (Sony cambió o retiró el archivo), **detente**: no sigas con otro firmware.

## Si falla

- `fwtool` falla en la sección WBI anidada → procedimiento alterno en `docs/firmware-analysis.md`.
- No hay `requirements.txt`: si un script pide un paquete, `.venv/bin/pip install <paquete>`.
- Dependencias del bootstrap: `git curl 7z node npm unzip tar python3`.
