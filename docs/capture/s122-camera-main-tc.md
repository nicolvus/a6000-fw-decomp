# S122 — el módulo `[CAMERA_MAIN_TC]`: 127 trazas, doble emisión y *time compression*

**Hito de la línea de ingeniería inversa general** (A6000 fw3.21). No toca la línea del obturador
electrónico: **0** apariciones de `shut`, `silent`, `electro`, `mech`, `sensor`, `exposure`,
`drive`, `readout`, `jpeg`, `movie`, `stc`, `bracket`, `sweep` o `interval` en las 127 trazas.
Informe: [analysis/s122_camera_main_tc/camera_main_tc.md](../../analysis/s122_camera_main_tc/camera_main_tc.md) · Datos: `camera_main_tc.json` · Test: `tests/test_s122_camera_main_tc.py`.

## Hallazgo central

**127 cadenas** con la etiqueta `[CAMERA_MAIN_TC]: `, **127 textos distintos**, en **6 tramos no
contiguos** entre `0x43ca7fd7` y `0x43ccb350`. **123 están vivas** y **4 muertas** (`0x43cb6c6f`,
`0x43cb6c9b`, `0x43cb717a`, `0x43cb71a5`, de cancelación). Hay **256 sitios PIC en 41 funciones**:
**122 de las 123 vivas llevan más de un puntero** (2 en 116, 3 en idx 0, 4 en cinco pares) —cadena
completa (publicador OSAL) y texto interior (`printf` `0x43902718`)—: **126 trazas se emiten dos
veces** (idx 105 solo una) y el interior vive **18 bytes** después (`inner == vaddr + 18`).

## Anatomía y emisores

* Punteros: **127 `string` + 2 `prefix` + 127 `inner` = 256**. Lectura estructural: **128 sitios
  publican** (126 `string` + 2 `prefix`), **127 imprimen** y **1 no emite** (`0x437d07be`, idx 0:
  `ldr` a `0x43ca7fd4`, usado como tabla de bytes con `ldrb r1,[r3,r2]`).
* Los **17 publicadores** comparten prólogo byte a byte: **`0xB408`** (`push {r3}`), primer `bl`
  en **`p+0x1e` → `0x435612d0`** (`osal_try_valloc_msg`), luego `memset` `0x439c5a04`,
  `0x43561244`, `0x439c5004` y `osal_free_msg` `0x435612ec`. Mayores: `0x437d4828` (26),
  `0x43878570` (23), `0x43876c08` (15), `0x4387651c` (14), `0x437d6cf4` (13). La heurística
  "primera llamada" (128/115/9/4) es contraste; anomalías: `0x43876fcc` (usa `sb`, vía
  `0x43876ffe`) y `0x43879274` (cola `b 0x43879296` → `printf`).

## Despacho y relaciones

* **`ApolloSA_Main` `0x438730b0`** (14 sitios = 7×2): `tbb` `0x4387333e` (rango por modo) y
  `tbh` `0x4387348e` (tabla `0x43873492`, 9 casos): 0/1→`0x43875878`, 2→`JudgeBdroRslt`,
  3→`0x438735d8` (y convergencia; `bl 0x43872c94` en `0x438735e2`), 4→`0x437d48e8` (52 sitios),
  5/7→`0x438740c8`, 6/8→`0x43874270`.
* **Solo 2 llamadores**: la **panorámica** (S105) en **`0x437f1324`** (tras `cmp r7,#2`; `r7==2`
  llama `ApolloSA_Fin` `0x43873644` en `0x437f1314`) y **`0x438bdeac`** (zona `[IMAGING_CAP]`,
  función `0x438bddf0`; trazas `Apollo.cpp` `0x43cc6e15`, `Stage_Apollo.cpp` `0x43cc6e0f`).
* Es el **único cliente de `[APL]`** (S119): `0x438765c8`, `0x438765fc`, `0x4387668c`,
  `0x43876a80`, `0x43876ab4`, `0x43876b74` se llaman **desde dentro** de `0x438730b0`; otros
  bloques: **SMART ZOOM** `0x43876ea4` (31 sitios, llamador `0x4354af32`), **DDT** 18/8,
  **DIST** 13/3, **JudgeBdroRslt** `0x438e8204` (10 enteros).

## Diferencial A7S fw3.20 / A6300 fw2.01

**0** apariciones de `[CAMERA_MAIN_TC]`; **126/127** textos interiores presentes literalmente
(falta idx 105, interior vacío); **119 textos con refs PIC / 123 sitios** frente a 123/256.
Idéntico en ambas versiones: **115** con 1 sitio, **8** con 0, **4** con 2 (idx 46, 109, 110,
118). **Tres trazas pierden sus sitios**: idx 2 `calib_r_ave` `0x43ca8039`, idx 32
`TC:DIST:Err:SetDistMode1ForSync aspect` `0x43ca8547` e idx 108 `TC:DDT:Err: Osal Valloc Msg`
`0x43cb7524`. Lectura: fw3.21 **instrumenta** el módulo y añade tres trazas; el código de fondo
existe en las tres versiones y la etiqueta es **exclusiva de la A6000 fw3.21**.
## Nota de método y abierto / NO VERIFICADO
- Regla PIC **estricta** canónica (`analysis/s106_imaging_cap/scan_pic_refs_strict.py`): `add`
  emparejado con el `ldr` más cercano por detrás del mismo registro, ventana 4 KB, destino inicio
  de cadena. Escáner dirigido: **127 refs `string`, 0 discrepancias, 0 sitios ausentes**.
- Por qué idx 2/32/108 pierden sus sitios; llamada por puntero a `0x438786c4`, `0x43879204`,
  `0x438792dc`, `0x4387938e`; significado de `TC`, `DDT`, `DIST`, `STC`, `ARC`/`RC`, `Gmv`, `Lmv`;
  estructura de los publicadores en A7S/A6300; etiqueta en A7S fw3.21; pipeline interno de
  calibración/DIST/DDT/SMART ZOOM; qué estado representa `r7 == 2`; campos de `APL_*_INFO` y
  `JudgeBdroRslt`. **S51 A/B/C = NO se mantiene.**
