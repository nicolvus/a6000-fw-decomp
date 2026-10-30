# E26-R17 — Traza del BossFirm ARM7, semántica LDEC y segmentos TPZL

Fecha: 30-10-2026. Continúa [R16](e26-r16-ldec-hardware-audit.md) (`b12d4e9f`, presente en `main`). **Solo análisis estático offline.** Sin cámara, sin USB/UART, sin NAND, sin firmware instalable. `camera-dumps` y `exp2-session-log.jsonl` no se tocaron.

Etiquetas: **BINARIO** = desensamblado de BossFirm (`bootloader.bin[0x18800:+0x3800]`, ARM de 32 bits, base 0) · **SCRIPT** = salida de [`r17_arm7_full.py`](../../analysis/e26-recovery/r17_arm7_full.py) (`r17-arm7-full.json`) · **INFERENCIA** · **NO VERIFICADO**. Pruebas: [`tests/test_e26_r17_arm7.py`](../../tests/test_e26_r17_arm7.py) (5; comprueban instrucciones, no el silicio).

## 1. Resumen ejecutivo

1. **BINARIO. Todo el BossFirm es ARM (no Thumb).** Vectores `0x00–0x3c` = `ldr pc,[pc,#…]`; despachador principal `0xec8` con `ldr r1,[sb,r0,lsl#2]` / `bx r1` (`0xf14`–`0xf1c`) sobre la tabla de **18 punteros** en `0x379c` (op 0 = `0x1338`, solicitud LDEC). Recorrido recursivo + tabla + punteros de vectores: 98 entradas de función; el flujo alcanza el 95,9 % de las palabras de la imagen (SCRIPT; cifra **optimista**: el barrido lineal no separa por completo los pools de literales incrustados).
2. **BINARIO. El ARM7 toca el LDEC en solo 3 funciones** (únicos literales `0xf2903000`: `0x3f8`, `0x440`, `0x4d8`): configuración `0x3f4`, ISR `0x43c`, arranque `0x4d8`. `0xf290300c` se **escribe una vez** (`0x428`, valor `trabajo+0xc`) y **nunca se lee ni se compara** con ningún contador en el ARM7. Su semántica depende exclusivamente del silicio.
3. **BINARIO. La ISR del LDEC (`0x43c`) no tiene código de error «longitud/segmentos» identificado**: lee estado `+0x34`, lo reconoce escribiéndolo en `+0x30` y lo traduce: `0x10→0x29`, `0x02→0x2c`, `0x04→0x2b`, `0x08→0x2a`, `0x20→0x28`, `0x40→0x2d`, otro→0 (éxito). Qué fallo físico corresponde a cada bit: NO VERIFICADO.
4. **BINARIO. Residuo (`trabajo+8`): no lo lee ninguna instrucción de la ruta op 0.** `0x1338` solo usa `[r7]` (nº de entradas) y `[r7,#4]` (lista); pasa `r7` únicamente a `0x3f4` (que lee `+0xc` y `+0x10`). Las rutinas de lote reciben entradas de 12 B `{ptr, inicio, n}`, no el trabajo. El residuo solo influye vía *sector de inicio / nº de sectores* ya calculados por Loader3. No se prueba qué hace el silicio con los primeros 256 B.
5. **BINARIO. tulist: el envolvimiento en 0x80 es síncrono.** Cada tanda pasa por `0x81c`/`0x784`/`0x8ac` → `0x5f8` (comando de lectura NAND por DMA con `0xcec`/`0xc1c`), que **espera con sondeo** el indicador `[0x378c]==1` (`0x6d4`–`0x6dc`) antes de volver. Al llegar a 0x80 `0x1130` reescribe `[r5+8]`/`[r5+0xc]` (`0x12f8`–`0x1320`) con **las mismas constantes** (`0xf0020000`, base`+0x2068`): reutiliza el mismo tulist tras el drenado de la tanda anterior. 145 = 128 + 17 usa la misma ruta que 129 = 128 + 1; no hay límite dependiente del tamaño del segundo lote.
6. **Corpus (Prioridad E): NO ejecutada.** No hubo búsqueda externa; el corpus sigue siendo el de R16 (6 imágenes, ≈ 6 200 bloques, siempre 16×4 KiB, residuo 0). Q10/Q11 = sin evidencia nueva.
7. **Decisión: C — semántica parcialmente reconstruida.** Cadena y consumidores ARM7 identificados; la parte que decide (qué hace el LDEC con 1×64 KiB, con el residuo y con `+0xc`) no es observable desde el ARM7.

