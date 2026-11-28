# FILM-PB-1 — Escalera SSBI: por qué la WBI propia salió negra y cómo fabricar la del CFW

Fecha: 28-11-2026. Solo estático: kernel OSS de Sony, bytes de `upm.ko`/`libObj.so`/`im.elf` y las dos
instantáneas (WBI de fábrica 3.21 y captura del CFW del 27-11). Sin cámara, sin SWD ni escrituras.
Continúa el [traspaso de Astra](film-pb-1-traspaso-wbi-estatico-20261128.md) y el
[informe consolidado](film-pb-1-informe-wbi-nflasha5-20261128.md).

Etiquetas: **VERIFICADO** (bytes o fuente citada), **INFERENCIA**, **NO PROBADO** (requiere cámara).

## 0. Resumen

1. **La WBI no se fabrica de una vez: es una escalera de cuatro arranques** que hace el propio kernel, gobernada por
   la palabra `cxd90014_ssboot_stat` (VA `0x400523a0`) y por el vector de reanudación. **VERIFICADO** (§1).
2. **La captura del 27-11 tiene en `upm.ko` un último apagado `{factor 7, motivo 0x1b, código 0x1f}`.** La WBI de
   Sony tiene `{0x27, 0x1c, 0x20}`. Tras reanudar, `libObj` `GetInactiveFactor` (`0x7e7c18`) traduce `0x1b` a
   `OFF_TYPE_SUSPEND` y `0x1c` a `OFF_TYPE_COLDOFF`. La captura reanuda creyendo que vuelve de una suspensión;
   la de Sony, de un apagado en frío. **VERIFICADO** (§2).
3. **Causa:** el SWD del 27-11 cambió el factor solo dentro de `im.elf` (`0xA130`, `r3` 7→`0x27`). `im.elf` hizo
   el ritual tipo 8, pero `upm` (kernel, dentro de la instantánea) se quedó con el apagado del interruptor.
4. **El 4.07 tenía además el vector equivocado:** re-firmó `prof`→`WBI1` sin cambiar el vector `_profile`
   (`0x800523a4`), así que reanudó en perfilado (stat 1). El empaquetador lo hacía siempre (su `assert` era
   inerte, `or True`). **Corregido** y cubierto por regresión (§6).
5. El negro con re-suspensión en bucle del 4.07 (`mmc_hwip_system_off` repetido = `suspend` del driver SD,
   §3) encaja con (2)+(4). **INFERENCIA fuerte**: no hay log de espacio de usuario de ese arranque.
6. **Solución construida:** `scripts/cam/swd_upm_coldoff_0x27.cfg` intercepta en el receptor
   (`upm.ko` `.text+0xefec`, VA `0x3f334fec`, igual en Sony y en el CFW) y reescribe el mensaje a
   `{0x27, 0x1c, 0x20}` antes de que `upm` lo lea: el mismo registro que la fábrica. Lógica probada con
   registros y memoria simulados; **NO PROBADO** en cámara.
7. **Con eso la cámara completa sola la escalera** (§4): apagado → `prof`; perfilado → apagado → vector
   `_optimize`; arranque → optimiza y escribe `WBI0` → reinicio → sella `WBI1`. El resultado es una WBI del
   CFW con su `/usr` (Silent incluido), lista para meter en un paquete (§5).
8. La captura del 27-11 y `nflasha5-prof-optimize.bin` de Astra **no sirven**: heredan el registro de
   suspensión, y la sección de RAM no se puede reescribir sin un compresor LDEC.

## 1. La escalera SSBI — VERIFICADO

Fuente: `analysis/session18/codex-g/oss-linux/linux/` (`arch/arm/mach-cxd90014/{resume.S,pm.c}`,
`kernel/power/suspend.c`, `kernel/power/ssboot/{main.c,optimizer/basic.c}`, `arch/arm/common/warm.c`).

