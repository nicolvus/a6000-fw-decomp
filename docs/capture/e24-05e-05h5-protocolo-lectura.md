# E24-05e / E24-05h-5 — Protocolo de lectura de solo lectura (preparado, NO ejecutado) (27-10-2026)

Base `9dfa74cb`. 100 % offline: sin cámara, sin USB, sin escritura de RAM, sin modificar Darwin ni BIONZ, sin FDAT. Fuentes: texto de los scripts de cámara del repo, `av-cam.bin` (Capstone) y los informes previos. Script: `scripts/e24_05h5/protocolo.py` → `analysis/e24-05h-5/protocolo.json`; pruebas: `tests/test_e24_05h5_protocolo.py`.

## Veredictos

| | Pregunta | Resp. | Naturaleza |
|---|---|---|---|
| **A** | ¿Los scripts de T022/T023 leen SRAM de Darwin? | **NO** | Leen solo DRAM de BIONZ: ventana física `0x83f91e20..0x83f91f30` (= virtual `av-cam` `0x43f91e20` + `0x40000000`). Ningún script del repo usa un literal `0x20xxxxxx`/`0x4002xxxx` con `/dev/mem`. *Lo que no está demostrado* es que exista otra vía de lectura de Darwin: es evidencia insuficiente, no contradicción (§1) |
| **B** | ¿Se corrigió la documentación que atribuía a T022 acceso a Darwin? | **SÍ** | E24-05h-4 §6 y §8, E24-05h-3 §9, `PENDIENTES` (E24-05h-5, E24-05e, E24-05h-1) (§2) |
| **C** | ¿Productores BIONZ de `pkt[1]` y `pkt[2..3]` localizados? | **SÍ, parcial** | Ambos los escribe `0x43841070` (no `0x438d0064`) en `carga+0x40`. `pkt[1]`: completo salvo la semántica EFCS. `pkt[2..3]`: fórmula y filtro completos; el escritor de `[sl+0x162]` no es único (§3) |
| **D** | ¿Matriz EFCS ON/OFF con ≥ 3 disparos por configuración? | **SÍ** | 6 disparos en orden ABBAAB, misma velocidad y modo (§4) |
| **E** | ¿Separados los datos accesibles por T022 de los que exigen otra vía? | **SÍ** | §5: 5 magnitudes BIONZ (1 medida, 4 con dirección por bytes) frente a 12 de Darwin sin vía |
| **F** | ¿Persistencia de cada valor determinada? | **SÍ, con límite** | §6; la persistencia de `[sl+0x162]` no se sabe |
| **G** | ¿Criterios SÍ/NO definidos sin asumir que una foto normal prueba el funcionamiento sin rearme? | **SÍ** | §7 |

## 1. Qué espacios de memoria leen T022/T023

| Evidencia | Hecho | Estado |
|---|---|---|
| `camera_darwin_buffers.py` (T023; T022 usó la misma técnica) | `dd if=/dev/mem bs=16 skip=BASE/16`, `BASE=0x83f91e20`, `SIZE=0x110`; buffers `0x83f91e2e`, `0x83f91f24`, `0x83f91f1a` y paquete `0x83f91e32` | VERIFICADO (texto del script) |
| Conversión | físico = virtual de `av-cam` + `0x40000000` (comentario del script; coincide con `bz.py`: base `0x43541000`) | VERIFICADO con otras pruebas que usan la misma regla (`0x43e95950` → `0x83e95950`) |
| Alcance de las demás lecturas del repo | `0x83793166`, `0x83e7f4a8`, `0x83e9…`, `0x83edf…`, `0x83f9…`, `0x8401c670`: toda DRAM de BIONZ (`0x80000000–0xc0000000`, el mismo rango que vuelca `updater_full_dump.py`); SFR leído por el actualizador: `0xf0000000` (periféricos de BIONZ) | VERIFICADO (`analysis/e24-05h-5/protocolo.json`) |
| Solape con el mapa de Darwin | la ventana de T022/T023 no solapa `0x2000xxxx` (SRAM del FM3) ni `0x4000xxxx–0x400fxxxx` (periféricos del FM3: `0x40023000`, `0x40031094`, `0x40033008`) | VERIFICADO (aritmética) |
| Darwin como dispositivo del bus | Darwin es un MCU aparte (FM3, IC5700); BIONZ lo ve por CAIF/mss, no por memoria. No existe en el repo una lectura de su SRAM | INFERENCIA por ausencia: **no demostrado** que no haya vía |