## 2. Estado heredado de R16

Se mantiene todo. Correcciones a R16: (i) `0x4d8` no es «ISR»: es el **arranque** (`[LDEC+0x24]=1`, `[LDEC+4]=1`); la ISR es `0x43c`. (ii) Las rutinas `0x81c/0x784/0x8ac` sí se trazaron aquí: son envoltorios de comando NAND (§7). (iii) `0x5f8` y `0xcec` no programan el LDEC sino el controlador NAND/DMA (`0x20000`/`0xf0020000`).

## 3. Grafo de control (cada arista con su instrucción)

| De | A | Instrucción | Tipo |
|---|---|---|---|
| BIONZ/Loader3 `c01fccd2`/`c01fc4f8` | SRAM `0x3f40` (puntero al trabajo en `+0x14`) | R16 | BINARIO (Loader3) |
| `0xec8` bucle | `0x1338` (op 0) | `0xf14` `ldr r1,[sb,r0,lsl#2]`, `0xf1c` `bx r1`, tabla `0x379c` | BINARIO |
| `0x1338` | `0x3f4` configuración LDEC | `0x139c` `bl 0x3f4` | BINARIO |
| `0x1338` | `0x1130` por entrada de la lista | `0x13d0` `bl 0x1130` | BINARIO |
| `0x1130` | `0x1688` (entrada alineada) / `0x1738` (múltiplo de geometría `dev+0x18`) | `0x1280`, `0x12a8` | BINARIO |
| `0x1688`/`0x1738` | `0x81c` (cola) | `0x1734`, `0x1784` (`b 0x81c`) | BINARIO |
| `0x81c` | `0xcec`(cmd `0x47`), `0x5f8`, `0xcec`(cmd `0x42`) | `0x85c`, `0x868`, `0x878` | BINARIO |
| `0x5f8` | `0xc1c` emisión DMA y espera `[0x378c]==1` | `0x6d0`, `0x6d4`–`0x6dc` | BINARIO |
| `0x1338` (fin del bucle) | `0x4d8` arranque LDEC | `0x13f4` `bl 0x4d8` | BINARIO |
| `0x1338` | `0x4c0` espera `[0x3784]==1` (la pone `0x43c`) | `0x1400` `bl 0x4c0` | BINARIO |
| IRQ | `0x43c` (estado `+0x34`, ack `+0x30`, resultado `[0x3788]`, fin `[0x3784]=1`) | `0x450`–`0x4b8` | BINARIO |
| `0x1338` | respuesta: `[0x3f40+0x1c]` = máx(0xb-flag, resultado) | `0x13f8`, `0x1408/0x140c` | BINARIO |

Indirectos del ARM7 (SCRIPT): `bx r1` en `0xf1c` (despachador, resuelto: 18 destinos) y `mov pc,r3` en `0x144` (tabla de salto de excepción). Resto de `mov pc,lr` = retornos de la biblioteca aritmética (`0x3404…0x3764`). Orden: `0x3f4` (antes) → lotes NAND (durante la carga, síncronos) → `0x4d8` + `0x4c0` + ISR `0x43c` (descompresión) → respuesta.

## 4. Mapa de registros LDEC (`0xf2903000`)

