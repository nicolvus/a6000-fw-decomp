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
