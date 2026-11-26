# Evidencia — parche de `libmpr.so` que crea el sector FBM `0x31` (2ª iteración, QEMU)

Todo QEMU sobre **copias** de los volcados; la cámara no se ha tocado y no se ha usado `mcp_rea`.
Informe: [`reports/film-pb-1-sub-fbm-sector31-20261126.md`](../../../film-pb-1-sub-fbm-sector31-20261126.md).
Medidas crudas: [`medidas.txt`](medidas.txt).

## Parche

| fichero | qué es |
|---|---|
| `parche_fbm31_v3.py` | **parche final**: gancho `0x7126E6` → `bl 0x93B000` + cueva de `0x40` B en `0x93B000` (PC-relativo, sin literales). Salida `build/cfw_fbm_sector31_v3/libmpr.so`, sha256 `9be37312…00640`, 68 B distintos |
| `auditoria-parche-v3.txt` | salida de la auditoría del ELF (relocaciones, `ldr/adr` pc-relativos, punteros, diff exacto, cabeceras, desensamblado) |
| `emula_cueva.py` · `emulacion-cueva-v3.txt` | pre-vuelo en Unicorn (Cortex-A15/Thumb-2) de la cueva: éxito, error y handle distinto |
| `parche_fbm31_v2.py` · `auditoria-parche-v2.txt` | v2 (descartada): llevaba el literal `0x00A36A64` en `.rodata`, sin reubicar → SIGSEGV (ver `run-v2-crash/`) |
| `parche_fbm31.py` · `auditoria-parche.txt` | v1 (descartada): `InitBackupData(6,3)`, bloqueada por la guarda `+0x10` de `0x9D23FC` |
| `build_shim_fbm.sh` | compila `sonyshim-fbm.c` → `sonyshim.so` con la receta de `scripts/gui/harness/shim/build.sh` |

## Arnés

| fichero | qué es |
|---|---|
| `sonyshim-fbm.c` | shim del arnés + hilo `FBMTAB` (vuelca `0xA3699C` cada 5 s) y sonda `FBMPROBE=1` (tabla completa, `CheckExistSector`/`OpenSector32`/`GetSectorInfo` del `0x31`, `GetIdx` de `(0x21,3)`/`(0x04,3)` y `ReadFirstPackData` en un proceso hijo) |
| `fbm_run.py` | lanzador: initrd con overlay propio, `NFLASH4=<sha256[:12]>` en `SHIMENV`, `FBMFIN` (espera al final del guion), `NF4DUMP`/`NF4IMG` (diff y extracción de la imagen) |
| `im_fbm.sh` | guion del invitado; bloque `NF4DUMP=1` que compara `/cam/nflasha4.img` con la prístina y la saca por consola con `NF4IMG=1` |
| `run-r0/` | **sin parche**, imagen D1: `nh=1` (`0xA0`), `CheckExistSector(0x31)=0x48`, `ReadFirstPackData=0x10100001` |
| `run-v2-crash/` | parche **v2**: SIGSEGV en `0x93B010` (`addr=0xA36A68`) por el literal sin reubicar |
| `run-r1v3/` | **parche v3**, imagen D1: `nh=2` (`0x31`,`0xA0`), `idx10 sector=0x0031 handle=2 valido=1 om=6`, `CheckExistSector=0x45`, `ReadFirstPackData=0x10100003`; NAND `+394 B` en `0x9D400`; `nflash4.img` escrita (sha256 `609afa73…`) y `pagina-9D400-{antes,despues}.bin` |
| `run-r2/` | **sin parche**, imagen de `run-r1v3`: `nh=1`, `CheckExistSector(0x31)=0x48`, `ReadFirstPackData=0x10100001` (la persistencia no va sola) |
| `run-r2b/` | **parche v3**, imagen de `run-r1v3`: `nh=2`, `0x10100003`; el DFB escribe otra página de control en `0x3D800` |
| `run-sin/`, `run-con/`, `run-control/`, `run-control-d3/` | pasadas de la **1ª iteración** (v1 con `InitBackupData(6,3)`, sin `NFLASH4` en `SHIMENV`): `nh=0`; se conservan por trazabilidad |
| `run-r2c/` | igual que `r2b` con `NF4IMG=1`: imagen extraída, 1160 B distintos en los sectores 236/237, **492/493**, 1514/1515 (`sector-492.bin`: página con `81`,`a0`,`31`) |

## Tablas y desensamblados (1ª iteración, siguen valiendo)

`tabla-9D23FC.txt` (37 × `0x18`), `lista-9D2380.txt` (los 30 fileType, `0x31` = índice 10),
`tabla-9D2794-fileTypeSizeInfo.txt`, `dump-ram-camara.py`/`.txt` (los 4 handles de la cámara),
`dis/` (desensamblados de `WriteBaseData`, `CreateSector_Body`, `0x2B3000`, `0x2B2E54`, `0x2B45A8`…),
`find_cave.py`, `elfh.py`, `sonyshim-fbm.c`.

Las dos imágenes completas de 10 MiB (`run-r1v3/nflash4.img`, `run-r2c/nflash4.img`) **se borraron**
tras medirlas (no se versionan volcados de NAND); queda su sha256, el diff exacto en `medidas.txt` y
la página de control en bytes (`run-r1v3/pagina-9D400-*.bin`, `run-r2c/sector-492.bin`). Se
reconstruyen aplicando esos 394 B sobre el volcado de origen.

Imágenes usadas (sha256 de 10 485 760 B):
`analysis/camera-dumps/nand-20261020/dev_nflasha4.bin` → `a5ab15ca743950d6a8c64c17a8ed024cddc6d5c94a24a08cf60ca5d4e9ac7247`;
la escrita por el parche → `609afa7308d10b9738e1677e48a67b9b040a42d6f4999df85ef1c8a3271ded9b`
(idéntica a la de `reports/evidence/fbm-initb-6-3-nflasha4-20261126/run5`).
