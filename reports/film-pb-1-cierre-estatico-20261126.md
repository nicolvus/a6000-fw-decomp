# FILM-PB-1 — Cierre estático: qué está verificado, qué está descartado y qué falta

Fecha: 26-11-2026. Este documento sustituye como **resumen de estado** a
[fallo-global](film-pb-1-fallo-global-pb-20261126.md) y a
[diagnóstico cerrado](film-pb-1-diagnostico-cerrado-20261127.md), que se conservan como registro.
Todo lo que sigue tiene evidencia enlazada; lo que no la tiene está marcado **NO_VERIFICADO**.

## 1. El síntoma, del usuario

1. Un clip convertido a 25p da «No se puede visualizar.».
2. **Un clip grabado por la propia cámara tampoco se reproduce.**
3. La miniatura no aparece; el vídeo sí se lista.
4. «Recuperar BD imág.» no cambia nada.

## 2. La cadena del error, cerrada instrucción a instrucción

`MprIf::PlayMovie` (`0x7229E0`) → orden `0x4000001D` → `FUN_00437BC0` (`0x437BC0`).
De sus **seis** salidas, solo dos producen el mensaje de la cámara:

| Salida | Condición | Código |
|---|---|---|
| `0x437BFA` | guarda A `0x447A1E` = 0 | `0x1A` («Pb Disable!! ref) dsm get») |
| `0x437C2C` | guarda B `0x447F26` = 0 | `0x1A` («Detect UnSupported Content») |

Las otras cuatro dan `0x0A`, `5` o el código del motor, con mensajes distintos.
[Reencuadre §2](film-pb-1-fallo-global-pb-20261126.md).

**Las dos guardas fallan por el mismo motivo**: el `mp4Ifo_If` no está *loaded*.
`GetInhInfo` (`0x67B6E0`) devuelve error en ese caso (guarda A) y
`Mp4IfoIf::GetPlayThumbnailInfo` (`0x6E8430`) devuelve `0xB0100002` al no poder tomar el
mutex del objeto (guarda B). [Guarda A por bits](film-pb-1-sub-guardaa-bits-20261126.md) ·
[ifoFramework](film-pb-1-sub-ifoframework-20261126.md).

## 3. La prueba directa: el log de la propia cámara

El dump `analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin` (1 GiB, por SWD,
**anterior al CFW**) conserva el anillo de log del proceso MPR en VA `0x82DF9300`–`0x82DFC400`
(130 líneas, reproducible con
`reports/evidence/film-pb-1-log-real-20261126/extraer_anillo.py`). Dice:

- **La cámara es NTSC**: `SetLoadInfo : TvSystem is NTSC, frameRate 3`, y `frameRate 3` =
  30000/1001, el de los siete clips. La premisa PAL del diagnóstico del 27-11 es falsa.
- **Ningún IFO se carga**: `MountCmd : Flash Mount Error`, `mp4Ifo faild … 0xB0800001`,
  `LoadSub : MP4 Load Error`, `CreateAndLoad Error` (`0x31000006`) y
  `LoadExec : Flash Load Error` en AVCHD, XAVC y MP4.
- **La BD de respaldo falla**: `CheckSalvageStatus() 0xA0100003` + `Err RcsBackupTblData`,
  que es justo lo que consulta «Recuperar BD imág.».
- **No es solo vídeo**: en reproducción de imagen, `[CACHE]BUFFER SIZE TOO SMALL : 00000000`,
  `Failed to dfs::seek offset=0x0049CE00 errcode=0x0E100001` y
  `Failed to read errcd=0xC3000101`.
- **El `0:02`**: `[MprCnv] Warning ResumeInfo Structure Size is different! 64 vs 60`.

[Informe del log](film-pb-1-log-real-20261126.md).

## 4. Lo que está descartado, con su evidencia

