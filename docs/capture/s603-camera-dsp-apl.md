# S603 — módulo `[CAMERA_DSP_APL]` (18 trazas): exclusivo de A6000 fw3.21

**Estado: VERIFICADO** — 18 cadenas únicas con el prefijo `[CAMERA_DSP_APL]` en la A6000 fw3.21; **0 en A7S fw3.20** y **0 en A6300 fw2.01** (búsqueda literal `strings -a` en los tres `av-cam.bin`).

---

## 1. Censo de trazas (18 únicas, direcciones virtuales base 0x43000000)

| # | VA | Texto |
|---|---|---|
| 1 | 0x43c901da | [Error] cannot free reference memory |
| 2 | 0x43c90211 | [Error] MemOpen (%X) |
| 3 | 0x43c90238 | [Error] sapl_mov_stop - TIMEOUT |
| 4 | 0x43c9026a | [Error] sapl_SetDmaAddrTar - MEMORY_TARGET |
| 5 | 0x43c902a7 | [Error] sapl_SetDmaAddrMEOut - MEMORY_MEPRIVATE |
| 6 | 0x43c902e9 | [Error] sapl_SetDmaAddrMEOut - MEMORY_MEPRIVATE 4K2K CORE1 |
| 7 | 0x43c90336 | [Error] sapl_SetDmaAddrOut - FMT_SRC_REF0_ADDR is NULL |
| 8 | 0x43c9037f | [Error] sapl_SetDmaAddrMBLOut - MEMORY_MARBLEOUT |
| 9 | 0x43c903c2 | [Error] sapl_SetDmaAddrMBLOut - MEMORY_MEPRIVATE 4K2K CORE1 |
| 10 | 0x43c90410 | [Error] sapl_SetDmaAddrOut - HME_COPY_SRC_ADDR is NULL |
| 11 | 0x43c90459 | [Error] sapl_SetDmaAddrParamBuffer - MEMORY_ESRAM |
| 12 | 0x43c904af | [Error] APL Small eSRAM Alloc (%X) |
| 13 | 0x43c904e4 | [Error] APL LGR eSRAM Alloc (%X) |
| 14 | 0x43c90517 | [Error] APL Small eSRAM Free (%X) |
| 15 | 0x43c9054b | [Error] APL LgrDl eSRAM Free (%X) |
| 16 | 0x43c9057f | [Error] APL Base DDR Free (%X) |
| 17 | 0x43c905b0 | [Error] APL TAR DDR Free (%X) |
| 18 | 0x43c905e0 | [APL Driver] IIB stop Timeout No=%x, IIB_STT=%x |

---

## 2. Funciones emisoras (REA `xrefs` + `procedure_pseudo_code`)

Las xrefs apuntan a funciones en tres rangos:

| Rango | Funciones | Descripción |
|---|---|---|
| **0x436bd830–0x436bd8ce** | `FUN_436bd830`, `FUN_436bd88c` | Liberación referencia / Setup DMA genérico |
| **0x43a30000** | `FUN_43a2ff90` | `sapl_mov_stop` TIMEOUT (200 reintentos) |
| **0x436be5ac** | **FUN_436be5ac** (entry points múltiples) | **FUNCIÓN PRINCIPAL APL DRIVER** — ~600 líneas, maneja MemOpen, DMA, eSRAM/DDR, IIB |
| **0x436bf1dc–0x436bf7c6** | Handlers específicos | Errores Alloc/Free eSRAM/DDR |

### 2.1 Función principal: `FUN_436be5ac` (0x436be5ac / 0x436be60c / 0x436be696 / 0x436be6e0 / 0x436be71a / 0x436be784 / 0x436be7ba / 0x436be84e / 0x436be948 / 0x436be978 / 0x436be9ec / 0x436bea4c / 0x436beaae)

Ghidra identifica la **misma función** en 13 entry points distintos (cuerpo idéntico). Maneja todo el flujo APL:

- **Validación** inicial: `FUN_43acb0f8` → `FUN_436bd2a4`/`FUN_436bd2cc` (comprueba estado)
- **MemOpen**: error #2 en `FUN_436bd88c` (param_1==3 → 0x60000000; else `FUN_439032d8` + `FUN_43a3aa0c`)
- **DMA address setup**: `sapl_SetDmaAddrTar/MEOut/MBLOut/Out/ParamBuffer` → `FUN_436bd88c` con distintos tipos de memoria
- **eSRAM/DDR Alloc/Free**: Small/LGR/LgrDl eSRAM, Base/TAR DDR
- **IIB stop timeout**: #18 sin xref directo (probablemente vía tabla)
- **Logging**: `FUN_436bd784` (nivel 10) + `FUN_43902770` (OSAL logger)
- **Helpers**: `FUN_436bf6d4`, `FUN_436bf51c`, `FUN_436bf4f0`, `FUN_436bf548`, `FUN_436bf840`, `FUN_436bf870`, `FUN_436bf424`, `FUN_436bf484`, `FUN_43a3aa0c`