Consecuencia: T022/T023 observan lo que **BIONZ envía** a Darwin (buffers de envío) y nada de lo que Darwin tiene en su RAM. `S+0x32 = 0x1600` de E24-05h es un valor *derivado* de `pkt[2..3]` (copia por `0x17f8c`), no una lectura de la SRAM de Darwin.

## 2. Correcciones aplicadas

* **E24-05h-4 §6**: afirmaba «con el método de lectura de T022» para 12 valores, todos de Darwin (`0x2000xxxx`, `0x4002xxxx`, `0x4003xxxx`) salvo el tipo de bobina (deducido). La tabla pasa a indicar la **vía**: ninguno alcanzable por T022. La frase «Solo con 3, 4, 7 y 9 (RAM) ya se distingue…» queda sin vía y se marca así. El §8 y el veredicto G apuntan a este informe.
* **E24-05h-3 §9**: mismo error («con el método de lectura de RAM de T022 … `S+0x146/0x147`, `0x2000381e/f`»); nota de corrección.
* **PENDIENTES**: E24-05h-5 reescrito (solo cierra lo observable por T022; el resto exige vía nueva y queda sin criterio de cierre ejecutable); E24-05e apunta al protocolo; E24-05h-1 queda parcialmente cerrado.
* Sin cambio: E24-05h §6 punto 2 (carga `[obj+0x4ad8]+0x40..0x55`) es BIONZ y sí es accesible; E24-05a §7 (`pkt[+1]`) también.

## 3. Productores BIONZ de `pkt[1]` y `pkt[2..3]` (E24-05h-1, parte estática)

`0x437f87fe–0x437f8816` calcula `r4 = [obj+0xd8]… + 0x40` y llama a `0x43841070` pasándolo como 5.º argumento (`ldr r4,[sp,#0xc8]`, `0x43841088`): **el `pkt` de 22 B es `carga+0x40`**. El constructor `0x438d0064` rellena después los bytes `0, 7, 8–9, 0xc, 0xd, 0xe, 0x12 b3`; no toca 1–3. Corrige la nota de E24-05h §3 («no los escribe `0x438d0064`» era correcta, pero el productor no estaba localizado).

**`pkt[1]`** (`0x43841344–0x438413b4`, VERIFICADO por instrucciones):

| Condición | Valor |
|---|---|
| `[sb+0x4bc] & 0x20` | `0x40` si flag `[0x43f9b503]` = 1, si no 0 |
| si no, clase `[0x43eedecc]` = 1 | `0x40` si flag = 1; si no `[sb+0x4bc] & 0x20` = 0 |
| si no, clase = 3 | `0x42` si flag = 1; si no `2` |
| otro | `[sb+0x4bc] & 0x20` = 0 |
| luego | `+0x14` si `[arg+2] = 1`; `\| 0x80` si `[r6+0x14] ∈ 1..3` |

La clase y el flag son las copias estables escritas por `0x43842158` (→ `0x4383f5e4`), ya documentadas en E24-05a §7. **No hay una asignación EFCS ↔ valor**: sigue siendo E24-05e.

**`pkt[2..3]`** = `u16 [sl+0x162]`, con filtro: si `0x4382fe08([sl+0x162]) = 1` se escribe 0. `0x4382fe08` devuelve 1 si el byte global (`GOT`) ≠ 1 **y** valor < `0xb00` **y** `[g+0x102] & 8 = 0`; si no, 0.

