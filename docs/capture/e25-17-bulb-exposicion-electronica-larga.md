# E25-17 — Exposición electrónica de 1/8000 s a 30 s y BULB (investigación estática)

**Fecha:** 28-10-2026 · **Binario:** A6000 fw 3.21 `av-cam.bin` (SHA-256 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`, base `0x43541000`) ·
**Alcance:** análisis estático (Capstone sobre bytes), emulación de código real (Unicorn) y diseño de experimentos.
**No se conectó la cámara, no se escribió RAM/NVRAM/firmware, no se ejecutó ninguna prueba física.**
Etiquetas: **V** = bytes/instrucciones o emulación del código real; **I** = inferencia con evidencia; **N** = no verificado.
La emulación demuestra aritmética del firmware, **no** el comportamiento del IMX210.

> Nota de nomenclatura: PENDIENTES ya usaba «E25-17» para T052-A/B0. Esta investigación mantiene el ID pedido y
> absorbe esa fila (T052-B0 queda como su antecedente); los pendientes derivados son E25-18 (C3-B) y E25-19 (B0-bis).

## 0. Resumen y decisión

1. **El límite de ~65 ms no es una restricción del firmware, sino de la ruta manual `r5`.** El productor nativo `0x4383fa40` ya
   planifica exposiciones de 1/15 s a 30 s: devuelve `shd = 1` (el suelo), `svd = N − 1` (cuadros enteros adicionales,
   `record+0x68`) y un VTS ampliado para el cuadro con resto (`record+0xd8`). Con VTS 4219: 1/15 s → `svd 0`, cuadro de
   4389 líneas; 1 s → `svd 14`; 30 s → `svd 472` (§1.2, V por emulación). Esto **corrige** E25-14 («clamp a un cuadro»),
   E25-15 J («sin cuadro más largo») y T052-B0 §4.4 («`record+0x68` no es un contador útil»): `record+0x68` es el `svd`
   que `SetExposure` escribe en los registros ID3/ID4 **y** el valor que compara el contador de pasos del host.
2. **El contador de pasos del host no es el mecanismo de exposición larga.** `StartExposure` pone `cap+0x650 = 0` tras cada
   llamada cuando `cap+0x740 == 0` (§1.3), de modo que con ese valor la secuencia es de un solo paso aunque `svd > 0`.
   Los pasos repetidos (`0x43b1e7f2`) solo existen con `cap+0x740 ≠ 0` (productor no localizado).
3. **BULB y las exposiciones largas con obturador mecánico se temporizan en el host por tramos de un cuadro** (`0x438c74b0`,
   `bulbFrameCount = cap+0x72c`): el objetivo `0` equivale a «sin límite». No se identificó el despacho de la pulsación ni
   de la liberación, ni qué hace el sensor entre tramos (§2).
4. **No hay prueba física** de que el IMX210 mantenga una única integración durante `svd + 1` cuadros. El fundamento es
   aritmético y de diseño (el productor es de Sony, usa la misma identidad `exposición = líneas totales − shd` que T047
   midió dentro de un cuadro), no una medición.

**Decisión final: C — secuenciador multicuadro**, entendido como `svd` en el sensor + VTS ampliado por cuadro (A como
componente) + temporizador del host; **no** como repetición de pasos del host. Orden por probabilidad de éxito:
**C/A** (media; complejidad media-alta; compatibilidad alta; riesgo medio solo con RAM) > **D** (media-baja; falta el
fin de integración) > **B** (baja con la evidencia actual) > E. El siguiente experimento mínimo es **de solo lectura**
(§10) y decide entre C y E.

## 1. P0 — S57 frente a T052-B0

### 1.1 Secuencia coherente (V salvo nota)

```
Tv (settings+0x162) ──► record+0xf6
0x4383fa40(record, imager)                      ; solo escribe record; lee +0xc +0x1c +0x20 +0xf6, imager+0x4b8
   líneas L = µs(Tv)/período            ─► record+0xf0
   R   = max(suelo + L, VTS)  (+ VTS si 0x43a12ca8 = 1)          ; suelo = record+0x1c
   shd = R − L                          ─► record+0x64  (= r5)
   svd = ⌊R / VTS⌋ − 1  (mín. 0)        ─► record+0x68
   d8  = (R mod VTS) + VTS              ─► record+0xd8 ; da = dc = VTS  (+0xda, +0xdc; con svd = 0 los tres = R)
0x4383fd6c: record+0x64..0x73 ─► cap+0x64c   ; param+0 = shd, +4 = svd, +6 = spl, +8 = sint, +9 = ShutMode
0x437b21b8 (planificador por VD): record+0x60 = d8 (1.er cuadro) | dc (último) | da (intermedios); cap+0x6bc/0x6be (bloque SetRead)
0x438c828c StartExposure, paso 0 (cap+0x4b9c = 0):
   SetExposure(cap+0x64c): ID3/ID4 = svd, ID5/ID6 = shd, ID7/ID8 = spl, ID1 según ShutMode, obj+0x3a8 = svd
   SetRead(cap+0x6bc) ; SSB ; Execute(1)                          ; pasos ≥ 1: solo Execute(0)
host: cap+0x650 (= svd) frente a cap+0x4b9c en 0x43b1e7f2
```

### 1.2 Productor ejecutado (`scripts/e25_17/emular_productor.py`, `analysis/e25-17/productor.json`)

Línea 3891 (Q8) = 15,2 µs, VTS 4219, suelo 1, predicado 0. Invariante comprobada: `d8 + svd·VTS = max(suelo + L, VTS)` y `R − shd = L`.

| Velocidad | Líneas L | shd (r5) | svd | d8 (VTS del cuadro con resto) |
|---|---:|---:|---:|---:|
| 1/8000 | 8 | 4211 | 0 | 4219 |
| 1/250 | 263 | 3956 | 0 | 4219 |
| 1/60 | 1097 | 3122 | 0 | 4219 |
| 1/30 | 2194 | 2025 | 0 | 4219 |
| 1/15 | 4388 | 1 | 0 | **4389** |
| 1/8 | 8224 | 1 | 0 | **8225** |
| 1/4 | 16448 | 1 | 2 | 8011 |
| 1/2 | 32896 | 1 | 6 | 7583 |
| 1 s | 65792 | 1 | 14 | 6727 |
| 2 s | 131585 | 1 | 30 | 5016 |
| 8 s | 526342 | 1 | 123 | 7406 |
| 15 s | 999552 | 1 | 235 | 8088 |
| 30 s | 1999104 | 1 | 472 | 7737 |

E25-16 usaba suelo 0 y por eso veía `r5 = 0` («saturan a 0») sin mirar `svd`/`d8`; con suelo 1 el productor da `shd = 1`.
Con el predicado en 1 (valor configurado en NVRAM = 0 ⇒ predicado 1, T052-B0) todo suma un cuadro: 1/30 → shd 6244, svd 1;
1 s → shd 4220, svd 15. Es un modo con cuadro previo (dummy), no una exposición más larga.

### 1.3 Respuestas obligatorias

| | Pregunta | Respuesta y evidencia |
|---|---|---|
| A | ¿Qué es `record+0x68`? | **`svd`** (12 bit útiles): copia a `cap+0x650` = `param+4`; `SetExposure` lo escribe en ID3 (`svd[7:0]`) e ID4[3:0] (`svd[11:8]`) y en `obj+0x3a8` (`0x436d6faa`, `0x436d6fba`, `0x436d6fe2`, `0x436d6ff8`). No es una «ventana» (T052-B0 §4.4 lo leyó como `blk+0x50`, que es la misma cifra). Su valor: cuadros enteros − 1 (V, §1.2). |
| B | ¿El mismo valor llega al sensor y al contador del host? | **Sí, es la misma celda `cap+0x650`** (V), pero con dos interposiciones: con `cap+0x504 == 1` el `svd` pasado a `SetExposure` es 0 (`0x438c82f0`, se restaura en `0x438c8334`); y con `cap+0x740 == 0` el cap queda en 0 tras `StartExposure` (`0x438c83c4`). |
| C | ¿La rama de cuadro extra influye en la duración de una secuencia? | **Sí en el plan**: suma `VTS` a `R` (`0x4383faa0`) ⇒ `svd + 1` y `shd = VTS + suelo`. No es independiente del VTS; solo `record+0xf0` lo es (C3-B). |
| D | ¿El secuenciador puede esperar varios VD? | **Solo con `cap+0x740 ≠ 0`**: `0x43b1e7f2` (paso con contador) se repite hasta `cap+0x4b9c == cap+0x650`, con `svd = 0` envía el mensaje de fin sin exponer (`0x43b1e7f8`). Con `cap+0x740 == 0` (valor por defecto del reposo) es un solo paso. El productor de `cap+0x740` no se localizó (N). El evento que dispara cada paso no se trazó (S57 lo infiere por VD, I). |
| E | ¿Integración continua o lectura/reinicio? | **N.** Los pasos ≥ 1 solo ejecutan `Execute(0)` (reinicio del P2S sin datos, S57 V); ningún registro se reescribe al terminar (`ExposureTimerEnd!`, S57 V). Que el sensor cuente `svd` cuadros internamente es I (nombres `svr_num`/`VdNum`/`svd`, aritmética de §1.2). |
| F | ¿Dependencia `r5`/`svd`/`shd`/`spl`/contador/lectura? | `exposición = (svd·VTS + d8) − shd` (V, §1.2). `spl` y `sint` se fijan a 0 (`0x4383fac8`, `0x4383fad0`). El instante de lectura depende además del temporizador del host (§2) y no se pudo atar a un registro. |

Las 37 comprobaciones de bytes y 5 cadenas están en `analysis/e25-17/evidencia.json` (0 fallos).

## 2. P1 — BULB

### 2.1 Qué es `0x4381106c`, y qué no es

`StrtExps` (CAMERA_MAIN_SYNC) valida `svd = n·svr_num − 1` y no es una función de BULB (S57). `0x43810fa8` pertenece al mismo
planificador. Las rutas de exposición están en dos familias de **flujos de captura** (tabla de 12 flujos construida en
`0x437ec074..0x437ec10e` a partir de entradas GOT; índice por tipo de captura, N):

| Familia | Flujos | Pasos | Qué hace |
|---|---|---|---|
| Corta | `0x43b1ae2a`, `0x43b1aea2`, `0x43b1aeee` | `0x438c8474` · **`0x43b1e854`** (StartExposure) · **`0x43b1e7f2`** (paso con contador) · `0x43b1e878` · `0x437ed568` | Un `StartExposure` (+ pasos si `cap+0x740 ≠ 0`). |
| Con temporizador | `0x43b1af3a`, `0x43b1af90`, `0x43b1afc6` (este con `0x438c8038` SplitExpRead) | `0x438c8474` · **`0x438c86b0`** (ExposureTimerStart/End) · `0x437ed674` | Exposición cronometrada por el host. |

No se trazó qué tipo de captura elige cada flujo ni cuál corresponde a BULB (N).

### 2.2 Temporizador por tramos (V, `0x438c74b0`)

- `r7` = período de cuadro (`0x436d6264` sobre el bloque SetRead; mín. 1; unidad ms, I), objetivo `T` = `[settings+0x66]` (u16; origen N).
- `T ≠ 0`: si `T ≤ (bulbFrameCount+1)·r7` el último tramo dura `T − bulbFrameCount·r7`; si no, un tramo de `r7`.
  **`T = 0`: todos los tramos son de un cuadro y el último nunca llega** (sin límite). Tramo en ticks: `valor × 0x7a12` (31 250).
- Callbacks de fin de tramo: `0x43b1e4e4` (flag `0x2000`, tramo completo), `0x43b1e508` (flag `0x4000`, último tramo con `cap+0x4b84 = 0`)
  y `0x43b1e4c0` (flag `0x100000`, último tramo con lectura dividida, `cap+0x4b84 ≠ 0`).
- `0x438c86b0` ante `0x2000`: mensaje `(4,0x1e,2)`, `bulbFrameCount++` (`0x43b1e42a`, `cap+0x72c`), nuevo tramo y, si
  `cap+0x4b84 == 0`, `0x437f9a64(cap,1)`. Ante `0x8000` llama a `0x43ae7636(cap,4)`. El fin se decide (`0x43afff8e` con `r2 = 1`) con
  `0x4000` (y `4b84 = 0`), `0x100000` (y `4b84 ≠ 0`) **o `0x8000`**: la parada externa usa la misma salida que el final por temporizador.
  Los emisores de `0x8000` (`0x438d0e64`, `0x43b1f16c`, por GOT) y su disparo (botón/liberación) **no** se trazaron.
- Cadenas: `[IMAGING_CAP]: SplitExpRead (snr_expread_count %d, bulbFrameCount :%d)` en `0x43cc8b31`, `bulb Table` en `0x43ca6c02`.

### 2.3 Programación del sensor en la ruta con temporizador (V)

Primer paso de `0x438c86b0`: `cap+0x655 = 1` (ShutMode 1), `cap+0x64c = 0`, `svd = 0`, `spl = 0` → SetExposure,
SetRead, SSB, `Execute(1)`, mensaje `0x107` a Darwin con `cap+0x56c/0x570` (tiempo) y luego el temporizador. En cambio, la
ruta corta usa los bloques del productor/foto (ShutMode 0 o 3, `shd` ≥ 1, `svd` del plan). ShutMode 1 fija en ID1 los bits 2, 7 y 6 y
`obj+0x3a0 = shd·(período)/1000 + 1` (tiempo que espera el host): con `shd = 0` espera 1 ms; el sensor no recibe duración (I).
Tabla de ShutMode (`0x436d70c6`): 0 → ID1{b2=0,b7=0,b4=0,b6=1}; 1 → {1,1,0,1}; 2 → {1,1,1,0}+ID0x100/0x101; 3 → {1,1,1,1}; 4 → {0,1,0,1}.

### 2.4 Diagramas

**A. Fotografía normal (mecánica)**

| Paso | Función / dirección | Entrada → salida | Evidencia |
|---|---|---|---|
| 1 Botón → petición | N (UI/Darwin; fuera de E25-17) | petición `req` con flags `Cap_core_mode` y `req+8` (PGA, SHD, 28Limit, LongObMode) | V cadenas `0x43cc893a..` |
| 2 Preparación | `0x438c7800` | SetMode `0x436d61a4`, SetRead `0x436d6398`, `Execute(1)`, mensaje `0xf013` | V |
| 3 Flujo corto | `0x43b1ae2a…` | `0x43b1e854`/`0x43b1e7f2` | V |
| 4 Exposición | `0x438c828c` | SetExposure(shd, svd, ShutMode) → SetRead → SSB → `Execute(1)`; mensaje `0x107` | V |
| 5 Finalización | `0x43b1e878` | cierre; sin escritura de registros de fin | S57 V |
| 6 Lectura → RAW | `0x438c814c` ReadExecute | tiempo de lectura `cap+0x724` | V |

**B. BULB (candidata; solo estructura)**

| Paso | Función / dirección | Evidencia |
|---|---|---|
| Botón mantenido | N | — |
| Preparación | `0x438c8474` | V |
| Comienzo | `0x438c86b0` paso `cap+0x4b9c = 0`: ShutMode 1, `shd=svd=spl=0`, SetRead, SSB, `Execute(1)`, mensaje `0x107` | V código; asociación a BULB **I** |
| Espera | `0x438c74b0` con `T = 0`; tramos de un cuadro; `bulbFrameCount++` | V código; `T=0` ⇔ BULB **I** |
| Liberación | flag `0x8000` → `0x43ae7636(cap,4)` | V el consumo; el emisor **N** |
| Finalización | `0x437f9a64(cap,1)` y ReadExecute | V las llamadas; su efecto en el sensor **N** |
| Lectura → RAW | `0x438c814c` | V |

**Pregunta decisiva.** La diferencia entre una foto normal y la ruta con temporizador **sí modifica la secuencia electrónica**
(ShutMode 1 y `shd=svd=spl=0` frente a ShutMode 0/3 con `shd`/`svd` del plan; V código). Que BULB use esa variante es
inferencia; que la duración la fije solo el control mecánico (Darwin) o también el sensor es **N**. DFE/CamCore: no se
trazó su intervención (N).

## 3. P2 — Hipótesis H1, H2, H3

**H1 — Extender el cuadro (VTS).** El firmware **lo planifica**: `d8` = VTS del cuadro con resto (4389 para 1/15 s, 8225 para 1/8 s),
`0x437b21b8` lo vuelca a `record+0x60` por cuadro y el bloque SetRead (`cap+0x6bc/6be`), y `0x437b22dc` envía `período·VTS` a
`0x436ef628` (campo `0x43e849c0+0x40`). Falta el sumidero físico (generador de VD/DFE/registro del sensor) y si el IMX210 va en esclavo
(INFERENCIA débil: el VTS no aparece en `SetExposure`). **Veredicto: ruta nativa identificada en software; ruta demostrable y utilizable: no.**

**H2 — Integración hasta una orden de fin.** Sin evidencia de un registro de fin (S57/S202/E25-14 se mantienen). Que ShutMode 1/3 con `Execute(1)` deje
al sensor integrando hasta la orden de lectura es plausible (la exposición mecánica de segundos lo exige) pero es **I**. La lectura no se
puede retrasar con ningún mecanismo comprobado. **Veredicto: sin mecanismo identificable independiente de la cortina.**

**H3 — Varios períodos VD.** El contador del host no sostiene la integración (§1.3 D). Sí lo hace, en teoría, la combinación `svd`+VTS del plan.
**Veredicto: técnicamente fundada (aritmética nativa), no demostrada físicamente.** El contador cuenta pasos; `Execute(0)` no escribe datos.

## 4. P3 — LongObMode y SetReadZ

**LongObMode** (V): `u32[req+8][+4]`, junto a `PGA` (`+2`), `SHD` (`+1`) y `28Limit` (`+0`) de la misma subestructura. En
`0x438c7800` se registra y se empaqueta con `0x43b1e57c` en el mensaje `0xf013` (`0x438c796c`); no entra en `SetExposure` ni en el
cálculo de `svd/shd`. Con `PGA`, `SHD`, `28Limit` y `opb_out` forma un conjunto de parámetros de ruido/OB, no de duración (I). **No controla
la integración** (capacidad ausente en la ruta examinada). Usos de `cap+0x740 == 1` con `req[5]` (bloque con ShutMode 4, `shd` 0/8,
`cap+0x570` duplicado) sugieren la trama oscura de la reducción de ruido de larga exposición (`Stage_NotifyLongExpNRCapturing`, I débil).

**SetReadZ** (V): `0x43ae93ca` es un `b.w 0x436d63d4` sin llamador directo ni puntero; `0x436d63d4` es **`SetRead_ZAF`** (cadena
`0x43c9333c`), vtable+0x34. Es la lectura ZAF, **no** una ruta de exposición. Hipótesis cerrada; sin más tiempo.

## 5. P4 — A7S y A6300

Las cadenas `bulbFrameCount`, `ExposureTimerStart!`, `SplitExpRead`, `LongObMode`, `bulb Table` y `ReadExecute` existen en el A7S y en el A6000 con el
mismo recuento: **el temporizador por tramos es código común**, no específico de Silent. Lo específico del A7S es el armado `0x436f43c0`
(`obj+0x3dc = 2`) y `0x43b73044(0xe)` (E25-14), que la A6000 no tiene en su `+0x30`. No se encontró en la A6000 un equivalente funcional en otro
subsistema; la A6000 sí tiene lo que el A7S no usa para esto: `svd`/`shd`/`spl` de 12–14 bit (ID3–ID8) y el plan nativo de §1. Las diferencias de
hardware (IMX235 sin registros equivalentes, columnas estáticas por modo, S202) impiden trasladar registros o direcciones. **El A6300 no se comparó**
(no hay `av-cam` en `analysis/rea-independent/input`). Capacidades comprobadas, A6000: planificación multicuadro nativa (V), temporizador por tramos (V),
ShutMode 0–4 (V). No comprobado: armado de fin de exposición equivalente al del A7S.

## 6. P5 — Auditoría offline de C3-B

| Punto | Resultado |
|---|---|
| Scratch de 0x158 B | Suficiente: el productor solo escribe `+0x64,+0x68,+0x6a,+0x6c,+0x6d,+0xd8,+0xda,+0xdc,+0xf0` y lee `+0xc,+0x1c,+0x20,+0xf6` + `imager+0x4b8` (V, 0 stores fuera de `record`) |
| Registros y pila | Preserva `r4–r11,lr`; sin buffer de pila propio (V). El cueva debe salvar `r0–r3,r12,lr` |
| Objeto imager | El 2.º argumento es el objeto con `+0x4b8` (E25-16); no el de ajustes |
| Independencia de VTS/predicado | `L = record+0xf0` se calcula y guarda antes del predicado (`0x4383fa88..0x4383fad8`) (V) |
| Referencia 4219 | Medida (T046/T047), no leída; válida si `L ≤ 4217` ⇒ 1/30 s (L = 2194) sí, 1/15 s (4388) no |
| Cambio de modo | Guardar `record+0xc == 3891` |
| `r5 ≥ 2` | Correcto para C3-B; el suelo de Sony es 1 (§1.2), que en la ruta larga es válido con `svd` |
| Transferencia | Escribir solo `cap+0x64c`/`cap+0x655`; no tocar `cap+0x650` (svd) ni `cap+0x6bc` |
| Fallback | Si `r5` no es válido, no escribir nada |
| **Punto de enganche** (matizado por [E25-18 §3](e25-18-integracion-silent-todas-velocidades.md): `0x438c82fe` es correcto para ≤ 1/30 s, pero no corrige el plan que leen el planificador de VTS y el host) | **Hallazgo nuevo.** `0x43b1e520` (llamado en `0x438c82dc`) lee `cap+0x655` y fija `cap+0x73b` (que gobierna `0x43b1e448/474`). Un enganche en `0x438c82a0` (E25-16) cambia esa entrada con ShutMode 0, condición que T046/T047 **no** ejercitaron (parchearon dentro de `SetExposure`, `0x836d6fb6`/`0x836d7000`). Recomendado: enganchar en `0x438c82fe` (tras `0x43b1e520` y antes de `0x436d6320`), que además solo se ejecuta en el paso 0 (`0x438c82d8`) |
| Bloque forzado | Si `0x43a12c64` vale 2 o 3, `0x438c82ac..82c8` pone `cap+0x64c = 2`, svd/spl = 0, ShutMode 0 *después* de `0x438c82a0`: un enganche anterior se sobrescribiría |

**N — C3-B sigue válido** para 1/8000–1/30 s (V emulación + T047 en 1/4000, 1/1000, 1/250, 1/60; 1/8000 y 1/30 solo emulación),
con el punto de enganche corregido. No es una implementación: la autonomía no está demostrada físicamente.

## 7. Matriz de velocidades

Evidencia: «T046/47» = medida dentro de un cuadro con `r5` manual; «Prod» = productor nativo ejecutado (§1.2).

| Velocidad | Tiempo | Ruta candidata | Evidencia | Límite |
|---|---|---|---|---|
| 1/8000 | 125 µs | C3-B | Prod (L=8, shd 4211); sin T046/47 | cuantización de línea (−2,7 % por truncamiento); sin medida |
| 1/4000 | 250 µs | C3-B | T046/47 + Prod | integración autónoma no demostrada |
| 1/250 | 4 ms | C3-B | T046/47 + Prod | ídem |
| 1/60 | 16,7 ms | C3-B | T046/47 + Prod | ídem |
| 1/30 | 33,3 ms | C3-B | Prod (shd 2025) | falta prueba física |
| 1/15 | 66,7 ms | C (VTS 4389, shd 1, svd 0) | Prod | cuadro más largo: sumidero N; r5 manual es inválido |
| 1/8 | 125 ms | C (VTS 8225, shd 1) | Prod | ídem |
| 1/2 | 500 ms | C (svd 6, d8 7583) | Prod | `svd` físico N |
| 1 s | 1 s | C (svd 14) | Prod | ídem |
| 2 s | 2 s | C (svd 30) | Prod | ídem |
| 8 s | 8 s | C (svd 123) | Prod | ídem |
| 15 s | 15 s | C (svd 235) | Prod | ídem |
| 30 s | 30 s | C (svd 472) | Prod | ídem; 472 < 4095 (límite de 12 bit) |
| BULB | variable | D (tramos de un cuadro, `T = 0`) | estructura V | fin de integración N; `svd` máx. 4095 ⇒ ≈ 262 s por tramo, más exige re-armar |

| Velocidad | ¿Representable? | ¿Programable por el código? | ¿Secuencia de sensor identificada? | ¿Validación física? | ¿Cambia el modo de lectura? | ¿Intervención mecánica? | ¿Una integración RAW? |
|---|---|---|---|---|---|---|---|
| 1/8000 | Sí (L=8) | Sí (r5 4211) | Sí (ShutMode 0) | No | No | No (objetivo) | No medido |
| 1/4000–1/60 | Sí | Sí | Sí | **Sí** (T046/47) | No | No | **Sí** (uniforme) |
| 1/30 | Sí | Sí | Sí | No | No | No | No medido |
| 1/15–1/8 | Sí (VTS ampliado) | Sí (productor) | Parcial (ruta en SetRead, V código) | No | **Sí** (VTS por cuadro) | N | No |
| 1/2–30 s | Sí (svd ≤ 472) | Sí (productor) | Parcial (`svd` en ID3/4, I) | No | **Sí** | N | No |
| BULB | Sí en tramos (I) | Estructura sí | No (inicio/fin sin demostrar) | No | N | N | No |

Disponibles en el menú original no implica compatibles: ninguna velocidad ≥ 1/15 está validada.

## 8. Veredictos obligatorios

NO = contradicción demostrada (C), capacidad ausente en la ruta examinada (A) o evidencia insuficiente (EI).

| | Pregunta | Veredicto | Evidencia |
|---|---|---|---|
| A | ¿`svd` controla pasos sucesivos? | **SÍ**, solo con `cap+0x740 ≠ 0` | `0x43b1e842/84a/7f8`; con 740=0 el cap se anula (`0x438c83c4`) |
| B | ¿Relación `record+0x68`–`svd`–duración? | **SÍ** | §1.2: `d8 + svd·VTS = L + shd`; físico N |
| C | ¿Esos pasos mantienen una única integración electrónica? | **NO** (EI) | `Execute(0)` sin datos; sin medición |
| D | ¿Ruta específica de BULB? | **NO** (EI) | tramos con `T = 0` (V) pero sin despacho ni botón |
| E | ¿BULB usa otra secuencia de sensor? | **NO** (EI) | la variante ShutMode 1 existe (V); su uso en BULB es I |
| F | ¿Cómo inicia la integración? | **NO** (EI) | candidato: `0x438c86b0` paso 0 |
| G | ¿Cómo termina? | **NO** (EI) | sin escritura de fin (S57); `0x437f9a64`/flag `0x8000` sin efecto trazado |
| H | ¿Depende de la cortina mecánica? | **NO** (EI) | el tiempo viaja a Darwin (`0x107`); efecto N |
| I | ¿Modo de cuadro extendido utilizable? | **NO** (EI) | plan nativo `d8`/`record+0x60` (V); sumidero N |
| J | ¿Secuencia demostrable > 65 ms? | **NO** (EI) | planificada (V), no medida |
| K | ¿LongObMode controla la duración? | **NO** (A) | §4 |
| L | ¿SetReadZ en una ruta alcanzable? | **NO** (A) | `SetRead_ZAF`, sin llamador |
| M | ¿Equivalente aprovechable del A7S? | **NO** (A/EI) | §5 |
| N | ¿C3-B válido dentro de un cuadro? | **SÍ** | §6 |
| O | ¿Diseño fundamentado para 1/15–30 s? | **SÍ** (como diseño de experimento) | §1.2 y §10; no implementación |
| P | ¿Diseño fundamentado para BULB? | **NO** (EI) | falta fin/liberación |
| Q | ¿1/8000–30 s implementado en Silent? | **NO** (A) | no hay implementación; T046/T047 fueron parches RAM de prueba (1/4000–1/60) |
| R | ¿Pruebas físicas nuevas? | **NO** | — |
| S | ¿Se modificó RAM o firmware? | **NO** | — |

Nada de lo anterior afirma imposibilidad del hardware.

## 9. Límites

Tipo de captura → flujo (N); productores de `cap+0x740`, `cap+0x504`, `cap+0x4b80/4b84` y de `[settings+0x66]` (N); emisores de los flags
`0x8000/0x4000` (N); sumidero físico del VTS por cuadro (N); significado eléctrico de ShutMode/ID1/ID3–ID8 (sin datasheet, I); la
convención `svr`/`shr`/`spl` de otros sensores Sony no se usó como prueba. Cuenta `record+4` como índice de cuadro: I.
El planificador y los contadores no se emularon completos.

## 10. Experimento mínimo para la sesión siguiente (no ejecutado)

**Fase 1 — solo lectura (E25-19, reversible, sin escribir).** Reutilizar el patrón de `scripts/t052_b0_readonly.py` tras fotos **mecánicas** normales de 1/30, 1/8, 1 s,
4 s y un BULB de ~10 s, sin ningún parche, y leer `cap+0x64c..0x655`, `cap+0x650`, `cap+0x4b9c`, `cap+0x4b84`, `cap+0x72c`, `cap+0x724/0x728`,
`cap+0x740`, `cap+0x504`, `cap+0x4b80`, `cap+0x73b`, `[settings+0x66]` y `record+0x60/0x64/0x68/0xd8/0xda/0xdc/0xf0`. Requisito previo: localizar `cap`
(N desde T052-A). **Decide:** si la foto normal de 1 s usa `svd = 14` (C), o ShutMode 3 con `shd = 1` y `svd = 0` (E); y si BULB sube `cap+0x72c`.

**Fase 2 — solo con autorización expresa (RAM).** Sobre el sitio T046/T047, `ShutMode 0`, `shd = 1`, `svd = 1` a una escena fija: criterio de éxito, luminancia
RAW ≈ 2× la de `svd = 0` (±10 %, misma escena y `shd` constante), exposición uniforme por filas ±5 % y ninguna lectura intermedia. Abortar con cualquier desviación,
reiniciar con apagado. Después `svd = 3` y `svd = 14`.

## 11. Entregables

- Informe: este documento. Evidencia: `analysis/e25-17/{productor,evidencia}.json`.
- Scripts: `scripts/e25_17/{fw,scan_field,xrefs,emular_productor,evidencia}.py`.
- Pruebas: `tests/test_e25_17_long_exposure.py`.
- Regenerar: `python3 scripts/e25_17/emular_productor.py && python3 scripts/e25_17/evidencia.py`.