| Hipótesis | Por qué no |
|---|---|
| Cadencia / selector PAL-NTSC | La cámara es **NTSC** y los clips 29,97: coinciden (log real). Un clip propio también falla |
| NVRAM con cambio de sistema | 64 volcados, 16 102 propiedades, ningún selector N/P cambia ([informe](film-pb-1-nvram-pal-ntsc-20261127.md)) |
| BD/catálogo corrupto como causa única | La guarda B es *fail-open* si falta el registro, y «Recuperar BD imág.» no cambia el síntoma ([informe](film-pb-1-sub-bd-tarjeta-20261128.md)) |
| Parche de código en la ruta de reproducción | `libmpr.so` no viaja en el paquete; las 12 direcciones de la ruta no cambian; el mapa `0x1A→7` es idéntico ([auditoría CFW](film-pb-1-auditoria-cfw-20261127.md)) |
| `av-cam` de otra versión | Es el de 3.21 + 40 B integrados + 34 KB de tablas de curvas; `vmlinux.bin` e `initrd.img` son byte a byte los de 3.21; 37 679 cadenas idénticas ([reencuadre §6](film-pb-1-fallo-global-pb-20261126.md)) |
| `libObj` parcheado rompe el arranque | Los **263** inicializadores `.init_array` son idénticos y se ejecutaron: 262/262 retornan igual, ninguna entrada toca los rangos parcheados ni el ifoFramework ([informe](film-pb-1-sub-libobj-init-20261126.md)) |
| Decodificador H.264 caído | Está **fuera de Linux** (en `av-cam`, microcódigo `ZM_AVCD*` de `/usr/sabin`); su fallo sería posterior a `PbStart` y las miniaturas JPEG seguirían saliendo ([informe](film-pb-1-sub-decodificador-20261128.md)) |
| Fuga del mutex del `mp4Ifo_If` | Censo completo: 106 acquire / 106 release, un par por método, todos los caminos liberan; reentrada 0 ([informe](film-pb-1-sub-fuga-mutex-20261126.md)) |
| Arranque en frío (sin `nflasha5`) | Ningún script distingue caliente de frío (`check_bootmode` solo mira `ADJUST`/`BIS`); `warm.ignore_drop=1` hace `wbi_drop` un no-op; el único vector vivo es `dmm.ko` ([informe](film-pb-1-sub-arranque-wbi-20261128.md)) |

## 5. Lo que queda vivo

**El IFO del MP4 no se carga.** Todo lo demás son consecuencias. Y no se ha podido determinar
*por qué* en el estado actual de la cámara, porque hacen falta datos que solo están en ella o
en la tarjeta.

Y hay una segunda lectura del mismo log, que apunta más arriba: `[CACHE]BUFFER SIZE TOO SMALL :
00000000` **no es un fallo de lectura**, es un **área de memoria sin reservar**. Ojo, corregido el
26-11 (`reports/film-pb-1-sub-streamarea-20261126.md`): **ese `SetArea(0)` es del camino de FOTO**
(hueco 13), no del de vídeo — llega antes del callback `EnterStillPb` y el `C1000010h` lo emite el
`GetArea` del `StillCache`. El hueco 11 (movie) lo asigna siempre `EnterMoviePb` con
`StreamAreaAllocate` (`r2=1`) y con `m_systemType = 1` el modo alcanzable es el **14**
(`0x01400000`, 20 MiB), no el 1. Lo emite
`StreamCache::SetArea` (`0x7594E0`), que compara el tamaño **pedido** contra el mínimo
`GetEepData(0x3C0057) << 10`; el `0` que imprime es el pedido, que sale del descriptor
`MemInfo[+0x140]` — es decir, el reproductor pidió un área de tamaño 0. El `0xC1000010` que
sigue es literalmente «STREAMCACHE NOT SET AREA», y el `dfs::seek` posterior muere en la
comprobación de estado (`0x0E100001`: handle que no está en la lista de abiertos), **sin tocar
el medio**. Conclusión: el log muestra **inicialización incompleta del subsistema de
reproducción**, no una tarjeta dañada ([informe](film-pb-1-sub-cache-still-20261126.md)).

### 5.1 El dato que cierra el volumen: las fotos sí muestran miniatura

Comprobado en la cámara por el usuario (26-11-2026): **las miniaturas de las fotos aparecen**.
Las fotos se leen del mismo volumen, por el mismo `dfs` y con el mismo montaje. Por tanto:

- El volumen, la tarjeta, el sistema de ficheros y la lectura **funcionan**.
- El `[CACHE]BUFFER SIZE TOO SMALL` / `dfs::seek` del log del 20-10 **no** son el estado actual
  (ese día el volumen ni siquiera montaba: `MountCmd : Flash Mount Error`).
