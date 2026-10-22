# S167 — el módulo `[SAD]` (44 trazas) del firmware A6000 fw3.21

> Hito de la línea de RE general por módulos de trazas. Sólo análisis de bytes
> (sin REA/Ghidra, sin ejecutar firmware). Convención **vaddr = 0x43541000 + file_offset**.
> Regla de referencias: **estricta** (canónica del repo, `analysis/s106_imaging_cap/scan_pic_refs_strict.py`).

---

## 1. Resumen

| cifra | valor |
|---|---|
| cadenas que empiezan por `[SAD]` | **45** (45 tokens `[SAD]` en el binario) |
| cadenas **con mensaje** (excluye la que es solo el prefijo) | **44** |
| sitios de emisión (PIC, regla estricta) | **49** |
| funciones emisoras | **5** |
| cadenas sin referencia | **0** |
| pares PIC verificados a mano | **49/49 OK** (0 fallos) |
| discrepancias contra `pic_refs_strict_global.json` | **0** |
| A7S fw3.20 / A6300 fw2.01 | **0** apariciones del token `[SAD]` |

**Qué es `[SAD]`**: el **módulo de depuración/diagnóstico del subsistema «SA»**
(el acelerador escalar del firmware). Vuelca el estado de configuración, el estado
y los datos de la FIFO de JPEG, los tiempos de cálculo, las cabeceras de programa
SA (`SaProgHdr`) y la gestión de handles de unidad/DMM. Es un módulo de
**instrumentación**, no de captura.

**La sigla NO tiene base textual.** No existe en el binario ninguna cadena (RTTI,
nombre de fichero, símbolo, tabla) que exponga «SAD» como sigla. **Se deja sin
desarrollar** — no se inventa.

**Interés para la línea del obturador: NINGUNO.** 0 apariciones de
`shutter`/`silent`/`obtur`/`expos`/`imager`/`sensor`/`readout`/`drive`/`brack`/
`sweep`/`interval`/`still`/`movie`/`focus`/`aperture`/`iso` en las 45 cadenas.
**S51 (A/B/C = NO) se mantiene.**

---

## 2. La sigla «SAD»: lo que se sabe y lo que NO se sabe

### 2.1 NO VERIFICADO — sin expansión textual

Búsqueda exhaustiva sobre el binario de la A6000 fw3.21:

| patrón | resultado |
|---|---|
| `SAD` | 45 ocurrencias = **solo** las 45 trazas `[SAD]` |
| `SAD_` | 0 |
| `_SAD` | 0 |
| `Sad[A-Za-z]` | 0 |
| `SaD` | 11, **todos** del subsistema de audio (`SaDriverBase` `0x43cde8f1`, `SaDriverZoomNr` `0x43cdda06`, …) — ninguno es `SaDebug` ni similar |
| `\bSA\b` (palabra suelta) | 0 en identificadores; sólo en textos de otros módulos (`[SA]SetZoomNrPreset` `0x43cde2ad`, `SA Dummy Massage Send` `0x43ce0609`, …) |
| nombres de fichero `.cpp/.c/.h` con `sad`/`SaD` | 0 |

En los **148 `.so`** de `firmware/extracted/fw321/.../lib/`: **0** apariciones de
`[SAD]` (los `SAD` sueltos de `libScalarDaemon.so`, `libBizFw.so`, `libObj.so`,
`libsencore.so`, `libInfraMediaCommon.so` son bytes arbitrarios, no cadenas).

→ **La sigla queda SIN DESARROLLAR.** No se propone «SA Debug», «Scene Auto
Detection», «Shot Assist Detection» ni ninguna otra: ninguna tiene respaldo en los bytes.

### 2.2 Indicios (indirectos, NO una expansión)

1. **Contexto de `.rodata`**: las 44 cadenas `[SAD]` (`0x43ce546b`–`0x43ce59c1`) están
   **intercaladas** entre cadenas inequívocamente del subsistema SA:
   `SA0_V1.0SA5_V1.0` `0x43ce5402`, `ZMA1V1.0SA5_V1.0` `0x43ce5413`,
   `SA1_V1.0SA5_V1.0` `0x43ce5424`, `ZMA0V1.0SA5_V1.0` `0x43ce5435`,
   y justo después `SA_PREINSTALLED_PRG:` `0x43ce561f`, `SA_JPEG_ENC` `0x43ce5634`,
   `SA_JPEG_DEC` `0x43ce5640`.
2. **Proximidad de código**: el emisor está en la misma zona que el gestor de
   programas preinstalados SA (`0x4399ede0` referencia `SA_PREINSTALLED_PRG:`).
3. **RTTI con «sad»**: el único es `N15NS_SCALAR_INFRA41ScalarInfraSequenceSaStageAutoexec_sadoneE`
   `0x43ce7004` — que pertenece a `NS_SCALAR_INFRA` (etapa `Sa` del `ScalarInfra`),
   **no** al módulo `[SAD]`. Es una coincidencia de subcadena.

---

## 3. Las 44 trazas con dirección

Todas en `.rodata` de `av-cam.bin`, bloque contiguo `0x43ce546b`–`0x43ce59c1`.

### 3.1 Las 45 cadenas NO forman un bloque contiguo

Están repartidas en **3 bloques** separados por material ajeno al módulo:

| bloque | rango | nº | contenido |
|---|---|---|---|
| **A** | `0x43ce546b`–`0x43ce54bb` | 3 | handles de unidad |
| *(hueco)* | `0x43ce54bc`–`0x43ce55bb` | 256 B | tabla de índices `0x03`–`0x1b` con relleno `0x1c` (ajena a `[SAD]`) |
| **B** | `0x43ce55bc`–`0x43ce5618` | 3 | errores de cabecera SA |
| *(hueco)* | `0x43ce5619`–`0x43ce564b` | 51 B | cola de tabla + `SA_PREINSTALLED_PRG:` `0x43ce561f`, `SA_JPEG_ENC` `0x43ce5634`, `SA_JPEG_DEC` `0x43ce5640` |
| **C** | `0x43ce564c`–`0x43ce59d1` | 39 | volcados de depuración |

### 3.2 Bloque «HANDLE / ALLOC» (6) — gestión de handles de unidad y DMM

| vaddr | texto | sitios PIC |
|---|---|---|
| `0x43ce546b` | `[SAD] Same Unit Handle Get` | `0x43998602` |
| `0x43ce5486` | `[SAD] same hndl get_cnt=0x%08x` | `0x43998614` |
| `0x43ce54a5` | `[SAD] alloc_cnt=0x%08x` | `0x43998626` |
| `0x43ce5958` | `[SAD] Dmm Same Handle Get Num` | `0x439a153e` |
| `0x43ce5976` | `[SAD] SameHandleGetCnt=0x%08x` | `0x439a154e` |
| `0x43ce5994` | `[SAD] Alloc all Cnt=0x%08x` | `0x439a1562` |

### 3.3 Bloque «SA_HDR_ERR» (3) — error de cabecera de programa SA

| vaddr | texto | sitios PIC |
|---|---|---|
| `0x43ce55bc` | `[SAD] !!! CdcSaPrg Hdr Err !!!` | `0x4399d4d2` |
| `0x43ce55db` | `[SAD] !!! NmlSaPrg Hdr Err !!!` | `0x4399d5d8` |
| `0x43ce55fa` | `[SAD] !!! RsdSaPrg Hdr Err !!!` | `0x4399d6ac` |

### 3.4 Bloque «DBGPRT_CMD» (1) — recepción del comando de depuración

| vaddr | texto | sitios PIC |
|---|---|---|
| `0x43ce564c` | `[SAD] DbgPrt CmdRcv` | `0x439a11b4` |

### 3.5 Bloque «CFG_STATE» (4) — volcado del estado de configuración

| vaddr | texto | sitios PIC |
|---|---|---|
| `0x43ce5660` | `[SAD] CfgStatePrt` | `0x439a11e4` |
| `0x43ce5672` | `[SAD]      D3,D2,D1,D0` | `0x439a11f6` |
| `0x43ce5689` | `[SAD] ----------------` | `0x439a1208`, `0x439a1290` |
| `0x43ce56a0` | `[SAD] ZmCfg=0x%08x` | `0x439a121c` |

### 3.6 Bloque «FIFO» (10) — estado y datos de la FIFO de JPEG

| vaddr | texto | sitios PIC |
|---|---|---|
| `0x43ce56b3` | `[SAD] ` *(solo prefijo; 3 usos)* | `0x439a1230`, `0x439a1328`, `0x439a13b4` |
| `0x43ce56ba` | `[SAD] SaCfg=0x%08x` | `0x439a1234` |
| `0x43ce56cd` | `[SAD] = FifoStatePrt =` | `0x439a1274` |
| `0x43ce56e4` | `[SAD] D3:dummy,D2:WrtPtr,D1:RdPtr,D0:NumQue` | `0x439a1284` |
| `0x43ce5710` | `[SAD] OpnCmd=0x%08x` | `0x439a12b2` |
| `0x43ce5724` | `[SAD] JpgNrm=0x%08x` | `0x439a12e2` |
| `0x43ce5738` | `[SAD] JpgSrt=0x%08x` | `0x439a1312` |
| `0x43ce574c` | `[SAD] = FifoDataPrt =` | `0x439a1336` |
| `0x43ce5762` | `[SAD] JpgNrmIndex=0x%02x` | `0x439a1354` |
| `0x43ce577b` | `[SAD] JpgSrtIndex=0x%02x` | `0x439a136e` |

### 3.7 Bloque «FIFO» (cont.) — índices y tamaño

| vaddr | texto | sitios PIC |
|---|---|---|
| `0x43ce5794` | `[SAD] OpnCmdIndex=0x%02x` | `0x439a138e` |
| `0x43ce57ad` | `[SAD] FifoSize=0x%02x` | `0x439a13a4` |
| `0x43ce57c3` | `[SAD]     D3,D2,D1,D0` | `0x439a13c2` |
| `0x43ce57d9` | `[SAD] ---------------` | `0x439a13d0`, `0x439a1474` |
| `0x43ce57ef` | `[SAD] Fifo=0x%08x` | `0x439a13e6` |

### 3.8 Bloque «CALCTIME» (8) — tiempos de cálculo

| vaddr | texto | sitios PIC |
|---|---|---|
| `0x43ce5801` | `[SAD] = CalcTimePrt =` | `0x439a1400` |
| `0x43ce5817` | `[SAD] (ave):(max) (dummy):(count)` | `0x439a140e` |
| `0x43ce5839` | `[SAD] --------------------------` | `0x439a141a` |
| `0x43ce585a` | `[SAD] Data=0x%08x 0x%08x` | `0x439a1446` |
| `0x43ce5873` | `[SAD] = End ==` | `0x439a145a` |
| `0x43ce5882` | `[SAD] = CalcTimeSum Prt(sum:4byte)=` | `0x439a1466` |
| `0x43ce58a6` | `[SAD] Data=0x%08x` | `0x439a1498` |
| `0x43ce58b8` | `[SAD] = End =` | `0x439a14aa` |