| Registro | Escrituras | Lecturas | Valores | Interpretación demostrada | Incertidumbre |
|---|---|---|---|---|---|
| `+0x00` | `0x420` (0), `0x4b8` (1) | — | 0/1 | indicador de estado de la ISR en el mapa interno (`0x4b8` escribe en la dirección del *flag* RAM, no confirmado en LDEC) | alta |
| `+0x04` | `0x408` (1), `0x434` (0), `0x4b4` (1), `0x4e4` (1) | — | 0/1 | conmutado alrededor de la configuración y de la parada (INFERENCIA: habilitación/reset) | nombre funcional no demostrado |
| `+0x0c` | `0x428` ← `trabajo+0xc` (=16 en Sony y 3.25) | **ninguna** | 16 | recibido de Loader3 como `tam_bloque>>12`; el ARM7 no lo compara ni lo cuenta | segmentos / unidades de 4 KiB / páginas: **indeterminado** |
| `+0x10` | `0x430` ← `trabajo+0x10` | ninguna | de Loader3 | campo no identificado | alta |
| `+0x24` | `0x4e0` (1) | — | 1 | parte del arranque | alta |
| `+0x28`, `+0x2c`, `+0x30` (init) | `0x41c` (0x7b), `0x418` (4), `0x410` (0x7b) | — | 0x7b / 4 / 0x7b | constantes de configuración | alta |
| `+0x30` (ISR) | `0x454` ← estado | — | eco de `+0x34` | reconocimiento de interrupción | media |
| `+0x34` | — | `0x450` | bits 0x02/04/08/10/20/40 | estado de error → códigos `0x28–0x2d` (§1.3) | significado físico de cada bit: NO VERIFICADO |

No se asigna nombre funcional a ningún registro; «+0xc = nº de segmentos» (R16 §10) pasa a **hipótesis sin respaldo en el ARM7**.

## 5. Semántica de `+0x0c` (Q5–Q7)

Ninguna comparación del ARM7 usa `+0xc`. No hay lectura posterior, ni contador de terminadores, ni código de error de longitud nombrado. Por tanto: *«¿espera dieciséis terminadores o solo debe producir 16 unidades de 4 KiB?»* **no es decidible desde el ARM7**; depende del silicio. No existe condición demostrada que rechace un segmento de 64 KiB. Una lectura posible (INFERENCIA, no demostrada): `0x10` en estado ↔ un fallo de longitud/fin de flujo, pero no hay prueba.

## 6. Residuo de 256 B (Q3–Q4)

Métodos: recorrido de `0x1338` y de `0x3f4` (único receptor del trabajo), comprobación de que `0x1130`/`0x1688`/`0x1738`/`0x81c`/`0x784`/`0x8ac` reciben entradas `{ptr,inicio,n}` (prueba `test_op0_never_reads_job_plus8`), y búsqueda de literales del buzón (`0x3f50`: 11 sitios, todos en otras operaciones del despachador). **Ningún lector de `trabajo+8`.** El comienzo exacto del flujo llega al LDEC como el sector de inicio `off>>9` (R16) más lo que haga el hardware con los primeros `res` bytes: NO VERIFICADO. Accesos indirectos no resueltos: el trabajo se copia entero (`0x18` B) en SRAM y una lectura por DMA o por el LDEC no aparecería como `ldr`. No se afirma que el hardware ignore el residuo.

## 7. tulist y envolvimiento (Q8–Q9)

`0x1130` limita cada tanda a 0x80 entradas (`cmp r0,#0x80`, `0x1168`); al llenar reinicia el contador y reescribe `[r5+8]=0xf0020000`, `[r5+0xc]=[0x3f50]+0x2068` (`0x12f8`–`0x1320`) y sigue con el resto (`r4`). La ejecución de cada tanda (`0x81c`→`0x5f8`) es **bloqueante** hasta que el flag `[0x378c]` lo ponga la ISR del controlador NAND (`0xd24`, `0xd30`). Luego la reutilización del tulist no solapa con el hardware. La operación de 145 sectores = 2 tandas (128 + 17); no se encontró ninguna condición que dependa del tamaño de la segunda. **Límite:** esto es la ruta de lectura NAND; si el LDEC lee el mismo buffer concurrentemente (el arranque `0x4d8` ocurre tras todas las tandas) no se ha trazado.

## 8. Comparación 16×4 KiB frente a 1×64 KiB

Datos de R16 (`r16-lz-features.json`). Sin restricción del descompresor demostrada: ni el ARM7 ni la ISR distinguen segmentos. Una propiedad que explicaría la convención de Sony es la **resincronización**: 16 terminadores de 4 KiB permiten reanudar la descompresión por segmento (acceso aleatorio y límite de ventana LZ de 4 KiB). Es una INFERENCIA sobre el empaquetador, no una restricción demostrada. Un segmento de 64 KiB válido para `fwtool`/Loader3 no prueba nada sobre el LDEC.