- Queda descartada la familia «M2 — volumen/DFS».

Lo que queda es **el camino de vídeo**: el `mp4Ifo_If` y los ficheros de índice AV, o el área de
memoria que ese camino reserva y el de foto no.

### 5.2 Familias que siguen vivas

| Familia | Qué la sostiene | Qué la confirmaría |
|---|---|---|
| **M1 — tabla de buffers del modo**: el hueco del área del reproductor vale 0 | ver §5.4: el tamaño **se copia de una tabla estática por modo**, no se pide al DMM | traza nivel 5 (`CMD(SET_AREA)`, `Type2Mode:`) o que dependa del modo de arranque |
| **M3 — índice/journal AV**: `AVF_INFO\AVIN0001.INP` o el pack `RcsTbl` incoherentes | ver §5.3 | renombrar `AVF_INFO` y dejar que la cámara lo reconstruya, o formatear en la cámara |

El log del 20-10 mostraba las dos a la vez porque el volumen no montaba; con las fotos
funcionando, la que sigue viva es la que solo afecta al vídeo.

Un candidato concreto del destructor, ya verificado en desensamblado: `0x6E81BC` destruye
aunque el acquire haya fallado, libera un lock que no posee, borra el semáforo tomado y **no
limpia `[handle+4]`**. Si algo hace destruir el acsr, el `mp4Ifo_If` queda inservible para el
resto de la sesión. Parche mínimo propuesto: `0x6E81E0: 20 B1 → 80 B9`
([auditoría](film-pb-1-sub-fuga-mutex-20261126.md)).


### 5.3 Corrección: `RcsBackupTblData` no lee ficheros, y el dato de las fotos tiene un límite

Auditado (`reports/film-pb-1-sub-rcsbackup-20261126.md`): `RcsBackupTblData` (`0x35EA1C`)
**no abre ningún fichero**. Es un envoltorio de `0x35E04C`, que hace `BkRead` de un pack de
sectores por `(userId, backupId)` (`0x2B39B8` → `0x2B2F48` → `0x2B3948`); no hay ni una cadena
`AVIN*` ni `PRV00001.BIN` en esas funciones. El pack se llama **`RcsTbl`** y guarda el journal
de la última grabación (`rootDirName`, `recDirName`, `recFileName`, flags y `contFileNo`).

- `Err RcsBackupTblData` solo sale con cabecera `0x10` (`0x3AFAFE`/`0x3AFB06`); el caso típico,
  `0x10100001`, significa **«esa entrada no tiene reader registrado»**.
- Un desajuste real del journal da `0x00500003` → «Need Salvage» + flag `[obj+0x44]=1`, que es
  **otra firma**.

Ficheros de `AVF_INFO` (constructor de rutas `0x12C5C8`, tabla `0x7A9070`): `AVIN0001.INP`
(+0xBC, primario), `AVIN0001.BNP` (+0xC9, respaldo) y `AVIN0001.INT` (+0xF0, tabla interna);
`mp4Ifo` **no tiene índice propio: su catálogo es el `INP`**, y sin `.BNP`/`.INT` el IFO sigue
cargando.

Y el límite del dato de las fotos: la rejilla de miniaturas lee `DCIM`/EXIF y **no pasa por el
IFO**, mientras que el IFO de foto (`FlashLoadHdm`, `0x5D2BD0`) falla igual si falla el journal.
O sea: «fotos sí» prueba que **la lectura de ficheros funciona**, no que el journal AV esté sano.

Consecuencia práctica: si el código del log es de la familia `0x10xxxxxx`, **ningún fichero
copiado lo arregla**; hay que dejar que la cámara reescriba el pack. Y como «Recuperar BD imág.»
se apoya en ese mismo journal, el gesto que sí fuerza reconstrucción es **renombrar `AVF_INFO`**
(y, si eso no basta, formatear en la cámara).


### 5.4b El área de movie es una FILA de tabla, y hay modos con movie=0 y still>0

Verificado (`reports/film-pb-1-sub-tabla-buffers-20261126.md`): `DistributeBufInfo` (`0x5F703C`)
copia la entrada `0xC` B de la tabla del modo (`+0`=tamaño, `+4`=orden, `+8`=índice; terminador
`+8 == -1`) al singleton `0xA4F368 + idx*0x18` (`+0` vAdrs, `+4` pAdrs, `+8` size), con el store
`dst+8 = [src+0]` en `0x5F73E0`. Lista de modos en `0x8D87E8` (35 entradas), puntero en
`0xA4F0A4`. Hueco **11 = movie** (`+0x108/+0x110`), hueco **13 = still** (`+0x138/+0x140`).

