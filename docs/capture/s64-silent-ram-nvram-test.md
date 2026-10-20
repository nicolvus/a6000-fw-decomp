# S64 — prueba en cámara: SilentShutter en RAM, NVRAM y consumidores

20-10-2026. Cámara ILCE-6000 fw 3.21 en service mode (PMCA, `scripts/senser_*.py`); análisis estático con REA (una sesión, cerrada) y barrido Capstone de `av-cam.bin` (SHA `b60c845c…6bb9`). Sin flasheo, sin parche; la única escritura fue una palabra de RAM, restaurada.

## Hechos medidos en la cámara (VERIFICADO)

1. **Acceso:** service mode lee memoria física (`readMemory`) y el shell escribe con `dd of=/dev/mem` (`scripts/senser_write_poll.py`). Física = virtual de `av-cam` − `0x40000000`.
2. **Campo Silent** `0x43edf684+0x238` = física `0x83edf8bc`: `0→1→0` con lectura confirmada. Con la sesión abierta el valor se mantuvo 60 s (48 977 lecturas). La primera observación (a 0 unos 40 s tras escribir y releer en otra sesión) **no está explicada**.
3. **NVRAM:** backups `mem` y `flash` (852 647 B) en tres estados (base, Silent=1, revertido). `flash` idéntica en los tres; `mem` difiere en 3 bytes (33, 237 673, 613 374) y esos cambios están ya en «Silent=1» y siguen en «revertido» ⇒ no dependen del modo. `analysis/camera-dumps/silent-nvram-20261020/` (no versionado).
4. **RAM 4 MB** (`0x83c00000–0x84000000`), 4 ciclos off/on: 9 palabras cambian de forma consistente (la escrita + 8 punteros/banderas). **Control** idéntico escribiendo en `0x83dab230` (zona a cero, sin relación): la palabra escrita + 7 del mismo tipo ⇒ esas palabras son artefacto del procedimiento (`dd` en el shell), no del modo.
5. Escribir el campo directamente **no ejecuta el handler `0x40e3`**: no prueba nada sobre su efecto, solo que no hay cambios colaterales visibles en esas regiones.

## Hallazgos estáticos (`av-cam.bin`)

- El bloque `0x43edf684` tiene 5 referencias directas (`0x43803f14`, `0x43803f56`, `0x438045c0`, `0x43804c52`, `0x43804dea`). Getter `0x43804de8` (22 llamadoras) y `0x43804c38` (4): ninguna llamadora carga/guarda con `#0x238` o `#0x280` (VERIFICADO sobre desensamblado).
- Copia de 0x560 B bloque → objeto de trabajo `0x43ed4d28+0x48` en `0x437dfd58` (llamadoras `0x43808774`, `0x43b02206`); el campo queda en `+0x280`. Los 15 usos del puntero GOT `0x44023bbc` no tienen cargas `+0x280/+0x238`.
- **`0x43804610`** (no reconocida por REA, Thumb): lee un byte con `Backup_read` (wrapper `0x435613b0`, slot `0x298` de la tabla de servicios) y **reinicializa el bloque a valores por defecto, poniendo `+0x238` y `+0x280` a 0** (`0x438047b6`, `0x43804810`). Única llamadora: `0x437881a8`. El byte de backup no fija `+0x238`.
- `0x43802614`: handler hermano que escribe `+0x280` (otro comando, patrón «un campo por comando»; sin estudiar).
- Escritura de backup en `av-cam`: wrappers `0x43561420` (write), `0x43561458` (write_multi), `0x43561474` (async), `0x43561494` (multi_async). Única llamadora cercana al bloque: `0x43809148` (despachador de mensajes `0x3000–0x3034`): escribe un byte 0 en los mensajes `0x3000/0x3003/0x3006/0x3007/0x300c`; sus campos del bloque son `+0x40a/+0x4cc/+0x450…/+0xd0`, no `+0x238`.

## Conclusión

**No se encontró** ruta que persista el modo Silent en NVRAM; la inicialización lo deja a 0. No se puede «fijar» el modo por backup. Sin consumidor de captura demostrado. S51 A/B/C = NO VERIFICADO; «electrónico completo» NO VERIFICADO.

## Límites

Barrido lineal de `av-cam`: 882 sitios `+0x238/+0x280` (872 Thumb, 10 ARM); solo se trataron los de la zona del bloque. Slots de backup sin wrapper (`write_vsize`, `setting_attr_async`, `sync_subsystem`) no cubiertos. Lecturas indirectas (copias en bloque a otras estructuras) no vistas. Solo 4 MB de RAM comparados.

