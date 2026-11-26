# `FBM InitB 6 3` con `/dev/nflasha4` real emulado (`NFLASH4=1`)

**Fecha:** 2026-11-26 · **Binario:** `analysis/camera-extract/usr/lib/libmpr.so` (fw 3.21) · **Volcado:** `analysis/camera-dumps/nand-20261020/dev_nflasha4.bin` · **Evidencia:** `reports/evidence/fbm-initb-6-3-nflasha4-20261126/` · Cámara no usada (sólo QEMU); sin `mcp_rea`.

## Resumen (18 líneas)

1. Perfil nuevo `analysis/gui/g22/harness/live/nf4/`: el shim del arnés **no se toca**; se añade un 2º `.so` (`nf4inject.so`) y el lanzador reescribe en memoria la línea `LD_PRELOAD` de `im.sh` (`pb_run_nf4.py:51-56`).
2. Imagen: copia del volcado (sha256 `a5ab15ca743950d6a8c64c17a8ed024cddc6d5c94a24a08cf60ca5d4e9ac7247`, 10 485 760 B) → `run.build_initrd(nflash4=…)` la deja en `/usr/share/nflasha4.img` y `sonyshim.c:136-141` la copia a `/nflasha4.img` (fd real).
3. Con `NFLASH4=1` la tabla `0xA3699C` queda **1/30** tras el arranque (sólo `0xA0`: h1/s1/om9); con `/dev/null` inerte era 0/30.
4. `FBM InitB 6 3` por el handler real `0x2B50D8` devuelve **1** y la tabla **no cambia**: idx 10 = `031/h0/s0/om0` antes y después ⇒ **criterio FAIL** (run1, run2, run3).
5. Las otras 29 tampoco cambian: 1/30 antes, 1/30 después (sólo `0xA0`), ninguna empeora.
6. Causa medida (no es `CreateSector32`): `0x2B3000(6,3)` devuelve **`0x10800010`** y `WriteBaseData` (`0x2B4030`) aborta en `0x2B406A`/`0x2B4072` con línea `0xF47`, **antes** de `CreateSector32` (`0x2B40C8`).
7. Por qué falla `0x2B3000`: la tabla estática `0x9D23FC` tiene **`fn=0` y `arg=0` en sus 37 entradas** (volcado en vivo, run2/run3) y el bucle salta toda entrada con `fn==0` (`0x2B3018`-`0x2B301A`: `ldr r2,[r3,#4]` / `cbz r2`); sin coincidencia cae en `0x2B3034` y devuelve `0x10800010` (literal en `0x2B3088`).
8. Control `0x2B3000(9,8)` (par del sector `0xA0`) → también `0x10800010`: no es específico de (6,3).
9. `BackupMgr::InitBackupData(6,3)` (`0x2B43F0`) devuelve **`0x10800010`** — es el código que el comando imprime como `Error:0x10800010`.
10. `CreateSector32` ya **no** da `0x7`: `CreateSector32(0x31, 0, &h, &id)` → **`ret=0`, `handle=3`, `id=0x31`** (run3, run6; run1 ya daba `ret=0`). `GetErrorString(0)` = `"unknown"`.
11. El `0x7 = FBS_INVALID_PROCESS` era el `/dev/null` inerte: con la imagen real el FBS sí crea el sector.
12. `InitB 6 3` **no escribe nada** en la imagen (diff 0 B tras la orden, run3). Quien escribe es `CreateSector32`: **394 B** en la página `0x9D400` (página de control nueva, seq `0x2C2`, entradas `0x81`, `0xA0` y **`0x31`** = `31000000000507ff`, 5 bloques).
13. Lectura `RcsBackupTblData`: tras `InitB 6 3` no hay handle y las dos lecturas siguen dando **`0x10100001`** (`BkRead(0x04,3)` en run1/2/3/5; `BkRead(0x21,3)` en run7).
14. Con la entrada poblada (`FBM SetSMI 10 31 3 1 6`, sintético, sin NAND) las dos lecturas pasan a **`0x10100003`**: ya no es «sin reader», falla en `ReadPack` (`0x2B267C` → `FlashLib::ReadSector`; código fijado en `0x2B26FC`).
15. La **2ª** llamada a `BkRead` en el mismo proceso se queda bloqueada (run1/2/3/5/6); por eso `(0x04,3)` y `(0x21,3)` se midieron en pasadas distintas.
16. Control con la imagen ya parcheada (run5): al arrancar **no** abre `0x31` (sigue 1/30), aunque el arranque sí escribe en el dispositivo (766 B, `0x1d800`..`0xbd7ff`); causa no determinada.
17. El volcado del repo **no se modifica** (sha256 idéntico antes/después): se trabaja sobre copia y los cambios se miden en la copia del invitado (`/nflasha4.img`).
18. Comando exacto y perfil en §7; evidencia en `reports/evidence/fbm-initb-6-3-nflasha4-20261126/` (`README.md` con la tabla de ficheros).

