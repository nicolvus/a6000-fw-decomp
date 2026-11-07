# E26-R69 — Revisión de los informes del negro con EFCS activado (R56–R64) y cierre de las inferencias de R65–R68 (07-11-2026, estático)

Se revisaron R56 §8, R57, R58, R59, R60, R61, R62, R63 y R64 con lo establecido en [R65](e26-r65-darwin-efcs-on-resta-g42.md)–[R68](e26-r68-auditoria-r65-r67.md), y se intentó cerrar cada inferencia abierta con el código (`darwin_core.bin` 3.21, Capstone; `av-cam.bin`, REA) y los volcados.

## 1. Correcciones a informes anteriores (nota añadida al principio de cada uno)

| Informe | Afirmación | Estado | Motivo |
|---|---|---|---|
| R58 §13 | B = BK4 `0x30102` | **Corrige R58**: falso | B = `0x1850001` (R66) |
| R58 §3/§5 | `0x185…` = parámetros DSP | **Corrige R58**: falso | son los bloques de Darwin (R66) |
| R61 §4–5 | «`0x30102+0x88` llega a Darwin y gobierna la segunda cortina» | **Corrige R61**: anulado | `0x30102` no es B; en B, `+0x88 = −22` |
| R62 §3 | BK4 `0x30100` es la copia del estado de Darwin | **Corrige R62**: falso | la relectura va a `0x1850004/05`; coinciden 181 de 512 B (MEDIDO, 20-10 y 05-11) |
| R62 §4 | `s8[B+0xc6..c8]` = 0; `G+0x42` entra en `ip` | **Corrige R62** | valen 29/37/35; `G+0x42` solo entra en `ip` con EFCS desactivado |
| R63 §6 | prueba `0x30102+0xc6` sobre Darwin | **Corrige R63**: no tocó Darwin | íd. |
| R64 §2/§5/§6 | `t` ∈ {1, 2} (INFERENCIA fuerte); prueba A/B/C | **Corrige R64** | `t` = 0 al arrancar (R65); la prueba A/B/C no podía decidir nada sobre Darwin |

Siguen vigentes: R56 §7 (calibración electrónica), R57 §5 y §8 (negro también con Sony; pérdida medida, con la etiqueta corregida en R62 §1), R57 §12 y R58 §9 (NAND y software intactos), R60 (restar líneas a `sl` no compensa), las medidas de R62 §2 y las medidas por SWD de R63 §1–2.

## 2. Inferencias de R65–R68: resultado

| Inferencia | Resultado | Evidencia |
|---|---|---|
| B (P4E ← 1) es el instante en que se suelta la segunda cortina | **CERRADA (VERIFICADO el patrón; INFERENCIA mecánica)** | Barrido de las 147 llamadas a `0x51c0`: **P4D** (delantera) sube antes (`0x20c90` desde `0x1f694/0x1f8a2/0x1f914/0x20154`) y baja en A; es un imán de retención, que suelta al cortar. **P4E** (trasera) solo sube en B (`0x20d00`, y en `0x20d26/0x20e6e` en la rama intermedia) y baja después en un paso temporizado de la lista (`0x207be/0x207e8` → `0x20cd4`, retardo `(X+0x31 − X+0x32)·100`). P4E está a 0 antes de B, así que no retiene la cortina: el pulso de B es el que la suelta |
| La separación A–B no depende de `ip` | **CERRADA (VERIFICADO)** | `0x18d6e` llama a `0x1a738(·, ip)` en `0x18e48` y arma A y B después, con retardos calculados solo con `S+0x48` y `B+0x84..0x8a`. `ip` va a otra máquina de estados (`0x237cc`, lista propia) cuyo papel no se ha determinado (límite, no pendiente) |
| `t` sigue a 0 durante el uso | **CERRADA como INFERENCIA fuerte** (no verificable estáticamente) | Vale 0 al arrancar (zona puesta a cero). Su único escritor son las órdenes `0x62–0x65`, del grupo de órdenes `0x40–0x9f` (categoría `0x1b` de la tabla `0x2a19c`), y no se ha localizado su emisor en el BIONZ. Con `t` ∈ {1, 2}, EFCS activado iría por la rama mecánica (`T − 435`) y sobreexpondría, lo contrario de lo medido |
| El sistema de backup entrega a Darwin la propiedad del mismo ID | **CERRADA como INFERENCIA fuerte** (no trazable) | Coinciden IDs y tamaños (4 de 4). El registro pasa por servicios del sistema operativo (`FUN_435614ec` → tabla `+0x2cc`, `FUN_43561298` → `+0x1e8`) y la llamada a `0x436bc514` es indirecta |
| `0x30102` no llega a Darwin | **CERRADA con límite** | no es el bloque B; sus lectores en el BIONZ (`FUN_438d49bc/509c`) no tienen ninguna ruta conocida hacia Darwin |

## 3. Pendientes nuevos de R66–R67

* **E26-R66-B86: DESCARTADO.** Se satura (R68), y la alternativa `G+0x42` tiene lectores con efecto desconocido. Además, compensar antes de saber la causa (E26-R66-RESET) sobreexpondría a 1/125 y más lentas, donde hoy no hay pérdida.
* **E26-R67-GPIO9: FUSIONADO en E26-R66-RESET**, con el procedimiento listo (§4).
* **E26-R66-RESET: el único que queda abierto.** Exige medir en la cámara; desde el binario ya no se puede decidir nada más.

## 4. Procedimiento listo para E26-R66-RESET (solo lectura; requiere autorización)

1. Sonda SWD del BIONZ todavía soldada (antes de E26-R49-SONDA). Batería cargada; 3.37 oficial; EFCS activado; M, ISO fija, luz sin parpadeo.
2. `python analysis/e26-r59/bz_mon.py <serie> 30 f2910010:4 f2910110:4 f2910210:4 f2910310:4 f2910410:4 f2910510:4 f2910610:4 f2910710:4 …` (registro RDATA de cada banco GPIO; solo lectura de MMIO, sin halt). Disparar 3 veces a 1/1000 y 3 a 1/125; repetir con EFCS desactivado.
3. Criterio:
   * hay un bit que sube y baja en cada disparo, en los dos modos, con el pulso de P4C (de `0x16e7a` a A): **la línea llega**, y la pérdida está en el BIONZ/sensor (régimen de reinicio, R62 §2);
   * ningún bit acompaña a los disparos: **fallo físico de P4C → AA13/AD21**, posiblemente desde que se abrió la cámara (R46). Siguiente paso, continuidad CN4900 ↔ BIONZ con la cámara apagada.
4. Límite: a ~400 barridos/s la resolución es de ≈2,5 ms. Basta para ver el pulso, pero no para medir el retardo de 1,27 ms. Para medirlo hace falta un analizador lógico en P4C y `CIS0_VD`.