## Ampliación: cuándo se reinicializa y tabla de comandos «de estado»

- `0x43804610` se llama desde la secuencia de arranque de `av-cam` (`0x437881a8`, entre `0x437e18b4` y `0x4378f9b4`, junto a otras inicializaciones de módulo). Es una inicialización de arranque, no una reposición periódica. Que ocurra también al cambiar de sesión de service mode: NO VERIFICADO.
- Tabla de entradas `{ID, handler|1, 0}` en `0x43fffbb8…` (IDs `0x40d7…0x40f3`, VERIFICADO por bytes). Cada handler guarda un único campo del bloque `0x43edf684`: `0x40e2→+0x234`, **`0x40e3→+0x238`**, `0x40ed→+0x23c`, `0x40ee→+0x240`, `0x40ef→+0x242`, `0x40f0→+0x244/248/24c`, `0x40f1→+0x250`, `0x40e4→+0x35c`, `0x40e6→+0x360`, etc. El bloque es un espejo de ajustes enviados por UIPC; ningún handler hace más que almacenar.
- `+0x280` lo escribe otro handler (`0x4380260c`), fuera de esa tabla (tabla no localizada).

## Comparación con la A7S (`av-cam.bin` fw 3.20, mismo base `0x43541000`; Capstone Thumb, sin REA)

- Handler `0x40e3` A7S: `0x437a9cb0` → `str.w r2,[bloque+0x250]`; bloque A7S `0x43ea1d84`, único getter `0x437ab600` (52 llamadas).
- Ninguna de las 52 llamadas al getter carga/guarda `+0x250/+0x251/+0x252` en las 14 instrucciones siguientes (VERIFICADO sobre el desensamblado lineal). Copia en bloque análoga a la A6000: `0x43814700` (`movw r2,#0x584`, destino `objeto+0x50` ⇒ campo en `+0x2a0`), objeto `0x43ee69a8`. Las 18 funciones que cargan ese puntero GOT no leen `+0x29c…+0x2a2` en 120 instrucciones.
- Conversor tipo 0/2 `0x4379ec04`: devuelve tipo 2 si `[objeto 0x43ea3108 + 0x7a] != 0`. Es el único lector de ese byte entre los 284 usuarios del puntero GOT (offset `0x78c4`); **no se encontró su escritor** (ni un `strb #0x7a` en 90 instrucciones tras cargar el puntero, ni a ≤25 instrucciones de una llamada al getter del bloque).
- Conclusión parcial: la ausencia de un lector directo de `+0x238` en la A6000 **no distingue** A6000 de A7S, porque en la A7S tampoco aparece un lector directo de `+0x250`. El enlace «estado `0x40e3` → byte `+0x7a` → tipo 2» de la A7S no está demostrado; **NO VERIFICADO**. Pendiente: escritor de `0x43ea3108+0x7a` (REA con sesión abierta y `trace_native_values`).

### Consumidor A7S localizado (REA, sesión A7S abierta y cerrada; pseudocódigo + bytes)

- `0x43813d90` (A7S, inicialización del objeto de captura `param_1`) hace `FUN_4379ec04(*(*FUN_437b38ec() + 0x250), param_1)` ⇒ **el estado Silent (`+0x250`) llega al conversor a través de un puntero a «ajustes activos»** (`FUN_437b38ec()` devuelve `0x43ea70a0`; análogo al selector `0x43804c38` de la A6000), no a través del getter `0x437ab600`. El resultado se guarda en `param_1+0x78c`; si vale 2, `param_1+0x748 = 1`.
- El conversor `0x4379ec04` devuelve 2 si el byte `[0x43ea3108+0x7a]` es distinto de cero (tras descartar `param_2+0x4b84`, `+0x785` y `+0x1e0==0x19`). El byte `+0x7a` no lo escribe ninguna de las funciones que cargan ese puntero GOT; sí lo escriben, desde un parámetro (`r0`), `0x437042f6`, `0x4383a364`, `0x437eab66` (a partir de un byte `+0xc` de una petición), `0x4385ed62`. Su origen real: NO VERIFICADO.
- Implicación para la A6000: el lector equivalente sería un acceso `*[ajustes activos]+0x238` en la inicialización del objeto de captura. Los 61 `ldr … #0x238` del binario A6000 se revisaron por contexto: son llamadas virtuales (`vtable+0x238`, p. ej. `0x43abb770`), volcados byte a byte del bloque a una estructura de diagnóstico (`0x437b2f18…0x437b33b4`, destino `+0x86a…+0x87f`) o campos de otras estructuras; ninguno reproduce el patrón A7S «leer estado → conversor → tipo 2». Coherente con H1 refutada; el barrido manual no es exhaustivo.