## 9. Propagación del error (Prioridad G)

Del ARM7: ISR `0x43c` → códigos `0x28–0x2d` → `[0x3788]` → `[0x3f40+0x1c]` (con `0xd→0xc`) → MuMin → Loader3 `c01fcf70` (máscara `0x3000000`; −0x20005/−0x20006) → `c01fe006`/`c01fe118` (4 intentos) → `c01f2c2a` → `c01f4690` (todo ≠ 0 → −302). La correspondencia exacta código ARM7 → −0x2000x no se trazó (NO VERIFICADO). Se mantienen abiertas H1 (BOS), H2 (Backup) y la de escritura incompleta; **no se atribuye el bloqueo al LDEC.**

## 10. Pruebas

`tests/test_e26_r17_arm7.py`: 5 pasan (despachador, 3 sitios de la base LDEC, escritura única de `+0xc`, ausencia de lector de `trabajo+8` en op 0, mapa de la ISR). Ruff y mypy sin avisos en los archivos nuevos. Estas pruebas verifican instrucciones, **no** el comportamiento físico.

## 11. Matriz de evidencia

| Afirmación | Evidencia | Nivel |
|---|---|---|
| ARM7 = ARM, 18 ops, op 0 = `0x1338` | `0xf14`–`0xf1c`, tabla `0x379c` | BINARIO |
| `+0xc` solo escrito | 3 sitios LDEC, 0 lecturas | BINARIO |
| Semántica de `+0xc` | — | NO VERIFICADO |
| Residuo no leído en op 0 | prueba de `0x1338`/`0x3f4` | BINARIO (con límite indirecto) |
| Tulist síncrono por tanda | `0x6d4`–`0x6dc` | BINARIO |
| 145 sectores sin límite propio | misma ruta que 129 | BINARIO + INFERENCIA |
| TPZL 1×64 KiB auténtico | no se buscó | sin evidencia |

## 12. Límites

No se ejecutó la ampliación del corpus Sony (Prioridad E): sin búsqueda externa. Cobertura del ARM7: flujo alcanzable, no emulación; no se resolvió el uso de `0x1aa4/0x1ae4` (geometría), ni se emuló ISR/DMA. No se trazó LDEC↔buffer concurrente ni la correspondencia exacta código→−0x2000x. Tests de conocimiento: ver §15.

## 13. Preguntas de cierre

**Q1.** Flujo de control del ARM7: SÍ para la ruta op 0; cobertura del 95,9 % (optimista). **Q2.** SÍ para el despachador y las llamadas de la ruta LDEC; no se resolvieron todos los punteros de las otras 17 operaciones. **Q3.** NO. **Q4.** PARCIAL: llega el sector de inicio; el desplazamiento en bytes, no demostrado. **Q5.** NO: solo se sabe que se escribe desde `trabajo+0xc` sin lectura. **Q6.** NO demostrado. **Q7.** NO. **Q8.** SÍ (tanda síncrona, reutilización tras drenado). **Q9.** NO hay límite demostrado. **Q10/Q11.** Sin evidencia nueva (no se buscó). **Q12.** Cadena ARM7 → estado `0x28–0x2d` identificada; sin nueva explicación de −302. **Q13.** A favor de H3 se mantiene solo la diferencia de segmentos; en contra se debilita el argumento ARM7 («no hay comparación»). **Q14.** Corpus Sony externo; emulación de `0x3f4/0x43c`.

## 14. Decisión

**C — semántica parcialmente reconstruida.** Recomendación para R18: ejecutar la Prioridad E (búsqueda documental pública de TPZL con 1 segmento o residuo ≠ 0) y trazar `0xd24`, `0x1aa4/0x1ae4` y las demás operaciones del despachador.

## 15. Validación

`tests/knowledge`: 79/79 pasan (tras `extend_triage.py`, que añadió las filas nuevas de OPEN-QUESTIONS a `triage.json`). Reindexado con el procedimiento `knowledge-maintenance` (`index_docs`→`build_graph`→`export_corrections`→ídem; grafo estable 1461/3255). Tests R14–R17 y Ruff/mypy: ver resultado del commit.
