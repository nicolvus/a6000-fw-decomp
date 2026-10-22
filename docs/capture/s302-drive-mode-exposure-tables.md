# S302 — Tablas de drive mode / exposición: A7S (IMX235) vs A6000 (IMX210) campo a campo

> Hito **Agente B (S300+)** — Imager: estado, drive modes y gates.
> Síntesis de S124, S134, S140, S201, S202, S204.
> Análisis estático de `av-cam.bin` A6000 fw3.21 (SHA `b60c845c...56bb9`) y A7S fw3.20 (SHA `b857d338...5103e`), base `0x43541000`.

---

## Resumen ejecutivo

| Aspecto | A6000 (IMX210) | A7S (IMX235) | Clasificación |
|---|---|---|---|
| **Arquitectura de parámetros** | 6 campos fijos (`shut, svd, shd, spl, sint, gs, epdsel`) | Columnas de matriz por modo de lectura (34 modos) | **DISTINTO** |
| **Cantidad de modos** | 13 modos (IDs 0–12) | 34 modos (IDs 0–33) | **DISTINTO** |
| **Modos Silent** | **Ausentes** (`SetMode` rechaza `0x4e`/`0x4f`) | 2 modos dedicados: `0x4e` (idx 29), `0x4f` (idx 30) | **DISTINTO** |
| **Selector drive mode** | Carga columna de matriz por modo (`0x436d6570`) | Selector `0x43826d58(modo,sub,tipo)` con `tipo==2`→Silent | **DISTINTO** |
| **Registros de tiempo** | 3 registros sombra 16b: svd/shd/spl (ID3–ID8) | Columnas estáticas por modo en matriz `0x43fee598` | **DISTINTO** |
| **Fórmula svd** | `svd = n·svr_num − 1` (o `/ VdNum − 1`) | No recuperada (valores fijos por columna) | **DISTINTO** |
| **Fórmula A6000 usa `shut`** | `shut` es índice/contador (peso en fórmula) | `shut` no existe como tal; modo `0x4e`/`0x4f` implícito | **DISTINTO** |
| **Fin de integración** | Sin reescritura al terminar | Sin comando extra | **IDÉNTICO (NO_VERIFICADO)** |
| **Transporte P2S** | DFE0, mismo hardware | Mismo hardware | **IDÉNTICO** |

---

## 1. Arquitectura de parámetros de exposición

### A6000 (IMX210) — S124, S134, S140
**Bloque de 6 parámetros** emitido por `[CAMERA_MAIN_SYNC]`:
| Parámetro | Origen (offset en estado/contexto) | Tipo | Notas |
|---|---|---|---|
| `shut` | `[ctx_sync+0x1f8]` | u8 | **Índice/contador de obturación**, NO selector de mecanismo |
| `svd` | `[estado+0x28]` u16 bajo | u12 | Pasos de exposición / periodos VD (INFERENCIA) |
| `shd` | `[estado+0x24]` | u14 | Sombra / dark time |
| `spl` | `[estado+0x28]` u16 alto | u12 | Línea / readout time (empaquetado con svd) |
| `sint` | `[estado+0x2c]` | u8 | Desconocido |
| `gs` | Flag binario (1 si `svd==9`) | u8 | Centinela `svd==9` → usa `shut=1` |
| `epdsel` | (no recuperado en S134) | — | — |

**Validación** (`0x4381106c`): `svd_esperado = (svd==9 ? 1 : shut) * svr_num − 1` (o `/ VdNum − 1`). Desborda → error.

### A7S (IMX235) — S201, S202
**Matriz de 34 modos** (`0x43fee370` + valores en `0x43fee598`):
- Cada modo = una **columna completa de valores de registros** (estáticos)
- No hay fórmula aritmética visible; los valores vienen precalculados por modo
- Modos Silent: **índice 29 = `0x4e`**, **índice 30 = `0x4f`** (S201 §5, S203)
- Diferencia mínima vs modos `0x4c`/`0x4d`: solo 1 registro cada uno (`0x000c`/`0x000a`)

---

## 2. Selector de modo / Drive mode

