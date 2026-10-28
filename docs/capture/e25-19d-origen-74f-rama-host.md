# E25-19d — Origen de `cap+0x74f` y viabilidad de la rama de host

Fecha: 28-10-2026. Modalidad: **solo estático y emulación** sobre `av-cam.bin` (fw 3.21, base `0x43541000`); cámara **no accesible** (23 y 8080 cerrados), sin RAM escrita, sin parche. Etiquetas: V = bytes, E = emulación del código real, I = inferencia.

Evidencia: `analysis/e25-19d/` (`barrido-74f.json`, `escritores-lectores-74f.json`, `rama-host-emulacion.json`). Scripts: `scripts/e25_19d/` (`escritores_74f.py`, `tabla_escritores.py`, `xref_pc.py`, `rama_host.py`). Pruebas: `tests/test_e25_19d.py` (5) + regresiones E25-17/18/19 (98 en total, verdes).

## 1. Escritores de `cap+0x74f` (P0)

Barrido Thumb-2 de todo el binario (stores con desplazamiento 0x74c–0x74f y construcciones de la constante; 135 hits, 3 escriben el byte `0x74f`). Tabla verificada contra los bytes (`tabla_escritores.py`):

| # | Instrucción | Función | Valor | Condición | Evid. |
|---|---|---|---|---|---|
| W1 | `0x438acc9c strb.w r1,[r3,#0x74f]` | `0x438ab3e8` (copia de bytes `plan[0x136..0x155]` → `[0x744..0x765]`, `r2`=plan, llamada por `0x438ccd78` vía veneer `0x43af66b8`) | `plan[0x142]` | siempre al construir; `plan+0x142` es un halfword que fijan 8 ramas con `2×0x4387b520(…)` | V |
| W2 | `0x437df5e8 strb.w r8,[r4,#0x74f]` | `0x437df338` (arranque de captura, `r0`=cap: usa `+0x774/+0x4a00/+0x5400`) | **0** | solo si `r8==0`, con `r8=0x437e1e48(…)` (petición de modo/arranque; si `r7≠0` y devuelve 0 registra error nivel 5 y hace `cap[0x4fd0]|=1`, `0x43ae7636`); con `r7==0` → `r8=1` y no escribe | V |
| W3 | `0x438c2562 strb.w r3,[r4,#0x74f]` | `0x438c2538` (admisión del `0x0b`, E24-05g) | **0** | `G=[0x4402546c]=0x43e95950`; `G[0x7e]≠0` **y** `G[0x7f]==cap[0x1d8]` (id de petición cancelada, I) | V |

Resultado: **ningún escritor directo pone un 1**. Los dos que escriben ponen 0 (fallo de arranque, cancelación); el 1 solo puede llegar por la copia W1. No hay `memcpy`/`memset` de `cap` completo que lo cubra (el `cap` se reserva de pool con `0x4378764c`→`0x437dcfc8`, sin copia de otro `cap`; sí lo rellena W1).

**Contradicción abierta (honesta):** `plan[0x142]` = `2×lookup` en las 8 ramas visibles, luego su byte bajo es par y no puede valer 1; en vivo (E25-19b) `cap+0x74c..0x74f = 00 01 00 01`. O el destino de W1 (`[sp+0xd0]` de `0x43b13b2c`) no es el `cap` observado, o el plan se completa por otra vía. **No resuelto** (E25-19e).

## 2. Quién usa cada rama (P1)

Lectores de `cap+0x74f` (V): 26 sitios — `0x438c2566`, `0x438c29fa` (admisión), `0x438c83ce`, `0x438c8ac2` (armado), `0x43b1f15e` y **21 manejadores** `0x438d025c…0x438d0dc8` (todos abren con `ldrb.w r3,[r0,#0x74f]`).

