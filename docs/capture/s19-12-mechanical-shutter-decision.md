# S19-12 Follow-up: Mechanical Shutter Decision Points & CAIF/Darwin Path Conditions

**Fecha:** 2026-10-21  
**Alcance:** Sony A6000 FW 3.21, análisis estático de `av-cam.bin` (base LIRO `0x43541000`)  
**Fuentes:** LLVM desensamblado, exportaciones REA/Ghidra `exp2*.jsonl`, documentación sesiones 17–19  
**Clasificación:** Cada hallazgo marcado **VERIFICADO**, **NO_VERIFICADO**, **INFERENCIA**, **DESCARTADO**

---

## 1. Selector de captura `0x437eabfc` y tabla de 15 filas en `0x43edccf8`

### 1.1 Estructura del selector (VERIFICADO)

El selector `0x437eabfc` (llamado desde `0x437df338` en `CaptureManager`) elige una fila de 20 bytes (5 palabras) de una tabla de **15 entradas** en BSS `0x43edccf8`. La tabla **no tiene contenido en la imagen estática** (es BSS cero), pero **sí es recuperable estáticamente** vía su inicializador maestro `0x437ebed8` (sesión 18, `s18-main-init-437ebed8.md` §3).

El inicializador `0x437ebed8` puebla el slot GOT `DAT_44022934` (que el selector usa) con 15 descriptores GOT que resuelven a **15 funciones Thumb reales y contiguas** en `0x43b1bc0d`–`0x43b1c097`:

| Offset fila | GOT descriptor | Función real (Thumb) | Seleccionable dinámicamente |
|---|---|---|---|
| `0x00` | `0x440236b8` | `0x43b1bc0d` | No |
| `0x14` | `0x440223a4` | `0x43b1bc25` | No |
| `0x28` | `0x44026110` | `0x43b1bc71` | No |
| `0x3c` | `0x44021940` | `0x43b1bcc7` | No |
| `0x50` | `0x440241a0` | `0x43b1bd13` | No |
| `0x64` | `0x440268e0` | `0x43b1bd5f` | No |
| `0x78` | `0x44020b28` | `0x43b1bdb5` | No |
| `0x8c` | `0x44025d08` | `0x43b1be01` | No |
| **`0xa0`** | `0x44023a6c` | `0x43b1be37` | **Sí** (iVar7=8) |
| **`0xb4`** | `0x440265b8` | `0x43b1be99` | **Sí** (rama directa, 1ª condición) |
| **`0xc8`** | `0x4401f664` | `0x43b1bf05` | **Sí** (iVar7=0xA) |
| **`0xdc`** | `0x44023054` | `0x43b1bf67` | **Sí** (iVar7=0xB) |
| `0xf0` | `0x44026070` | `0x43b1bfc9` | No |
| **`0x104`** | `0x44022dd4` | `0x43b1c035` | **Sí** (iVar7=0xD) |
| `0x118` | `0x44023c3c` | `0x43b1c097` | No |

> **VERIFICADO:** Las 15 filas son trampolines Thumb de 4 bytes (`push {r2}; b <destino>`) que saltan a implementaciones reales en `~0x43b1c2c9`–`0x43b1c32b` (s18-main-init-437ebed8.md §6). No son stubs vacíos.

### 1.2 Semántica de los campos del descriptor de 5 palabras (INFERENCIA fuerte / NO_VERIFICADO parcialmente)

Cada fila de 20 bytes se inicializa en `FUN_437de944` con el patrón:
```
offset +0:  vptr común (DAT_44020894)
offset +4:  estado inicial = 0
offset +8:  puntero a descriptor específico (desde GOT de la fila)
offset +12: (no documentado en inicializador)
offset +16: (no documentado en inicializador)
```

La decompilación de la fila `0xb4` (`0x43b1be99` → `FUN_43b1be98`) muestra que opera sobre **los mismos campos del struct de petición de captura** que el selector:
- `+0x4b70`, `+0x754`, `+0x4d8`, `+0x4a7c` — campos de decisión
- Escribe bytes en `+0x23`..`+0x27` tras llamada a `FUN_43ae9226(..., 0x9400, ...)` — metadatos tipo EXIF/lente
- **No contiene ninguna marca de modo Silent/EFCS**

> **INFERENCIA:** El descriptor de 5 palabras contiene: (1) vptr a vtabla de máquina de estados, (2) estado, (3) puntero a datos de configuración de la fila, (4-5) campos adicionales de contexto. La correspondencia exacta fila → primer comando CAIF/Darwin **NO_VERIFICADA**.