| Campo | A6000 (IMX210) | A7S (IMX235) |
|---|---|---|
| **Función selector** | `SetMode` → `0x436d6570` carga columna de matriz `0x43fe9b74` | `0x43826d58(modo, sub, tipo)` |
| **Entradas** | `NowDrv` `[r1+0]`, `PrevDrv` `[r1+4]`, `NextDrv` `[r1+6]`, `shut` `[r1+9]` | `modo`, `sub`, `tipo` (u8/u8/u8) |
| **Lógica Silent** | **No existe**; `shut` es contador, no selector | `tipo == 2` → `sub==0` devuelve `0x4e`, `sub==1` devuelve `0x4f` |
| **Modos Silent** | **0** (rechaza `0x4e`/`0x4f` con error 2) | **2** (`0x4e` idx 29, `0x4f` idx 30) |
| **Modos no-Silent** | 13 modos totales | `sub==0`→`0x0b`, `sub==1`→`0x35`, `sub==2`→`0x17`; modo 5→`0x0c` |
| **Evidencia bytes** | `0x436d6570` carga matriz | `0x43826d58`: `cmp r2,#2`=`02 2a`; `movs r0,#0x4e`=`4e 20`; `movs r0,#0x4f`=`4f 20` |

---

## 3. Tabla de modos de lectura (comparación detallada)

| Índice | A6000 (IMX210) Modo / Valor | A7S (IMX235) Modo / Valor | Clasificación |
|---:|---|---|---|
| 0 | `0x00` (inválido) | `0x00` | — |
| 1 | `0x01` | `0x01` | — |
| ... | ... | ... | — |
| 12 | `0x0c` (modo 5) | `0x0c` (modo 5) | IDÉNTICO |
| 13 | `0x0b` | `0x0b` (sub 0 no-Silent) | IDÉNTICO |
| ... | ... | ... | — |
| 29 | **Ausente** (error 2) | **`0x4e` Silent sub 0** | **AUSENTE EN A6000** |
| 30 | **Ausente** (error 2) | **`0x4f` Silent sub 1** | **AUSENTE EN A6000** |
| 31–33 | — | Otros modos | **AUSENTE EN A6000** |

**Total modos**: A6000 = 13, A7S = 34. **21 modos adicionales en A7S**, incluidos 2 Silent.

---

## 4. Registros de tiempo (svd / shd / spl)

### A6000: Registros sombra 16-bit (ID3–ID8)
| Registro | ID | Campo | Bits | Escritor |
|---|---:|---|---|---|
| ID3 | 3 | svd bajo | svd[7:0] | `SetExposure` (`0x436d6f6c`) |
| ID4 | 4 | svd alto | svd[11:8] (ID4[7:4] preservado) | `SetExposure` |
| ID5 | 5 | shd bajo | shd[7:0] | `SetExposure` |
| ID6 | 6 | shd alto | shd[13:8] (ID6[7:6] preservado) | `SetExposure` |
| ID7 | 7 | spl bajo | spl[7:0] | `SetExposure` |
| ID8 | 8 | spl alto | spl[11:8] (ID8[7:4] preservado) | `SetExposure` |

**Espejo condicional**: 0x144–0x149 (mismos bytes), activo si `[G+0x7f]≠0xFF`.

### A7S: Columnas estáticas por modo
- No hay registros sombra individuales
- Cada modo de lectura tiene su **columna completa** de valores en matriz `0x43fee598`
- Valores incluyen equivalente a svd/shd/spl pero **precalculados por modo**
- No hay fórmula aritmética visible en el binario

---

## 4. Fórmula svd vs Valores fijos

| Aspecto | A6000 (IMX210) | A7S (IMX235) |
|---|---|---|
| **Fórmula** | `svd = n·svr_num − 1` (o `n/VdNum − 1`) | **No recuperada** |
| **Variables** | `svr_num = u8 [estado+0x14e]`, `VdNum = u16 [estado+0xcc]`, `n = [ctx+0x3c] o [ctx+0x1f8]` | N/A (valores en matriz) |
| **Centinela** | `svd == 9` → usa `shut = 1` | No aplica |
| **Validación** | `0x4381106c` emite error si desborda | No recuperada |
| **Unidades** | Desconocidas (líneas/ciclos/µs) | Desconocidas |

---

## 5. Parámetros adicionales: SSB, ShutMode, ID1