* En T022 `pkt[2..3] = 0x1600 ≥ 0xb00` ⇒ el filtro no actúa; coherente con el dato medido.
* Consecuencia para la matriz: **un valor < `0xb00` (con las condiciones anteriores) daría `S+0x32 = 0` y, según E24-05h §1.3, la variante de espera de P29 sin plazo.** Hay que registrar `pkt[2..3]` en cada disparo y no cambiar la velocidad entre configuraciones. La unidad de `[sl+0x162]` no se determina (el código la usa también como `0x1000 − x` en `+0x166/+0x16a`: escala de 12 bits, INFERENCIA).
* `sl` = resultado de `0x4383fbc4`: una de dos estructuras globales (`0x43f79f94` ó `0x43f7cac0`, GOT `0x4401eee4+0x1904/+0x79d0`) según `0x43b08d42`. Escritores de `+0x162` en la imagen: 22 sitios de `strh`; los plausibles son `0x4383ffe6` (valor `[x+0x4cc]` si `[x+0x2be]=1`), `0x437b43a2` (tabla `0x94/0x96/0x98` si modo 9), `0x437b0e24` y `0x43831f56` (ajuste). **No se demostró cuál escribe en `0x43f79f94/0x43f7cac0`** (el cierre de punteros queda fuera del alcance acotado). Estado: NO_VERIFICADO.
* **`pkt[8]`**: `0x43841070` escribe `pkt[8] = 0xa0` (`0x43841448–0x4384144a`), pero T022 leyó 0. No es contradicción: `0x438d0064` reescribe `pkt[8..9]` con `u16 [obj+0x1450]` (`0x438d01ec/0x438d01f2`, VERIFICADO) y T022 midió 0, es decir `[obj+0x1450] = 0` (que el constructor se ejecute antes que `0x438d0064` es INFERENCIA por el orden de envío). El resto de los campos coincide con el constructor (`pkt[2..3]`, `[4..5] = 0x13bd`, `[0xa..b] = 0x0e53`, `[0x13] = 0x90`).

## 4. Matriz EFCS ON/OFF (preparada, no ejecutada)

**Condiciones fijas** (registrar en el log y no cambiarlas): Darwin 3.22 tipo 0 instalado (T024); modo M; **una sola velocidad** (la de T022 si se conoce; si no, la misma para todos los disparos y anotada por `/ss` y EXIF); misma apertura/ISO/enfoque; disparo único; «RR exp. larga» desactivada; sin flash; escena y encuadre fijos; app RemoteShutter abierta como en T023–T027; batería suficiente. EFCS la cambia **el usuario en el menú** (no el software). Sin escritura de RAM.

| Paso | Acción | Lectura (solo lectura) |
|---|---|---|
| 0 | Reposo, EFCS ON, sin disparar | R0: filas de la tabla del §5 |
| 1–6 | Disparos en orden **ON, OFF, OFF, ON, ON, OFF** (ABBAAB: reparte la deriva); tras cada cambio de EFCS el usuario confirma el ajuste y se hace R antes de disparar | Tras cada disparo: espera 6 s (T023), `/status` (contador `done N` debe incrementar), luego R |
| 7 | Reposo, EFCS OFF | R7 |

Una lectura **R** = `pkt` 22 B + clase + flag + `[sl+0x162]` de las dos estructuras (§5). Orden ABBAAB ⇒ 3 ON + 3 OFF. Si hay tiempo, bloque opcional con una segunda velocidad (misma matriz); nunca mezclar velocidades dentro de un bloque.

**Lectura**: patrón de `camera_tipo2_sweep.py::rd` (`dd if=/dev/mem bs=1 skip=ADDR count=N`, `hd` vía `chroot /android`), con `ADDR` físico del §5. Control igual que T022: leer también `G+0x808` o la ventana `0x83f91e20..+0x110` y comprobar que es coherente. No se emite ninguna escritura; tampoco `of=/dev/mem`.

## 5. Datos accesibles por T022 frente a los que exigen vía nueva