### 3.9 Bloque «SA_PROG_HDR» / «DDS_DATA_ADD» (6)

| vaddr | texto | sitios PIC |
|---|---|---|
| `0x43ce58c6` | `[SAD] DdsDataAdd=0x%08x` | `0x439a14b8` |
| `0x43ce58de` | `[SAD] !!! SaProgHdr Err !!!` | `0x439a14d4` |
| `0x43ce58fa` | `[SAD] PrgID=0x%02x` | `0x439a14ea` |
| `0x43ce590d` | `[SAD] Add=0x%08x` | `0x439a14fc` |
| `0x43ce591e` | `[SAD] Data=0x%08x 0x%08x 0x%08x 0x%08x` | `0x439a151e` |
| `0x43ce5945` | `[SAD] SaProgHdr OK` | `0x439a1532` |

### 3.10 Bloque «SELCODE» (2) — errores de código de selección

| vaddr | texto | sitios PIC |
|---|---|---|
| `0x43ce59af` | `[SAD] data1=other` | `0x439a1576` |
| `0x43ce59c1` | `[SAD] SelCodeErr` | `0x439a1582` |

**Recuento**: 6 + 3 + 1 + 4 + 15 + 8 + 6 + 2 = **45 cadenas** = **44 con mensaje**
(la 45.ª, `0x43ce56b3`, es el prefijo `[SAD] ` sin texto, usado 3 veces como
separador/continuación de línea) + **49 sitios**.

---

## 4. Funciones que referencian las trazas (mapa función → traza)

Cinco funciones emisoras, todas en el bloque `0x43990000`–`0x439a1600`:

### 4.1 `0x43998578` — gestión de handle de unidad (3 sitios)

```
0x43998578  push {r4, r5, lr}
0x4399857a  add  r3, pc              ; r3 = 0x43ce546b '[SAD] Same Unit Handle Get'
0x4399857e  add.w r1, r3, #0x1fe    ; fin del barrido (r1 = 0x43ce5669)
0x43998582  ldrh r4, [r3], #2        ; recorre tabla de u16 (handles)
0x43998586  cmp  r4, r0              ; r0 = handle buscado
0x43998588  bne  0x43998594
0x4399858a  mov.w r2, #-1
0x4399858e  strh r2, [r3, #-0x2]     ; marca la entrada con 0xFFFF
0x43998592  movs r2, #1              ; r2 = "encontrado"
0x43998594  cmp  r3, r1
0x43998596  bne  0x43998582          ; bucle
```
- Trazas: `0x43ce546b` (sitio `0x43998602`), `0x43ce5486` (`0x43998614`), `0x43ce54a5` (`0x43998626`).
- Semántica observada: **barrido de una tabla de u16 buscando un handle; al encontrarlo
  lo invalida con `0xFFFF`** y sigue; al final cuenta los asignados (`alloc_cnt`) y
  vuelve a contar los «mismo handle» (`same hndl get_cnt`).
- **Sin llamadores `bl` directos** (ni de 32 bits ni de 16 bits) → se invoca por
  puntero (vtable) o no es alcanzable desde el código caller del binario.

### 4.2 `0x4399d464` — validador de cabecera **Cdc**SaPrg (1 sitio)

- Traza: `0x43ce55bc` (sitio `0x4399d4d2`).
- Código verificado: `push.w {r4-r8, sb, sl, fp, lr}`; reserva 0x14; llama a
  `0x43998290` (resolución de unidad) y a `0x43a3a9b4` (reserva de bloque de 0x12,
  tipo 3); lee `ldrb.w fp,[r5,#4]`; invoca el validador común `0x4399d378`;
  si el resultado no es 1, escribe el código de error `0xd` y **emite la traza**.
- **12 llamadores `bl`** en **4 funciones**: `0x4399a970`, `0x4399aa7c`, `0x4399ab68`, `0x4399ac30`.

### 4.3 `0x4399d528` — validador de cabecera **Nml**SaPrg (1 sitio)

- Traza: `0x43ce55db` (sitio `0x4399d5d8`).
- Código verificado: comprueba `ldrb r3,[r1,#1]` contra `0x51`; si coincide usa
  `ldrb.w sb,[r1,#4]`, si no `ldrb r1,[r1,#9]` + llamada a `0x43998144`; reserva
  0x12/3; compara `ldrb.w r8,[r5,#0xb]` con `ldrb.w fp,[r0,#0xe]` y, si el primero
  es menor, escribe el error `0xc` y **emite la traza**.
- **5 llamadores `bl`** en **4 funciones**: `0x439986b0`, `0x439987f8`, `0x4399895c`, `0x43998aa0`.

### 4.4 `0x4399d618` — validador de cabecera **Rsd**SaPrg (1 sitio)

- Traza: `0x43ce55fa` (sitio `0x4399d6ac`).
- Código verificado: reserva 0x14; `ldrb r1,[r1,#9]` + `0x43998144`; reserva 0x12/3;
  lee `ldrb r3,[r0,#0xe]`; si vale 0 escribe el error `0xc` y **emite la traza**;
  si no, invoca `0x4399d378` y, si falla, error `0xd`.
