# G33 — Picture Profile: Black Level, Black Gamma, Knee, Detail y Gamma Still aplicados en el núcleo (11-11-2026)

Continúa [G32](g32-auditoria-picture-profile-3-73.md). **Offline**: construido y probado con Unicorn sobre `av-cam.bin`; **nada probado en cámara ni instalado**. Código: `scripts/gui/pp_tone.c` (C → Thumb-2 con clang, versionado como `pp_tone.bin`/`pp_tone.syms`), `scripts/gui/pp_tone_patch.py` (cueva, tramplines y gancho), `tests/test_g33_pp_tone.py` (14 pruebas). Entra en la imagen del núcleo con `build_base_pp` (CFW 3.74).

## 1. Qué se descubrió

- **Curva de gamma**: los constructores de la LUT de 96 puntos (`0x43853214`, `0x438538e4`, `0x43853c70`) muestrean los 2048 puntos de la curva (`TAB[gamma·2 + modo]`) y luego aplican las tablas 1D de Creative Style. Cualquier cambio sobre esos 2048 puntos llega al hardware sin tocar nada más. Los demás sitios que cargan `TAB` (`0x43852f9c`, `0x4385408c`, `0x4385498e`, `0x43854eb6`, `0x4385503c`) solo leen los 26 B de parámetros del final (`0x43854d14` no se revisó entero).
- **APC (detalle/apertura)**: el núcleo calcula las ganancias (`apgain`, `vapgain`, `hapgain`; `FUN_438b3570`), el coring (`FUN_438b2ac4`), el LPF, la máscara, el «yld» y «zoukou» en funciones propias, con tablas por ISO y por nivel de nitidez de Creative Style, y deja el resultado en la pila (`sp+0xe0`, `sp+0xc8`) justo antes de escribirlo al hardware (`FUN_43b68c88`/`…d18`). Hay además una rama nativa por una bandera global (`0x43f9a1c2`: `[0]` activa; tablas de nivel `[1…0xf]`, V/H `[0x20…0x29]`, Hi-Light `[0x1b…0x1f]`) y campos `ctx+0x139…0x13f` que se parecen a los siete bytes de Detail del PP, pero **nadie en el binario las rellena** y no se pudo establecer su origen offline; por eso el parche actúa sobre las salidas, no sobre esa rama.
- El `cfg` del PP (`0x4066`) no tiene más consumidores que los ya listados en G32; los bytes `0x17…0x26` del mensaje se copian ahora a un snapshot propio en el desempaquetador (`0x43802b64`).

## 2. Qué hace cada ajuste ahora

| Ajuste | Implementación (todo sobre la salida, por lo que no cambia nada con PP apagado) | Estado |
|---|---|---|
| **Gamma Movie** | sin cambios: Movie = la curva de vídeo `0x0a` que ya usa el A6000 (idéntica a la de la A7S/A6300); en foto la curva no existe (puntero nulo, como en la A7S) | igual que A7S |
| **Gamma Still** (vídeo) | usa los puntos de la curva de **fotografía** (gamma 0: `y(25 %)` = 485 frente a 621 de Movie), conservando los 26 B de parámetros de vídeo | **desviación consciente**: en la A7S/A6300 la curva de vídeo de `(0,0)` es casi igual a Movie, y `(0,0)` reinició la A6000 (10-11-2026) |
| **Black Level** (−15…+15) | `y += nivel·4·(blanco − y)/blanco`: levanta/baja el negro y se desvanece hasta el blanco de la propia curva (no cambia el blanco) | todas las gammas |
| **Black Gamma Range / Level** (Wide/Middle/Narrow; −7…+7) | campana `4t(1−t)` sobre el 30 / 20 / 10 % inferior, amplitud 5·nivel códigos (+ aclara, − oscurece) | no en S-Log2/S-Log3/ITU709(800 %) |
| **Knee** Manual (Point 0…12 → 75…105 %; Slope −5…+5) | por encima del punto: pendiente `0,5 − 0,07·slope` (0,15…0,85); sin efecto si el punto ≥ 100 % | solo ITU709, Movie, Still |
| **Knee** Auto (Max Point 0…4 → 90…100 %; Sensibilidad High/Mid/Low) | pendiente fija suave 0,78 / 0,88 / 0,96 desde el punto máximo; sin efecto en 100 % | ídem. **El valor por defecto de Max Point en la `libObj` de la A6000 no está verificado**: si no fuera 100 % la rodilla automática se notaría un poco |
| **Detail Mode** | Auto (0) deja el cálculo nativo; Manual (1) aplica los cuatro siguientes | |
| **Detail Level** (−7…+7) | multiplica `apgain` por 0,18…1,82 | |
| **V/H Balance** (−2…+2) | `vapgain` ×(1 ± 0,15·n) y `hapgain` inverso (tope 0x10) | |
| **Limit** (0…7) | tope de `apgain` = 0x1FF·(limit+4)/11 (7 = sin tope) | |
| **Crispening** (0…7) | multiplica los umbrales de coring vertical y horizontal por 1…2,1 | |
| **B/W Balance, Hi-Light Detail** | **sin implementar**: dependen de los bloques «yld»/«zoukou» (detalle según nivel de luminancia), cuyos parámetros no se han podido mapear con seguridad | siguen sin efecto |