| Magnitud | Virtual → físico | Bytes | Estado | Vía |
|---|---|---|---|---|
| `pkt` 0x0c completo | `0x43f91e32` → `0x83f91e32` | 22 | **MEDIDO** (T022) | T022 |
| Clase (`pkt[1]`) | `0x43eedecc` → `0x83eedecc` | 4 | dirección por bytes; lectura no probada | T022 |
| Flag (`pkt[1]` bit 6) | `0x43f9b503` → `0x83f9b503` | 1 | ídem | T022 |
| `[sl+0x162]` (estruct. 1) | `0x43f7a0f6` → `0x83f7a0f6` | 2 | ídem | T022 |
| `[sl+0x162]` (estruct. 2) | `0x43f7cc22` → `0x83f7cc22` | 2 | ídem | T022 |
| Tipo de bobina (`0x20c74`) | no es celda: `[0x20000050+ch]` y `0x1b080(0)` | — | deducido de P4D/P4E | **vía nueva** |
| Estado del sistema | `0x20002a04` (SRAM Darwin) | 1 | — | **vía nueva** |
| FSM de captura pos/id | `0x200036fc/d` | 2 | — | **vía nueva** |
| ADC-B pos/id/celda | `0x2000381e/f`, `0x20003820` | 3 | — | **vía nueva** |
| `S+0x14c`, `S+0x32`, `S+0x444`, `S+0x170` | `0x20003824`, `0x2000370a`, `0x20003b1c`, `0x20003848` | — | — | **vía nueva** (`S+0x32` solo se *infiere* de `pkt[2..3]`) |
| ADC-A pos/id/celda, duraciones | `0x2000381c/d`, `0x20003818`, `0x20000331/2` | — | — | **vía nueva** |
| Temporizadores | `0x20002d68`, `0x20002d6c/d`, `0x20002d70`, `0x20002d5c` | — | — | **vía nueva** |
| Registros del periférico y P29 | `0x40023004/14/1c`, `0x40031094`, `0x40033008/108/208/408` | — | — | **vía nueva** |

Las direcciones de las cinco primeras filas están verificadas por bytes (`protocolo.json`). Los buffers de T023 (IDs `0x0f/0x12/0x13`) y el bloque de 210 B ya se leyeron a cero: no se repiten.

**Vías nuevas posibles, sin evaluar ni autorizadas** (este informe no las prepara): analizador lógico pasivo en P29, P4B, P4C y CAIF (ya en E24-05h-2); variables de captura de BIONZ alimentadas por los mensajes `0x10`/`0x11`/`0x14` de Darwin (direcciones no localizadas; los bloques del buzón se liberan al consumirlos, E24-05d §1). No se propone el uso de depuración por SWD ni se sabe si está accesible.

## 6. Persistencia tras el disparo

| Valor | ¿Persiste? | Cómo medirlo |
|---|---|---|
| `pkt` (`carga+0x40`) | **Sí**, hasta el siguiente envío del `0x0c` (se reconstruye por fotografía y en cada reintento de la clase 1 del `0x0b`: solo queda el **último** envío) | tras el disparo (T022) |
| Clase y flag (`0x43eedecc`, `0x43f9b503`) | Sí (copias estables; se reescriben en el siguiente disparo) | tras el disparo |
| `[sl+0x162]` | **No se sabe**: AE puede reescribirlo con la vista en directo; `pkt[2..3]` es su copia estable (salvo filtro) | tras el disparo; si difiere de `pkt[2..3]`, lo reescribió AE o actuó el filtro de `0xb00` |
| Bloques Darwin→BIONZ del buzón | **No**: se liberan al consumirlos (E24-05d §1) | solo durante la ejecución; sin dirección fija |
| Estado de Darwin (ADC, temporizadores, P29, FSM de captura) | La SRAM no se borra al terminar, pero **no es alcanzable**; los valores intermedios de la captura (1→4→7, esperas, nivel de P29) solo existen durante ella | sin vía |

Lectura **durante** el disparo (sondeo en bucle, como `camera_imx210_timing.py`): solo para el paquete de BIONZ, no recomendada en la matriz mínima (efecto del observador, §8). No hay valor de Darwin que pueda medirse ni durante ni después con la vía actual.

## 7. Criterios SÍ/NO

