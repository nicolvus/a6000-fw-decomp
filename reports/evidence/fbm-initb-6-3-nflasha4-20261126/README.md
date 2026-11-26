# Evidencia — `FBM InitB 6 3` con /dev/nflasha4 real emulado (`NFLASH4=1`)

Todo es QEMU sobre una **copia** del volcado; la cámara no se ha tocado y no se ha usado `mcp_rea`.

| fichero | qué es |
|---|---|
| `nf4inject.c` | 2º `.so` precargado (junto a `sonyshim.so`): espera a que `FBM::Init` llene `0xA3699C`, vuelca la tabla, ejecuta `FBM …` por el handler real `0x2B50D8`, mide `0x2B3000` / `BackupMgr::InitBackupData` / `CreateSector32` / `GetErrorString`, llama a `BkRead 0x2B39B8` y compara `/nflasha4.img` con `/usr/share/nflasha4.img`. Modos por `NF4MODE`: `main` (InitB 6 3 + CreateSector32 + SetSMI + `BkRead(0x04,3)`), `b21h` (`BkRead(0x21,3)` con handle), `b21`, `ver` (imagen ya parcheada) |
| `nf4inject-v1.c` | primera versión (run1): sólo `InitB 6 3` + `CreateSector32` + dos `BkRead` |
| `pb_run_nf4.py` | lanzador: `run.build_initrd(..., nflash4=IMAGEN)` + `qemu_cmd`, `-serial file:consola.log`; reescribe en memoria la línea `LD_PRELOAD=` de `im.sh` para precargar los dos `.so`; corta la VM al `[FBMC] FIN` |
| `make_page.py` | reconstruye en `/tmp` las dos imágenes (origen y origen + página `0x9D400`) desde el volcado del repo; **no** se versionan los 10 MiB |
| `comando.sh` | repetición completa (build + tres pasadas) |
| `run1/consola.log` | 1ª pasada: `InitB 6 3` → tabla 1/30, `CreateSector32(0x31)` → `ret=0`, `BkRead(0x04,3)` → `0x10100001`; la 2ª `BkRead` se bloquea |
| `run2/consola.log` | tabla estática `0x9D23FC` en vivo (`fn=0/arg=0` en las 37), `0x2B3000(6,3)`→`0x10800010`, `0x2B3000(9,8)`→`0x10800010`, `InitBackupData(6,3)`→`0x10800010` |
| `run3/consola.log` | **pasada buena**: diffs por paso (`inicio`=0 B, `tras-InitB`=0 B, `tras-CreateSector32`=394 B), volcado hex de la página nueva, `SetSMI`, `BkRead(0x04,3)`=`0x10100003` |
| `run3/ctrl_page_9d400.bin` | los 1 KiB de la página de control nueva tal cual quedaron en `/nflasha4.img` (seq `0x2C2`, entradas `0x81`, `0xA0`, `0x31`) |
| `run3/pagina-0x9D400.txt` | la misma página en texto (cabecera, seq, cks y las 18 entradas de 8 B) |
| `run5/consola.log` | control: imagen con la página parcheada → al arrancar sigue 1/30 (no abre `0x31`); `BkRead(0x04,3)`=`0x10100001` |
| `run6/consola.log` | `BkRead(0x21,3)` con handle → `0x10100003` (la 2ª lectura del proceso se bloquea) |
| `run7/consola.log` | `BkRead(0x21,3)` sin handle (primera del proceso) → `0x10100001` |

Imágenes usadas (sha256):
- origen = `analysis/camera-dumps/nand-20261020/dev_nflasha4.bin` → `a5ab15ca743950d6a8c64c17a8ed024cddc6d5c94a24a08cf60ca5d4e9ac7247` (10 485 760 B)
- parcheada (run5) → `609afa7308d10b9738e1677e48a67b9b040a42d6f4999df85ef1c8a3271ded9b`

Perfil del arnés: `analysis/gui/g22/harness/live/nf4/` (ignorado por git, como los demás `live/*`).
El `sonyshim.so` es el del arnés (`analysis/gui/g22/harness/overlay/cam/usr/lib/sonyshim.so`, 21-11), sin recompilar.

Nota: durante la sesión las copias de 10 MiB vivieron en este directorio (`nflasha4-origen.bin`,
`nflasha4-con-sector-31.bin`) y se borraron al terminar; los `.bin` de NAND no se versionan.