---

## 1. Montaje: qué se añadió y qué no

- **Shim del arnés intacto.** `analysis/gui/g22/harness/overlay/cam/usr/lib/sonyshim.so` (21-11) es el que usa `build_initrd` (`run.py:44-45`); no se recompiló nada de `scripts/gui/harness/shim/`.
- **2º `.so` precargado:** `analysis/gui/g22/harness/live/nf4/overlay/cam/usr/lib/nf4inject.so` (fuente `reports/evidence/…/nf4inject.c`, 9,7 KiB). El lanzador sustituye en memoria `LD_PRELOAD=/usr/lib/sonyshim.so` por `LD_PRELOAD="/usr/lib/sonyshim.so /usr/lib/nf4inject.so"` (`pb_run_nf4.py:51-56`; el `im.sh` del repo no se toca). El inyector vive en su propio hilo y sólo usa `dlsym(RTLD_DEFAULT)` + desplazamientos de libmpr.
- **Imagen:** `pb_run_nf4.py` pone `LIVE_NFLASH4=<imagen>` (`live.py:74-84` añade `NFLASH4=<sha256[0:12]>` a `SHIMENV`) y pasa la imagen a `run.build_initrd(..., nflash4=IMAGEN)` (`run.py:50-52`), que la deja en `cam/usr/share/nflasha4.img`. El shim, en el primer `open("/dev/nflasha4")`, la copia a `/nflasha4.img` y devuelve ese fd real (`sonyshim.c:136-141`); el resto de dispositivos no modelados siguen siendo `/dev/null` (`sonyshim.c:142-143`).
- **Perfil:** `analysis/gui/g22/harness/live/nf4/` (sólo `overlay/cam/usr/lib/nf4inject.so`).

## 2. `InitB 6 3`: lo que pasa de verdad

Tabla `0xA3699C` (30 × 0x14 B) volcada desde el propio proceso, antes y después de la orden, con la imagen real (`run3/consola.log`):

| momento | `handle != 0` | idx 10 (`0x31`) |
|---|---|---|
| tras el arranque (`FBM::Init`) | **1/30** (`0xA0` = h1/s1/om9) | `031 h0 s0 om0` |
| tras `FBM View` + `FBM InitB 6 3` | **1/30** (idéntico) | `031 h0 s0 om0` |
| tras `SetSMI 10 31 3 1 6` (sintético) | 2/30 | `031 h3 s1 om6` |

- El handler devuelve `1` siempre (`0x2B5B5E`), así que **el retorno de la consola no dice nada** del resultado.
- Las otras 29 entradas quedan exactamente igual (misma ristra de `h/s/om` antes y después): el «no empeoran» se cumple por no tocarlas.
- Criterio pedido (idx 10 con `handle != 0` y `+8 == 1`): **no se cumple**; la línea `[NF4] CRITERIO idx10 sec=0x31 handle=0 +8=0 => FALLA` está en `run1`, `run2` y `run3`.

## 3. Por qué: `0x2B3000` corta antes de crear

`WriteBaseData` `0x2B4030` (desensamblado con capstone sobre `libmpr.so`):

```
002b406a: bl 0x2b3000          ; (OM, mediaID, &handle)
002b406e: mov r4,r0
002b4070: cmp r0,#0
002b4072: bne 0x2b40fc         ; -> r4 = 0x10800010, línea 0xF47
...
002b40c8: blx 0x11fa5c         ; FlashLib::CreateSector32  (sólo si 0x2B3000 dio 0 y handle==0)
```