### 1.3 Condiciones de selección de fila en `0x437eabfc` (VERIFICADO)

El selector usa campos del objeto de captura:
- `+0x4b70`, `+0x54a5`, `+0x54a8`, `+0x70`, `+0x1d8`, `+0x1e0` (ver `s19-mechanical-shutter-decision-points.md` fila corregida)
- Índice calculado como `iVar7 * 0x14` con `iVar7 ∈ {8, 0xA, 0xB, 0xD}` para filas dinámicas `0xa0, 0xc8, 0xdc, 0x104`
- Fila `0xb4` alcanzada por rama directa (primera condición), no por el cálculo `iVar7*0x14`

> **NO_VERIFICADO:** Qué valores concretos de esos campos seleccionan cada fila, y qué fila (si alguna) evita CAIF/Darwin.

---

## 2. Guardas en RelMgr, Dispatcher Local, CaptureStart, CaptureManager

### 2.1 RelMgr — `0x4379e6a8` (VERIFICADO)

```
0x4379e6a8: Consulta objeto de bloqueos por slots +0x18/+0x1c para factores 1, 0xF, 0x11, 0x15
    → Rechazo: emite tipo 5 / 0x4045
    → Admisión: 0x4379eba0 construye tipo 2 / 0x3011 hacia cola 0x40193
```
**Es una puerta previa a captura, no una prueba de cortina.** El puente `0x3011/0x40193` → dominio local `0x100..0x207` permanece **NO_VERIFICADO**.

### 2.2 Dispatcher Local — `0x43807f4c` caso `msg[0]==0x100` (VERIFICADO)

```
0x43807f4c: Sólo deriva código 0x100 a 0x43807d80
```
Llegada a `0x43809ed8` (instalador `CaptureStart`) condicionada por:
- Retorno nulo/no nulo de helpers: `0x43b015ce`, `0x43b0228c`, `0x43b02142`, `0x43b0219c`, `0x43b0213a`
- `msg[+0xc] == 4` en `0x43807e4e..0x43807e52`
- `r4+0x1c` igual a 4 o 2
- Puntero global `+0x30` no nulo (una ruta)

> **VERIFICADO:** Fallar estas guardas toma limpieza, notificación o retorno, **no** el instalador. Nombres semánticos de helpers/campos **NO_VERIFICADOS**.

### 2.3 CaptureStart — Instalador `0x43809ed8..0x43809f18` (VERIFICADO)

```
Construye callback a 0x437df640 y llama 0x43b0172c(objeto, 0)
NO bifurca por modo de obturador (Silent/EFCS/mecánico)
```
Por inspección directa, un flag de Silent/EFCS **no puede atribuirse a este punto**.

### 2.4 CaptureStart — Despacho `0x437df640` (VERIFICADO)

```
cfg[+0x265] bits 2..3 (valor >> 2 & 0x0F):
  1, 2, 3 → recorridos específicos
  resto   → llamada ordinaria 0x437df338 en 0x437df876..0x437df87a
Para valor 2: global+0x14 == 1 también llega a 0x437df338 (0x437df79c..0x437df7a0); si no, toma 0x301f
```
**Es una selección de clase de captura, no una clasificación mecánica demostrada.**

### 2.5 CaptureManager — `0x437df338` (VERIFICADO)

```
Tras recursos e ImageParamCapture:
  Crea Image
  Llama 0x437eabfc (selector)
  Copia 5 palabras del descriptor seleccionado
  Despacho indirecto de etapa vía 0x43b04730(Image)
```
**Último selector comprobado antes de ejecutar la máquina de estados de captura.**

---

## 3. Condiciones EFCS en `0x43842158` (VERIFICADO / DESCARTADO)

### 3.1 Selector de clase de exposición (VERIFICADO)

```
En 0x43842158, banco +0x41c (campo EFCS):
  Si bank[+0x4bc] & 0xe0 == 0:
    EFCS != 1 → clase 3
    EFCS == 1 → parte de 1; según modo +2, +0x38c y umbral puede volver a 3
  Si máscara 0xe0 tiene bits → otras condiciones seleccionan 1 o 5
Diagnóstico GOT 0x44022728 +0x7e puede forzar clases 0–7
Anulación por campos +0x36/+0x37 del primer argumento
```

### 3.2 Clases de exposición ≠ obturación electrónica (DESCARTADO)