- **4 llamadores `bl`** en **4 funciones**: `0x43998be4`, `0x43998cac`, `0x43998d70`, `0x43998e34`.

### 4.5 `0x439a119c` — **despachador de depuración** (43 sitios)

Es el emisor principal. Firma: `push {r0, r1, r2, r3, r4, r5, r6, lr}`.

```
0x439a119e  movw  r3, #0x9548        ; id de mensaje esperado
0x439a11a2  ldrh  r2, [r0, #2]       ; campo id del mensaje recibido
0x439a11a6  cmp   r2, r3
0x439a11a8  bne.w 0x439a158e         ; no es para nosotros -> salir
0x439a11ac  ldr   r3, [pc, #0x3e4]   ; 0x439a1594 -> W=0x344494
0x439a11b4  add   r3, pc             ; -> 0x43ce564c '[SAD] DbgPrt CmdRcv'
0x439a11b6  bl    0x439a10f0         ; impresor (0x93, 0, 1)
0x439a11ba  ldrb  r3, [r4, #4]       ; sub-tipo: debe ser 1
0x439a11bc  cmp   r3, #1
0x439a11be  bne.w 0x439a157a         ; -> '[SAD] SelCodeErr'
0x439a11c2  ldrb  r3, [r4, #5]
0x439a11c4  subs  r3, #1
0x439a11c6  cmp   r3, #5
0x439a11c8  bhi.w 0x439a156e         ; -> '[SAD] data1=other'
0x439a11cc  tbh   [pc, r3, lsl #1]   ; tabla de 6 casos en 0x439a11d0
```

**Tabla `tbh` de 6 subcomandos** (base `((0x439a11cc+4) & ~3)` = `0x439a11d0`):

| subcomando | offset | destino | bloque que imprime |
|---|---|---|---|
| 1 | `0x0006` | `0x439a11dc` | CfgStatePrt (`ZmCfg`, `SaCfg`) |
| 2 | `0x004e` | `0x439a126c` | FifoStatePrt (`OpnCmd`, `JpgNrm`, `JpgSrt`) |
| 3 | `0x0111` | `0x439a13f2` | FifoDataPrt (índices, `FifoSize`, `Fifo`) |
| 4 | `0x016f` | `0x439a14ae` | DdsDataAdd |
| 5 | `0x0178` | `0x439a14c0` | SaProgHdr (`PrgID`, `Add`, `Data`) |
| 6 | `0x01b3` | `0x439a1536` | Dmm Same Handle Get Num (`SameHandleGetCnt`, `Alloc all Cnt`) |

- **Único llamador `bl`**: `0x4399b5ac`, dentro del dispatcher padre `0x4399b074`.
- `0x4399b074` está registrado en la tabla de handlers en `0x43fd2a88`
  (valor `0x4399b075`, Thumb) → es un **handler de mensaje del subsistema SA**.

---

## 5. Ficheros fuente

**Las 5 funciones emisoras NO imprimen `file=%s`**: el módulo `[SAD]` **no embebe
ningún nombre de fichero propio**. → fichero fuente propio: **NO VERIFICADO**.

Lo que sí es verificable es el **contenedor**: la zona de código
`0x43990000`–`0x439a1600` pertenece al bloque **ScalarInfra / NS_SCALAR_INFRA**,
cuyos ficheros vecinos son:

| fichero | vaddr | referenciado desde |
|---|---|---|
| `ScalarInfraAsyncMain.cpp` | `0x43ce59fd` | `0x439a18d6`, `0x439a1944`, `0x439a1e10` |
| `ScalarInfraSequenceSa.cpp` | `0x43ce6c15` | `0x439a4024`…`0x439a45f2` |
| `ScalarInfraSequenceSaStage.cpp` | `0x43ce6e16` | `0x439a47a0`…`0x439a4de2` |

Además, el **bloque C** de las cadenas `[SAD]` termina en `0x43ce59d1`, justo antes de
`N15NS_SCALAR_INFRA21ScalarInfraSequenceIfE` (`0x43ce59d2`) y de
`ScalarInfraAsyncMain.cpp` (`0x43ce59fd`), lo que sitúa el módulo dentro del mismo
conjunto de objetos que el módulo `[SFRA]` (S118).

---

## 6. Relación con los módulos ya documentados

