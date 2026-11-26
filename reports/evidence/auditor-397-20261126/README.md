# Evidencia — auditoría independiente 3.97 / rollback 3.98 (26-11-2026)

Todo se generó **desde cero** a partir de los `.dat` entregados; no se copió nada de auditorías previas.
No se ha tocado la cámara, no se ha usado `git` ni `mcp_rea`, no se ha instalado nada.

## Ficheros

| Fichero | Qué demuestra |
|---|---|
| `01-extrae.log` | sha256 del `.dat` (69447a27…), DEND, descifrado == `.fdat`, `firmware.tar` 0f2dac…, `nflasha15` 29ff5bee…, TPZL y ext2 |
| `02-elf.log` | cabecera/5 `PT_*`/25 secciones idénticas, bytes del gancho, cueva, 132 021 relocaciones sin aciertos, símbolos |
| `03-rodata-vecindad.log` | volcado de `.rodata` alrededor de 0x93B000: hueco de ceros 0x93AFD4..0x93B081 y cueva nueva |
| `04-contexto-literal.log` | el «puntero» a 0x93B014 en 0x495390 es parte de dos instrucciones (`str.w` + `lsls`), no un literal |
| `05-desasm-cueva.log` | desensamblado capstone de la cueva y del punto de gancho (fábrica y nuevo) |
| `06-firmas-llamadas.log` | sitios que llaman a 0x2B1DEC/0x2B43F0/0x2B4820/0x4A8864 y prólogos (firma real) |
| `07-llamante-712530.log` | función llamante completa: marco alineado y `r0..r3` muertos tras el gancho |
| `08-pila-y-2b4820.log` | prólogo de 0x2B4820 y ausencia de accesos de 64 bits en los tres destinos |
| `09-emulacion-cueva.log` | Unicorn: guarda 0 y 1, argumentos de las 3 llamadas |
| `10-emulacion-retorno.log` | Unicorn: retorno a 0x7126EA, SP y r4/r5 restaurados |
| `11-audit-397-base394.json` | `audit_package_nflasha15.py --base-dat <.dat 3.94>` → `todo_ok: true` (22/22) |
| `12-rollback-398.log` | 3.98: sha256, cabecera 3.98, `firmware.tar` == base 3.94 (`cmp`), 104 miembros idénticos, `libmpr` 9a74a3bb… |
| `13-hueco-referencias.log` | barrido de punteros de 32 bits a todo el hueco de ceros: 0 reales |
| `14-compara-397-394.log` | 3.97 vs 3.94: 2 miembros del tar, 1 fichero del ext2 (`lib/libmpr.so`), TPZL 2373 bloques / 13 distintos |
| `15-fsck.log` | e2fsck de fábrica (limpio) vs 3.94/3.97/3.98 (mismos avisos de contadores: heredados) |
| `16-shas-libmpr.txt` | sha256 de los cuatro `libmpr.so` (paquete, parche C, fábrica, rollback) |
| `17-push3-y-64bit.log` | recuento de `push` de 3 registros (2 127) y ausencia de `ldrd/strd/vldr/vstr` |

Scripts usados (reproducibles): `extrae.py`, `elf_analisis.py`, `emu_cueva.py`, `rollback398.py`,
`compara_397_394.py`.

## Reproducir

```sh
source .venv/bin/activate
export TMPDIR=$PWD/build/aud397/tmp      # /tmp suele estar lleno
python3 reports/evidence/auditor-397-20261126/extrae.py
python3 reports/evidence/auditor-397-20261126/elf_analisis.py
python3 reports/evidence/auditor-397-20261126/emu_cueva.py
python3 reports/evidence/auditor-397-20261126/compara_397_394.py
python3 reports/evidence/auditor-397-20261126/rollback398.py
python3 scripts/gui/audit_package_nflasha15.py \
  build/cfw_fbm31_pkg397/pkg-3.97/package-3.97/firmware_packed.dat \
  build/cfw_fbm31_pkg397/files --base-dat build/cfw_avcam_limpio/firmware_packed-3.94.dat
```
