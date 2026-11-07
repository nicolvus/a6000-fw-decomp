# E26-R74 — Conclusión final: por qué con EFCS activado las fotos a 1/1000 y más rápidas salen negras (07-11-2026, estático)

> **Corregido por [R75](e26-r75-verificacion-r74-y-darwin-b-a.md):** (1) son 14 las lecturas de `0x30097+0x15` (todas lecturas); (2) la clase 3 fija con EFCS tiene tres vías posibles, no solo `cap+0x41c ≠ 1` (§2); (3) la lectura de §4 «transitorio ligado al evento A» no se sostiene: la pérdida es igual de bien función de `B − t0 = máx(B − A, 0)` y no cambia al mover A 2 ms en la rama corta; la variable es el retardo de B desde el armado. La causa física (§1) sigue vigente.

Cierra la investigación de R56–R73. REA (`av-cam.bin` 3.21, Ghidra con 1 h por llamada), Capstone sobre `av-cam.bin` y `darwin_core.bin` 3.21, los 28 `backup_flash.bin` y las medidas de R57, R62 y R71. Sin cámara.
Prueba: `tests/test_e26_r74_efcs_bionz.py`.

Etiquetas: **VERIFICADO** · **MEDIDO** · **INFERENCIA**.

## 1. Conclusión

**La causa no está en el firmware ni en los datos de la cámara. Está en el hardware: cómo responde el obturador, o su circuito, a la secuencia de eventos A y B de Darwin.** Confianza:

* **alta** en que no es firmware ni datos, por los §2 y §3;
* **media** en que es hardware, porque es lo único que queda;
* **baja** en qué pieza concreta falla (§5).

Las fotos salen negras porque, con EFCS activado, la exposición real es ≈ T − 1,25 ms para todas las velocidades de 1/300 y más rápidas. A 1/1000 (1 ms) la exposición es ≤ 0.

## 2. BIONZ: el plan del sensor en el EFCS oficial no depende de T (VERIFICADO)

* **El planificador EFCS `0x43841070` solo se ejecuta si `[0x30097+0]` o `[0x30097+0x15]` ≠ 0.** `pcVar22` = GOT `0x4402059c` → `0x43f72b62` = imagen RAM de la propiedad **BK4 `0x30097`** (índice 39 de `0x43ff3200`/`0x43ff2fac`). Valores medidos: `+0 = 1`, `+0x15 = 0`, iguales en los 27 volcados legibles (20-10 → 05-11).
* **Con `+0x15 = 0` (firmware oficial) el registro de exposición no pasa por `0x4383fa40`.** `0x438417b6`: `ldrb r2,[r0,#0x15]; cmp r2,#1; bne` → `0x438417c6`: `record+0x64` (`sl`, la línea de reinicio) = `record+0x1c`, con `+0x68 = +0x6a = 0`.
  * `record+0x1c` es la geometría del modo del sensor (`cap+0x5dc`, igual en toda A6000, R57 §11).
  * `record+0x6d` (modo de obturador del sensor) = la clase global `0x43eedecc`.
  * **Nada de esto depende de T.**
  * `0x4383fa40`, con su umbral `max([rec+0x1c] + sb, VTS)`, solo entra en el modo electrónico de nuestros parches (`+0x15 = 1`, E25-16).
* **Clase de exposición** (`0x43842158` → `0x43eefb7c` → copia en `0x43eedecc`):
  * con `cap+0x41c == 1`, la clase es 3 si `Tv ≤ u16[BK4 0x3012b + 0] = 0x1760` (≈ 1/166 s ≈ 6,0 ms) y 1 si es más rápido;
  * con otro valor de `cap+0x41c`, siempre 3;
  * la rama mecánica (`cap+0x4bc & 0xe0 ≠ 0`) da 1, o 5 si `0x30087+0xb0 ≠ 0` (vale 0).

  El umbral de 6 ms cae justo en el cambio de régimen medido (5→8 ms), **pero no actúa en EFCS**. El paquete `0x0c` leído por SWD con EFCS activado da `pkt[1] = 0x02` **a 1/500 y a 1/125** (R58, `20261105-bionz-swd-disparos/`), y `0x02` solo sale con la clase 3 (`0x43841366…`: la clase 1 da `0x00`/`0x40`). Por tanto, en EFCS `cap+0x41c ≠ 1` y la clase es 3 a cualquier T. **Es una coincidencia, descartada como causa.**