| módulo | relación con `[SAD]` | evidencia |
|---|---|---|
| **`[SFRA]`** (S118) | **El más fuerte.** `[SFRA]` = `NS_SCALAR_INFRA`; el **bloque C** de las cadenas `[SAD]` termina justo antes de sus cadenas RTTI y de ficheros en `.rodata` (`0x43ce59d2`, `0x43ce59fd`) y su código está en la misma zona (`0x4399xxxx`). Además `ScalarInfraSequenceSa.cpp` (`0x43ce6c15`) y `ScalarInfraSequenceSaStage.cpp` (`0x43ce6e16`) son los ficheros vecinos de las funciones SAD. | `0x43ce59d2`, `0x43ce59fd`, `0x43ce6c15`, `0x43ce6e16` |
| **`[SFRS]`** (S116) | Comparte subsistema y zona (`[SFRS]` = `0x439a0000`–`0x439c0000`; las funciones SAD están en `0x43998578`–`0x439a119c`, justo antes). `SFRS` gestiona `SET_SA_NOTIFY`/`GET_SA_RESULT` — la misma familia SA. | `analysis/s116_sfrs/sfrs.md` |
| **`[CAMERA_SA]`** (S108) / **`sa_func_*`** (S84) | El driver del SA (`Camera::SaFuncDrv`) **no** emite trazas `[SAD]`: el `[SAD]` es la capa de *diagnóstico* del subsistema, no la de invocación de funciones. No hay solapamiento de cadenas. | `analysis/s108_camera_sa/camera_sa.md` |
| **`[AIP]`** (S121) | `SaWrapper`/`SaDriverBase`/`SaDriverZoomNr` (`0x43cdd839`, `0x43cde8f1`, `0x43cdda06`) son **otro** SA (el de audio). No comparten cadenas con `[SAD]`. | `analysis/s121_aip/aip.md` |
| **`[ADF]`** | Los 3 únicos "núcleos" que S130 encontró en la A7S son las **líneas de guiones** (`----------------`, `---------------`, `--------------------------`), que en la A7S existen bajo la etiqueta `[ADF]`. Coincidencia tipográfica, no contenido común. | `analysis/s130_new_modules/new_modules.json` |

---

## 7. Diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01

### 7.1 Tokens y mensajes

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| ocurrencias del token `[SAD]` | **45** | **0** | **0** |
| cadenas con mensaje | **44** | **0** | **0** |
| mensajes interiores compartidos | — | **0** | **0** |

→ **La etiqueta `[SAD]` y sus 44 mensajes son material propio de la fw3.21 de la A6000.**
No es un renombrado: el contenido **no existe** en los otros dos firmwares
(0 apariciones de `DbgPrt`, `CfgStatePrt`, `FifoStatePrt`, `FifoDataPrt`, `CalcTimePrt`,
`CalcTimeSum`, `SaProgHdr`, `CdcSaPrg`, `NmlSaPrg`, `RsdSaPrg`, `Same Unit Handle Get`,
`Dmm Same Handle Get Num`, `Alloc all Cnt`, `SelCodeErr`, `DdsDataAdd`, `JpgNrm`, `JpgSrt`,
`ZmCfg`, `SaCfg`, `OpnCmd`, `FifoSize` en ambos).

### 7.2 Lo que SÍ es común: el subsistema SA

| cadena | A6000 | A7S | A6300 |
|---|---|---|---|
| `SA_PREINSTALLED_PRG:` | `0x43ce561f` | `0x43cda81c` | `0x43df8959` |
| `SA_JPEG_ENC` | `0x43ce5634` | `0x43cda831` | `0x43df896e` |
| `SA_JPEG_DEC` | `0x43ce5640` | `0x43cda83d` | `0x43df897a` |
| `SA0_V1.0SA5_V1.0` | `0x43ce5402` | `0x43cda6ac` | `0x43df8906` |
| `ZMA0V1.0SA5_V1.0` | `0x43ce5435` | `0x43cda6df` | `0x43df8939` |
| `SA_A_ENC_AC3` | **ausente** | — | `0x43df8986` |

→ El **motor SA y sus programas preinstalados existen en los tres**; lo que la fw3.21
de la A6000 añade es la **instrumentación `[SAD]`** (44 mensajes de diagnóstico).

### 7.3 Hallazgo estructural diferencial (bytes)

En la A7S y el A6300 hay una **tabla de 300 bytes** entre `ZMA0V1.0SA5_V1.0` y
`SA_PREINSTALLED_PRG:`. Su estructura (verificada byte a byte):

- **cabecera de 27 B** `00 01 01 01 00 01 01 02 04 08 83 83 83 04 83 83 83 07 07 07 07 07 07 07 07 07`
  → **idéntica en los tres firmware** (A6000 en `0x43ce5445`, A7S en `0x43cda6ef`,
  A6300 en `0x43df89bc`);
- **cola de 9 B** `04 03 02 03 02 07 83 07 01` + separador;
- **tabla de 25 índices** `0x03 0x04 … 0x1b` embebidos en un mar de `0x1c` (231 bytes `0x1c`);
- **cola final** `00 01 02 00 01 02`.

En la **A6000** la estructura es la misma pero **las 44 cadenas `[SAD]` están
intercaladas en dos puntos**:

| región | A7S | A6000 |
|---|---|---|
| tras la cabecera de 27 B | `07 07 07` + cola de 9 B | cola de 9 B (`04 03 02 03 02 07 83 07 01`) + `00` |
| … | tabla de índices `0x03..0x1b` en mar de `0x1c` (256 B) | **3 cadenas `[SAD]`** (`0x43ce546b`–`0x43ce54bb`) + **la MISMA tabla de índices** (`0x43ce54bc`–`0x43ce55bb`) |
| … | cola `00 01 02 00 01 02` | **3 cadenas `[SAD]`** (`0x43ce55bc`–`0x43ce5618`) + cola `00 01 02 00 01 02` (`0x43ce5619`) |
| … | `SA_PREINSTALLED_PRG:` etc. | `SA_PREINSTALLED_PRG:` etc. (`0x43ce561f`) |
| … | (nada) | **39 cadenas `[SAD]`** (`0x43ce564c`–`0x43ce59d1`) |

**Verificación**: la secuencia de 25 índices no-`0x1c` de la A6000
(`0x43ce54bc`–`0x43ce55bb`) es **byte a byte idéntica** a la de la A7S
(`0x43cda716`–`0x43cda816`): `03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f 10 11 12 13 14 15 16 17 18 19 1a 1b`.

