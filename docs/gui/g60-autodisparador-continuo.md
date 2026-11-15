# G60 — Autodisparador continuo en `libObj`: el bucle existe, pero su espera es el retardo del modo y no hay contador de tomas; gancho de fin de captura localizado (15-11-2026)

Estático sobre `libObj.so` 3.21 (Thumb, VA = offset; Capstone + referencias de literal PC-relativas) y `viewUnified2/4.so`. Sin cámara, sin CFW construido, sin tocar `scripts/gui/harness/`. Resultado: **parcial** (rama 4 del brief). No se escribió parche, ajustes de menú ni prueba Unicorn/arnés: la premisa «N e intervalo son datos que el bucle lee» se cumple solo a medias (§3) y parchear sin contador sería inventar lógica sin verificar.

## 1. Origen de los valores (VERIFICADO en bytes)
- La clase es el `ActionObject` de `ObjCamera` (campos del objeto `r4`): `+0x19c` modo, `+0x1a0` «INTERVAL», `+0x1a4` «REPEAT», `+0x1a8` «WITH_DRIVE_MODE», `+0x1b4` estado (0 libre, 1 cuenta atrás, 2 cancelando), `+0x1b8` tiempo acumulado, `+0x1bc` retardo, `+0x1c0` modo de Drive a restaurar.
- `pvt_ActionSetSelfTimerMode` (`0x6899dc`): lee la `ParamList` del mensaje: `0x149` MODE→`+0x19c`, `0x14a` INTERVAL→`+0x1a0` (por defecto `0x3e8`), `0x20d` REPEAT→`+0x1a4`, `0x26a` WITH_DRIVE_MODE→`+0x1a8` (por defecto 10). Cuatro `Invalid ParamList PARAMID_DATA_SELF_TIMER_*` en `0x689a44/6a/92` y `0x689a22`.
- **Fuente de la ParamList: Backup, lectura nativa.** `pvt_ActionSetSelfTimerModefromBackup` (`0x688684`) lee con `0xdd5f4(id, &out)`: **`0x107010e` → modo**, **`0x10708ff` → INTERVAL**, **`0x1070900` → REPEAT** (literales en `0x688778/7c/80`; error ⇒ modo 2 / 0 / 0). `viewUnified2/4` leen y escriben los mismos tres ids (`viewUnified2` `0x1c66b0` escribe `(modo, intervalo, repetición)`; el arranque la llama con `(4, 0x64, 1)` en `0x13a3e4`; `viewUnified4` `0x89a00` los envía como `0x149/0x14a/0x20d`). `av-cam.bin` no contiene esos ids ni ninguna cadena de autodisparador: **todo el autodisparador es `libObj` + vistas**.
- Defaults (`0x68c62a`): modo 2 («sin autodisparador»), interval 0, repeat 0, drive 10.

## 2. El bucle (VERIFICADO)
1. Retardo por modo (`+0x1bc`), tres copias idénticas: **modo 0 → `0x2710` (10 s), 1 → `0x7d0` (2 s), 4 → `0xbb8` (5 s), resto → 0**. Sitios y bytes: `0x689acc` `42f21073` (`movw r3,#0x2710`), `0x689ada` `4ff4fa63` (`mov.w r3,#0x7d0`), `0x689ae8` `40f6b833` (`movw r3,#0xbb8`); copia en `0x688732/38/3e` (`06e0` `4ff4…`/`03e0` `40f6…`/`00e0 0023`, offsets de rama distintos) y `0x67e178/7e/84`.
2. Arranque (`0x67dbf0`, `TIMER_REQ_CMD`): estado `+0x1b4=1` y primer tick por `0x131f28(obj, [+0x268], 0x5c, [+0x1a0])`.
3. **Tick** (`0x67e234`, `ActionSelfTimer`): `+0x1b8 += +0x1a0` y, mientras `+0x1bc > +0x1b8`, rearma con periodo `+0x1a0`. **El intervalo (`0x10708ff`) es el periodo del tick de la cuenta atrás (100 ms de fábrica), no el tiempo entre tomas.**
4. Al cumplirse el retardo (`0x67e2de`): dispara con `0x67b4b0` = mensaje **`0x750a`** a `0x3100` (petición de captura, parámetros `0x9836`). Si `REPEAT == 0` (`0x67e340` `d4f8a431`, `ldr.w r3,[r4,#0x1a4]`) restaura los defaults (fin); si `REPEAT != 0` (`0x67e38a`) pone `+0x1b8 = 0` y sigue en estado 1.
5. **Fin de captura** (`0x66de44`, `SeqSelfTimerCmp`): recibe el evento `0x9502` con resultado `[r7+0x34]`; **`== 0xf000` = toma correcta** (`0x66de94`). Entonces, si `+0x1b4 == 1` (`0x66df10`), `+0x1b8 = 0` y **rearma el tick con `0x131f28(obj, [+0x268], 0x5c, [+0x1a0])` en `0x66df4e`** (bytes `c3f6ebf7`, `bl 0x131f28`). Es decir: tras cada toma el modo vuelve a esperar el retardo (10/2/5 s) y vuelve a disparar mientras `REPEAT != 0`.