* En los manejadores (p. ej. `0x438d058c`, `0x438d060c`, `0x438d0b44`): **`74f==0` salta la espera CAIF** (`0x437db858`/`0x437db9f0`) y retorna OK; `74f≠0` espera el mensaje de Darwin. Es decir, `74f` = «secuenciación con confirmaciones de Darwin»; con 0 BIONZ avanza **sin esperar ninguna confirmación** (V). Excepción: sub 9 (`0x438d08e8`) cambia la espera de mensaje por `twai_flg(0x13,0x100000)`.
* `0x43b1f15e`: con `74f≠0` salta a `0x43560d1c(0x1d)`; con 0 retorna.
* `0x438c83ce` (tramo de `StartExposure`, junto a `+0x30`): si `cap+0x740==0`, `[4b84]==0` y `74f≠0`, el argumento `r6` de `0x43795dec` (→ `0x43ad3b92`, método del sensor) vale 4 si `G[0x60]==0`, si no 3; con `74f==0` siempre 3 (V). Efecto sobre el sensor **no decodificado** (pendiente).

**Veredicto P1: E (C + fallo de arranque), no fotografía convencional.** Los únicos caminos que ponen 0 son cancelación (W3) y arranque rechazado (W2); todas las fotos observadas (E25-19/19b/19c) tienen `74f=1`. No hay evidencia de un modo normal (corta/larga/BULB/silent/vídeo) que seleccione 0; **«ShutMode determina el campo» no se confirma ni se descarta** (no hay lector de ShutMode en W1–W3 salvo vía el plan, no trazada).

## 3. Rama del host reconstruida y emulada (P2, P5)

Flujo (V): `[sl+0x162]` (Tv) → `0x4382fac8` (µs; `0x4384157a`) → global `0x43eee76c` (`0x4384157c`) → `0x43840f7c` (lo devuelve, µs) → `0x438c8ad8 lsrs #5; adds #1` → `cap+0x728` → `0x43b1f1ec(0, ticks, 0x43b1e4c0)` → temporizador HW (`0xf2403000`, carga en `+8`, ctrl `…0b0111`, modo bits 5:4=1) → callback `0x43b1e4c0` (`set_flg(0x13,0x100000)`) → `0x438d08e8`: `twai_flg(0x13,0x100000)` + `clr_flg` → retorno de sub 9. Condición de armado (V): `cap+0x73a==0`, `[cap+0x4b84]==0`, `74f==0`, `cap+0x740≠1`; si no, `ticks=−1` (cronómetro libre) con callback `0x43b1e447`.

**El Tv es el mismo del paquete `0x0c`:** `0x43841070` guarda `pkt[2..3]=[sl+0x162]` (`0x438413c8..d2`; solo `pkt[2..3]=0` si `0x4382fe08(Tv)==1`) y el temporizador de host usa `0x4382fac8([sl+0x162])` (`0x43841576`). Tv 3243 → 10,07 s (E) ✓ con la lectura de E25-19c; no hay transformación adicional.

Emulación Unicorn del tramo real `0x438c8abc..0x438c8b18` con `cap` sintético (`74f=0`), Tv = `4096−256·log2(t)`:

| t | Tv | µs (0x4382fac8) | ticks | t por ticks | error |
|---|---:|---:|---:|---:|---:|
| 1/8000 | 7415 | 125 | 4 | 0,128 ms | +2,4 % |
| 1/1000 | 6647 | 1000 | 32 | 1,024 ms | +2,4 % |
| 1/250 | 6135 | 4002 | 126 | 4,032 ms | +0,8 % |
| 1/60 | 5608 | 16674 | 522 | 16,70 ms | +0,22 % |
| 1/30 | 5352 | 33348 | 1043 | 33,38 ms | +0,13 % |
| 1/15 | 5096 | 66696 | 2085 | 66,72 ms | +0,08 % |
| 1/8 | 4864 | 125000 | 3907 | 125,02 ms | +0,02 % |
| 1 s | 4096 | 1 000 000 | 31251 | 1,0000 s | +0,003 % |
| 4 s | 3584 | 4 000 000 | 125001 | 4,0000 s | +0,001 % |
| 8 s | 3328 | 8 000 000 | 250001 | 8,0000 s | +0,0004 % |
| 15 s | 3096 | 14 993 286 | 468541 | 14,993 s | −0,045 % |
| 30 s | 2840 | 29 986 572 | 937081 | 29,987 s | −0,045 % |