→ **Interpretación**: la fw3.21 de la A6000 ha **insertado las 44 cadenas `[SAD]` en
dos huecos** de esa tabla de datos (desplazando 3 bytes de cabecera y partiendo el
bloque en dos). La tabla de índices y la cabecera sobreviven intactas; lo nuevo es
la instrumentación de diagnóstico. Esto **confirma** que `[SAD]` es material **propio
de la fw3.21 de la A6000**, insertado en el subsistema SA, y **no** un módulo
preexistente reetiquetado.

---

## 8. Interest para la línea del obturador

**NULO. Verificado por barrido literal de las 45 cadenas:**

| término | apariciones |
|---|---|
| `shutter` | 0 |
| `silent` | 0 |
| `obtur` | 0 |
| `expos` | 0 |
| `imager` | 0 |
| `sensor` | 0 |
| `readout` | 0 |
| `drive` | 0 |
| `brack` / `sweep` / `interval` | 0 / 0 / 0 |
| `still` / `movie` | 0 / 0 |
| `focus` / `aperture` / `iso` | 0 / 0 / 0 |
| `jpg` | **4** (`JpgNrm` `0x43ce5724`, `JpgSrt` `0x43ce5738`, `JpgNrmIndex` `0x43ce5762`, `JpgSrtIndex` `0x43ce577b`) |

Las 4 apariciones de `Jpg` son **índices de la cola FIFO** (`JpgNrm` = índice
JPEG normal, `JpgSrt` = índice JPEG sort), NO capturas ni lectura de sensor.

**El módulo no habla de obturación, disparo, lectura del sensor ni exposición.**
**S51 (A/B/C = NO) se mantiene sin cambios.**

---

## 9. NO VERIFICADO / abierto

1. **Sigla «SAD» sin expansión textual** — NO VERIFICADO. No hay ninguna cadena en
   el firmware (RTTI, ficheros, símbolos, los 148 `.so`) que la developed. **No se inventa.**
2. **Fichero fuente propio del módulo** — NO VERIFICADO (las 5 funciones no imprimen `file=%s`).
3. **Significado de `CdcSaPrg` / `NmlSaPrg` / `RsdSaPrg`** — NO VERIFICADO. Sólo se sabe
   que son **tres tipos de cabecera de programa SA** validados por tres funciones distintas
   (`0x4399d464`, `0x4399d528`, `0x4399d618`), con 12 / 5 / 4 llamadores.
4. **Qué son exactamente la «unit» y el «Dmm»** (handle) — NO VERIFICADO. El barrido de
   `0x43998578` invalida la entrada con `0xFFFF`; la semántica del «Dmm» (memory pool) no está confirmada.
5. **Subcomandos 1..6 del comando `0x9548`** — los *destinos* del `tbh` están verificados
   y sus mensajes asignados; la **semántica funcional** de cada subcomando (qué triggers
   lo emiten, quién los envía) es NO VERIFICADA. El mensaje entrante se recibe por la cola
   OSAL (`osal_rcv_msg` `0x43561260`, llamada en `0x4399b136` con id `0x101`).
6. **¿Existe código equivalente sin etiqueta en A7S/A6300?** — NO VERIFICADO en cuanto al
   código; lo verificado es que **no existen** las cadenas ni el mensaje `0x9548`, y que las
   direcciones homónimas de la A7S contienen otra cosa (§11.5). La intercalación de las
   trazas en la tabla del driver SA (§7.3) sugiere que allí no había nada que
   «desetiquetar», pero eso es una inferencia, no una medición.
7. **`ZmCfg` / `SaCfg`** — NO VERIFICADO qué registers/flags representan (el volcado de
   `CfgStatePrt` lee un array de 0x5c/4 = 23 words, `0x439a120e`–`0x439a1224`).

---

## 10. Reproducir

```bash
.venv/bin/python analysis/s167_sad/scan_sad.py        # cadenas + sitios PIC + diferencial
.venv/bin/python analysis/s167_sad/verify_pic.py      # verificación a mano de los 49 pares PIC
.venv/bin/python analysis/s167_sad/build_sad_json.py   # genera sad.json
.venv/bin/python analysis/s167_sad/s167_verify.py     # verificación independiente (49/49)
.venv/bin/python analysis/s167_sad/s167_build.py      # añade las claves verif_indep_* a sad.json
.venv/bin/python -m pytest tests/test_s167_sad.py tests/test_s167_sad_indep.py -q
```

Ficheros:
- `analysis/s167_sad/sad.json` — datos estructurados (incluye las claves `verif_indep_*`)
- `analysis/s167_sad/sad_raw.json` — datos crudos del escáner
- `analysis/s167_sad/sad_pic_verified.json` — los 49 pares PIC verificados
- `analysis/s167_sad/sad_pic_verificado.json` — los 49 pares PIC verificados (2º sub-agente)
- `analysis/s167_sad/scan_sad.py`, `verify_pic.py`, `build_sad_json.py` — scripts
- `analysis/s167_sad/s167_*.py` — escáneres y verificaciones independientes

---

## 11. Complemento: verificación independiente (2º sub-agente)