| Criterio | SÍ si | NO significa |
|---|---|---|
| **C1 Integridad** | las 6 lecturas devuelven 22 B completos, el control de ventana es coherente y `done N` incrementó en cada disparo; velocidad/modo idénticos | repetir; no concluir |
| **C2 Repetibilidad** | dentro de cada configuración los 3 paquetes coinciden en `pkt[1]`, `pkt[2..3]`, `pkt[0xc]`, `pkt[0xd]` (los bytes 8–9 y los campos temporales aparte) | *evidencia insuficiente* (hay otra variable no controlada); no se interpreta ON/OFF |
| **C3 Discriminación EFCS** | existe un byte (en especial `pkt[1]` o `pkt[0xd]`) con valores **disjuntos** entre ON y OFF | *EFCS no viaja en el `0x0c`*: E24-05e se cierra en negativo por esta vía; el tipo de mecanismo sigue inferido |
| **C4 Variante de espera** | `pkt[2..3] ≥ 0xb00` en las 6 lecturas | si alguna da 0: `S+0x32=0`, variante de P29 sin plazo; riesgo documentado |
| **C5 Lectura del predicado** | con el valor de `pkt[1]` de cada configuración, la tabla de verdad de `0x196a2` (E24-05a §7: `0→1`, `2→0`, `0x40→1`, `0x42→1` con tipo 0) da resultados explicables | *contradicción* con la tabla: reabrir E24-05a §7 |

**Decisión D1 — ¿basta para cerrar E24-05e?** SÍ si C1–C3 (y C5 para interpretar). NO si falla alguno; C2 o C1 = evidencia insuficiente, C5 = contradicción.

**Decisión D2 — ¿basta para avanzar a sin rearme (E24-06)?** **Nunca con T022 solo**, aunque todos los criterios den SÍ:

1. Una fotografía normal con la cámara tal como está **se hace con el rearme activo**; que salga bien no ejercita las rutas que existirían sin rearme, ni demuestra que los estados 3/32 ven a ADC-A y ADC-B en terminal, ni el grupo de P29, ni los eventos del canal 0 y del canal 11 (E24-05h-4).
2. Lo que T022 puede aportar (cinco magnitudes de BIONZ) decide E24-05e y aclara el modo de espera (C4), pero ninguna magnitud de Darwin.
3. Cualquier paso hacia E24-06 requiere además un dato directo de Darwin por una vía nueva (§5) **y** autorización expresa del usuario. Este informe no declara E24-06 autorizado.

## 8. Riesgos

| Riesgo | Tratamiento |
|---|---|
| Lectura de una dirección no probada (`0x83eedecc`, `0x83f9b503`, `0x83f7a0f6`, `0x83f7cc22`) | misma DRAM y mismos rangos que otras lecturas (`0x83e7…`–`0x8401…`); leer primero la ventana de T022 y solo después las nuevas, con `bs=1`/`count` mínimos; abortar si la cámara no responde |
| Efecto del observador (sondeo en bucle durante el disparo) | no usarlo en la matriz mínima |
| EFCS cambiado por el usuario con la app activa | confirmar en pantalla y esperar la lectura en reposo antes de disparar |
| Valores obsoletos (el `pkt` queda del disparo anterior) | usar `done N` y comparar con la lectura de reposo; si no cambia nada entre configuraciones, no es evidencia (C3 = NO) |
| Desgaste mecánico | 6 disparos (12 con el bloque opcional) |
| Escritura accidental | el protocolo no incluye `of=/dev/mem`; revisar el comando antes de enviarlo. La técnica sí escribe un fichero temporal `/android/dev/z` (no RAM) y lo borra, como T022/T023 |
| Interpretar `pkt[8..9]` | es `[obj+0x1450]`, no EFCS (§3); se registra pero no discrimina |

## 9. Pruebas y límites

`tests/test_e24_05h5_protocolo.py` (verifica en `av-cam.bin` los puntos del §3: constructor, filtro `0xb00`, argumento `carga+0x40`, direcciones del §5; en el repo: que T022/T023 solo leen DRAM de BIONZ y que ningún script con `/dev/mem` usa literales `0x20xxxxxx`; y que el paquete de T022 es coherente con el constructor y con la reescritura de `0x438d0064`).

Límites: no se siguieron los escritores de `[sl+0x162]` hasta la fuente (AE); no se determinó la unidad de `pkt[2..3]`; no se probó que `/dev/mem` devuelva datos en las direcciones nuevas; la existencia de otra vía hacia Darwin no se descarta. **Las mediciones quedan pendientes de autorización expresa del usuario.**
