# Evidencia — vía de consola que registra el sector 0x31 en `0xA3699C` (26-11-2026)

Todo es QEMU sobre **copias** del volcado de `/dev/nflasha4` (perfil `nf4`, `NFLASH4=1`): la cámara no se ha
tocado y no se ha usado `mcp_rea`. Informe: [`reports/film-pb-1-sub-consola-sector31-20261126.md`](../../film-pb-1-sub-consola-sector31-20261126.md).

## Respuesta en una línea

`FBM LTC 1` (o `FBM EWBDFD 4 3 0`) y después `FBM InitB 6 3` dejan **idx 10 = `0x31 / handle!=0 / +8=1`**,
`BkRead(0x04,3)` pasa de `0x10100001` a **`0`** (`LTC 1`) o **`0x10100003`** (`EWBDFD`), y **persiste** al
reiniciar porque queda escrito en `nflasha4` (1 300 B en 3 zonas).

## Ficheros

| fichero | qué es |
|---|---|
| `nf6inject.c` | 2º `.so` precargado (junto a `sonyshim.so`): espera a `FBM::Init`, vuelca `0xA3699C`/`0x9D23FC`, ejecuta líneas `FBM …` por el **handler real** `0x2B50D8`, mide `0x2B3000`/`BkRead` `0x2B39B8`, compara `/nflasha4.img` con el origen y **vuelca los tramos distintos en hex** (`DIFF`/`DIFFB`). Modos por `NF4MODE`: `orden` (ChgSec 6 3, ChgSec 4 3, CRFB, INRFB, DRWBI, WBI), `ewbdfd` (EWBDFD+InitB+WBI), `ewchg` (EWBDFD+ChgSec), `ltc` (LTC 1+InitB+WBI), `ver` (sólo mirar, para la 2ª pasada) |
| `pb_run_nf6.py` | lanzador: `run.build_initrd(..., nflash4=IMAGEN)` + `qemu_cmd`, `-serial file:consola.log`, precarga los dos `.so` reescribiendo en memoria la línea `LD_PRELOAD=` de `im.sh`; corta la VM en `[FBMC] FIN` |
| `make_page.py` | reconstruye en `/tmp` la copia de trabajo desde `analysis/camera-dumps/nand-20261020/dev_nflasha4.bin` (sha256 `a5ab15ca…7247`); **los 10 MiB no se versionan** |
| `patch_desde_log.py` | aplica los tramos `DIFF`/`DIFFB` del log sobre el volcado → imagen equivalente a la del invitado (para el reinicio real) |
| `comando.sh` | repetición completa (build + A, C, E, G + D, H, F) |
| `evidencia/mprdis.py` | desensamblador por VA de `libmpr.so` (capstone): nombres del `.dynsym`, PLT→símbolo importado, cadenas del pool de literales |
| `evidencia/tabla_cmds.py` | vuelca la tabla de comandos `0x7E7FAC` (29×12 B) con parser de cada argumento y destinos `bl` → `evidencia/tabla-comandos-fbm-detalle.txt` |
| `evidencia/xref_bl.py` | llamantes `bl`/`blx` (decodificación manual Thumb-2) de una VA |

## Pasadas (cada `consola.log` es la prueba)

| dir | qué mide | resultado |
|---|---|---|
| `runA-orden/` | `ChgSec 6 3`, `ChgSec 4 3`, `CRFB`, `INRFB`, `DRWBI`, `WBI` en ese orden | tabla 1/30 antes y después, **0 B** de flash en cada paso, `BkRead(0x04,3)` = **`0x10100001`**; `IsNeedRepairFlashBackup()` = 0; `WBI` devuelve 0 |
| `runC-ewbdfd-wbi/` | `EWBDFD 4 3 0` + `InitB 6 3` + `WBI` + volcado del diff | `0x9D23FC[13] fn=base+0x2B5185`; idx10 = **`0x31 h3 s1 om6`**; **1 300 B** en `0x9D400`/`0xBD780`/`0x380000`; `BkRead` = **`0x10100003`**; tras `WBI` idx10 = `h1/+8=1` |
| `runE-ewbdfd-chgsec/` | `EWBDFD 4 3 0` + `ChgSec 4 3` | **no crea** (0 B, tabla 1/30, `BkRead` = `0x10100001`): `ChangeSector` exige handle de origen (`0x10100006`) |
| `runG-ltc1/` | `LTC 1` + `InitB 6 3` + `WBI` + diff | `0x9D23FC`: `[04][05][13][14]` con `fn`/`arg` de prueba; idx10 = **`0x31 h3 s1 om6`**; **1 300 B**; `BkRead` = **`0`**; tras `WBI` `h1/+8=1` |
| `runD-reinicio/` | reinicio real con la imagen de `runC` | idx10 = **`0x31 h1 s1 om6`** ya en el arranque; `BkRead` = **`0x10100003`**; diff 0 B |
| `runH-reinicio-ltc1/` | reinicio real con la imagen de `runG` | idx10 = **`0x31 h1 s1 om6`**; `BkRead` = **`0`**; diff 0 B |
| `runF-sin-pagina-datos/` | imagen sin la página de datos `0x380000` | idx10 = `h1` pero **`+8=0`**; `BkRead` = `0x10100003` ⇒ el estado 1 lo pone la página de datos |

Imágenes (sha256):
- origen = volcado `dev_nflasha4.bin` → `a5ab15ca743950d6a8c64c17a8ed024cddc6d5c94a24a08cf60ca5d4e9ac7247` (10 485 760 B)
- tras `EWBDFD`+`InitB` → `6d2ab43aa2fe386dc4c4df0e3ed3c8633328f74d24112ef2e87770b57a5dca51` (1 300 B distintos)
- tras `LTC 1`+`InitB` → `4ae884d5bfaa5402e39c013f552f06d80c525201afed550e035ddf3627b220d8` (1 300 B distintos; 104 B de la página de datos difieren de la ruta `EWBDFD`)
- sin página de datos → `66e5380f4631845ddd443db91986fb2d80bfb405810aeaaec2154a1f36837b23` (788 B)

Perfil del arnés: `analysis/gui/g22/harness/live/nf4/` (ignorado por git, como los demás `live/*`).
`sonyshim.so` es el del arnés (`analysis/gui/g22/harness/overlay/cam/usr/lib/sonyshim.so`, 21-11), sin recompilar;
sólo se añade `nf6inject.so` al `LD_PRELOAD`.

Nota: durante la sesión las copias de 10 MiB vivieron en `/tmp` y **no** se versionan.