## 3. Lo que NO es un parámetro
- **No hay contador de tomas.** `+0x1a4` solo se compara con 0 (`0x66deba`, `0x67db30`, `0x67dea8`, `0x67e340`); ninguna instrucción lo decrementa ni lo compara con un número (barrido de todos los `str/ldr [r4,#0x1a4]` de `0x660000–0x6a0000`). Los «3/5 disparos» no se cuentan en esta clase; el origen de la parada tras N queda **sin localizar** (candidatos: contador de la capa de aplicación `0x8078/79`, o el modo de Drive «WITH_DRIVE_MODE» en `av-cam` por mensaje `0x7520`/`0x9539`, `pvt_SetDriveModeforSelfTimer` `0x683048`).
- **El tiempo entre tomas no es `INTERVAL`** sino el retardo del modo (una de tres constantes de 10/2/5 s) más el tiempo de captura. Parchear `0x10708ff` solo cambiaría la resolución del tick.

## 4. Consecuencia para el parche pedido
- «Intervalo» sustituible: bastaría reemplazar las tres constantes de retardo (en sus tres copias) por una lectura de Backup del ajuste CFW, pero **«N.º disparos» exige código nuevo** (contador + parada en `0x67e340`/`0x66df10`), no solo datos. Con la forma de las tres copias (`movw`/`mov.w` con registros fijos) la sustitución cabe en una cueva (patrón `scripts/g57/focus_bracket_patch.py`), sin verificar en Unicorn aquí.
- Ajustes CFW y arnés (pasos 2 y 4) no se hicieron: sin contador no hay semántica de «N» que probar, y el arnés no arranca el autodisparador continuo sin la ruta de menú de Drive (pendiente).

## 5. Gancho común «tras cada toma» (para `FOCUSSHIFT-HOOK` y `LIVECOMP-F1`)
- **Punto**: `0x66df4e` (`bl 0x131f28`, bytes `c3f6ebf7`), rama de toma correcta del evento `0x9502`, justo antes de rearmar la espera; `r4` = objeto con `+0x1b4 == 1`. Es el único sitio donde se sabe que la captura terminó y aún no ha empezado la siguiente.
- **Enganche de `fb_paso` (g57)**: sustituir el `bl 0x131f28` por `bl cueva`; la cueva llama a `fb_paso`, y solo cuando este devuelva «motor parado y listo» ejecuta el `bl 0x131f28` original (rearme). Limitación: solo cubre disparos que pasen por el autodisparador continuo; la ráfaga y el disparo único no usan este objeto.
- No implementado: sin prueba Unicorn de la cueva.

## 6. Pendientes
`INTERVAL-F1` (contador y parada de N en el autodisparador continuo), `INTERVAL-F2` (ajustes CFW y arnés) y `INTERVAL-F3` (localizar quién corta tras N de fábrica) en [PENDIENTES](../PENDIENTES.md).