Y lo importante: **cinco modos tienen movie = 0 con still > 0** — `0x03` (24 MiB), `0x06` (22),
`0x12` (24), `0x13` (16) y `0x20` (3) —, y con `m_systemType = 1` los alcanzables son `0x03`,
`0x06`, `0x12` y `0x20`. La miniatura de foto va por el hueco 13 y el vídeo por el 11: **basta la
fila del modo para tener exactamente el síntoma** (foto sí, vídeo no, con cualquier clip y con la
tarjeta recién formateada).

El modo activo se lee en `0x9DECAC`; en cámara basta leer `0x9DECAC`, `0xA4F478` (movie) y
`0xA4F4A8` (still), y la línea `StreamAreaAllocate(next): complete ret=%ld` (`0x8DA720`) para
separar «la tabla dice 0» de «falló el allocate».

### 5.4 Corrección de M1: el área no la da el DMM, la da una tabla estática por modo

Auditado (`reports/film-pb-1-sub-dmm-area-20261126.md`):

- `StreamCache::SetArea` **no calcula** el tamaño: copia `[X+0x138]` (dirección) y `[X+0x140]`
  (tamaño) de una entrada de 0x18 B (`+0`=vAdrs, `+8`=size) del singleton `.bss` `0xA4F368`.
  `0x138/0x18 = 13` es el hueco del *still* y `0x108/0x18 = 11` el de *movie*.
- Las rellena `DistributeBufInfo` (`0x5F703C`) a partir de una **tabla estática por modo**
  (`mp_modeTblForBufTbl` `0x8D87E8` → «Movie Pb» `0x9DB0E4`, «Still Pb» `0x9DBD20`), elegida en
  `Type2Mode` (`0x5F699C`) según `m_systemType` (`[0x9DEFE0]`=1).
- Las direcciones físicas van por `MemConfig::Mmap` (`0x5F6544`) a `/dev/stream` o `/dev/mem`.
  **El DMM no interviene**: en libmpr solo sirve «units» (`UnitMemAllocate`…).

Tres formas de que el tamaño sea 0: (a) el modo no define ese hueco y el `.bss` nunca se
escribió; (b) `StreamAreaFree` (`0x5F802C` → `0x5F63CA(entry,0)`) lo puso a cero dejando el
puntero válido; (c) `setupMode > 5` → `SetArea(0,0,1)` literal (`0x43944E`–`0x43945C`).

Y un límite importante: `dmm.ko` (que sí tiene símbolos) espera `DmmConfig=/setting/DmmConfig.bin`
o `/usr/share/dmm/DmmConfig.bin`, y **ninguno de los dos está en la imagen `0700`**; si faltara en
la cámara, `GetConfigData` devolvería −1 y `osal_abort` la pararía. Como la cámara arranca, el
fichero está: el DMM queda fuera de la ecuación.

### 5.5 El fallo real, con nombre: `0x10100001`, una entrada de la tabla de readers sin puntero

Verificado (`reports/film-pb-1-sub-mp4ifo-load-20261126.md`):

- Las líneas 1749 y 1340 del anillo son `0x698EE6` (`mp4Ifo_General::FlashLoadForMsv`,
  `0x698EC8`) y `0x698F4A` (`mp4Ifo_General::CheckSalvageStatus`, `0x698F18`); la segunda es un
  **eco** de la primera. `FlashLoadForMsv` tiene **una sola** condición de fallo: que `0x3AFA94`
  devuelva ≠ 0.
- Y `0xB0800001` **no es un código de fichero**: es el `default` del traductor `0x6F0D4C`.
- El estado real es **`0x13100001`** = `0x350124(0x10100001, …)`, y `0x10100001` lo da `0x2B39B8`
  cuando **`[0xA3699C + 0x14*idx + 4] == 0`**, es decir cuando esa entrada de la tabla de readers
  **no tiene rutina de lectura**: `ReadFirstPackData` (`0x2B3948`) **ni se ejecuta**.