| stat | Entrada (vector) | Qué hace el siguiente `warm` / la reanudación | Firma escrita |
|---|---|---|---|
| 0 `CREATE_MINSSBI` (frío) | — | `free_some_memory` + imagen completa; vector `_profile` (`pm.c:381`) | `prof` (`warm.c:1154`) |
| 1 `PROFILE` | `0x800523a4` `_profile` | al reanudar, `start_profiling` (`suspend.c:372`); en el `warm`, **solo** reescribe la cabecera con vector `_optimize` (`pm.c:384`) | `prof` |
| 2 `CREATE_OPTSSBI` | `0x800523ac` `_optimize` | al reanudar descongela solo hilos del kernel, `ssboot_optimizer_optimize()` lee `/log/ssbi_prof.bin`, imagen nueva con vector `_ssboot_pre` y `em_reboot(1)` (`suspend.c:120/379`, `pm.c:387`) | `WBI0` (`warm.c:1157`) |
| 3 `SSBOOT_PRE` | `0x800523b4` `_ssboot_pre` | `cxd90014_pm_finish` reescribe la cabecera `WBI1` + `_ssboot`, `SSBI Create Completed!` (`pm.c:273`) | `WBI1` |
| 4 `SSBOOT` | `0x800523bc` `_ssboot` | arranque caliente normal; un `warm` aquí dejaría `invl` (`warm.c:1160`, caso por defecto) | — |

Bytes de las cuatro entradas en la propia captura del CFW (`mov r1,#N; b 0x400523c4`; el bloque común hace
`sub r0,pc,#0x2c` → `0x400523a0` y `str r1,[r0]`), idénticos en la WBI de Sony. `scripts/wbi/escalera.py`:

```
WBI Sony 3.21 : firma WBI1, 1164 secciones, vector 0x800523bc (stat 4), stat guardado 2 (CREATE_OPTSSBI), Loader3 OK, modo 10
captura 27-11 : firma prof, 1397 secciones, vector 0x800523a4 (stat 1), stat guardado 0 (CREATE_MINSSBI), Loader3 OK, modo 12
```

`stat guardado 2` en la de Sony prueba que la imagen vendida es la que escribió el peldaño 2. Su klog
(`evidence/film-pb-1-ssbi-20261126/wbi-sony-klog.log`) lo confirma: `optimizing image done` y luego
`count_sections_p2:1164`. Loader3 acepta `prof` como modo 12 (medido el 26-11, `resultado-ciclos-1-2.txt`).

- `upm.ko` `0xeff0`: con factor `0x27`, `msleep(2000)` y, si hay perfilado, `ssboot_optimizer_stop_profiling`,
  que escribe `/log/ssbi_prof.bin` (`basic.c:777-884`). **El `0x27` que cierra el perfilado es el mismo que
  dispara el siguiente `warm`.**
- No hay swap: la partición 8 mide 0 (`partinf.conf`) y `swap_prepare.sh` solo corre en modo BIS. La imagen
  lleva toda la memoria anónima; las páginas de fichero se releen de disco. Por eso el `/usr` instalado debe ser
  **byte a byte** el de la instantánea.
- Tablas de montaje de las dos instantáneas (`scripts/wbi/montajes.py`): **idénticas**, `/android/data` desmontado
  en ambas, `/setting`, `/log`, `/tmp` y `/lens` vfat rw. La captura no es «más rara» que la de Sony en sistemas de
  archivos.
- La WBI de Sony también es una instantánea de un **arranque en frío** (peldaño 0) llevada por la escalera. Una WBI
  del CFW hecha igual es de la misma naturaleza; lo que el frío no inicializa (decodificador,
  [búsqueda del decodificador](film-pb-1-busqueda-decodificador-frio-20261128.md)) lo resuelve la reanudación, no
  el contenido de la RAM de fábrica. **INFERENCIA**.
- La tabla FBM (`libmpr+0xA3699C`) de la WBI de Sony tiene **1 de 30** entradas con handle (solo `0xA0`; `0x31`
  vacío). La captura del CFW tiene 3 (`0x62`, `0xA0`, `0xB2`). **La WBI no aporta los sectores FBM de vídeo**
  (`scripts/wbi/fbm_tabla.py`). **VERIFICADO**.

## 2. La diferencia decisiva: el último apagado que guarda `upm` — VERIFICADO

`upm.ko` copia el mensaje `UPM_CMD_OFF_FACTOR` recibido en `g_off_factor+4` y `+0x14`
(`k_upm_off_factor_handler_active` `0xf024-0xf038`; `g_off_factor` = `.data+0x608`, VA `0x3f33af48` en las dos
imágenes). Lo devuelve a espacio de usuario `UPM_CMD_GET_HCRN_OMOTE` (`0x920161`, `k_upm_apicb_off_factor`
`0xe3ac-0xe3f0`). `scripts/wbi/upm_modulo.py`:

