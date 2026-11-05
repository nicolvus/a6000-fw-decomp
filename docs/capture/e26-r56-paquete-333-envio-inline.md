# E26-R56 — 3.33: el modo Electronic solo con un parche en línea en el envío (sin cuevas, bloque 0 intacto)

Fecha: 04-11-2026. Continúa [R55](e26-r55-paquete-331-bloque0-lz.md) y [R54](e26-r54-paquete-330-envio-pkt0e.md). Offline; sin instalar.

Etiquetas: **MEDIDO** · **INFERENCIA** · **NO VERIFICADO**.

## 1. Por qué

R55 §5: con el contenido oficial (3.32) el sector 12 de `dnflasha3` se lee y adb no cuelga; con cualquiera de nuestros paquetes (3.27–3.31) se cuelga. Lo que cambia en el bloque TPZL 0 son las cuevas de `0x43541800…` (selector, envío y C3-B). No se halló una zona libre segura fuera del bloque 0 (MEDIDO): dentro del código no hay huecos ≥ 96 B; las zonas de ceros candidatas siguen a cero en la cámara en marcha, pero todas tienen referencias (la de `0x43b873a7` es el final de una tabla de 3 KB que lee `0x4382f6xx`; las de `0x43be…`/`0x43c1…` tienen accesos relativos al PC; la de `0x43faf28c` tiene un puntero absoluto; la de 2,4 MB se usa).

## 2. Cambio (`scripts/e26_r56/patch_send_inline.py`, `build.py --inline`)

En `0x438d0064` el tramo `0x438d01ae–0x438d01c1` solo calcula el valor de Sony de `pkt[0x0e]` (`[obj+0x4b68] − [obj+0x1d8]` o `0xff`), que consume el `strb.w r3,[r2,#0x4e]` de `0x438d01fa`. Se sustituye en el sitio por `ldr r3,[pc,#8]; ldr r3,[r3]; b 0x438d01c2`, con el literal `0x43edf894` en los bytes muertos tras el salto. El objeto del envío (`0x43ecfe24` en RAM) **no** tiene el EFCS en `+0x41c` ni un puntero al bloque de ajustes (MEDIDO por SWD), de ahí el literal absoluto.

Se quitan el selector de `0x43841070` (lo pisaba el envío) y C3-B (sin efecto de exposición comprobado; la exposición correcta se obtuvo con el parche de RAM de E25-11, R54 §5). Darwin sin cambios (compuerta `0x4318`).

## 3. Resultado (MEDIDO, offline)

* Bloques TPZL cambiados: **solo el 57**; el bloque 0 es idéntico al de Sony.
* Emulación desde `0x438d01ae` hasta el `strb`: Sony original → `0xff`; 3.33 → `pkt[0x0e]` = ajuste (0/1).
* `verify-333.json` 35/35 (nuevas: `bloque_0_identico_a_sony`, `envio_inline_presente`); tests del constructor y de R56 (26) pasan.
* Paquete `analysis/e25-27/artifacts-333/package-3.33/firmware_packed.dat` (`d4a2e880…`, no versionado).

**NO VERIFICADO:** que con el bloque 0 intacto adb no cuelgue; que el obturador electrónico funcione igual que en el 3.30 (mismo `pkt[0x0e]` en el envío); exposición (sin C3-B: usar el parche de RAM de E25-11).

## 4. En cámara (04-11-2026, MEDIDO)

Instalado 3.32 → 3.33 (`Done`; reporta 3.33). Parche en RAM en `0x838d01ae` = `024b 1b68 06e0 00bf 00bf 94f8ed43 00bf…` (telnet). `dd if=/dev/dnflasha3 skip=12 count=1` → `1+0 records` al instante. **adb activado sin cuelgue**; conexión por Wi-Fi (`adb_shell`, puerto 5555): `ScalarA`, `uid=2000(shell)`. Cierra `E26-R51-ADB-HANG`: la causa era el bloque TPZL 0 modificado (R55 §5). Falta la foto electrónica.

## 5. 3.33 en cámara: la cortina suena (usuario) → 3.34

Con el 3.33 la cortina sigue sonando. Causa (MEDIDO en código): el paquete de la foto (`pkt[8]=0xa0`) lo arma `0x43841070`, que escribe `pkt[0x0e]=0` en `0x43841476` (`strb r3,[r4,#0xe]`, `r3 = 0xa0 − 0xa0`); `0x438d0064` (parcheado en el 3.33) arma los envíos posteriores. En el 3.30 lo cubría la cueva del selector.