O sea: no falta un dato del MP4, falta un **puntero a función** en una tabla del `.bss`. Por eso
falla igual MSV, DCF y XAVC, por eso la tarjeta recién formateada no cambia nada, y por eso el
formato del fichero es irrelevante. Y la foto se salva porque su miniatura va por `DCIM`/EXIF,
sin pasar por ese almacén.

## 6. Reproducibilidad en el arnés

- El arnés QEMU **arranca hoy** y llega a la pantalla de disparo (medido: `alive=206`,
  `threads=90`, 80 módulos, dos arranques).
- `0x5BAD00` (Acquire) se ejecuta ≥16 veces con el mutex **libre** (`[obj+4]=1`, sin dueño):
  el fallo **no** se reproduce por sí solo.
- La galería no abre `view/INDEX_PLAYBACK` ni `view/SINGLEPB` (abren y cierran en 10 ms), así
  que `0x6E8430` y `0x61A8F0` no llegan a ejecutarse.
- El estado guardado del 20-11 (`live/e2e17b/estado.zst`) **sí contiene** el log del MMgr con
  el mismo cuadro que la cámara: `MountCmd : Flash Mount Error`, `LoadSub : MP4 Load Error`,
  `mp4Ifo faild … 0xB0800001`, `LoadExec : Flash Load Error`, más
  `CheckMSId : MS IDs are not same!` y los `BeginRepair`/`Inconsistency` del menú de
  reparación (503 líneas extraídas y deduplicadas en
  `reports/evidence/film-pb-1-arnes-log-20261126/`).

[Informe del arnés](film-pb-1-sub-arnes-galeria-20261126.md).

## 7. Qué falta y cómo se obtiene, por orden de riesgo