### 2.2 `FUN_43a2ff90` (0x43a30000) — `sapl_mov_stop` TIMEOUT

```c
do {
  FUN_436c14f8(0, uVar1);  // stop core 0
  FUN_436c14f8(1, uVar1);  // stop core 1
  FUN_43acb378(uVar1);     // sync
  FUN_4356129c(_DAT_43a30014, msg); // OSAL msg wait
  iVar2 = FUN_436c201c(uVar1); // check stop
} while (iVar3-- != 0);  // 200 retries
```

---

## 3. Subsistemas y tipos de memoria (inferidos de trazas)

| Sigla | Significado | Contextos |
|---|---|---|
| **SAPL** | Sony APL (Application) | `sapl_mov_stop`, `sapl_SetDmaAddr*` |
| **MEMORY_TARGET** | Buffer objetivo | DMA Tar |
| **MEMORY_MEPRIVATE** | Memoria privada ME (Motion Estimation) | DMA MEOut, 4K2K CORE1 |
| **MEMORY_MARBLEOUT** | Salida MARBLE | DMA MBLOut |
| **MEMORY_ESRAM** | Embedded SRAM | DMA ParamBuffer, eSRAM Alloc/Free |
| **DDR Base/TAR** | DRAM principal | Base DDR, TAR DDR |
| **IIB** | Image Input Block | IIB stop Timeout, IIB_STT register |
| **4K2K CORE1** | Núcleo 1 para 4K/2K | MEOut, MBLOut |
| **HME** | High Efficiency Motion Estimation | HME_COPY_SRC_ADDR |
| **MARBLE** | Módulo Marble | MARBLEOUT |
| **FMT** | Format | FMT_SRC_REF0_ADDR |
| **LGR / LgrDl** | Long GOP Reference / Download | eSRAM LGR |

---

## 4. Diferencial A7S fw3.20 / A6300 fw2.01

| Firmware | Cadenas `[CAMERA_DSP_APL]` | Conclusión |
|---|---|---|
| A6000 fw3.21 | 18 únicas / 18 totales | **Módulo presente** |
| A7S fw3.20 | 0 | **Ausente** |
| A6300 fw2.01 | 0 | **Ausente** |

**Verificación:** `strings -a` literal en los tres `av-cam.bin` (SHA256 distintos). REA `search_strings` en A6000 confirma 18 cadenas únicas con xrefs válidas.

---

## 5. Evidencia y reproducibilidad

- **JSON + test:** `analysis/s603_camera_dsp_apl/`
  - `camera_dsp_apl.json` — catálogo completo
  - `test_camera_dsp_apl_exclusivity.py` — test automatizado (3 asserts)
- **Herramientas:** REA (MCP `search_strings`, `xrefs`, `procedure_pseudo_code`) + `strings -a` / `grep` como control positivo.
- **Binario:** `av-cam.bin` A6000 fw3.21 (SHA256 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`).

---

## 6. Límites / NO_VERIFICADO

- Función principal `FUN_436be5ac` es **extremadamente grande** (~600 líneas pseudocódigo) con 13 entry points; Ghidra la muestra como cuerpo idéntico en direcciones distintas.
- Nombres de archivo fuente no recuperados.
- Semántica SAPL/IIB/HME/MARBLE/FMT/LGR inferida de formato de trazas; no confirmada en símbolos.
- Strings #14, #15, #18 no tienen xrefs directos (probablemente tabla de punteros).
- No se probó alcance en runtime (sin firmware ejecutado).
- La ausencia en A7S/A6300 es **estática**; no prueba incapacidad de hardware.

---

## 7. Conclusión para la línea del obturador electrónico

**Sin efecto directo en S51 (A/B/C = NO).** El módulo es el **driver APL (Application) del DSP de cámara** — gestiona memoria (eSRAM, DDR), DMA, Motion Estimation, HME, MARBLE, IIB, 4K2K. Es un subsistema de **procesado de video/imagen** exclusivo de la A6000 fw3.21. No menciona `shutter`, `silent`, `electronic`, `EFCS`, `curtain`, `mechanical`, `flicker`.

---

**Próximo:** S604 — decodificar `[LENS_YC]` y `[IMAGING_RAW]`.