- Clase 2 produce máscara `0x94` vs `0xD4` de clase 3 (difiere en bit `0x40`)
- Clase 2 escribe **dos registros adicionales** IMX210 vía GOT `0x4401f790` y `0x44025b0c` (args +8, +0x14) y calcula otra temporización
- **NO VERIFICADO** que bit `0x40` sea cortina trasera electrónica
- **NO VERIFICADO** que forzar clase 2 produzca fotografía válida
- `SetExposure` sigue programando el IMX210; clase 2 **modifica temporización/registros adicionales**, no suprime cortinas

> **CONCLUSIÓN:** EFCS es selector de parámetros de exposición existente. **No se equipara a obturación totalmente electrónica.**

---

## 4. Frontera CAIF/Darwin — Evento 1 y control de cortinas

### 4.1 Envío CAIF evento 1 (VERIFICADO)

```
0x437db858(evento=1) → 0x436b8a50 → 0x436ba234(0x10300, 0x16, ...)
```
Empaqueta y encola **22 bytes** (operación `0x10300`). Diferencia con A6300 (31 bytes, bit Silent en `+12`): A6000 **no escribe bit Silent** en este paquete (silent-caif-transport.md §44-62).

### 4.2 Control de cortinas en Darwin (VERIFICADO — fm3-gpio-shutter-mapping.md)

**Pines FM3 (IC5700 MB9AF004B) — base GPIO `0x40033000`, alias bit-band `0x42668000`:**

| Alias | Registro | Pin | Red (CN4900) | Función |
|---|---|---|---|---|
| `0x42668234` | PDOR4 b13 | P4D (SIN2_2) | FP-2045 pin 10 | **1ST_CURTAIN_MG** |
| `0x42668238` | PDOR4 b14 | P4E (SOT2_2) | FP-2045 pin 11 | **2ND_CURTAIN_MG** |
| `0x42668230` | PDOR4 b12 | P4C (SOT2_1) | — | CA_1ST_CURTAIN_START |
| `0x4266822C` | PDOR4 b11 | P4B (SIN2_1) | — | CA_RELEASE_LOCK_MSS |

**Escritores en tiempo de ejecución (A6000 Darwin):**

| Función | Efecto | Llamadores |
|---|---|---|
| `0x20C90` | P4D=1 (1ª cortina) | `1f694 1f8a2 1f914 20154` |
| `0x20CB2` | P4D=0 | `20286 20300 2063e 206f2 209d4 20a00 20a8e 20af8` |
| `0x20D00` | P4E=1 (+`5C9E`,`210C0`,`5C88`) | `203c2 20448 20ac0` |
| `0x20CD4` | P4E=0 | `1f698 206f6 207c2 207ec` |

**Todas pasan por filtro `0x20C74` = `0x1B080(0)&7 ∈ {1,2,3}`** — si no, retorna sin escribir.  
**Esto confirma que el control es independiente del estado Silent** y depende de un byte de «tipo de hardware» cuyo origen sigue **NO_VERIFICADO** (`0x1B080` → tabla `0x1B0E0`/`0x1B0E4+0x50`).

> **VERIFICADO:** P4D/P4E son GPIO salida (modo 1), **NO son serie** (MFS2 no activado en perfiles, fm3-gpio-shutter-mapping.md §2). La cadena de potencia: P4D/P4E → FET Q6832 → bobinas 1C/2C CN302 (10 pines) con SHUTTER_5.5V.

---

## 5. ¿Existe una ruta que omita cortinas sin romper exposición/lectura/limpieza?

### 5.1 Estado actual (NO_VERIFICADO)

| Requisito | Estado |
|---|---|
| Fila del selector que no emita transacción CAIF/Darwin de cortinas | **NO_VERIFICADO** |
| Conserva contratos de exposición, lectura, finalización, limpieza | **NO_VERIFICADO** |
| Condición de esa fila y su alternativa | **NO_VERIFICADO** |

### 5.2 Lo que se necesita (mínimo diagnóstico)

1. **Antes de CaptureStart:** petición rechazada por RelMgr o guardas del dispatcher local (puente `0x3011→0x100` NO_VERIFICADO)
2. **Tras CaptureStart:** clase `cfg+0x265` evita rama ordinaria o conduce a implementación sin descriptor convencional (ramas 1/2/3 **no probadas como electrónicas**)
3. **En ejecución LIRO:** fila resultante de `0x437eabfc` no emite transacción CAIF/Darwin de cortinas, conservando contratos

> **HIPÓTESIS:** Una divergencia segura, si existiera, debe estar en `0x437eabfc` o antes de ejecutar su descriptor. **No se debe modificar basándose sólo en esta hipótesis.**

