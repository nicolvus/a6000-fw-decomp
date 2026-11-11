# E26-R86 — CFW 3.76: Silent calibrado en la imagen y tabla EFCS de la segunda tanda (11-11-2026)

Continúa [R85](e26-r85-calibracion-fotos-3749-3779.md). Etiquetas: **VERIFICADO** (bytes/emulación) · **MEDIDO** · **NO PROBADO EN CÁMARA**.
Pedido del usuario: tabla EFCS solo con la segunda tanda (DSC03786–03806), nivelar los tres modos y construir el CFW nuevo con los últimos cambios de PP.

## 1. Los tres modos
| Modo | Corrección | Dónde | Estado |
|---|---|---|---|
| Mecánico (EFCS off) | Ninguna: es la referencia | — | — |
| EFCS on | Tabla R86 (`analysis/e26-r85/tabla-r86.json`) en NVRAM `0x1850000+0x48` (Darwin v3) | NVRAM (el CFW no la escribe) | Lista, sin escribir |
| Silent (electrónico) | ShutMode 0 + `r5` desde el Tv, solo en foto y con Silent activado | `av-cam` del CFW 3.76 (`scripts/g22/patch_silent_r5.py`) | Construido, emulado, sin instalar |

## 2. Tabla EFCS R86 (solo DSC03786–03806)
Puntos (x = B − A, pérdida): (−1157, 1008), (−913, 814), (−425, 964), (525, 978) µs; 1/60 y 1/125 sin efecto de `c` (cola a 0 desde x = 4570, R85 §7).
Tabla `[(1304, 1008), (1465, 943), (1752, 868), (2205, 939), (2240, 1008), (2349, 899), (2457, 1116), (2609, 1008), (3504, 964), (4411, 797), (5863, 541), (7008, 350), (12000, 4)]`
(13 de 14 entradas). Predicción: E/T = 0,985–1,015 de 1/4000 a 1/30. Tramo 1/350–1/160 interpolado (no hay 1/250 en la tanda).
Límite (R85 §7): el degradado vertical sigue; EFCS uniforme solo hasta 1/500.

## 3. Silent en la imagen (VERIFICADO offline)
* Enganche `0x438c82fe` (`bl 0x436d6118` → `bl 0x43fb7e00`), el mismo sitio que C3-B de E25-26, paso 0 de la secuencia de foto, justo antes de `SetExposure` (`r1 = cap+0x64c`).
* Cueva de 100 B en `0x43FB7E00` (hueco de G18, tras el código de `pp_tone` y antes de su búfer `W` `0x43FB7EC0`; estaba a cero). Fuera del bloque TPZL 0 (R55).
* Lógica: llama a `0x436d6118` y conserva su r0; si `cap+0x41d == 1` (Silent, de `patch_tristate`) lee Tv = `ajustes+0x162` (`0x4383fbc4([cap+0x1e0],[cap+0x1d8])`, mismo par que `0x4383fd6c` con r6 = cap+0x20, comprobado en `0x437f8a64`); para `0x1400 ≤ Tv ≤ 0x1e00` (1/16…1/16000) `q8 = 0x4382fa94(Tv)`, `r5 = 4329 − q8·K>>32` (K = 2^32/(15,48·256)), acotado a ≤ 4218; si `r5 < 10` no toca nada; escribe `cap+0x64c = r5` (u16) y `cap+0x655 = 0`.
* Constantes: R56 se ajustó con T nominal de la app (1/60 = 16 667 µs); aquí T es el real del Tv (1/60 = 15 625 µs), así que se reajustó a los mismos valores medidos: 1/60 → 3320 y 1/250 → 4077 exactos (15,48 µs/línea, 110 líneas de retardo); 1/15 → 292 (R56: 331, +1 %).
* Emulación (Unicorn sobre el `av-cam` del CFW, `tests/test_e26_r86_silent_r5.py`): 1/60 → 3320, 1/250 → 4077, 1/500 → 4203, ≥ 1/1000 → 4218 (1 línea), 1/8 y Silent off → sin cambios (`r5 = 1`, ShutMode 3).
* **Limitaciones:** (1) por encima de ~1/600 el modelo R56 da ≤ 0 líneas (exposición mínima ≈ 1,7 ms equivalente): el Silent rápido puede seguir claro; sin medir. (2) Tv tomado de `ajustes+0x162`: si en algún modo la foto usara otro Tv, el `r5` saldría de esa velocidad (fallo seguro solo fuera de rango). (3) Que el hueco de G18 no se pise en ejecución se apoya en G29/G31 (PP funcionando desde 3.65/3.71), no en una prueba de esta cueva.