Constantes (amplitudes, anchos de rango, pendientes) son **estimaciones razonables, no valores de Sony**: ajustables en `pp_tone.c` sin tocar nada más (`pp_tone_patch.py` recompila).

## 3. Mecanismo y espacio

- Cueva `0x43FB7500…0x43FB8EE0` (la que ya ocupaba `pp_color_patch` en sus primeros `0x100` B): snapshot `pp` (16 B) y caché (24 B), gancho del desempaquetador (`b.w` en `0x43802b64`, repite `ldrb.w r2,[r0,#0x35]`), cinco tramplines (`bl`) con el código original del sitio, `pp_curve`/`pp_gain`/`pp_coring` (966 B) y la copia de trabajo `W` de la curva (`0x43FB7EC0`, 0x1020 B). Sin libgcc, sin NEON (`-mfpu=none`; la primera compilación usó `vld1` y Unicorn la rechazó).
- Sitios: curva `0x43853226`, `0x4385392E`, `0x43853C8E`; Detail `0x438B3D52` (ganancias) y `0x438B336E` (coring). `lr` no está vivo en ninguno (comprobado). Las instrucciones originales se verifican byte a byte al construir.
- `pp_curve` devuelve el puntero original si PP está apagado o no hay nada que aplicar (valores neutros); si hay que modificar, recalcula `W` (≈ 2 048 iteraciones) y la reutiliza mientras no cambie el snapshot (el núcleo ya vuelve a construir la LUT cuando cambian `cfg+0x150…0x15f`, que compara en `0x43800fcc`).
- Riesgos: (1) `W` es única: si dos constructores corrieran a la vez con curvas distintas saldría una mezcla; (2) estimaciones de §2; (3) no se ha comprobado en cámara que los constructores citados sean los que alimentan el vídeo en grabación (`0x43854d14` no se revisó entero); (4) la cueva vive en el hueco de G18, que ya sobrevive 3.71–3.73 en cámara.

## 4. Construcción

`scripts/gui/build_cfw_completo.py analysis/gui/g22/pkg-374w --version 3.74` (no versionado): `.dat` sha256 `a7bea1422640008030a1a30f38dc447fdd53076172259f8605bd29c5749294d5`, `nflasha3` con `AV-CAM.BIN` de 33 418 B cambiados respecto del 3.38+Silent (curvas, color y G33). Comprobado en Unicorn sobre el `AV-CAM.BIN` extraído del paquete: Black Level +15 sube `y[0]` de 5 a 64 y conserva el blanco; con PP apagado devuelve el puntero original. **No instalado.** No se pasó la auditoría independiente del `.dat` (`audit_package_nflasha15.py`).

## 5. Pendiente (PENDIENTES G33-A…)

1. **G33-A** Instalar el CFW 3.74 (autorización) y medir: Black Level ± en una carta de grises, Black Gamma, Knee manual con una luz fuerte, Still frente a Movie, Detail Level/V-H/Limit/Crispening sobre una carta de nitidez.
2. **G33-B** B/W Balance y Hi-Light Detail (bloques yld/zoukou).
3. **G33-C** S-Log3 (G32-C) sigue sin causa demostrada.