* **Overflow:** 937 081 ≪ 2³²; no hay saturación en el cálculo. El ancho del contador HW no está documentado (sin hoja de datos) pero 937 081 < 2²⁰ (I). Límites distintos corto/largo: no hay; el −0,045 % de ≥15 s es la tabla de `0x4382fac8`, no el contador.
* **Precisión matemática ≠ física:** esto es solo el cronómetro de BIONZ (arranque de la espera); no mide integración del sensor.
* **No verificado:** si el temporizador HW es de un disparo o periódico (ctrl bits 5:4=1 sin documentar) → posible repetición del callback; quién lo cancela (`0x43b1f1c2` se llama justo antes de armar, `0x438c8ab8`; stop en `0x43b1f254`); carrera con un `0x0e` tardío (con `74f=0` el `caif_recv` de sub 9 ni se invoca). Orden `twai_flg`→`clr_flg` correcto según el código (V), sin ejecutarlo.

## 4. Darwin con la rama de host (P3)

| Pregunta | Respuesta | Nivel |
|---|---|---|
| A. ¿BIONZ sigue enviando `0x0c`? | **SÍ**: el constructor `0x43841070` y sus alrededores no leen `74f` (los 26 lectores están en otras funciones) | V (BIONZ) |
| B. ¿mismo Tv? | **SÍ**, `pkt[2..3]=[sl+0x162]` | V |
| C/D/E. Darwin sigue su secuencia, cortina y `0x0e` | **Inferido SÍ**: `74f` es un campo de RAM de BIONZ que no viaja; Darwin recibe lo mismo y su máquina (E24-05a/f: estado 31 → `0x0e`) no depende de él | I (E24) |
| F. ¿BIONZ ignora `0x0e`? | Con `74f=0` sub 9 no llama a `caif_recv`; el `0x0e` queda en el buzón `[0x43e77284]` y lo consumiría la siguiente espera CAIF con otra subclase (o se descarta por subclase): **no verificado** | I |
| G. ¿Lectura sin esperar? | BIONZ **avanza sin esperar** ninguna confirmación (21 manejadores omiten sus esperas) | V |
| H. ¿Orden de fin electrónico independiente? | **No hallada** | V (ausencia limitada) |
| I/J. Doble finalización / lectura anticipada | Con `74f=0` el temporizador BIONZ puede terminar **antes** de que Darwin cierre la cortina (el valor es el mismo tiempo nominal, empieza al armar, no al abrir): riesgo de lectura anticipada o de un `0x0e` huérfano **no descartado** | I |

## 5. ShutMode 0 e integración (P4, P6)

La rama de host **solo sustituye el criterio de salida de una espera de software**: el temporizador no toca `SetExposure`, `SetRead` ni el sensor (V; coincide con E25-19 §4i: «sin operación al sensor entre inicio y fin de la espera»). No hay reset electrónico, ni fin electrónico de integración, ni lectura intermedia en esa ruta. El plan `cap+0x64c` (`shd=1, svd=0, ShutMode=3`) no depende de `74f` (los lectores en el tramo de `StartExposure` solo afectan al argumento `r6`, §2). Por tanto **retrasar la lectura con ella no mantiene la integración**: no cumple el objetivo sin una integración electrónica continua que hoy no está demostrada (E25-18: C; sumidero físico del VTS sin hallar). Compatibilidad `74f=0` con ShutMode 0: **no demostrada ni refutada**.