## 4. CFW 3.76
`scripts/gui/build_cfw_completo.py analysis/gui/g22/pkg-376w --version 3.76` (`build_base_pp` aplica ahora `patch_silent_r5`; `--sin-silent-r5` lo omite).
* `.dat`: `analysis/gui/g22/pkg-376w/pkg-3.76/package-3.76/firmware_packed.dat`, sha256 `f90356cd725a431f53985b1c9e9ed6642216841d9af083e6caea50b3a95a2a41` (no versionado).
* Frente al 3.75: `/usr` idéntico (los cambios de PP más recientes, G34/G35 hasta PP10 y valores de fábrica, ya estaban en el 3.75); `av-cam` difiere en 101 B (enganche + cueva), igual a `apply_bytes(av-cam 3.75)`.
* Auditoría independiente (`audit_package_nflasha15.py --darwin-v3`, `analysis/gui/g22/audit-3.76.json`): contenedor, sumas del tar, `nflasha15` (bloque 0 idéntico, LDEC), ext2 y Darwin v3 correctos; fallan solo «miembros previstos» porque el auditor no conoce `nflasha3` ni la retirada de `nflasha5`: **el mismo resultado que el 3.74 instalado y que arranca**.
* Desde el 3.74 instalado, el 3.76 añade también lo de G34/G35 (emulado, nunca instalado).

## 5. Instalación y prueba (requiere autorización y la cámara)
1. `pmca-console firmware -f analysis/gui/g22/pkg-376w/pkg-3.76/package-3.76/firmware_packed.dat` (como el 3.73).
2. Tabla EFCS: `PYTHONPATH=references/pmca .venv/bin/python scripts/senser_efcs_table_write.py --tabla analysis/e26-r85/tabla-r86.json --execute`.
3. Tripletas ARW (Silent / EFCS on / EFCS off) a 1/4000, 1/1000, 1/500, 1/250, 1/125, 1/60, **sin** app ni parche RAM: Silent/off y on/off ≈ 1.
Reversión: reinstalar 3.74/3.75 (`.dat` en `pkg-374w`/`pkg-375w`) y `--zero` para la tabla.

## 6. Instalación (11-11-2026, MEDIDO; autorizada por el usuario: «instálalo»)
* `pmca-console firmware --flash --confirm …/package-3.76/firmware_packed.dat` (la versión actual de `pmca-console` ya no admite `-f`): primer intento «unexpected response (device returned more data than requested)» al pasar a modo actualizador (`054c:03e2`); segundo, con la cámara ya en ese modo, `Done`. Arranca normal (`054c:07c4`) y `pmca-console info` da **firmware 3.76**. Registros `analysis/gui/g22/install-3.76*.log`.
* Tabla EFCS: la NVRAM tenía la de prueba (`e167d007…` = {30000, 2000}). `senser_efcs_table_write.py --tabla tabla-r86.json --execute` (dos expiraciones al entrar en service mode, como en R84): «verificación en memoria: OK», «sincronizado a flash»; la cámara se apagó sola al terminar. Registro `analysis/e26-r85/escritura-tabla-r86.log`.
* Falta: relectura de la tabla tras encender y las tripletas de comprobación (§5.3).
