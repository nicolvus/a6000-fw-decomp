# FILM-PB-1 — por qué el WBI no convive con Silent y cómo tener reproducción + Silent

Fecha: 28-11-2026. Continúa [la búsqueda de la causa del decodificador en frío](film-pb-1-busqueda-decodificador-frio-20261128.md)
(que cerró: *en frío el core AV no arranca el decodificador; en caliente sí*).

**Modo**: análisis estático y construcción **offline**. No se ha tocado la cámara. Lo que exige la cámara
está en [§6](#6-prueba-física-pasos-exactos-petición) como petición con pasos exactos.

Evidencia: [`reports/evidence/film-pb-1-wbi-silent-20261128/`](evidence/film-pb-1-wbi-silent-20261128/).

> **Objetivo de hoy.** Resolver por qué el WBI (arranque caliente, que es lo único que reproduce vídeo)
> no funciona con Silent Shooting, y dar una solución para que las dos cosas convivan.

---

## 0. Respuesta en una página

**Silent son dos capas, y solo una es incompatible con el WBI.**

| Capa | Dónde vive | ¿Sobrevive al WBI? |
|---|---|---|
| **Comportamiento** (ShutMode 0, `r5`, tristate hacia Darwin) | `av-cam.bin` → `nflasha3` (`/system`) | **Sí**: `av-cam.bin` tiene **0 de 2 200 páginas** dentro del WBI y Loader3 lo recarga en **ambos** modos (RAMCFG `0x1000000` y `0x4000000`) |
| **Bandera** (Silent 0/1, `[0x43EDF684+0x238]`, comando `0x40e3`) y **entrada de menú** | `libObj.so`, `CautionConfig.so`, `viewUnified2.so`, `share/app/*.uxc` → `nflasha15` (`/usr`) | **No**: el WBI congela el `/usr` de Sony (TOC en `0x8D3B8000` + **1 654 páginas de 77 ficheros**, `libObj.so` 998/4 254) |

Además la bandera **no se puede dejar puesta**: el bloque de ajustes se reinicializa en cada arranque
(`0x43804610`) y `+0x238` queda a 0 (§2.4), así que no hay atajo «seleccionar Silent una vez».

Y el motivo de que fuera **irreversible**: **la cámara no vuelve a fabricar su WBI**. `im.elf` escribe
`"warm"` en `/sys/power/state` solo si una compuerta (`0x9F44`) deja, y esa compuerta compara un
**contador persistente** (Backup `0x940004`) con un límite; pasada la cuenta escribe `"mem"` y la
instantánea se queda como estaba. Encima, el instalador **borra la cabecera** de `nflasha5` en cada
actualización (`ud_wbi_drop`), así que todo CFW instalado en frío se queda en frío para siempre: **no hay
forma de que el WBI se rehaga con el `/usr` nuevo** y el menú Silent nunca aparece en caliente.

**La solución (dos vías, la primera es la buena):**

1. **S1 — forzar UNA regeneración del WBI.** Parche de **4 bytes** en `/usr/bin/im.elf` (`0x9F44`:
   `movs r0,#1 ; bx lr`) dentro del paquete CFW, que se instala **sin** `nflasha5`. Secuencia:
   instalar → primer arranque **en frío** (aquí el menú Silent existe, la reproducción aún no) → apagar con
   el interruptor → la cámara escribe un **WBI nuevo con el `/usr` del CFW** → a partir de ahí **arranca
   caliente con el `/usr` del CFW**: reproducción **y** Silent. La regeneración la hace la cámara sola, sin
   ningún ajuste de fábrica: los seis eslabones de la cadena están verificados en §8.
   Construido y verificado offline en esta sesión (§5). `build/wbi_silent/pkg405sony/` (23/23).
2. **S2 — Silent sin `/usr` (respaldo, si la cámara no coopera).** Dejar el disparo de Silent en un ajuste
   del menú **de fábrica** en vez de en la entrada nueva: el bloque de ajustes ya tiene
   `+0x210` = EFCS y `+0x238` = Silent (`scripts/g22/patch_tristate.py:18`). Cambiando la fuente de las dos
   lecturas (`+0x238` → `+0x210`) Silent queda gobernado por «Front Curtain Shutter» y **no se toca `/usr`**:
   el paquete lleva el WBI de Sony y aun así funciona. **No implementado** (cambia la semántica del
   obturador y hay que medirlo en cámara; ver §4.2).

---

## 1. Anatomía de Silent (VERIFICADO)

| Pieza | Evidencia |
|---|---|
| Escribe `cap+0x64C` (= `r5` de `SetExposure`) y `cap+0x655 = 0` (ShutMode) solo si Silent está activo | `scripts/g22/patch_silent_r5.py`, enganche `0x438C82FE bl 0x436D6118`, cueva `0x43FB7E00` |
| Tristate hacia Darwin: `cap+0x41C = EFCS\|silent`, `cap+0x41D = electronic`, `pkt[0x0E] = silent` | `scripts/g22/patch_tristate.py`, sitios `0x43845F2E`, `0x43841472`, `0x438D01AA`, `0x4384219E/2270` |
| La bandera la pone el menú: comando `0x40e3` → `[0x43EDF684+0x238]`; `+0x210` es el EFCS de fábrica | `scripts/g22/patch_tristate.py:18` |
| Las tres piezas son de `av-cam` (`nflasha3`), no de `/usr` | los VA `0x43…` son del BIONZ; `nflasha3` es `/system` |
| El menú («Silent Shooting») se inyecta en `viewUnified2.so` + `CautionConfig.so` + 25 `.uxc` | [G11 §13](gui/g11-auditoria-307-nflasha15.md), `scripts/gui/build_silent_menu_test.py` |

---

## 2. Por qué el WBI y el Silent «de menú» no conviven (VERIFICADO)

### 2.1 El WBI no es un volcado de subsistemas: es una suspensión del Linux del BIONZ

`nflasha5` = `WBI1`, 1 164 secciones, `dataSize` 41 993 728 B, `oDataSize` 172 998 656 B; cada sección es un
chorro LZ77 de 4 096 B. Contiene las páginas **en uso** del nodo 0 —imagen del kernel, **page cache de
`/usr`** y memoria de los procesos MPR/`libObj`— más las 12 regiones `wbimem=` de la cmdline.

Medido por páginas de 4 KiB contra los ficheros de fábrica:

| Fichero | Páginas en el WBI | Total |
|---|---:|---:|
| `lib/libObj.so` | 998 | 4 254 |
| `lib/viewUnified2.so` | 50 | 1 209 |
| `lib/CautionConfig.so` | 8 | 409 |
| `bin/im.elf` | 5 | 5 |
| **todo `/usr`** | **1 654** (77 ficheros) | 30 003 |
| `av-cam.bin` (`/system`) | **0** de 24 432 páginas no nulas del WBI | 2 200 |

Medición propia y reproducible (`scripts/gui/cuenta_paginas_wbi.py`, 20 líneas con `fwtool.sony.wbi` +
SHA-1 por página): [evidencia](evidence/film-pb-1-wbi-silent-20261128/02-paginas-del-wbi.txt).

Y el TOC TPZL de `nflasha15` está materializado en RAM en `0x8D3B8000` (1 sola coincidencia: es el índice
con el que el kernel resuelve `/usr` cuando arranca caliente).

### 2.2 Instalar un `/usr` recompuesto y conservar el WBI de Sony = no arranca

Es la serie medida de [G11 §11](gui/g11-auditoria-307-nflasha15.md): **0/6** con `nflasha15` recompuesto
frente a **3/3** con el de Sony. Todo `nflasha15` recompuesto mueve el TOC (primera entrada distinta: 594,
687, 995…), y el kernel reanudado usa el TOC y las cachés **de Sony** sobre una imagen cuyo ext2 ya no
coincide.

### 2.3 Aunque el TOC no se moviera, las páginas restauradas ganan

El `libObj.so` que el sistema ve en caliente sale del page cache restaurado (994 páginas de Sony), no del
ext2 nuevo. Es el otro motivo documentado por el que se quita el WBI: «en caliente los parches de `/usr`
no se cargan nunca».

⇒ **Conclusión:** Silent en su forma actual (menú + bandera) exige `/usr`; `/usr` y el WBI de Sony son
incompatibles. La única salida es **que el WBI se rehaga con el `/usr` nuevo**.

---

### 2.4 Y la bandera de Silent no se puede «dejar puesta» (VERIFICADO)

Medido en [S64](capture/s64-silent-ram-nvram-test.md): el bloque de ajustes `0x43EDF684` se **reinicializa a
valores por defecto en cada arranque** (`0x43804610` lee un byte de `Backup` y pone `+0x238` y `+0x280` a 0; «el
byte de backup no fija `+0x238`»), y las escrituras de `Backup` cercanas al bloque tocan `+0x40a/+0x4cc/+0x450/+0xd0`,
**nunca** `+0x238`. Es decir: Silent **no es persistente** y siempre arranca a 0.

Consecuencia doble:

* no existe la vía «poner el ajuste una vez y que sobreviva a los arranques»;
* el único que lo pone es el menú en caliente (comando `0x40e3`), que vive en `/usr` ⇒ vuelve al problema de §2.

⚠️ Y un aviso de S64 que condiciona el plan B: escribir 10 palabras de `0x230…0x254` del espejo
(`0x83EDF684`, solo RAM) **reinició la cámara**. Cualquier variante debe **cambiar lecturas del firmware, no
escribir ese bloque**.

## 3. El eslabón que faltaba: la cámara ya no fabrica su WBI (VERIFICADO contra bytes)

`/usr/bin/im.elf` (ELD Thumb, VA = offset + `0x8000`; desensamblado completo en
[`01-im-elf-compuerta-wbi.txt`](evidence/film-pb-1-wbi-silent-20261128/01-im-elf-compuerta-wbi.txt)):

| VA | Qué hace |
|---|---|
| `0xA270` | el llamante calcula el modo: `1` si un global vale 1 y un campo != 0; si no `0` |
| `0x9FB4` | abre `/sys/power/state` (`0xC0B7`) y, según el modo, escribe **`"warm"` (4 B, `0xC0C8`)** o **`"mem"` (3 B, `0xC0F4`)**; los logs son `WARM(warm_count=%d)` y `SUS(warm_count=%d)` |
| `0x9F68` | `Backup_read(0x94, 0x940004, &v)`; si cambió, resincroniza; luego `v+1` y `Backup_write` ⇒ **contador persistente** |
| `0x9F44` | **compuerta**: si el límite (`0x154D4`) es 0 devuelve 1; si no, `1` solo mientras `contador <= límite` |
| `0x9A84` | existe una rutina que **pone el contador a cero** (`Backup_write(0x94, 0x940004, 0)`) |

Con el contador por encima del límite, el apagado escribe `"mem"` (suspensión a RAM normal, que no crea
instantánea) y el WBI **no se rehace jamás**. Eso explica el hecho medido de la sesión anterior: la cámara
quedó `BootMode 1` en **dos** encendidos seguidos aunque `warm.mode=2` está en la cmdline.

**Es exactamente la pieza que hacía imposible «WBI + Silent»**: la mezcla no solo era mala, es que no había
mecanismo que la regenerase.

---

## 4. Las dos soluciones

### 4.1 S1 — forzar una regeneración del WBI (recomendada; construida)

**Idea.** Un solo interruptor de 4 bytes: `warm_permitido()` devuelve 1 siempre (`0x9F44`:
`06 4B 80 B5` → `01 20 70 47` = `movs r0,#1 ; bx lr`), así el siguiente apagado escribe `"warm"` y el kernel
fabrica un WBI **con el sistema que tiene cargado** (el CFW). No se toca el obturador, ni el decodificador,
ni el `/usr` funcional: solo la política de apagado. **El efecto se agota solo**: cuando el WBI existe,
Loader3 elige `BootMode 11`, no se ejecuta `/sbin/init` y `im.elf` no vuelve a correr.

**Paquetes construidos** (ver §5), los dos con **`--sin-wbi`** (el primer arranque tiene que ser frío para
que `im.elf` corra):

| paquete | tar base | diferencia frente a la base | para qué |
|---|---|---|---|
| **`build/wbi_silent/pkg405sony`** (recomendado para la prueba) | **Sony 3.21 de fábrica** | solo `nflasha15` (el `/usr` del CFW Silent + `im.elf` parcheado) y la retirada de `nflasha5` | aísla exactamente la variable del objetivo |
| `build/wbi_silent/pkg405` (línea Film/PP) | `build/cfw_func393/base/base-film.tar` | además lo que ya traía el tar del film (PP/Darwin) | si se quiere seguir sobre la base Film |

Los dos llevan el mismo `nflasha15` (29 ficheros, sha256 `ed456f8a…`) y el mismo `im.elf` parcheado.

**Secuencia esperada:**

| Paso | Qué se ve | Por qué |
|---|---|---|
| 1. Instalar | `Done` + reinicio | actualizador normal |
| 2. Primer encendido | **frío**: arranque lento, `BootMode 1`; menú **Silent** presente; vídeo **no** reproduce | `/usr` es el del CFW; el decodificador no arranca en frío |
| 3. Apagar con el interruptor (no quitar la batería) y esperar a que termine | LED de apagado normal, más lento que otras veces (escribe ~40 MB) | `im.elf` → `"warm"` → `cxd_create_warmbootimage` |
| 4. Encender | **caliente**: arranque rápido, **sin** mensajes de `init`; **reproduce vídeo** y el menú **Silent** sigue ahí | el WBI nuevo trae el page cache del `/usr` del CFW |

**Riesgo y marcha atrás.** Si el paso 3 no produce un WBI válido, la cámara sigue en frío (sin
reproducción, con Silent): se recupera instalando de nuevo el paquete B de la bisecta (3.21 íntegro con su
WBI de fábrica) o cualquier versión mayor con el `/usr` de Sony. Riesgo de cuelgue en la reanudación: el
mismo que ya existe al conservar el WBI; la salida documentada es R48 + paquete con el `/usr` de Sony.

**Ventaja frente a otras vías:** no inventa semántica de obturador (se usan los parches Silent ya medidos en
R85/R87) y no necesita recompresor de WBI: lo fabrica la propia cámara con su hardware (`cmpr`) y su
`nand.ko`.

### 4.2 S2 — Silent sin `/usr`, si la cámara no regenera (diseñada, no implementada)

El bloque de ajustes tiene **`+0x210` = EFCS** (lo pone el menú de fábrica «Front Curtain Shutter») y
`+0x238` = Silent (lo pone el comando `0x40e3` del menú del CFW). Los dos parches leen `+0x238`:

* `patch_tristate.py`: `ldrb.w r4,[r4,#0x238]` en el copiador `0x43845F2E`.
* `patch_silent_r5.py`: `LIVE_SILENT = 0x43EDF684 + 0x238`.

Cambiando esas dos lecturas a `+0x210` se conserva el ajuste de fábrica «Front Curtain Shutter» como mando. La
polaridad correcta, según los tres estados medidos en [R87](capture/e26-r87-disparo-remoto-y-recalibracion.md)
(mecánico = `(+0x210, +0x238)` = `(1,0)`, EFCS = `(0,0)`, Silent = `(1,1)`), es **usar `+0x210` invertido**:
EFCS **On** (`+0x210 == 0`) ⇒ Silent; EFCS **Off** (`+0x210 == 1`, el valor de fábrica que hoy da mecánico) ⇒
mecánico. Así el ajuste de fábrica pasa a elegir entre mecánico y electrónico, **sin tocar `/usr`** ⇒ convive con el WBI de Sony tal cual y la reproducción sigue
funcionando. **No se implementa aquí** porque cambia el significado de un ajuste de fábrica (quien tenga
EFCS On de fábrica pasaría a Silent, y Silent no sincroniza con flash) y eso exige medirlo en cámara; queda
como plan B con el cambio ya localizado en dos instrucciones.

### 4.3 Descartadas

| Vía | Por qué |
|---|---|
| Conservar el WBI de Sony + `/usr` recompuesto | **0/6** arranques (G11 §11) |
| Conservar el WBI y parchear solo las páginas no cacheadas de `/usr` | `libObj.so` tiene 998 de 4 254 páginas restauradas: mezcla garantizada |
| Construir un WBI offline | requiere recompresor LZ77 + `wbi_calc_cksum` + el layout ext2 exacto: inviable (84 615 168 B del CFW frente a 84 042 977 B de Sony) |
| Quitar el WBI y aceptar no reproducir | es el estado actual: no cumple el objetivo |

---

## 5. Verificación offline hecha en esta sesión

Todo reproducible sin cámara:

```bash
# 1. parche de 4 B en im.elf (+ 3 pruebas)
.venv/bin/python3 scripts/gui/patch_im_elf_warm.py \
  firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/bin/im.elf \
  build/wbi_silent/pkg/im.elf
.venv/bin/python -m pytest tests/test_patch_im_elf_warm.py -q      # 3 passed

# 2. nflasha15 con el /usr del CFW Silent + im.elf parcheado
.venv/bin/python3 scripts/gui/build_nflasha15.py \
  firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15 \
  build/wbi_silent/files build/wbi_silent/nflasha15-405.bin

# 3. comprobación independiente de la imagen construida
.venv/bin/python3 scripts/gui/verify_nflasha15_im_elf.py \
  build/wbi_silent/nflasha15-405.bin build/wbi_silent/files/bin/im.elf \
  --sony firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/bin/im.elf
```

| Comprobación | Resultado |
|---|---|
| `im.elf` parcheado: solo cambian 4 B, cabecera ELF intacta | ✅ `f0f18142…` → `522f2f2e…`, 4 bytes distintos |
| `im.elf` dentro de la `nflasha15` construida == el parcheado | ✅ `522f2f2e…`, compuerta `01207047` |
| `nflasha15` nueva: tamaño, `fsck`, bloque TPZL 0 igual que Sony | ✅ 84 615 168 B, `fsck` limpio, `bloque0_igual_que_sony: true`, 467 bloques recompuestos, CRC `0980738a` |
| Cabe en la partición (104 857 600 B) | ✅ |
| Paquete `firmware_packed.dat` 4.05 con `--sin-wbi` | ✅ 171 102 360 B; `sin_wbi: true`; línea de suma `0,0980738a,050b2000,…`; `pkg405` sha256 `584d2aac…`, `pkg405sony` sha256 `92cbd3b2…` |
| Auditoría independiente del `.dat` (`audit_package_nflasha15.py`) | **23/23**, `todo_ok: true`. `pkg405sony` frente a B (= 3.21 de fábrica + WBI): cambian **solo** `dev/nflasha15` y `part_image.sum`; se retira `dev/nflasha5`; 29 ficheros distintos en el ext2, **0** diferencias de atributos, 65/65 sumas, 467 bloques TPZL recompuestos, `fsck` solo contadores de libres. [JSON](evidence/film-pb-1-wbi-silent-20261128/06-audit-405-sony-23de23.json) |

**Límite de esta verificación:** es estática. Que la cámara escriba de verdad el WBI y que lo reanude solo
se prueba en cámara (§6).

---

## 6. Prueba física: pasos exactos (petición)

1. **Antes**: anotar versión instalada (4.02) y hacer una foto de `MAH04204.MP4` como referencia.
2. Instalar `build/wbi_silent/pkg405sony/package-4.05/firmware_packed.dat` (el auditado 23/23) con
   `pmca-console firmware <dat> --flash --confirm --reflash`.
3. Primer encendido. Confirmar **frío**: `busybox cat /proc/uptime` pequeño y arranque lento. Comprobar
   que el menú muestra **Silent Shooting** y que un vídeo **no** se reproduce (es lo esperado).
4. Menú → activar **Silent Shooting** antes de apagar (así, si H2 se cumple, la bandera viaja en la
   instantánea; si no, se activa a mano en cada sesión).
5. **Apagar con el interruptor** y esperar a que el LED termine (puede tardar más: escribe la instantánea).
   **No quitar la batería.** Es el único gesto que dispara la creación: `upm.ko` → mensaje `0x92014F` →
   `im.elf` → `"warm"`, y el instalador ya dejó la cabecera a cero, así que no hace falta nada más.
6. Encender. Confirmar **caliente**: arranque rápido y, en telnet,
   `busybox dd if=/dev/nflasha5 bs=16 count=1 2>/dev/null | busybox od -c` debe empezar por `W B I 1`
   (antes estaba a cero).
7. Probar las dos cosas juntas: reproducir `MAH04204.MP4` **y** disparar con Silent activado.
8. Si algo falla: reinstalar el paquete **B** de `build/cfw_bisect/B` (3.21 íntegro con WBI de fábrica) y
   anotar el punto exacto (`WARM(warm_count=…)` / `SUS(warm_count=…)` en `/log`).

---

## 7. Límites

- **No** está medido que la cámara acepte el `write("warm")` con `nflasha5` a cero: el código lo permite en
  todos sus pasos (§8) y el dispositivo está registrado con 62 MB en el `/log` real, pero la escritura de
  42 MB en NAND no se puede simular aquí.
- El parche hace que **cada** apagado por interruptor reescriba la instantánea (~42 MB). Sony limitaba eso
  con el contador `0x940004`, probablemente por desgaste de NAND; sin el contador, la partición de 60 MB
  recibe una escritura por ciclo. Uso normal (miles de apagados) queda dentro de la resistencia típica, pero
  es un coste real. Refinamiento posible si molesta: parchear la compuerta para que devuelva 1 solo cuando
  `nflasha5` no tenga cabecera válida (no implementado).
- El contador `0x940004` y su límite son **persistentes**: si el límite ya está agotado en la unidad del
  usuario, el parche es lo que lo salta; sin el parche, la única vía sería poner el contador a cero (existe
  la rutina `0x9A84`, pero no se ha localizado una orden de consola que la ejecute).
- S2 cambia la semántica de un ajuste de fábrica y no se ha implementado ni medido.
- La reanudación de un WBI creado con el `/usr` del CFW **no** está probada: podría fallar por mezcla igual
  que la de Sony (aunque aquí la coherencia es total: mismo ext2, mismo page cache). Riesgo asumido y con
  marcha atrás documentada.
- `warm.mode`, `warm.mem_dst`, `warm.mem_work`, `wbi_cmpr.*` se han leído en `warm.c` y en la cmdline; su
  interpretación exacta en Loader3 no se ha verificado (binario ausente).

---

## 8. La cámara crea sola el WBI nuevo (VERIFICADO en estático)

El usuario no quiere depender de disparar Silent desde el ajuste de fábrica: el paquete tiene que dejar la
cámara en un estado en el que **ella misma** fabrique la instantánea con el `/usr` del CFW. La cadena
completa, eslabón por eslabón, con la prueba de cada uno
([evidencia 07](evidence/film-pb-1-wbi-silent-20261128/07-garantia-creacion-wbi.txt)):

| # | Eslabón | Estado | Prueba |
|---|---------|--------|--------|
| 1 | Al instalar, el actualizador **invalida** el WBI aunque el paquete no traiga `nflasha5` | VERIFICADO | `config/config.xml:25` lanza `us_mkfs.sh` al procesar `partconf_sum/partconf.sum` (va en **todo** paquete), y `us_mkfs.sh:106` llama a `ud_wbi_drop.elf` **sin condición**, antes del `exit_flag`; el binario resuelve `/dev/nflasha%d` desde `partinf.conf` (`nflasha5`, `0x03B40000`, `0x03C00000`, **type 0x02** = Warm Boot Image) |
| 2 | «Invalidar» = 512 B a cero en el sector 0 ⇒ `fVersion` = 0 ⇒ sin instantánea | VERIFICADO | `__wbi_drop()` en `warm.c:359-388`: `memset(buf,0,512)` + `write_sector(...,0,1)` |
| 3 | En cada arranque el kernel registra el dispositivo WBI con sitio de sobra | VERIFICADO (log de cámara) | `/log` real: `wb_default_device: sector_size=0x40000,phys_sector_size=0x200` y `WBI partition[5]: id=2, start_secor=0, num_sectors=121344` = **62 128 128 B** de capacidad frente a los **42 293 120 B** de la imagen de Sony |
| 4 | Escribir `"warm"` en `/sys/power/state` es la **única** vía que crea instantánea | VERIFICADO | `kernel/power/suspend.c:50-58`: `[PM_SUSPEND_MEM]="mem"` y, con `CONFIG_WARM_BOOT_IMAGE`, `[PM_SUSPEND_DISK]="warm"`; `WBI_MODE(state,mode) = (state==PM_SUSPEND_DISK && mode)` (`warm.c:66`) y `warm.mode=2` en la cmdline de A y B ⇒ `image_mode=2` |
| 5 | Nada aborta la creación | VERIFICADO | la cmdline **no** trae `chk_opened=` ⇒ `wbi_mount_points[0]==NULL` ⇒ `wbi_chk_opened_files()` devuelve 0; `warm.errmode` ausente ⇒ `wbi_errmode=0` ⇒ un fallo solo se registra; `warm.ignore_drop=1` (irrelevante: ya está a cero) |
| 6 | `im.elf` pide `"warm"` sin depender del contador | VERIFICADO contra instrucciones | compuerta `0x9F44` es **pura** (lee dos globales, devuelve 0/1, no escribe); **un solo** `bl #0x9f44` en todo el binario, en `0x9FF2`; `cbz r0` → rama `"warm"` (`0xA012`) o `"mem"` (`0xA034`). Parche `06 4B 80 B5` → `01 20 70 47` verificado en el artefacto (`verify_nflasha15_im_elf.py`: `01207047`, `im.elf` sha256 `522f2f2e…`) |

Con los seis eslabones, la secuencia posterior a la instalación **no necesita ninguna acción de fábrica**:

1. Instalar → reiniciar (**frío** obligatorio: la cabecera está a cero). Menú con Silent, vídeo no.
2. Menú → **Silent Shooting ON** (si se quiere la bandera dentro de la instantánea; ver H2).
3. **Apagar con el interruptor.** `upm.ko` envía `0x92014F` → `im.elf` escribe `"warm"` → el kernel
   escribe la instantánea del `/usr` **del CFW** en `nflasha5` (cabecera `WBI1`).
4. Encender: **caliente**. Vídeo sí, y el `/usr` restaurado es el del CFW.

### H2 (INFERENCIA, no verificada): la bandera Silent puede viajar dentro de la instantánea

La instantánea es una copia de la RAM; la bandera `+0x238` del bloque `0x43EDF684` (la que enciende Silent)
está en RAM. Si en el momento del apagado vale 1 y esa página entra en la imagen, el arranque caliente
empezaría **con Silent ya activo**, sin volver a tocar el menú. En contra: `0x43804610` reinicializa el
bloque a 0 al arrancar el programa, y no está medido si un arranque caliente vuelve a ejecutar ese código o
reanuda el proceso tal cual. **Comprobación funcional**: tras el paso 4, mirar si el menú sigue en Silent
Shooting. Si no lo está, Silent se activa a mano en cada sesión — que ya cumple el objetivo (vídeo **y**
Silent a la vez), porque el problema nunca fue la bandera sino la instantánea.

### Si algo de la cadena falla, cómo se ve

- **`nflasha5` sigue a cero después del apagado** (`dd if=/dev/nflasha5 bs=16 count=1 | od -c` da ceros):
  el `write("warm")` no llegó. Mirar en `/log` la línea `WARM(warm_count=…)` (llegó) frente a
  `SUS(warm_count=…)` (se fue por `"mem"`), y `do_make_image` / `dropped wbi` del kernel.
- **Se apaga pero el siguiente arranque es frío**: la imagen se escribió a medias (`fVersion` queda `invl`
  hasta el final, a propósito) o Loader3 la rechaza. No hay riesgo de ladrillo: un arranque frío siempre
  funciona; se repite el apagado con el interruptor.
- **Marcha atrás**: reinstalar `build/cfw_bisect/B/pkg/package-4.02/firmware_packed.dat` (3.21 íntegro,
  el actualizador vuelve a dejar el WBI de Sony válido y sale caliente como de fábrica).

### Petición de lectura en cámara (no ejecutada: cámara apagada)

Con telnet, tras el primer apagado y antes de dar el caso por bueno:

```sh
cat /sys/power/image_mode                 # esperado: 2
cat /sys/power/image_dev                  # esperado: una línea con '*' delante de nflasha5
cat /sys/power/image_mem                  # esperado: las 12 regiones wbimem de la cmdline
busybox dd if=/dev/nflasha5 bs=16 count=1 2>/dev/null | busybox od -c   # esperado: W B I 1
grep -E 'do_make_image|rewrite header|warm_count' /log/* 2>/dev/null | tail
```