* Tampoco dependen de T ni de la unidad `0x30087` (va a StillInfo, R73), los ganchos de depuración (R73) ni `0x30100`/`0x30102` (R66/R69).

**Corrige:** R62 §2, R66 §3 y R73 §4, que proponían `0x4383fa40` como el umbral de régimen o como quien gobierna el reinicio en EFCS (no se ejecuta en el oficial), y R58 §12, que proponía un parche sobre `sb` (en el EFCS oficial `sb` no se usa).

## 3. Darwin: la única dependencia de T es la separación continua entre A y B (VERIFICADO)

* `0x18d6e`: `S+0x48 = T − u16[G+0x42]` (3407).
  * Rama corta (`S+0x48 < −150`, T < 3,26 ms): A retrasado y B inmediato, `B − A = T − 3401`.
  * Rama intermedia: `0x20544`.
  * Rama larga (T > 3,46 ms): A inmediato y B retrasado, `B − A = T − 3428`.
  * Los otros umbrales de la función (`S+0x32 < 0x1400`, ≈ 1/16 s; 50 000 / 250 000 / 25 000 µs) solo afectan a exposiciones largas.
* G y B (`0x1850000/01`) no han cambiado desde el 20-10 (R66), y el código de Darwin es idéntico al original (R58).
* Imanes: `0x20c74()` = `([0x200002c0] ≠ 0 ? [0x20000050] & 7 : 0)` → {0, 1, 2, 3}.
  * Con 1/2: P4D se activa en la preparación (`0x20c90`) y se suelta en A (`0x20cb2`).
  * Con 3: P4D no se toca.
  * Con ≠ 0: B pulsa P4E (`0x20d00`, y `0x20cd4` lo baja).
  * Con 0, B no movería la segunda cortina. R71 midió que el fin de la exposición sigue a B, así que hoy vale ≠ 0.
  * El valor lo pone el cargador `0x0000–0x41ff` (R72) y **no se puede leer en estático**. Cambiar entre 1/2 y 3 solo cambia si P4D se mueve; no introduce ningún desfase de tiempo en el código.

## 4. Lo medido solo encaja con una respuesta física a la secuencia A/B (MEDIDO + INFERENCIA)

Pérdida de R62 §2 (`δ` normalizada con k = 1,058) y pérdida bruta (`δ_bruta = T − k·(T − δ)`), frente a la separación que impone Darwin:

| T (ms) | `B − A` (ms) | δ normalizada | δ bruta |
|---|---|---|---|
| 1,33 | −2,07 | 1,24 | 1,23 |
| 2,00 | −1,40 | 1,32 | 1,28 |
| 2,86 | −0,54 | 1,30 | 1,21 |
| 4,00 | +0,57 | 1,29 | 1,13 |
| 5,00 | +1,57 | 1,04 | 0,81 |
| 8,00 | +4,57 | 0,17 | −0,28 |
| 11,1 | +7,67 | 0,16 | −0,47 |

