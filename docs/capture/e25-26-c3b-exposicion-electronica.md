# E25-26 — C3-B: exposición electrónica condicionada a la modalidad

28-10-2026. Implementación offline de C3-B sobre el selector de [E25-24b](e25-24b-implementacion-selector.md).
Sin cámara, sin RAM/NVRAM/firmware, sin paquete instalable. Emulación Unicorn del
`StartExposure` real (`0x438c828c–0x438c83e8`) con la imagen combinada.

Base: `e65da7ba` + reubicación de cuevas de [E25-25](e25-25-validacion-carga-caves.md).

---

## 1. Punto de enganche y cueva

| Elemento | Valor |
|---|---|
| Enganche | `0x438c82fe` — `bl 0x436d6118` (obtener el imager), antes de `SetExposure` (`0x438c830c`) |
| Paso | solo 0: `0x438c82d8 cbnz [cap+0x4b9c]` salta a `0x438c833a` |
| Cueva | `0x43541840`, 58 B, zona reservada de cabecera (E25-25) |
| Condición | `cap+0x41c == 1` (Electronic) ∧ `r7 = svd nativo ≤ 1` ∧ VTS ≠ 0 ∧ (`shd > VTS` si `svd=1`) ∧ `shd' < VTS` |
| Escrituras | `cap+0x64c` (shd), `cap+0x650` (svd), `cap+0x655` (ShutMode) |
| No escribe | `cap+0x41c`, `cap+0x4b9c`, `cap+0x12f8`, `record`, Darwin, GPIO |

Bytes:

```
438c82fe  79 f4 9f fa   bl 0x43541840        (antes: 0d f6 0b ff  bl 0x436d6118)

43541840  02 b5            push {r1, lr}          ; conserva alineación y r0
43541842  d4 f8 1c 14      ldr.w r1,[r4,#0x41c]   ; modalidad por captura
43541846  01 29            cmp r1,#1
43541848  14 d1            bne 0x43541874         ; EFCS -> original
4354184a  01 2f            cmp r7,#1              ; svd nativo
4354184c  12 d8            bhi 0x43541874         ; svd>1 -> no tocar largas
4354184e  b4 f8 e0 25      ldrh.w r2,[r4,#0x5e0]  ; VTS de la captura
43541852  7a b1            cbz r2,0x43541874      ; VTS 0 -> fallo seguro
43541854  d4 f8 4c 36      ldr.w r3,[r4,#0x64c]   ; shd nativo
43541858  01 2f            cmp r7,#1
4354185a  02 d1            bne 0x43541862
4354185c  93 42            cmp r3,r2
4354185e  09 d9            bls 0x43541874         ; shd<=VTS -> no restar
43541860  9b 1a            subs r3,r3,r2
43541862  93 42            cmp r3,r2              ; shd' debe quedar < VTS
43541864  06 d2            bhs 0x43541874
43541866  c4 f8 4c 36      str.w r3,[r4,#0x64c]   ; shd' = VTS - líneas
4354186a  00 23            movs r3,#0
4354186c  84 f8 55 36      strb.w r3,[r4,#0x655]  ; ShutMode = 0
43541870  a4 f8 50 36      strh.w r3,[r4,#0x650]  ; svd = 0
43541874  94 f1 50 fc      bl 0x436d6118          ; llamada original
43541878  02 bd            pop {r1, pc}
```

`r0` (retorno del imager), `r4`, `r6` y `r7` se conservan; `r1`–`r3` son muertos en el
llamador (`0x438c8302` recarga `r1`; `0x438c8308` recarga `r2`). `push {r1,lr}` mantiene la
alineación de 8 B de la llamada original.

## 2. Por qué no se reejecuta `0x4383fa40`

El plan nativo ya está calculado y copiado a `cap+0x64c` por
`0x437f8a50 → 0x4383fd6c`. Volver a ejecutar el productor exigiría un `record` scratch y un
`imager`; la cueva no los tiene. Se **consume su salida** y solo se deshace el cuadro extra
del predicado (`shd −= VTS`, `svd −= 1`) y se fuerza `ShutMode 0`. El VTS se lee de
`cap+0x5e0` (misma fuente que `record+0x20`), no se fija a 4219.

## 3. Comportamiento por modalidad

### EFCS (`cap+0x41c = 0`)

La cueva sale en la primera comparación. Sony conserva `shd`, `svd`, `ShutMode`, la segunda
cortina y el orden `StartExposure → SetExposure → SetRead → Execute`. La emulación compara
con el firmware original: **idéntico** en los 4 casos probados (con y sin `cap+0x504`).

### Electronic (`cap+0x41c = 1`)

Plan nativo de 1/4000 (predicado 1): `shd=8422`, `svd=1`, `ShutMode=3`.
Resultado: `SetExposure(shd=4203, svd=0, ShutMode=0)`. Exposición modelo:
`(4219 − 4203) × 3891/256 = 243,2 µs` (−2,72 % del nominal, por cuantización de línea).

`cap+0x650` vuelve a `1` al salir (`0x438c8334` restaura `r7`): el contador del host sigue
viendo el plan nativo. `cap+0x655` queda en 0.

## 4. Emulación end-to-end (casos A–D)

`scripts/e25_26/emu.py` ejecuta el tramo real con stubs de `SetExposure`, `SetRead`, `SSB`,
`Execute`, imager y `0x437f8a50`. Resultados (`analysis/e25-26/evidence.json`):