Reproducción completa desde cero (sin usar `sad.json`), con la **regla estricta**
reimplementada: `analysis/s167_sad/s167_picscan.py`, `s167_verify.py`, `s167_build.py`,
`s167_pic.py`, `s167_funcs.py`, `s167_dataddrs.py`, `s167_disasm.py`, `s167_disasm2.py`,
`s167_blcallers.py`, `s167_sa_search.py`, `s167_strctx.py`, `s167_merge_extra.py`;
tests: `tests/test_s167_sad_indep.py` (17 tests, todos contra bytes reales).

**Todos los números de este informe se han reproducido de forma independiente**:
45 cadenas (44 con texto), 49 sitios, 5 funciones emisoras, 0 sin referencia,
**49/49 pares PIC verificados** y **0 discrepancias** contra
`analysis/s106_imaging_cap/pic_refs_strict_global.json` (la reimplementación local del
escáner reproduce el mapa canónico: 17 525 destinos, mismos sitios).

Datos adicionales no recogidos en las secciones anteriores:

### 11.1 Las trazas NO forman un bloque contiguo

| bloque | rango | nº |
|---|---|---|
| A — handles de unidad | `0x43ce546b`–`0x43ce54b8` | 3 |
| B — errores de cabecera SA | `0x43ce55bc`–`0x43ce5618` | 3 |
| *intercalado* — programas SA | `0x43ce561f`–`0x43ce564b` | 3 (`SA_PREINSTALLED_PRG:`, `SA_JPEG_ENC`, `SA_JPEG_DEC`) |
| C — volcado de estado | `0x43ce564c`–`0x43ce59d1` | 39 |

Entre el bloque A y el B hay **0x100 bytes** de relleno; el bloque C empieza
inmediatamente después de las cadenas de programa SA.

### 11.2 Canal de log propio → `[SAD]` es un módulo independiente de `[SFRA]`/`[SFRS]`

Las 45 trazas se emiten con el impresor `0x439a10f0` (id de mensaje OSAL **`0x93` = 147**,
tamaño de mensaje `0x9a`, reserva con `osal_try_valloc_msg` `0x435612d0`), mientras que
`[SFRA]`/`[SFRS]` usan el **logger global** `0x435ab880`. Son dos mecanismos de log
distintos: `[SAD]` es una biblioteca propia, no una etiqueta más del `[SFRA]`.

### 11.3 Tabla de versiones de los componentes "SA"

`0x43ce5402`–`0x43ce5445` (4 entradas × 16 bytes + NUL, dos campos de 8):
`SA0_V1.0|SA5_V1.0`, `ZMA1V1.0|SA5_V1.0`, `SA1_V1.0|SA5_V1.0`, `ZMA0V1.0|SA5_V1.0`.
El código compara **16 bytes byte a byte** (`ldrb`/`cmp`/`cmp r3,#0x10` en
`0x43993128`–`0x43993196`) contra cuatro globales en ejecución
(`0x43f2ef7c`, `0x43f2ef6e`, `0x43f2ef5c`, `0x43f2ef8c`, resueltos de los pools
`0x439931b4`–`0x439931cc`)
→ componentes **SA0, SA1, SA5, ZMA0, ZMA1**, todos `V1.0`.

### 11.4 Direcciones de datos de los emisores

Resueltas de los pools de literales de `0x43998578` (no de una búsqueda de bytes sueltos):

| dirección | contenido | cómo se resuelve |
|---|---|---|
| `0x43f84bfe` | tabla de **255** *u16* (handles) que recorre `0x43998578` | `ldr r3,[pc,#0xb8]` `0x43998574` + `add r3,pc` `0x4399857a`; fin = base+`0x1fe` |
| `0x43f85932` | tabla de **32** *u16* (handles) que recorre `0x43998578` | `ldr r3,[pc,#0x98]` `0x43998598` + `add r3,pc` `0x4399859a`; fin = base+`0x40` |
| `0x43f31368` | contador u32 (`alloc_cnt`) | `ldr r3,[pc,#0x80]` `0x439985b6` + `add r3,pc` `0x439985b8` |
| `0x43f84bfc` | contador u16 (`same hndl get_cnt`) | `ldr r3,[pc,#0x70]` `0x439985ca` + `add r3,pc` `0x439985d0` |

**NO VERIFICADO / retirado**: un puntero embebido `"PEG_DEC"` (= `SA_JPEG_DEC`+4) en
`0x43ce5644` con sitio en `0x439a11ac`. **Comprobado y FALSO**: el `ldr r3,[pc,#0x3e4]`
de `0x439a11ac` lee el pool `0x439a1594` = `0x344494`, y con el `add r3,pc` de
`0x439a11b4` el destino es **`0x43ce564c`** = `[SAD] DbgPrt CmdRcv` (no `0x43ce5644`).
La cadena `"PEG_DEC"` de `0x43ce5644` **no tiene ninguna referencia PIC** (0 sitios) y
no hay puntero embebido de 4 B a ella en el binario → es una subcadena muerta de
`SA_JPEG_DEC`.

### 11.5 Refuerzo del diferencial con anclas de **código**

| ancla (sitio PIC) | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| `[SIO]osal_valloc_msg` | `0x43990414` | `0x4397df30` | `0x43a24b68` |
| `SA_PREINSTALLED_PRG:` | `0x4399ee6a` | `0x4398c8cc` | `0x43a2accc` |
| `ScalarInfraAsyncMain.cpp` | `0x439a18d6` | `0x4398f122` | `0x43a387fa` |