* La pérdida es **constante (≈ 1,25 ms) mientras B ocurre antes de A**. Después **decrece unos 0,35 ms por cada ms que B se aleja de A**, hasta anularse hacia `B − A` ≈ 4–5 ms. El gradiente vertical (1,1 → 1,6 ms) desaparece con ella (R62 §2: ≈ 0 por franjas a 8 ms).
* En el código, Darwin y el BIONZ producen una exposición `T − constante` en todas las ramas (§2, §3). Un desfase fijo o una diferencia fija de velocidad de barrido darían la misma pérdida a 4 y a 8 ms (las dos son rama larga). **Lo que cambia la pérdida es lo cerca que ocurre B de A**, y esa dependencia no existe en ninguna ruta de código.
* R71 confirma que el BIONZ arranca la lectura un tiempo fijo después de B (Δ 4,2 ± 0,5 ms frente a 4,57) y que hace lo mismo con EFCS activado y desactivado.
* **Lectura (INFERENCIA):** cuando el pulso de la segunda cortina (B, P4E) cae antes del evento A o en los ≈ 4 ms siguientes, la cortina llega antes de lo previsto (≈ 1,25 ms arriba y ≈ 1,6 ms abajo), o el reinicio electrónico arranca más tarde. Pasados ≈ 4–5 ms, todo vuelve a lo nominal. Es la firma de un **transitorio físico ligado al evento A**, el instante en que Darwin baja P4C y, si el tipo es 1/2, suelta el imán P4D. Candidatos:
  * caída de tensión o acoplamiento entre los imanes del obturador;
  * una cortina con la dinámica alterada (muelle, enganche);
  * un fallo en la línea P4C o en los cables de la sonda SWD que siguen soldados desde el 03-11.

## 5. Lo descartado y lo que queda sin decidir

| Hipótesis | Estado | Evidencia |
|---|---|---|
| Firmware de Sony (BIONZ o Darwin) | **Descartada** | 3.37 oficial; código EFCS sin dependencia de T (§2–§3); Darwin idéntico byte a byte (R58) |
| Datos NVRAM (G, B, `0x30087`, `0x30097`, `0x3012b`, `0x30100/02`) | **Descartada** | Sin cambios en 27–28 volcados desde el 20-10; ninguno introduce dependencia de T en EFCS |
| Umbral `0x4383fa40` (R62) | **Descartada** | No se ejecuta en el EFCS oficial (§2) |
| Umbral de clase 6 ms (`0x3012b`) | **Descartada** | Clase 3 a 1/500 y 1/125 (`pkt[1] = 0x02`) |
| Nuestros parches | **Descartada** | Ocurre con el 3.37 oficial (R57) |
| Que la línea P4C no llegue | **Poco probable** | Señales del mecanismo en todos los disparos (R71), aunque P4C no se identificó |
| Tipo de mecanismo `[0x20000050]` | **Sin decidir** | Solo con el SWD de Darwin; aun así no explicaría la dependencia de §4 |
| Pieza física concreta | **Sin decidir** | Necesita pruebas físicas (§6) |

Límite de la premisa: «EFCS funcionaba» es un testimonio del usuario. No hay ninguna foto con EFCS activado a ≥ 1/1000 y firmware original anterior a T024 (R62 §1). El fallo pudo existir antes del 20-10. Además del montaje de la sonda (03-11), hay otro momento posible de daño: **el atasco del obturador del 20-10** tras la prueba de `CameraSequence`, cuando la cámara no arrancaba con objetivo y el obturador no reabría; se recuperó restaurando la NVRAM. La conclusión (hardware) no cambia, pero no se puede fechar el daño.

### Ajuste independiente (agente paralelo, sobre R57 §8)

* Una pérdida que se anula encaja 3 veces mejor (rmse 0,015) que una constante (0,046): 1,26 ms hasta T ≈ 4,3 ms y ≈ 0 entre ≈ 6 y 8 ms.
* En función de `B − A`: 1,26 ms constante hasta `B − A` ≤ +0,6 ms (incluida la rama corta), 1,0 ms a +1,57 y 0 a +4,57 ms. Gradiente vertical de 0,5 ms (la cortina, un 15 % más rápida que el barrido de reinicio).
* Coincide con §4.
* 1/250, 1/200 y 1/125 están en la misma rama larga de Darwin, así que **una causa mecánica simple (cortina más rápida o retardo fijo de imán) no basta**: hace falta algo que dependa de lo cerca que cae B de A.
* **Hipótesis «el BIONZ programa el reinicio con `0x4383fa40` y solo coincide con Darwin si `B − A` es grande»: DESCARTADA (VERIFICADO).**
  * `0x4383fa40` no se ejecuta en el EFCS oficial (§2).
  * Ninguna de las 13 referencias a `0x30097+0x15` escribe (todas son `ldrb`, REA xrefs + Capstone).
  * La imagen RAM la rellena el sistema de backup desde la NVRAM, donde vale 0 en los 27 volcados, tomados con EFCS activado y desactivado.
  * Por tanto el BIONZ no puede producir la dependencia `B − A` a través del plan de reinicio.