| Caso | Original (shd/svd/ShutMode) | Combinado | ¿Igual? |
|---|---|---|---|
| EFCS, predicado 1, `cap+0x504=0` | 8422 / 1 / 3 | 8422 / 1 / 3 | sí |
| EFCS, predicado 1, `cap+0x504=1` | 8422 / 0 / 3 | 8422 / 0 / 3 | sí |
| EFCS, predicado 0 | 4203 / 0 / 3 | 4203 / 0 / 3 | sí |
| Electronic, predicado 1 | 8422 / 1 / 3 | **4203 / 0 / 0** | cambio previsto |
| Electronic, predicado 0 | 4203 / 0 / 3 | **4203 / 0 / 0** | cambio previsto |
| Electronic, larga (`svd=2`) | 1 / 2 / 3 | 1 / 2 / 3 | sí (inhibida) |
| Bloque forzado (`0x43a12c64=2`) | 2 / 0 / 0 | 2 / 0 / 0 | sí |
| Modalidad inválida (`0x41c=2`) | 8422 / 1 / 3 | 8422 / 1 / 3 | sí |
| VTS 0 | 8422 / 1 / 3 | 8422 / 1 / 3 | sí |
| `shd ≤ VTS` | 100 / 1 / 3 | 100 / 1 / 3 | sí |

Alternancia `EFCS → Electronic → EFCS → Electronic`:

```
8422/1/3 → 4203/0/0 → 8422/1/3 → 4203/0/0
```

Sin residuo de la captura anterior (cada caso usa un `cap` nuevo; la modalidad se congela).

## 5. Velocidades modeladas

Productor real (`0x4383fa40`, predicado 1, VTS 4219, período 3891 Q8) y normalización C3-B:

| Velocidad | Tv | Nativo shd/svd | C3-B shd/svd | Exposición | Error |
|---|---:|---:|---:|---:|---:|
| 1/8000 | `0x1cf7` | 8430 / 1 | 4211 / 0 | 121,6 µs | −2,72 % |
| 1/4000 | `0x1bf7` | 8422 / 1 | 4203 / 0 | 243,2 µs | −2,72 % |
| 1/1000 | `0x19f7` | 8373 / 1 | 4154 / 0 | 987,9 µs | −1,21 % |
| 1/250 | `0x17f7` | 8175 / 1 | 3956 / 0 | 3997,4 µs | −0,07 % |
| 1/125 | `0x16f7` | 7912 / 1 | 3693 / 0 | 7994,8 µs | −0,07 % |
| 1/60 | `0x15e8` | 7341 / 1 | 3122 / 0 | 16 673,5 µs | +0,04 % |
| 1/30 | `0x14e8` | 6244 / 1 | 2025 / 0 | 33 347,1 µs | +0,04 % |

La emulación reprodujo `shd/svd/ShutMode` de las siete filas. Son objetivos de análisis, **no
velocidades certificadas**. ≥ 1/15 s queda fuera: la cueva se inhibe (`svd > 1`) y la ruta
larga sigue pendiente (VTS dinámico, multicuadro, `record` coherente: E25-20).

## 6. Integración con B1a / Darwin

| | EFCS | Electronic |
|---|---|---|
| `pkt[0x0e]` | 0 | 1 |
| Darwin `0x20c74` / `0x1fe66` | originales (3 / 4) | 0 / 0 |
| C3-B | no actúa | normaliza y `ShutMode 0` |
| Segunda cortina | ruta Sony | suprimida por Darwin |

C3-B no cambia la modalidad ni Darwin la infiere de `ShutMode`: la fuente sigue siendo el
selector (`cap+0x41c`). El orden es `selector → cap → pkt → Darwin` y, en paralelo,
`cap+0x64c → C3-B → SetExposure`.

## 7. Limitaciones y riesgos

1. **`cap+0x73b`**: `0x43b1e520` lo calcula **antes** del enganche con el `ShutMode` nativo
   (3). La emulación lo confirma; no se corrige porque E25-18 verificó que adelantar el
   enganche altera la condición de Sony. Es un riesgo residual para la capa inferior.
2. **`cap+0x650` se restaura** a `r7` en `0x438c8334`; el host ve el plan nativo. Es lo
   deseado para no cambiar el contador, pero significa que el `svd=0` solo existe durante
   `SetExposure`.
3. **Ruta larga**: no implementada; `svd > 1` se inhibe. El incidente de 30 s (E25-23) sigue
   abierto y no se usa como límite físico.
4. **Vídeo / Live View**: no se modelan. La condición de paso 0 y modalidad 1 debería
   aislarlos, pero no está demostrado; la prueba física debe cubrirlos.
5. **Sensor**: no se modela el IMX210; la emulación prueba aritmética y flujo, no integración
   ni uniformidad.
6. **Instalación**: la zona de cueva es apta offline pero el cargador no está demostrado
   (E25-25); la recuperación de Darwin sigue sin demostrarse (E24-04).

## 8. Reversión y reproducción

```bash
python3 scripts/e25_26/build_evidence.py
pytest -q tests/test_e25_26_c3b.py
```

`patch_c3b.restore_bytes()` + `patch_bionz.restore_bytes()` devuelven el `av-cam.bin` original
(SHA-256 `b60c845c…`). El manifiesto incluye los 89 bytes del diff (28 del selector + 61 de C3-B) y las
regiones protegidas.

## 9. Estado

**IMPLEMENTADO Y VERIFICADO EN EMULACIÓN (offline).** EFCS intacto, Electronic normalizado en
las siete velocidades rápidas, errores y alternancia cubiertos. **No instalado, no probado en
cámara.** La validación física es E25-27 y requiere autorización separada.