Desplazamiento A6000−A7S: `0x124E4` (1.ª ancla) → `0x1259E` (2.ª) → `0x127B4` (3.ª): el
bloque **crece** a lo largo de la zona.

**En la A7S no existe código equivalente a los emisores de `[SAD]`**: no hay ninguna
cadena `DbgPrt`/`CfgStatePrt`/`FifoStatePrt`/`SaProgHdr`/`Same Unit Handle Get` (0
apariciones), ni el mensaje `0x9548`. Las direcciones de la A7S que se citan a
continuación contienen **código de otra cosa** (verificado desensamblando), por lo
que **no se puede** afirmar que allí esté «el mismo módulo sin trazas»: lo único
verificable es que **la función de volcado no existe** en la A7S.

| dirección A7S | contenido real (desensamblado) |
|---|---|
| `0x4398ecd0` | `bne`/`cmp r4,#9`/`movs r0,#0xc3` → rama de error con `bl 0x4398190c` (otro módulo) |
| `0x43986100` | `push {r4,lr}` + `ldrb r3,[r0]` + `cmp r3,#0x5c` → comprobación de un byte, sin barrido de tabla de handles |

### 11.6 Refuerzo del §5 (ficheros)

En `0x43990000`–`0x439a1800` **ningún** sitio PIC — con la regla estricta **y también con
la regla ancha** (todos los `ldr` del registro en 4 KB) — apunta a un nombre `.cpp`/`.h`
ni a un nombre de clase RTTI. Las 65 cadenas referenciadas en esa zona son `[SIO]` (3),
`[SAD]` (45), la tabla de versiones SA (4), los nombres de programa SA (3) y literales
sueltos (`Sio`, `test start\n`, `MSG SEND\n`, `err = %d`). → el fichero propio de la
biblioteca `[SAD]` **no está embebido**: NO VERIFICADO (reforza §5).

### 11.7 Ramas de error del despachador (verificadas)

* `bhi.w 0x439a156e` (byte `+5` fuera de 1..6) → imprime **`[SAD] data1=other`** (`0x43ce59af`).
* `bne.w 0x439a157a` (byte `+4` ≠ 1) → imprime **`[SAD] SelCodeErr`** (`0x43ce59c1`).

---

## Revisión del agente principal (22-10-2026)

**Verificado y aceptado (124 tests: 106 del hito + 18 de verificación independiente):**

1. **Recuento y rango**: 45 apariciones del token `[SAD]` en la A6000 fw3.21 entre `0x43ce546b` y
   `0x43ce59d1` (44 con mensaje + el token suelto `[SAD] ` `0x43ce56b3`); **0** en la A7S fw3.20 y el
   A6300 fw2.01 → comprobado con `bytes.count()`.
2. **Estructura**: **49 sitios** (regla estricta) en **5 emisores** — `0x439a119c` (43, el
   despachador), `0x43998578` (3), `0x4399d464`/`0x4399d528`/`0x4399d618` (1 cada uno) — y **0**
   cadenas sin referencia. Los **49 pares PIC se verificaron a mano (49/49)** y la
   reimplementación del escáner reproduce el mapa canónico del repo (17 525 destinos) con **0
   discrepancias**.
3. **No son un bloque contiguo**: son **3 bloques** (3 + 3 + 39) separados por una tabla de
   índices ajena y por las 3 cadenas `SA_*`.
4. **Sigla sin desarrollar (correcto)**: `SAD` = 45 apariciones = solo las 45 trazas; `SAD_`,
   `_SAD`, `Sad[A-Za-z]` = 0; el único RTTI con «sad» es `exec_sadone` de `NS_SCALAR_INFRA`, que
   no es el módulo; **0** apariciones de `[SAD]` en los **148 `.so`** de la fw3.21 → la sigla **se
   deja sin desarrollar** (no se propone «SA Debug» ni «Scene Auto Detection»).
5. **Base textual del driver (común a los tres)**: `ScalarInfraSequenceSa` **10/10/10**,
   `ScalarInfraSequenceSa.cpp` **1/1/1**, `ScalarInfraSequenceSaStage.cpp` **1/1/1**,
   `SaStageAutoexec_sadone` **1/1/1**, `SA_JPEG_DEC` **1/1/1** → la **biblioteca SA es común**;
   lo propio de la fw3.21 es la **instrumentación** (`[SAD]` 45/0/0).
6. **Hallazgo de bytes**: la cabecera de 27 B y la tabla de 25 índices `0x03`–`0x1b` del driver SA
   son **byte a byte idénticas** en los tres firmware, pero en la A6000 las 44 trazas están
   **intercaladas** en ellas → la instrumentación se insertó *dentro* del driver SA.
7. **Negativo acotado**: 0 de `shutter`/`silent`/`expos`/`imager`/`sensor`/`readout`…; las 4
   apariciones de `Jpg` son **índices de cola FIFO** → **sin efecto en S51**.

**Corrección aceptada (el subagente retiró una afirmación de su primera versión):** el puntero
embebido `"PEG_DEC"` en `0x43ce5644` **no existe**. El `ldr r3,[pc,#0x3e4]` de `0x439a11ac`
resuelve al pool `0x439a1594` (`W=0x344494`) y, con el `add r3,pc` de `0x439a11b4`, el destino es
`0x43ce564c` = **`[SAD] DbgPrt CmdRcv`**. `"PEG_DEC"` es una **cadena muerta** (0 referencias PIC
y 0 punteros de 4 B). Verificado a mano en esta revisión.