| # | Acción | Riesgo | Qué decide |
|---|---|---|---|
| 1 | ¿Aparecen las **miniaturas de las fotos**? | nulo | si el fallo es del volumen/almacenamiento o solo del vídeo |
| 2 | Copiar `AVF_INFO\` y `MP_ROOT\` de la tarjeta a una carpeta del PC y ejecutar `scripts/filmpb1_audita_tarjeta.py <carpeta>` | nulo | si el índice miente: compara por clip la duración del índice con la del `mvhd`, el tamaño del índice con el de disco, y avisa de entradas huérfanas o con `bValid=0` |
| 3 | **Otra tarjeta formateada en la cámara**: grabar un clip y reproducirlo | nulo | tarjeta/volumen contra cámara |
| 4 | **Formatear la tarjeta actual** en la cámara (con los clips copiados) | nulo (se pierde el contenido, no la cámara) | arreglo real si el volumen está incoherente |
| 5 | Encender **sin tarjeta** | nulo | si el montaje y el aviso funcionan (la A6000 **no tiene memoria interna**: no hay nada que reproducir) |
| 5b | **Renombrar `AVF_INFO`** en el PC (`AVF_INFO_bak`) y poner la tarjeta: la cámara debe reconstruirlo | nulo y reversible | si el índice AV era el problema (M3) sin perder los clips |
| 6 | Flashear **A2** (todo Sony, versión > instalada, conservando `nflasha5`) | bajo | si el firmware tiene algo que ver; es el único flasheo que discrimina con contenido coherente. **Ya está construido y verificado**: `build/sony_puro_con_wbi_404/package-4.04/firmware_packed.dat` (`e45c502c…dc627`), cuyo `firmware.tar` tiene el **mismo SHA-256 que el de Sony 3.21** (`97024649…d5a8`), es decir payload byte a byte oficial con `nflasha5` dentro (`sin_wbi: false`) |
| 7 | Flashear **C** (`libmpr` con las guardas anuladas) | medio-bajo | solo discrimina las guardas; si el IFO no carga, cambiará el código de error |

El 3.21 oficial **tal cual no se instalaría**: el guard exige versión estrictamente mayor que
la instalada y rechaza antes de escribir. Ninguna vía toca `nflasha1`, Loader2/3, `nflasha0`
ni la tabla de particiones; el único camino a ladrillo es el core de Darwin
([auditoría de riesgo](film-pb-1-sub-riesgo-flash-20261126.md)).

## 8. Límites

- **NO_VERIFICADO** el estado actual de la cámara: el log real es del 20-10 y el volumen de
  entonces puede no ser el de ahora.
- **NO_VERIFICADO** que el `AVIN0001.INP` real use la rejilla del lector (está probado con un
  sintético, no con el fichero de la tarjeta).
- **NO_VERIFICADO** el dueño del mutex en la cámara y si el arnés destruye el wrapper.
- La emulación de `0x6E8430` no puede completarse sin el `dfs_If`/`MMgrIf` reales: se para en
  `ER_FAILED_ACQUIRE_SEMAPHORE`, que es precisamente el mecanismo que se quiere observar
  ([emu-fps](film-pb-1-sub-emu-fps-20261127.md)).

## 9.1 Dato de campo decisivo (26-11): formatear la tarjeta no arregla nada

El usuario **formateó la tarjeta en la cámara** y el vídeo sigue sin reproducirse. Con eso caen
las tres familias de contenido de golpe:

- La tarjeta, el volumen y el sistema de ficheros: el formateo los reconstruye.
- El índice AV (`AVF_INFO\AVIN0001.INP`): `CreateAVIndexFile` lo rehace desde cero.
- El journal `RcsTbl`: el formateo lo invalida y la cámara lo reescribe.

Y no cae el otro dato de campo: **las miniaturas de foto siguen apareciendo**. Es decir, la
lectura funciona, el reproductor de imagen funciona, y lo único roto es la **carga del IFO de
vídeo** (los tres formatos) y el **área de buffers del camino de movie**.

Eso deja el problema, sin ambigüedad, en el **firmware**: o la tabla de buffers del modo no
define el hueco de movie, o el `SetLoadInfo`/`Load` del `mp4Ifo` no acepta el contenido, o el
`av-cam` parcheado del CFW (que es el de 3.21 con tablas de curvas de Picture Profile) rompe algo
del camino de vídeo que no se había probado nunca.

## 10. Qué hacer ahora, en este orden

Todo lo que sigue es sin flashear y sin abrir la cámara.

> Los pasos 1 a 4 originales (auditar el índice, renombrar `AVF_INFO`, formatear) **ya no
> aplican**: el usuario formateó la tarjeta en la cámara y el síntoma sigue. Se conservan como
> registro de lo descartado. Lo que queda es el firmware y las pruebas de más abajo.

0. **Decidir con un dato de 10 s**: ¿la cámara reproduce vídeo si se enciende y se pulsa
   reproducción antes de que se generen miniaturas? Si el primer intento va y luego deja de ir,
   el área de buffers se libera (`StreamAreaFree`) y no se vuelve a asignar; si no va nunca, la
   tabla del modo no la define o el IFO no carga nunca.
1. **Sacar la tarjeta, copiarla entera al PC y ejecutar**
   `.venv/bin/python3 scripts/filmpb1_audita_tarjeta.py <carpeta>`. Devuelve, por clip, la
   duración del índice frente a la del `mvhd`, el tamaño del índice frente al de disco, las
   entradas huérfanas y las que tienen `bValid=0`. Si sale limpio, M3 pierde peso; si no, ya
   está el culpable.
2. **Renombrar `AVF_INFO` a `AVF_INFO.bak`** en el PC, poner la tarjeta y encender. La cámara
   debe reconstruir el índice. Es reversible y **no** es lo mismo que «Recuperar BD imág.»:
   esa opción se apoya en el journal `RcsTbl`, que es justo lo que puede estar mal.
3. Grabar un clip nuevo y reproducirlo. Si va, el problema era el índice y se puede devolver
   el resto de los clips copiándolos y dejando que la cámara los reindexe.
4. Si sigue sin ir: **formatear la tarjeta en la cámara** (con todo copiado) y repetir la
   grabación. Esto reconstruye `AVF_INFO` y el journal de cero.
5. Solo si tampoco así: el paquete **A2** ya está construido y verificado
   (`build/sony_puro_con_wbi_404/package-4.04/firmware_packed.dat`), que es Sony oficial byte
   a byte con `nflasha5`, para separar firmware de cámara.

Si en algún momento hay acceso a la cámara (red o USB), la traza de nivel 5 con
`CMD(SET_AREA)`, `Type2Mode:` y `StreamAreaFree` cierra M1 en un minuto, y el breakpoint en
`0x437C0A`/`0x437C3C` dice qué guarda dispara.