3.34 añade, también en línea y sin cuevas, la reescritura de `0x43841472–0x4384148b` (salvo el `ldr.w r3,[pc,#0x494]` de `0x4384147c`, que no se mueve): `ldr.w r3,[sb,#0x41c]; strb r3,[r4,#0xe]; lsls/lsrs` para `(r0&3)<<3` y `(r1&1)<<5`, `r2<<6`, sumas y `strb r1,[r4,#0xd]`. Emulación contra el original con cinco juegos de entradas: `pkt[0x0d]` idéntico y `pkt[0x0e]` = `cap+0x41c` (0/1). Flags y `r0/r1` se recalculan antes de usarse (`cmp` en `0x43841492`; `r0/r1` se recargan). Bloques cambiados: 48 y 57; bloque 0 idéntico a Sony; `verify-334.json` 36/36; paquete `artifacts-334/package-3.34` (`95e7b94f…`, no versionado).

## 6. 3.34 en cámara: la cortina sigue sonando → 3.35

Instalado 3.33 → 3.34 (`Done`; reporta 3.34). La cortina suena (usuario). SWD: los dos parches en línea están cargados (`0x838d01ac…`, `0x83841470…`); ajuste EFCS = 1 y `cap+0x41c` = 1. Diferencia con el 3.30 (que funcionaba): su cueva cubría el `strb` final de `0x438d0064`, es decir, **las dos ramas**; el 3.33/3.34 solo la rama `r6 ≠ 0`. En la rama `r6 = 0` (estado sin tipo en la tabla de `0x438d0084`; el estado del objeto leído es 0) Sony hace `r3 = r6 = 0` (INFERENCIA: es la rama del envío en la foto). 3.35: el mismo tramo de 20 B atiende las dos ramas (`0x438d01aa`: `mov r3,r6; b …` → `b 0x438d01b4`), con literal común en `0x438d01bc`. Emulación: las dos ramas dan `pkt[0x0e]` = ajuste (0/1); tests R56 9/9; `verify-335.json` 36/36; bloques 48 y 57; bloque 0 idéntico a Sony.

## 7. Calibración del parche de exposición con 3.35 (04-11-2026, MEDIDO)

Con 3.35 instalado, escena fija, RAW sin negro (media). Mecánico forzando a 0, cada 20 ms durante el disparo, el espejo EFCS `0x83EDF894` y la copia de trabajo `0x83ED4FC8` (el firmware reescribe el espejo tras cada disparo). Electrónico = EFCS desactivado + parche RAM (ShutMode 0 + `r5`).

| Velocidad / ISO | Media mecánica | Electrónica | `r5` |
|---|---|---|---|
| 1/60 / 400 | 123,05 | 122,45 | 3320 |
| 1/250 / 1600 | 87,59 | 87,77 | 4077 |
| 1/15 / 100 (predicción) | 127,75 | 130,75 | 332 |

Modelo: filas `N = 4219 − r5 = T/16,73 µs − 97`. Franjas a 1/60: H 0,97–1,03, V 0,99–1,01. Sin parche, el electrónico sale ≈ 3,3× más brillante que el mecánico a 1/60 (404 frente a 123). RemoteShutter v8c: `LINE_US` 16,73, `R5_LAG` 97 y parche solo con EFCS desactivado; prueba desde la app con `/silent?v=1`: mecánico 120,64 (sin parche), electrónico 126,73 (`r5` 3320, +5 %). NO VERIFICADO: velocidades > 1/300 (< 100 filas) y otras escenas/ISO.

## 8. Mecánico ≥ 1/1000 sale negro con el 3.35 (04-11-2026, MEDIDO)

Serie de 18 velocidades (menú EFCS activado, app v8c, RAW+JPEG): mecánico 1/1000, 1/2000 y 1/4000 con ISO 12800 → media RAW ≈ −5 (negro); 1/400 con el mismo ISO → 850. El usuario lo confirma también a ISO 25600. El electrónico no lo presenta.

* **Hipótesis `pkt[0x0e]` refutada (RAM, sin flashear):** con el código de Sony restaurado en RAM en el envío (`0x438d01aa/01ae`) y en el paquete de la foto (`0x43841472…`), el mecánico a 1/2000 (EXIF 1/2500, ISO 12800) sigue negro (`DSC03459`: −5,2). Revertido y verificado por lectura.
* **Ventana SWD** (`0x83E9BC48`, 64 palabras, ~45 Hz, solo lectura; sonda CMSIS-DAP): idéntica a 1/2000 (negro) y 1/250 (correcto) salvo contadores; no discrimina.
* **Reinicios de la cámara** durante pruebas con `shoot.py`/telnet+adb a 1/2000: log del kernel (`0x83400000`) → `WDT:RSTREQ_STAT=0x0`, `kernel BUG wdt.c:182` a los 51 s, sin oops previo (petición de reset de otro procesador). Con disparos solo por HTTP (sin dd/adb alrededor) no reinició. Causa NO VERIFICADA.
* El EXIF no coincide con la velocidad pedida en varias fotos (1/2000→1/2500, 1/250→1/200, 1/500→1/400), NO VERIFICADO por qué.
* Siguiente: comprobar si el negro ocurre con el disparador físico (sin app) y, si sí, si ocurre con el 3.32 oficial; candidato restante: el parche de Darwin.
