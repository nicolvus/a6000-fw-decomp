# S346 — el array `.bss` `0x43e906f4` no tiene escritor estático

22-10-2026. Carril B. Sesión S346. **Solo lectura estática; sin firmware en ejecución, sin cámara, sin flasheo.**

## Pregunta

El consumidor B de S342 (`0x43705748`) recorre 69 dwords en `0x43e906f4`, un puntero de la GOT. Ese array está en `.bss` (cero en la imagen). ¿Quién lo escribe?

## Veredicto

| Afirmación | Clasificación | Evidencia |
|---|---|---|
| El array está a cero en la imagen y su dirección aparece **una sola vez** en el blob: el slot GOT `0x44026240` | **VERIFICADO** | 1 ocurrencia del literal; 0x114 bytes a cero |
| El slot sólo se referencia desde **dos** sitios: `0x43705716` y `0x4370575e` (offset `0x1d00` sobre `0x44024540`) | **VERIFICADO** | ambos son los consumidores de S342 |
| No hay ninguna base PIC que apunte al array | **VERIFICADO (negativo acotado)** | 0 sitios |
| Los dos sitios **pasan la dirección** a *thunks* que despachan por la vtable `[global+0x14] + 0x2c8 / +0x2cc` | **VERIFICADO** | `0x4355f790` → `+0x2c8`; `0x4355f7ac` → `+0x2cc` |
| No hay escritor estático del array | **VERIFICADO (negativo acotado)** | 0 literales fuera del slot, 0 bases PIC, 2 referencias |
| La A6000 repite el patrón (`0x44020730` → `0x43e8197c`, offset `0x184c`, mismas dos referencias) | **VERIFICADO** | barrido de literales |
| Quién rellena el array | **NO_VERIFICADO** | lo hace el servicio de la vtable, no estático |

**S51 no cambia (A = NO, B = NO, C = NO).**

## Detalle

```
44026240   f406e943    ; slot GOT -> 0x43e906f4 (.bss, cero en la imagen)

43705716   ldr r3, [pc, #0x2c]   ; literal 0x00001d00
43705718   ldr r0, [r5, r3]      ; *(0x44024540+0x1d00) = 0x43e906f4
4370571a   add.w r0, r0, r7, lsl #2   ; &array[i]  -> argumento de 0x4355f790

4370575e   ldr r3, [pc, #0x20]   ; literal 0x00001d00
43705762   ldr r0, [r5, r3]
43705766   bl #0x4355f7ac        ; registra array[i]
```

Los dos *thunks* son envoltorios de una sola llamada indirecta:

```
4355f790  ldr r3, [pc, #0x10] ; add r3, pc ; ldr r3, [r3, r2]
4355f798  ldr r3, [r3, #0x14] ; ldr.w r3, [r3, #0x2c8] ; blx r3

4355f7ac  ldr r3, [pc, #0x10] ; add r3, pc ; ldr r3, [r3, r2]
4355f7b6  ldr r3, [r3, #0x14] ; ldr.w r3, [r3, #0x2cc] ; blx r3
```

Es decir: el array se entrega como **buffer de salida** al servicio; el cuerpo que lo llena vive en la vtable de runtime y no es estático.

## Límites

- Solo lectura estática; sin runtime, cámara ni flasheo.
- Un array en `.bss` puede llenarse en runtime sin dejar rastro estático: el negativo es sobre escritores con literal/slot, no sobre el hardware.
- Los *thunks* son envoltorios; el cuerpo real está en la vtable de runtime.
- S51 (A/B/C) no cambia.

## Reproducción

```bash
.venv/bin/python analysis/s346_array_producer/build_array_producer.py
.venv/bin/python analysis/s346_array_producer/verify_array_producer.py   # 14 comprobaciones
.venv/bin/python -m unittest tests.test_s346_array_producer              # 5 tests
```

Artefactos: `analysis/s346_array_producer/array_producer.json`, `build_array_producer.py`,
`verify_array_producer.py`, `tests/test_s346_array_producer.py`.
