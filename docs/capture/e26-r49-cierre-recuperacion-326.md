# E26-R49 — Cierre: cámara recuperada en el 3.26 (método SWD completo y resultado)

Fecha: 03-11-2026. **Incidente cerrado: la cámara arranca y reporta firmware 3.26.** Este informe consolida [R46](e26-r46-procedimiento-fisico-swd.md) (procedimiento físico planeado), [R47](e26-r47-primer-contacto-swd-lectura-ram.md) (primer contacto SWD, lectura de RAM y confirmación física de la causa) y [R48](e26-r48-plan-recuperacion-actualizador-swd.md) (plan de recuperación sin escribir NAND e intento interrumpido al 45 %), añade el método técnico que no había quedado escrito en el repositorio, y documenta la ejecución que terminó con éxito.

Etiquetas: **MEDIDO** · **LEÍDO** · **INFERENCIA** · **NO VERIFICADO**.

## 1. Resumen

| | |
|---|---|
| Causa del bloqueo | `nflasha3` del 3.25 recomprimida con un formato (residuo de sector) que Loader3→ARM7→LDEC no decodifica ([R36](e26-r36-causa-fallo-325.md)); confirmado físicamente: P2 (`CFG_E:Load file`) falla al cargar `\sabin\idt_cam.bin` de la partición 3 y devuelve −302 ([R47 §15](e26-r47-primer-contacto-swd-lectura-ram.md#15-doble-arranque-y-origen-del-302-confirmado-p2-sobre-sabinidt_cambin-03-11-2026-solo-lectura)) |
| Vía de recuperación | Forzar por SWD, solo en RAM/registro, que Loader3 crea que existe `\updater\mode`; arranca el actualizador de fábrica de `nflasha1` (intacto) y se instala el 3.26 oficial por USB — la NAND la escribe el actualizador de Sony, no nosotros ([R48](e26-r48-plan-recuperacion-actualizador-swd.md)) |
| Primer intento de instalación | Se cortó al 45 % con `Response error: 0x1063` (NG de Darwin); sin confirmar nada en la cámara (versión seguía en 3.25) |
| Resultado final | **Firmware 3.26 instalado y confirmado** (`pmca-console info`); la cámara arranca en modo normal (Mass Storage), sin el patrón de LED de error |
| Escritura manual en NAND | **Ninguna, en todo el procedimiento.** Solo escribió la NAND el actualizador oficial de Sony |

## 2. Montaje físico y topología de depuración (R46 + R47, consolidado)

| Elemento | Detalle |
|---|---|
| Sonda | RP2040 Zero con firmware `debugprobe-zero` v2.3.0 (CMSIS-DAPv2, `2e8a:000c`) |
| Conexión a la cámara | Hilo de cobre esmaltado soldado al pad del **lado BIONZ** de R4911 (SWCLK) y R4912 (SWDIO), más masa — opción 5a de R46 (sin montar resistencias de 0 Ω ni usar CN4906, que están sin poblar) |
| Tensión en reposo | R4911 = R4912 = 3,09 V (dentro de 3,0–3,3 V, lógica de 3,15 V) |
| Herramienta | OpenOCD 0.12.0, `adapter driver cmsis-dap`, `transport select swd` |
| Velocidades usadas | 100 kHz (primer contacto), 1 MHz (volcados y captura de arranque; sin discrepancias frente a 100 kHz en 256 palabras de prueba) |
| DPIDR | `0x3ba02477` |
| Mapa de Access Ports | AP0 = AHB-AP (memoria física, `CSW=0x02800062`); AP1 = APB-AP (depuración, `CSW=0x80000042`, `BASE=0x80000000`); AP2 = JTAG-AP; AP3–AP5 vacíos |
| Topología CoreSight (vía AP1) | Tabla ROM en `0x80000000`, anidada en `0x80100000`, con 4 núcleos **Cortex-A5** (`part 0xc05`), bases de depuración `0x80110000`/`0x80112000`/`0x80114000`/`0x80116000`, cada uno con su PMU/CTI/ETM. Todo el trabajo se hizo sobre el núcleo 0 (`0x80110000`) |
| eFuse / bloqueo de depuración | **Descartado para lectura**: AP0/AP1 responden sin restricción. No se probó para escritura de depuración más allá de `halt`/`set_reg` de registros de CPU |

**Lectura de memoria física (AP0, bajo nivel):** `chip.dap apreg 0 0x04 <dirección>` fija `TAR`, `chip.dap apreg 0 0x0c` lee `DRW`. Así se leyeron los primeros vectores de arranque y, más tarde, los rangos de destino de la tabla CFG (R47 §3/§10).

**Lectura de memoria a través del núcleo (`cortex_a`, con el CPU examinado):** una vez creado el target (`target create chip.cpu cortex_a -dap chip.dap -ap-num 1 -dbgbase 0x80110000`), `chip.cpu read_memory <addr> 32 <n>` lee a través de la vía de depuración del propio núcleo (respeta MMU/caché si están activas); se usó para los volcados de RAM y para inspeccionar código/pila tras un `halt`.

**Halt directo por registros (`fasthalt`), usado en toda la sesión para no depender de que el target ya esté examinado:** por AP1, en este orden — `DBGLAR` (`0x80110fb0`) = `0xc5acce55` (desbloqueo), `DBGOSLAR` (`0x80110300`) = `0`, `DBGDRCR` (`0x80110090`) = `1` (petición de halt). Es la secuencia estándar de depuración externa Cortex-A; no escribe memoria de aplicación ni NAND.

## 3. Técnica de puntos de parada encadenados y sus trampas (método, no estaba escrito antes de este informe)

El arranque completo (BootROM → Loader2 → Loader3) ocurre en menos de un segundo, y **los puntos de parada puestos durante Loader2 no sobreviven hasta Loader3** ([R47 §13](e26-r47-primer-contacto-swd-lectura-ram.md#13-corrección-de-12-los-puntos-de-parada-puestos-en-loader2-no-sobreviven-03-11-2026)): un punto de parada en la rutina del LED (que se ejecuta en todo arranque fallido) puesto desde Loader2 nunca saltó. La vía que sí funcionó, usada después en R47 §14/§15 y en R48 P1:

1. `fasthalt` en cuanto el DAP enlaza (lo más pronto posible tras encender, idealmente desde el BootROM).
2. Un único punto de parada en la **entrada de Loader3** (`0xc01f0000`).
3. En cada parada, **quitar los puntos de parada actuales, avanzar una instrucción (`step`) y volver a armar los siguientes de la cadena** antes de reanudar. Sin el `step` previo, un punto de parada puede volver a saltar decenas de veces sobre sí mismo sin que la cámara avance (pasó en un intento intermedio de R47 §15: 39 paradas en el mismo sitio que no eran 39 llamadas reales).
4. Repetir hasta la última etapa de interés.

**Trampa de los registros banked.** Los alias genéricos `sp`/`lr` de OpenOCD para este núcleo **no** resuelven al registro bancado del modo actual; dan `0x00000000` aunque la CPU esté en un estado perfectamente normal. Hay que pedir el registro bancado explícito del modo vigente (`sp_svc`, `lr_svc` en modo Supervisor, que es el que usa Loader3/el kernel del actualizador). Esta sesión lo confirmó dos veces: una lectura con los alias genéricos sugería un `mov pc, lr` hacia `NULL` (aparentando un fallo grave); repetida con `sp_svc`/`lr_svc` mostró una pila y un retorno perfectamente sanos.

**Riesgo de reinicio al parar demasiado tiempo.** Se descartó que hubiera un vigilante por tiempo de parada: en R47 §14 el enlace de depuración se perdía siempre en el mismo tramo del código (tras `Init Pwr2nd`/`OFF HotIC`) incluso variando la densidad de paradas, y en R47 §15 se confirmó sin depurador en absoluto que ese "reinicio" es en realidad un **doble arranque** normal de la cámara (véase §4).

## 4. Doble arranque: lectura corregida (R47 §15 corregido por R48 §7)

La primera lectura (R47 §15, intentos 4–5) sugería que **todo encendido** arranca dos veces: un arranque 1 que se apaga solo (`XPWR_OFF`, ~0,85 s) y un arranque 2, el real, que termina en el LED de error. Esta sesión, con la batería recién cargada, corrigió esa lectura ([R48 §7](e26-r48-plan-recuperacion-actualizador-swd.md)):

| Momento | Qué ocurre realmente |
|---|---|
| **Meter la batería** (interruptor en OFF) | Arranca Loader2 y Loader3 brevemente (~0,87 s) y se apaga sola (`XPWR_OFF`, rama de los BootMode 7/8/9/13/14). **Esto es lo que antes se interpretaba como "arranque 1 de cada encendido"** |
| **Encender con el interruptor** | **Un solo arranque continuo**, sin corte, desde el BootROM hasta el bucle de LED (BootMode 11), en unos 2,7 s |

Es decir: el "doble arranque" no es un paso de cada encendido, es la secuencia batería-luego-interruptor. El guion de P1 original (R48) asumía el patrón viejo (esperar un corte a los 5 s tras el primer arranque) y por eso su primer intento no vio nunca el corte y se detuvo solo sin tocar nada.

## 5. Causa confirmada en la cámara (R47 §9–§15, resumen)

Cadena de puntos de parada sobre el arranque 2 real: entrada de Loader3 → entrada de P2 (`0xc01f2f24`, `CFG_E:Load file`) → retorno de P2 (`0xc01f30ac`) → entrada de la rutina del LED (`0xc01f3b74`).

| Parada | Lo medido |
|---|---|
| Entrada de P2 | `r0 = 0xc005c000`: entrada 0 de la tabla CFG — partición **3**, destino `0x83501000`–`0x83540fff`, ruta `\sabin\idt_cam.b…` |
| Retorno de P2 | **`r0 = 0xfffffed2` (−302)** |
| LED | **`r0 = 0xfffffed2`**, `lr = 0xc01f1269` (rama normal de arranque) |

P2 no llega a intentar ningún otro fichero de la tabla: el primer fallo (cargar `\sabin\idt_cam.bin` de `nflasha3`) corta la carga. Esto confirma con medición física el diagnóstico estático de R36.

## 6. Por qué no se podía escribir la NAND directamente (R48 §2.1)

`muminblk_request` (`c01fd5a4`) en Loader3: si la petición es una **lectura**, llama a `muminblk_transfer`; si es una **escritura**, salta a `c01fd66a` con éxito **sin transferir nada** (la cadena de depuración interna dice `"write"` en vez de `"read"`). Loader3 trae en RAM las funciones de escritura del núcleo de MuMin, pero no las usa para bloques: su capa los ignora. Por eso las opciones A/B de R46 F8 (crear `\updater\mode` a mano o reescribir `nflasha3` completa desde el BIONZ) quedaron descartadas: no hay manera de escribir un bloque sin invocar a mano las funciones internas de gestión de MuMin, con riesgo de dañar la traducción de toda la NAND.

## 7. La vía que funcionó: forzar el modo del actualizador por SWD (R48, vía C)

En `c01f15c0`, Loader3 comprueba si existe `\updater\mode` (`cmp r0, #0` tras llamar a `c01f44c6`); si `r0 ≥ 0` elige BootMode 3 (actualizador de `nflasha1`, intacto) en vez del BootMode 11 normal. Forzar `r0 = 0` en esa parada equivale, para Loader3, a que el fichero exista — **sin escribir nada en memoria ni en NAND**, solo el registro de la CPU durante esa única parada. El actualizador de fábrica (`UdtrMain.sh`, extraído del volcado del 20-10) no necesita ese fichero: si no encuentra ningún `modeN`, entra por defecto en `MODE_USER` y espera firmware por USB.

### 7.1 Corrección del script para el arranque único

El script `analysis/e26-recovery/r48_updater_swd.cfg` (de R48) asumía el patrón de doble arranque con corte a los 5 s. Se corrigió para el arranque único real (§4): se quitó la espera del corte y el segundo `linkup`; ahora hace `fasthalt` en cuanto el enlace SWD responde (el único arranque relevante, el del interruptor) y entra directo a la cadena de puntos de parada desde la entrada de Loader3.

### 7.2 Ejecución de P1 (con autorización expresa del usuario)

Secuencia física seguida: batería fuera → insertada con el interruptor en OFF → esperar su asentamiento (el arranque corto de la batería, §4, no interfiere porque el script aún no ha empezado) → lanzar el script (que confirma "cámara apagada, esperando arranque") → encender con el interruptor.

Resultado medido (log íntegro):

```
esperando apagado
camara apagada, esperando arranque (interruptor, un solo arranque segun R48 §7)
arranque parado pc=0xffff142a
BP_HIT k=0 t=97   pc=0xc01f0000 r0=0x00000000 lr=0xc00303db                 (entrada Loader3)
BP_HIT k=1 t=443  pc=0xc01f15c0 r0=0xfffffed2 lr=0xc01f3f51  -> r0 forzado a 0  (chk updater)
BP_HIT k=2 t=523  pc=0xc01f1e16 r0=0x00000001 lr=0xc01f3f51                 (BootMode 3 elegido)
BP_HIT k=3 t=609  pc=0xc01f15c0 r0=0xfffffed2 lr=0xc01f3f51  -> r0 forzado a 0  (segunda llamada a chk updater)
BP_HIT k=4 t=693  pc=0xc01f1378 r0=0xc01ebff0 lr=0xc01f1339                 (entrada al actualizador)
FIN: actualizador en marcha; sonda en reposo
```

`chk updater` se llama dos veces en el camino hasta el actualizador (coincide con R48 §2.2: 8 sitios de llamada en total); ambas veces se forzó `r0 = 0` y se verificó releyéndolo. Todo el tramo, desde la entrada de Loader3 hasta la entrada del actualizador, duró **696 ms**.

## 8. Primer intento de instalación: 45 % y `0x1063`

Confirmado por USB (`lsusb`: `054c:03e2`, "Sony USB Device"; `pmca`: "camera in updater mode"). Se lanzó `pmca-console firmware -f recuperacion-326/firmware_packed.dat` (hash `c730f8e2…`, coincide con el manifiesto de R48 §2.5).

**Resultado:** avanzó hasta ~45 % de 213 MB y se cortó con `Exception('Response error: 0x1063')`; `pmca` salió con código 1 sin llegar a `CMD_COMPLETE`.

**Qué es `0x1063`.** No es una composición de `pmca`: es el `responseId` que la cámara devolvió tal cual en la cabecera del protocolo del actualizador (`pmca/usb/sony.py`, `_sendCommand`). El byte bajo, `0x63`, **ya estaba documentado** en el repositorio como el código de LED que ponen `us_darwin_firm.sh`/`ud_darwin_firmup.elf` cuando **Darwin (el MCU de alimentación, IC5700) no responde por SIO y no llega al estado 5** — «NG» ([e24-01](e24-01-arranque-recuperacion.md), [e24-02](e24-02-protocolo-actualizacion-darwin.md), [e24-03 F7](e24-03-auditoria-recuperacion-usb.md), [e24-04 M16/escenario D](e24-04-dictamen-seguridad.md), [darwin-via-actualizacion-2026-10-26](darwin-via-actualizacion-2026-10-26.md)). `e24-04` marca justo este escenario como el más peligroso de toda su matriz: "la cámara parece viva y es irrecuperable por software", y deja sin demostrar si ese fallo de Darwin también corta la escritura de las particiones principales ya en curso (M16).

**Diagnóstico tras el fallo (solo lectura, sin tocar nada más):**
- El canal del protocolo del actualizador quedó **latched**: devolvía `0x1063` a *cualquier* comando, incluidos `CMD_GET_STATE` y `CMD_INIT` (que no escriben nada). El USB seguía enumerado (`054c:03e2`), así que el proceso seguía vivo.
- Por SWD, `halt` + lectura de registros **bancados correctos** (`sp_svc`, `lr_svc`; véase la trampa del §3) mostró un `pc` en un retorno de función normal, con pila y `lr_svc` coherentes — el kernel Linux del actualizador **no estaba colgado ni en una excepción**. El bloqueo era del demonio de espacio de usuario (una bandera de error fija tras el NG de Darwin), no del sistema.
- `getFirmwareVersion()` seguía reportando `old=3.25`: nada se había confirmado, porque `CompleteUpdate` (lo único que actualiza esa versión, [R38](e26-r38-guard-y-entrada-updater.md)) nunca llegó a ejecutarse.

**Apagado y reinicio.** El interruptor tardó varios segundos en surtir efecto (Darwin estaba ocupado tras el NG), pero sí apagó la cámara: el log del kernel del PC registró la desconexión USB, un breve "USB Charger" (`idProduct 0994`, cámara apagada cargando) y, al volver a encender, una reconexión **automática** en modo actualizador (`idProduct 03e2`) — sin repetir la inyección por SWD, porque `\updater\mode` ya había quedado creado por el intento anterior (confirma el mecanismo de reintento previsto en R48 §2.4).

## 9. Segundo intento: instalación completa

Con el actualizador fresco confirmado por lectura (`CMD_GET_STATE`/`init()` ya sin error), se repitió `pmca-console firmware -f` con el mismo paquete:

```
Initializing firmware update
Updating from version 3.25 to version 3.26
Writing firmware
5% 10% 15% ... 95% 100%
Done
```

Esta vez `CMD_COMPLETE` se alcanzó sin error. No se investigó la causa puntual del NG de Darwin del primer intento (podría ser un fallo aislado o interferencia de la sonda SWD en las líneas de Darwin); queda sin cerrar, pero el reintento fue limpio.

## 10. Verificación final (P4)

Apagado con el interruptor, batería fuera 10 s, encendido normal sin OpenOCD:

```
Bus 003 Device 0xx: ID 054c:07c4 Sony Corp. ILCE-6000 (aka Alpha-6000) in Mass Storage mode
```

```
Model:              ILCE-6000
Firmware version:   3.26
Lens:               Model 0x12a08019 (Firmware 2.00)
```

**Sin patrón de LED de error. Cámara recuperada.**

## 11. Lecciones prácticas de la sesión SWD (para repetirlo o auditarlo)

- Lanzar OpenOCD con `nohup ... & disown`, nunca con un `&` simple dentro de un comando que el propio shell de la herramienta vaya a cerrar: el proceso en segundo plano puede morir con el shell padre.
- Nunca dos procesos de OpenOCD a la vez contra la misma sonda: compiten por el USB y dan errores de I/O. Matar el anterior antes de lanzar uno nuevo.
- `kill -9` a OpenOCD a mitad de una transacción de depuración puede dejar `DSCR` con `DTR_RX_FULL`; un `resume` posterior puede saltar al vector de abort. Preferir parar el script dejándolo terminar solo o con `SIGTERM`; si hace falta `-9`, dar por hecho que puede requerir un ciclo de energía de la cámara para limpiar el estado.
- Comillas en los heredocs que generan los `.cfg` de Tcl: sin ellas, el shell expande variables como `$j` antes de que las vea Tcl, y el script revienta.
- Antes de fiarse de un registro que parezca indicar un fallo grave (`lr`/`sp` en `0x0`), comprobar que no es el alias genérico equivocado: pedir el bancado del modo actual.

## 12. Qué queda abierto

- Por qué falló Darwin la primera vez (`0x63`): sin explicación; no se investigó más porque el reintento tuvo éxito.
- Si el NG de Darwin interrumpe o no la escritura de las particiones principales en curso (E24-04 M16): sigue sin demostrarse en general; en este caso concreto no hizo falta saberlo, porque `CompleteUpdate` nunca corrió y el reintento fue completo.
- Retirar la sonda SWD de la placa y, si procede, recomponer la cámara.