## Prueba en modo normal por telnet (cámara viva, 2026-10-20)

- **Acceso:** OpenMemories Tweak activa `busybox telnetd -l sh` (puerto 23, root sin contraseña) y `libadbd.so` (5555, usuario `shell`). Helper: `scripts/camera_telnet.py`; ADB con `adb-shell` (pip) sin binario `adb`. El busybox no trae `od/head/tr/id`; hexdump: `chroot /android /system/bin/hd <fichero en /android/dev>`.
- **Mismo bloque:** el bloque de ajustes `0x83edf684` en modo normal coincide con el de service mode en 299 de 344 palabras (las 45 distintas son ajustes ya rellenados por la app). `+0x238` = 0 al inicio. VERIFICADO.
- **Escritura RAM** `+0x238=1` (`dd` a `/dev/mem`): se mantiene al menos 5 s, pero **vuelve a 0 tras el primer disparo** (el espejo se reescribe).
- **Con el valor forzado a 1 cada ~20 ms** (bucle en la cámara) y 3 disparos: el obturador siguió siendo **mecánico** (reporte del usuario). La copia de trabajo `0x83ed4ff0` (`0x43ed4d28+0x48+0x280`) quedó en 0 en todas las muestras (397). ⇒ en modo normal de la A6000, el campo `0x40e3`/`+0x238` **no activa el obturador electrónico** y la copia no se refresca durante un disparo. NO VERIFICADO si la dirección de la copia es la correcta.
- Silent restaurado a 0 y bucles detenidos (verificado).
- **Disparo remoto:** `/dev/input/event0` es un teclado virtual (`tuttle2.kl`, sin tecla de disparador); S1/S2 son estados de `ScalarInput` (`ISV_KEY_S1_1/S2`), no teclas inyectables. Disparar desde el PC exigiría una app propia que llame a `CameraEx` (no hecho). Odex en `analysis/camera-dumps/live-android-20261020/` (ignorado por git).

## Disparo remoto y matriz de valores (2026-10-20)

- **Disparo remoto:** `tools/remote-shutter/` (APK `ar.shutter`, `build.sh`; toolchain JDK17 + build-tools 34 en `~/.local/android-build`). Abre `CameraEx` por reflexión **sin preview** (el overlay falla: `Overlay Creation Failed`) y hace `takePicture` por `GET :8080/shoot`; necesita permiso `CAMERA` (sin él: `CameraExService: Permission Denial`). Se instala con `pm install` por ADB y se arranca desde la lista de aplicaciones de la cámara (`am start` falla: «current activity is being kept for the user»). VERIFICADO: 3/3 y 6/6 disparos.
- **Matriz** (`scripts/camera_shutter_matrix.py`, valores mantenidos cada 20 ms; solo RAM): base, `+0x238`=1, `=2` (tipo 2 de la A7S), `+0x238`+copia `0x83ed4ff0` =1, =2, base. **Oído del usuario: los 6 disparos sonaron igual** (dos pasadas). NO se detecta obturador electrónico en modo de aplicaciones.
- **Bloque alternativo:** `0x43804c38` devuelve `ctx+8` (`0x43e93f3c`, `ctx=0x43e93f34`) si `ctx[+0x57c]!=0`; en vivo ese byte vale 0 ⇒ se usa el bloque primario (alternativo difiere en 70/344 palabras). VERIFICADO en vivo.
- **A7S:** el conversor `0x4379ec04` mapea el estado (0/1) por una tabla de 2 entradas; no se localizó su equivalente en la A6000 (42 candidatos con la misma forma `cmp r0,#1; ldr.w …lsl #2`, ninguno verificado).
- Los JPEG de `CameraEx` no traen notas de fabricante Sony (exiftool): no sirven para distinguir mecánico/electrónico. NO VERIFICADO si el modo de aplicaciones usa la misma ruta de captura que la app normal.

## Campos vecinos: reinicio de la cámara (2026-10-20)

- `scripts/camera_shutter_matrix.py HOST vecinos`: caso 1 (base) disparó bien (`done 410745`); en el caso 2 se escribieron **10 palabras `0x230..0x254` del espejo `0x83edf684` a 1** (bucle cada 20 ms, solo RAM) y la cámara **se reinició** (la conexión cayó durante el disparo; el usuario confirmó «se reinició»). Hay `exception.reboot=1` en la línea de comandos del kernel.
- No se sabe qué palabra (o la combinación con el disparo) provoca el reinicio: NO VERIFICADO. Siguiente: bisecar una palabra por vez (valor 1) y sin disparar, y luego disparando.