Experimento RAM reversible propuesto (**no ejecutado**, exige autorización expresa y backup NVRAM): en una foto normal de 4 s, tras crearse `cap` (antes de sub 9) escribir `cap+0x74f=0` y observar si sub 9 sale por `0x100000` a los ≈4 s sin `0x0e`, qué hace Darwin (cortina, `0x0e` huérfano) y si el RAW es íntegro. Reversión: restaurar el byte; riesgo de bloqueo del hilo (reinicio de batería).

## 6. Veredictos (P8)

| | Resp. | Justificación |
|---|---|---|
| A. ¿escritores hallados? | **SÍ** | W1–W3 por bytes; destino de W1 no demostrado como `cap` |
| B. ¿cuándo vale 0? | **SÍ, con límite** | W2 (arranque rechazado), W3 (cancelación); `G[0x7e/0x7f]` sin escritor trazado |
| C. ¿cuándo vale 1? | **NO** (pendiente) | solo vía W1, contradicha por el halfword par (§1) |
| D. ¿`74f=0` en fotos normales? | **NO** | solo error/cancelación; los `cap` leídos en vivo (fotos de 2/4/8 s, E25-19b) tienen 1 |
| E. ¿fuente de duración? | **SÍ** | `0x4382fac8([sl+0x162])`→`0x43eee76c`→`0x43840f7c` (µs) |
| F. ¿30 s sin overflow? | **SÍ** | 937 081 ticks (E); ancho HW sin documentar |
| G. ¿emulada la ruta real? | **SÍ** | `0x438c8abc..0x438c8b18` + `0x4382fac8`; no el RTOS ni el temporizador HW |
| H. ¿libera sub 9? | **SÍ en el código** | `set_flg`→`twai_flg`→`clr_flg`; one-shot/repetición sin verificar |
| I. ¿sigue `0x0c`? | **SÍ** | §4 A |
| J. ¿Darwin sigue controlando? | **SÍ (inferido)** | §4 C–E |
| K. ¿BIONZ avanza sin `0x0e`? | **SÍ** | §2: esperas omitidas / flag |
| L. ¿cambia la secuencia del sensor? | **NO demostrado** | solo `r6` 3/4 en `0x438c83ce` (efecto sin decodificar) |
| M. ¿fin electrónico de integración? | **NO** | hipótesis pendiente (no contradicha) |
| N. ¿ShutMode 0 compatible? | **NO** | pendiente |
| O. ¿RAW de 30 s continuo? | **NO** | pendiente; solo hay temporizador de espera |
| P. ¿ruta completa de SetExposure? | **NO** | sin avance respecto a E25-15/16/18 |
| Q. ¿cámara sin modificar? | **SÍ** | cámara inaccesible, nada escrito |
| R. ¿siguiente experimento mínimo? | **SÍ** | lectura (solo lectura): `G=0x43e95950` `+0x60/+0x7e/+0x7f`, `cap+0x74f/0x4fd0`, en reposo y en vuelo durante una foto normal y tras cancelar (medio pulsador/otro disparo), para fijar W3/valor 1; luego el RAM reversible de §5 |

## 7. Decisión final: **B — rama del host auxiliar, sin independencia de Darwin**

El temporizador existe y es correcto en cifras (1/8000–30 s, sin overflow), y con `74f=0` BIONZ no necesita el `0x0e`; pero es un mecanismo de **error/cancelación** que (i) no se selecciona en fotografía normal, (ii) no cambia nada del sensor, (iii) no desactiva a Darwin, que sigue recibiendo el `0x0c` y operando la cortina. No sustituye al control mecánico; para una integración electrónica faltan el fin de integración y la lectura (E25-18, C3-B). Elementos de D: la procedencia del 1 y los escritores de `G[0x7e/0x7f]` quedan sin cerrar → E25-19e. No se pasa a E25-20.

Límites: sin cámara; Darwin solo por E24 (estático); el ancho/modo del temporizador HW no está documentado; auditoría global de escritores de `G` pendiente.