```
WBI Sony 3.21 : 0x920141 factor 0x27 motivo 0x1c código 0x20  => OFF_TYPE_COLDOFF
captura 27-11 : 0x920141 factor 0x7  motivo 0x1b código 0x1f  => OFF_TYPE_SUSPEND
```

`libObj` `GetInactiveFactor` (`0x7e7c18`) pide ese registro (`0x7e7c68`, `0x920161` al buzón `0x920196`) y ramifica
por el motivo (`0x7e7cba`): `0x1b` → `">> OFF_TYPE_SUSPEND"` (1), `0x1c` → `">> OFF_TYPE_COLDOFF"` (2),
`0x1a` → `UNKNOWN`. Ese registro está en la RAM de la instantánea, así que **cada** arranque desde esa WBI lo lee igual.

Origen del `{7, 0x1b, 0x1f}`: `add_off_factor` (`0xe96c-0xe994`) fuerza el motivo a `0x1b` si no es `0x1b`/`0x1c`,
y `0x1f` es el código por defecto de `clear_hcrn` (`0xeac4`). **No** sale de `libObj` `0x8035f8`, cuya tabla de
códigos es `0x20,0x22..0x26` y `0x21` (`0xd8ef34`). El emisor del apagado del interruptor queda **sin identificar**.
Corrige `evidence/film-pb-1-ssbi-20261126/C5.md` §1.2 («interruptor = factor 7, motivo `0x1c`»). Por eso el cfg
intercepta en el receptor y no en el emisor.

## 3. Lectura del fallo del 4.07 — INFERENCIA fuerte

- `mmc_hwip_system_off START/END` es el `suspend` UDIF del driver `mmc_drv`. Sale una vez por cada apagado en
  cualquier log normal (`analysis/camera-dumps/mem-20261020-log/log.txt:5903`). **Repetido** tras `WARMBOOT` quiere decir que
  la cámara reanudada **volvía a suspenderse**, no que la imagen estuviera «a mitad del apagado».
- Ese arranque llevaba dos discrepancias con la fábrica: stat 1 (perfilado) por el vector `_profile`, y
  `OFF_TYPE_SUSPEND` en el registro de `upm`. La segunda es la que lee la aplicación para decidir cómo encender.
- Corrige [WBI propio](film-pb-1-wbi-propio-20261127.md) («foto a mitad del apagado») junto con el traspaso de Astra.
  Ambas imágenes están en el mismo `write("warm")` de `im.elf` (Astra, `pilas-suspension.json`). Lo que cambia es el
  vector y el registro de `upm`.

## 4. Cómo fabricar la WBI del CFW en la cámara — NO PROBADO

Requisitos (los del 27-11, **MEDIDOS**): CFW instalado sin `nflasha5` (arranque en frío), `/android/data` sin las apps
que retienen el montaje (Tweak, RemoteShutter, WbiMaker) ni volcados, `/setting` con espacio
(`docs/runbook-setting-llena.md`) y sonda SWD conectada. El `/usr` instalado será el de la WBI: no cambiarlo después.

| Paso | Acción | Qué debe verse | Cabecera de `nflasha5` al terminar |
|---|---|---|---|
| 0 | Frío, cámara arrancada del todo. `openocd -f scripts/cam/swd_upm_coldoff_0x27.cfg` y pulsar el interruptor | `NATIVE_OFF factor=0x7 …` → `CONVERTED …` → `FIN clean=1`; ritual tipo 8 (`make_init_bk.sh`, `umount AD` = 0) | `prof`, vector `0x800523a4` |
| 1 | Encender **sin SWD armado**: Loader3 `MODE#12`, `ssboot: basic: start profiling...`. Usar la cámara: imagen en vivo, menú con Silent, **reproducir un vídeo**, foto. Luego repetir el cfg y apagar | `CONVERTED`; en el apagado `stop profiling...` y `Profile File info`; aparece `/log/ssbi_prof.bin` | `prof`, vector `0x800523ac` |
| 2 | Encender: la cámara reanuda, optimiza, escribe y se reinicia **sola** | `ssboot: optimizing image...` / `done`, `count_sections_p2:` | `WBI0`, vector `0x800523b4` |
| 3 | Automático tras el reinicio: Loader3 `MODE#11` | `SSBI Create Completed!`; la cámara queda encendida | `WBI1`, vector `0x800523bc` |
| 4 | Apagado normal (sin SWD) y encender | `MODE#10`, `WARMBOOT`; **prueba**: reproducir vídeo y foto Silent | sin cambios (`mem` no toca la WBI) |
| 5 | Volcar `nflasha5` por el actualizador (`scripts/cam/ushell_pull_part.py`) y comprobar | `escalera.py`: `WBI1`, stat 4, Loader3 OK; `upm_modulo.py`: `OFF_TYPE_COLDOFF` | — |