### Qué es VERIFICADO y qué solo se decide midiendo

| Afirmación | Estado |
|---|---|
| El plan del sensor EFCS (`sl`, modo de obturador) no depende de T | **VERIFICADO** (bytes, REA, NVRAM) |
| Clase 3 fija con EFCS | **VERIFICADO** (código + `pkt[1] = 0x02` medido a 1/500 y 1/125) |
| Darwin: `B − A` continuo y datos sin cambios | **VERIFICADO** |
| La pérdida sigue a `B − A` | **MEDIDO** (R62 §2) + ajuste |
| Valor del tipo de mecanismo `[0x20000050]` | **Solo midiendo** (SWD de Darwin) |
| Pieza física (cortina, imán, alimentación, cables SWD, flex) | **Solo midiendo** (§6.1) |
| Cuándo apareció el fallo (20-10 o 03-11) | **No decidible** (no hay fotos de referencia) |

## 6. Recomendaciones

1. **Pruebas físicas, de la más barata a la más cara.** Tras cada una, repetir 1/1000 y 1/250 con EFCS activado.
   1. Desconectar la sonda del USB y retirar los cables soldados (E26-R49-SONDA).
   2. Reasentar el flex del obturador (CN4900) y comprobar la continuidad de P4C y P4E.
   3. Batería original cargada frente a adaptador de CA, en frío y en caliente (R58 §6).
   4. Si persiste, revisar o sustituir la unidad del obturador.
2. **Compensación en NVRAM (opcional; necesita autorización y copia previa).**
   * Cambio: `0x1850001+0x86` (s16) de 6 a **1256** (+1250), con `scripts/e26_r61/bk4_variante.py ENTRADA SALIDA 0x1850001 0x86 1250` y restauración por `senser_backup_restore.py`.
   * Efecto: adelanta A en la rama corta. Corrige por completo T ≤ 2,15 ms (1/500 y más rápido, **incluye 1/1000**). Entre 2,15 y 3,26 ms la exposición se queda en ≈ 2,15 ms (−14 % a 1/400, −31 % a 1/320). No toca 1/250 ni velocidades más lentas.
   * Riesgo bajo: `B+0x86` solo se lee en `0x18d6e`.
   * Alternativa más completa pero con más efectos: `0x1850000+0x42` (G42) de 3407 a 2157. Corrige todas las ramas rápidas, pero sobreexpone ≈ +1,25 ms a 1/125 y más lentas (+0,25 EV a 1/125) y alarga 1,25 ms los plazos de `0x182d8` (R70 §4).
   * Ninguna compensación arregla la causa: si el transitorio cambia con la temperatura o la batería, el ajuste se desplaza.
3. **Uso práctico mientras tanto:** EFCS desactivado a partir de 1/500, o el modo electrónico del 3.35 (R56).

## 7. Estado de los pendientes del problema

* **E26-R66-RESET: CERRADO (sustituido).** Lo que preguntaba (si la pérdida viene del BIONZ o del sensor) queda respondido en estático: el BIONZ no introduce dependencia de T, y la pérdida sigue a `B − A`. Lo que queda es físico: **E26-R74-FISICO**.
* **E26-R72-DARWIN-CFG:** sigue NO_VERIFICADO (solo con SWD de Darwin). Ya no bloquea la conclusión.
* **Nuevos:** E26-R74-FISICO (§6.1) y E26-R74-COMP (§6.2, opcional, con autorización).