| Parámetro | A6000 | A7S | Clasificación |
|---|---|---|---|
| **SSB (Strobe)** | Bit 3 del dato ID1, enviado 2 veces (1,0) en lote P2S | Bit `0x10` del byte +4 de registro en `SetExposure/SetRead` | **DISTINTO** |
| **ShutMode** | 0–4; bits 2/7/4/6 de ID1; en captura real solo 0 y 1 | 2 no soportado ("is not supported"); codificación distinta | **DISTINTO** |
| **Registro ID1** | Duplicado (A=`0x4401ca2c`, B=`0x4401c734`); modo+ShutMode+strobe | `0x000c` distingue `0x4e`/`0x4c`; `0x000a` distingue `0x4f`/`0x4d` | **DISTINTO** |

---

## 6. Transporte P2S / CISIF (IDÉNTICO)

| Aspecto | A6000 | A7S |
|---|---|---|
| **Hardware P2S** | DFE0 | Mismo (S56-15) |
| **MMIO bases** | `0xfc088300`/`0xfc088800`/`0xfc088900` | Mismas |
| **Formato trama** | `81|len|81|AH AL|datos` | Mismo |

---

## 7. Fin de integración (IDÉNTICO / NO_VERIFICADO)

| Modelo | Evidencia |
|---|---|
| **A6000** | `ExposureTimerEnd!` (`0x438c893a`) no reescribe registros ni emite SSB/Execute |
| **A7S** | No hay comando extra de "terminar integración" en matriz ni pulso (S57-D D.6) |
| **Clasificación** | **IDÉNTICO** (ambos ausentes), pero **NO_VERIFICADO** si sensor cierra integración internamente |

---

## 8. Conclusión para la línea del obturador

| Pregunta | Respuesta |
|---|---|
| **¿Tiene A6000 modo Silent equivalente a A7S?** | **NO** — A6000 rechaza `0x4e`/`0x4f`; no tiene selector `tipo==2`; no tiene 21 modos extra |
| **¿Es `shut` un selector de mecanismo?** | **NO** — es índice/contador de obturación; peso en fórmula svd, no en tabla |
| **¿Qué falta en A6000 para Silent?** | 1) Modos `0x4e`/`0x4f` en `SetMode`<br>2) Selector `tipo==2` equivalente a `0x43826d58`<br>3) Columnas de timings Silent en matriz de modos<br>4) Fin de integración identificado (ambos NO_VERIFICADO) |
| **¿Demuestra esto incapacidad hardware?** | **NO** (S51: A=NO, B=NO, C=NO) — IMX210 tiene lectura electrónica (vídeo/LiveView); DFE/P2S idénticos; solo falta integración firmware |

---

## 9. Artefactos y evidencia

| Fuente | Contenido |
|---|---|
| `docs/capture/s124-exposure-params.md` | Bloque parámetros, origen, diferencias instrumentación |
| `docs/capture/s134-imager-params.md` | Fórmula svd, origen 6 parámetros, validación |
| `docs/capture/s140-imager-register-map.md` | Vector 119 punteros `0x43fe995c`, estructura registro |
| `docs/capture/s201-imx210-imx235-registers.md` | 11 subsistemas comparados, tabla Silent |
| `docs/capture/s202-imx210-imx235-timing.md` | Tiempos, fórmula svd, fin integración |
| `docs/capture/s204-clasificacion-final.md` | Síntesis: 4 idénticos, 7 distintos, 0 ausentes-en-A6000 |
| `analysis/s201_imx210_imx235_registers/compare.json` | Tabla estructurada 11 subsistemas |
| `analysis/s202_imx210_imx235_timing/timing.json` | Tiempos estructurados |
| `tests/test_s201_imx210_imx235_registers.py` | 7 tests bytes |
| `tests/test_s202_imx210_imx235_timing.py` | 4 tests |

---

## 10. Verificación y tests

```sh
# Tests S201 (comparación registros)
python3 -m pytest tests/test_s201_imx210_imx235_registers.py -v
# Tests S202 (temporización)
python3 -m pytest tests/test_s202_imx210_imx235_timing.py -v
# Tests S124 (parámetros exposición)
python3 -m pytest tests/test_s124_exposure_params.py -v
# Tests S134 (fórmula imager)
python3 -m pytest tests/test_s134_imager_params.py -v
```

---

## 11. Próximos pasos (S301, S304)

| Item | Descripción |
|---|---|
| **S301** | Barrido xrefs a estado imager en A7S (encontrar objeto equivalente a `0x43f72d02`) y tabla diferencias A7S vs A6000 |
| **S304** | REA/Ghidra: callers de `FUN_43858338` (dumper gates S153) y código que carga GOT `0x4401f080` (tabla `0x43ff3200`) |