Notas:
- **Nunca** armar el SWD durante un arranque (memoria `feedback-swd-no-parar-en-arranque`). El cfg solo se detiene
  en un `UPM_CMD_OFF_FACTOR` (`msg0 == 0x920141`, `r4` en lowmem). Cualquier otra parada se deja pasar y se vuelve a armar.
- En el paso 1 el `0x27` es imprescindible: con un apagado normal (`mem`) la cabecera no avanza y no se escribe
  el perfil.
- Cada apagado tipo 8 vuelve a crear `/setting/init_bk.bak`. Con `/android/data` grande, el tar no cabe y llena
  `/setting` (CAM-SETTING-1). Molesta a la siguiente actualización (`0x1043`), no a la escalera. Antes de instalar
  nada, `rm /setting/init_bk.bak` desde el actualizador.
- Volver atrás: paquete 4.08 sin `nflasha5` (`build/wbi_propio/revivir/package-4.08`) o cualquier actualización,
  porque `ud_wbi_drop.elf` borra la cabecera.

## 5. El paquete CFW con su WBI

`scripts/gui/build_package_wbi_propio.py VOLCADO SALIDA VERSION` mete el `nflasha5` volcado en el paso 5 en un
paquete con el mismo `/usr`, `nflasha3` y Darwin del pkg405. Desde hoy **rechaza** todo lo que no sea `WBI1` con
vector `_ssboot` y no re-firma nada. Al instalarlo, `/setting` se rehace con los ficheros del paquete
(`first_ssboot`, `init_bk.bak` de Sony) y la primera reanudación reconstruye `/android/data` (`SyncAndroid_res`:
`BK files not found` → `Factory/A-Reset` → `tar xf /setting/init_bk.bak`, `libSyncAndroid.so` `0x28ee-0x2974`),
igual que tras una actualización de Sony.

## 6. Herramientas y pruebas

| Fichero | Qué hace |
|---|---|
| `scripts/wbi/escalera.py` | valida lo que mira Loader3, decodifica las 4 entradas de la propia imagen y genera variantes de firma/vector (`--paso`) |
| `scripts/wbi/upm_modulo.py` | localiza `upm.ko` por tablas de páginas y lee el último apagado guardado |
| `scripts/wbi/fbm_tabla.py` | tabla FBM `libmpr+0xA3699C` del `im.elf` guardado |
| `scripts/wbi/montajes.py`, `logs_ram.py` | árbol de `vfsmount` y texto de zonas físicas (anillos de log) |
| `scripts/wbi/snapram.py` | lector de instantáneas (de Astra, `build/wbi_silent/scripts-astra/mapas.py`) |
| `scripts/cam/swd_upm_coldoff_0x27.cfg` | apagado de fábrica por SWD (§4) |
| `tests/test_wbi_escalera.py` | regresión del empaquetador (4 rechazos + 1 aceptación) y la escalera/registro en las imágenes reales |

Los scripts de Astra se copiaron de `/tmp` a `build/wbi_silent/scripts-astra/` (fuera del control de versiones).

## 7. Límites

- No probado en cámara ningún paso de §4. La relación «`OFF_TYPE_SUSPEND` ⇒ negro» es inferencia: no se ha seguido
  qué hace la aplicación con cada tipo.
- El cfg se ha comprobado con un simulador de registros/memoria y `info complete` de Tcl, no contra el hardware. La
  parada es en modo privilegiado (las del 27-11 eran de usuario): es breve y solo en el apagado, pero es nueva.
- Si otro cliente envía `UPM_CMD_OFF_FACTOR` mientras el cfg está armado, se convertiría ese. Armar justo antes de
  pulsar el interruptor.
- La WBI resultante guarda en RAM el estado de **esta** cámara en el paso 0 (ajustes de usuario, fecha). Sony
  distribuye una sola WBI para todas las unidades, así que lo propio de cada unidad se relee al reanudar
  (**INFERENCIA**). Antes de repartir el paquete a otra A6000, probarlo en una segunda unidad.
- La reproducción de vídeo en caliente con el CFW no está demostrada: con Sony 3.21 caliente sí reproduce
  (medido) y en frío no; el mecanismo exacto sigue abierto.