`0x2B3000` recorre `0x9D23FC` (stride 0x18; literal `0x9D2408` en `0x2B3084`, base `-0xC` = `0x9D23FC`) y **descarta toda entrada cuyo `+0x10` (fn) sea 0**:

```
002b3018: ldr r2,[r3,#4]       ; entry+0x10 = fn
002b301a: cbz r2, 0x2b302a     ; fn==0 -> siguiente entrada
002b301c: ldr r2,[r3]          ; OM
002b301e: cmp r2,r8
002b3022: ldr r2,[r3,#-8]      ; mediaID
```

Medido en el arnés (`run2` y `run3`, volcado de `0x9D23FC` desde el proceso):

```
[13]u04/m3/ft031/om6/fn0/arg0   [14]u21/m3/ft031/om6/fn0/arg0   ... (las 37: fn0/arg0)
[NF4] 0x2B3000(OM=6,media=3,&h) -> ret=0x10800010 handle=0xdeadbeef
[NF4] 0x2B3000(OM=9,media=8,&h) -> ret=0x10800010 handle=0xdeadbeef
[NF4] BackupMgr::InitBackupData(6,3) -> 0x10800010
```

⇒ **`InitB 6 3` no puede llegar a `CreateSector32` en este firmware**: le pasa a cualquier `InitB` y también a `InitBackupData(9,8)` (el par del `0xA0`), que da el mismo `0x10800010` — el handle del `0xA0` que sí aparece al arrancar tiene que venir por otra vía, no determinada. `GetErrorString(0x10800010)` devuelve `"unknown"`: no es un código de FlashLib (su tabla `0x7E9488` empieza en 1), es el error FBM de `WriteBaseData` línea `0xF47`.

## 4. `CreateSector32` y `GetErrorString`

Llamada por símbolo (`_ZN8FlashLib14CreateSector32Em12FBS_MOVEFLAGPmS1_`), con la imagen real:

```
[NF4] CreateSector32(0x31, 0, &handle, &id) -> ret=0 handle=0x3 id=0x31  «unknown»
```

- **El `0x7 = FBS_INVALID_PROCESS` de la sesión anterior ya no aparece**: era el `/dev/null` inerte. Con `/dev/nflasha4` respaldado por la imagen, el FBS crea el sector y devuelve handle.
- `GetErrorString(0)` = `"unknown"` (0 no es un código de la tabla). Para el código del comando, `GetErrorString(0x10800010)` = `"unknown"`.
- Firma confirmada por el propio llamador: `0x2B40B6`-`0x2B40C8` pasa `r2 = &[r7]` (**handle**) y `r3 = &[r7+4]` (**id**, `unsigned short`); el manglado es `…PmPt`.
- Tras crear, el sector queda **vacío** (los datos son `0xFF`): sólo se reserva la entrada de control.

## 5. `RcsBackupTblData` después de `InitB 6 3`

`BkRead` `0x2B39B8` (el camino de `0x35E04C`/`RcsBackupTblData`) devuelve `0x10100001` en `0x2B3A28` cuando `[entrada+4] == 0`, y si hay handle sigue a `ReadFirstPackData` `0x2B3948`:

| lectura | tras `InitB 6 3` (sin handle) | con la entrada poblada (`SetSMI 10 31 3 1 6`) |
|---|---|---|
| `BkRead(0x04,3)` | **`0x10100001`** (run1/2/3/5) | **`0x10100003`** (run3) |
| `BkRead(0x21,3)` | **`0x10100001`** (run7) | **`0x10100003`** (run6) |

- `0x10100003` es el código de fallo de `ReadPack` `0x2B267C` → `FlashLib::ReadSector` (`blx 0x11E8D0` en `0x2B26AA`), fijado en `0x2B26FC` (literal `0x2B2930` = `0x10100003`). Es lo esperable con un sector recién creado y sin primer pack.
- **Límite reproducible:** la **segunda** llamada a `BkRead` en el mismo proceso se queda bloqueada (no vuelve) en run1, run2, run3, run5 y run6, siempre en el mismo punto (tras imprimir la marca previa). Por eso cada par se midió en una pasada con esa lectura como primera del proceso. No he determinado la causa (candidato: `0x2B1E68` → `0x2B5080`, el log del FBM, sin consumidor).