---

## 6. Resumen de condiciones para ruta mecánica vs electrónica

| Punto de decisión | Condición mecánica (verificada) | Condición electrónica (hipotética/no verificada) |
|---|---|---|
| **RelMgr** | Petición admitida (factores 1,0xF,0x11,0x15) | Petición rechazada → no llega a captura |
| **Dispatcher local** | Guards de helpers + `msg+0xc==4` + estados superados | Algún guard falla → limpieza/retorno |
| **CaptureStart instalador** | Siempre ejecuta (sin bifurcación Silent) | — |
| **CaptureStart despacho** | `cfg+0x265` valor ord. → `0x437df338` | `cfg+0x265` ∈ {1,2,3} → recorridos específicos (no probados electrónicos) |
| **Selector LIRO `0x437eabfc`** | Fila convencional (0x00,0x14..0x118 salvo 0xa0/0xb4/0xc8/0xdc/0x104) | **NO_VERIFICADO:** ¿fila 0xa0/0xc8/0xdc/0x104 evita CAIF? |
| **CAIF evento 1** | 22 bytes → Darwin → P4D/P4E via `0x20C90`/`0x20D00` | **NO_VERIFICADO:** ¿existe variante 0 bytes / bit Silent en paquete? |
| **Darwin cortinas** | `0x20C74` valida tipo HW 1/2/3 → escribe P4D/P4E | **NO_VERIFICADO:** ¿tipo HW 0 o 4 suprime escrituras? |
| **EFCS / Clase 2** | Programa IMX210 + 2 registros extra + temporización distinta | **DESCARTADO** como evidencia de obturación electrónica |

---

## 7. Próximos pasos de verificación (orden de prioridad)

1. **Decompilar filas dinámicas `0xa0` (`0x43b1be37`), `0xc8` (`0x43b1bf05`), `0xdc` (`0x43b1bf67`), `0x104` (`0x43b1c035`)** — buscar referencias a CAIF `0x10300`, `ObjCamera`, `EncodeStill`, `CBID_ENCODE_STILL`, o ausencia de llamada a `0x437db858`.
2. **Resolver origen del byte de tipo hardware en Darwin** (`0x1B080` → tabla `0x1B0E0`/`0x1B0E4+0x50`) — determina si existe tipo que suprime P4D/P4E.
3. **Parser CAIF en `darwin_core.bin` A6000 vs A7S** — comparar bit `0x20` en `pkt[+0x12]` (A7S lo usa para `no_silent` y evitar P4D/P4E; A6000 lo descarta, ver `s53-conclusions.md`).
4. **Trazar `+0x754` en objeto de trabajo** — inicializador `0x437881a8`, handler hermano `0x43802614` (ver `knowledge/CURRENT.md` S64).
5. **Correlacionar cada fila LIRO con primer comando CAIF/Darwin** — requiere decompilación completa de los ~15 manejadores en `0x43b1c2c9`–`0x43b1c32b`.

---

## 8. Conclusiones

- **VERIFICADO:** Cadena completa de guardas desde RelMgr → Dispatcher → CaptureStart → CaptureManager → Selector LIRO `0x437eabfc` → tabla 15 filas → CAIF evento 1 (22 B) → Darwin P4D/P4E.
- **VERIFICADO:** Tabla del selector **sí recuperable estáticamente** vía inicializador `0x437ebed8` + GOT (cierra blocker metodológico sesión 17).
- **NO_VERIFICADO:** Semántica exacta de los 5 campos del descriptor, correspondencia fila → CAIF/Darwin, existencia de fila que omita cortinas.
- **DESCARTADO:** EFCS / clases de exposición 1/2/3/5 como evidencia de obturación totalmente electrónica.
- **INFERENCIA fuerte:** La decisión física de cortinas la toma el MCU Darwin (parser CAIF); A6000 descarta bit Silent que A7S usa para `no_silent`.
- **SilentShutter NO declarado funcional.** S51 se mantiene: A=NO, B=NO, C=NO.

---

**Evidencia asociada:**
- `analysis/session19/evidence/mechanical-shutter-decision-points.json`
- `docs/capture/s18-main-init-437ebed8.md`
- `docs/capture/s19-liro-remaining-sequences.md`
- `docs/capture/fm3-gpio-shutter-mapping.md`
- `docs/capture/silent-caif-transport.md`
- `docs/capture/efcs-capture-selector.md`
- `docs/capture/s19-mechanical-shutter-decision-points.md`