## Bisección de campos vecinos (2026-10-20)

- `scripts/camera_bisect_fields.py` (`SHOOT=1`): cada palabra del espejo `+0x234…+0x254` (9 campos) forzada a 1 durante un disparo remoto: 9/9 disparos correctos; **el usuario oyó el obturador igual en todos**. Sin escritura (8 disparos) y con `+0x230` reescrito a su valor (3 veces): sin reinicio, por lo que los dos reinicios previos no se reproducen y no se atribuyen a un campo (NO VERIFICADO la causa).
- Valor 2 y copia de trabajo para estos campos: no probados.

## Búsqueda estática del lector de la captura (2026-10-20)

Sesión REA sobre `av-cam.bin` (REA no reconoce las funciones Thumb de esta zona: «no procedure starts at…»; se completó con capstone y `silent-liro.gpr` en solo lectura).

- **Copia de trabajo** (`0x437dfd58`): `memcpy(0x43ed4d28+0x48, bloque, 0x560)`. Sus 15 accesos PIC (`0x437dfb08…0x437e00fc`) son getters; los 14 llamadores de `0x437dfe4c` (retorno = obj+8) **no leen** `+0x278/+0x250/+0x280/+0x238` del retorno. Los accesos `[rX,#0x278/#0x280]` restantes (41/38 en todo el código) son otros objetos: bytes de tablas de ID (`0x4371b8a0`→ struct estática `0x43e86bbc`), `short*` (offset ×2) o contadores; ninguno es lector de Silent.
- **Selector `0x43804c38`**: solo 6 llamadores, accesores de campo (`+0xa5`, `+0x1f3`, `+0x2c4`…); ninguno lee `+0x238`.
- **`0x43804c5c`** (único llamador `0x43792d9e`, dentro de `0x43792a0c`): copia el bloque de 0x560 B **a `0x43e9b548`** ("instantánea actual", usada por ~170 sitios PIC en `0x4378e93c…0x4379467e`) conservando unos campos. Esta instantánea es el candidato nuevo: `0x43e9b548+0x238` = `0x43e9b780` (físico `0x83e9b780`, palabra 553283040). Los lectores directos de esa base no cargan `+0x238` (solo el descartado `0x43792fb4`, otra estructura).
- NO VERIFICADO: que la instantánea `0x43e9b548` esté viva en RAM ni que algo lea `+0x238` a través de punteros pasados a otras funciones. Prueba pendiente en cámara: comparar `0x83e9b548` con el espejo y forzar `+0x238` ahí (`BASE=0x83e9b548 SHOOT=1 scripts/camera_bisect_fields.py 1 0x238`). La cámara dejó de responder (`No route to host`); requiere que el usuario la reconecte.

### Prueba en cámara de la instantánea `0x83e9b548` (2026-10-20)

- RAM viva: 338 de 344 palabras iguales al espejo `0x83edf684`; `+0x238` = 0 en ambos.
- `BASE=0x83e9b548 SHOOT=1 camera_bisect_fields.py 1 0x238`: 1 disparo remoto correcto (`done 408841`), cámara viva; el usuario oyó **obturador mecánico**. Un solo disparo y valor 1; valor 2 y las 6 palabras distintas sin probar. Electrónico NO detectado.

### Disparo con la app normal y tres escrituras a la vez (2026-10-20)

- Bucle en la cámara (3000 × 20 ms): espejo `0x83edf8bc`, instantánea `0x83e9b780` y copia `0x83ed4ff0` forzados a 1. El usuario disparó con el botón en la pantalla normal de fotos: los disparos hechos sonaron como obturador de siempre y **la cámara se reinició**. No se sabe cuántos disparos completó antes ni si el reinicio lo causa una de las escrituras (tercer reinicio con escrituras en vuelo; en controles sin escritura no hubo ninguno). Reinicio borra los cambios de RAM; flash no se tocó. Electrónico NO detectado en la app normal. NO VERIFICADO la causa del reinicio.

### Repetición con app normal (2026-10-20)

- Mismo bucle (espejo + instantánea + copia a 1), disparos con el botón: el usuario oyó obturador mecánico («si suena»); sin reinicio reportado. Electrónico NO detectado. El reinicio anterior no se reprodujo (causa sigue NO VERIFICADO).