## 6. ¿Queda modificado el fichero de `nflasha4`?

Tres niveles, medidos (`run3/consola.log`):

| paso | bytes distintos entre `/nflasha4.img` y `/usr/share/nflasha4.img` |
|---|---|
| tras el arranque | **0** |
| tras `FBM InitB 6 3` | **0** |
| tras `CreateSector32(0x31)` | **394**, todos en `0x9D400`..`0x9D7FF` |

- La página escrita es el **siguiente hueco del anillo**: en el volcado, `0x9D000` es una página de control válida con seq `0x2BC` y `0x9D400` era `0xFF`×0x400. La página nueva (`run3/ctrl_page_9d400.bin`) tiene cabecera `000000004a004a00`, **seq `0x2C2`**, checksum `0xAC06D58F` y tres entradas de 8 B: `81000000010103ff`, `a0000000000101ff` y **`31000000000507ff`** (fileType `0x31`, 5 bloques, estado `0x07`).
- El fichero del repo **no cambia** (sha256 `a5ab15ca…` antes y después de las seis pasadas); el shim nunca escribe sobre `/usr/share/nflasha4.img`, sólo sobre su copia `/nflasha4.img` del invitado, que se pierde al apagar.
- Para que la prueba fuese reversible se trabajó siempre con una **copia** (`/tmp/nflasha4-origen.bin`, `make_page.py`), no con el volcado.

## 7. Repetición exacta

```sh
# 1) inyector (mismos flags que scripts/gui/harness/shim/build.sh)
sh reports/evidence/fbm-initb-6-3-nflasha4-20261126/comando.sh

# 2) a mano, la pasada principal
python3 reports/evidence/fbm-initb-6-3-nflasha4-20261126/make_page.py   # /tmp/nflasha4-origen.bin
NF4INJECT=30 python3 reports/evidence/fbm-initb-6-3-nflasha4-20261126/pb_run_nf4.py \
    300 reports/evidence/fbm-initb-6-3-nflasha4-20261126/run3 /tmp/nflasha4-origen.bin 30
```

- **Perfil:** `analysis/gui/g22/harness/live/nf4/` (overlay con `nf4inject.so`; el `sonyshim.so` sale de `analysis/gui/g22/harness/overlay/…`).
- **Variables que importan:** `LIVE_NFLASH4` (la pone el lanzador con el 3er argumento), `NFLASH4=<huella>` (la añade `live.construye_shimenv`), `NF4INJECT=<s>` (retardo del inyector) y `NF4MODE` (`main` por omisión, `b21h`, `b21`, `ver`).
- **Marcas en `consola.log`:** `[NF4] …` (medidas) y `[FBMC] FIN` (el lanzador corta la VM con ella).
- La línea de consola se ejecuta con la convención real del monitor: `argv = {"FBM","InitB","6","3"}`, `argc = 4` al handler del módulo (`0x6822F8`/`0x682230` → `0x2B50D8`).

## 8. Límites de esta prueba

1. Todo es QEMU sobre una copia del volcado: no se ha ejecutado nada en la cámara.
2. El bloqueo de `0x2B3000` (`fn==0` en las 37 entradas) es del **firmware**, no del arnés: `InitB` no sirve para crear sectores en esta build. La vía que sí crea es `FlashLib::CreateSector32` directa (handle=3) — pero deja la tabla `0xA3699C` sin alta, que es lo que hace `WriteBaseData` en `0x2B40DA`.
3. El alta sintética con `SetSMI` **no** crea nada en NAND (sólo escribe la tabla en RAM); sirve para medir la lectura, no como arreglo.
4. run5 (imagen con la página `0x9D400` parcheada) **no** consigue que `FBM::Init` abra `0x31` al arrancar; queda como control negativo sin causa determinada (candidatos: selección de página por seq/estado del anillo, o que `CheckExistSector` mire otra estructura).
5. Que `0xA0` sí tenga handle al arrancar y `0x30`/`0x62`/`0xB2` no, no lo he explicado: en el arnés sólo se abre el primero, aunque los cuatro están en el volcado de la cámara.
