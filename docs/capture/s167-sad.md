# S167 — el módulo `[SAD]` (44 trazas) del firmware A6000 fw3.21
> Sólo bytes; vaddr = `0x43541000 + file_offset`. Regla de referencias: **PIC estricta** (S106).

## Qué es
`[SAD]` es el **rótulo de diagnóstico del subsistema «SA»** (acelerador escalar) del bloque
`NS_SCALAR_INFRA` (el de `[SFRA]`/`[SFRS]`, S118/S116). Vuelca configuración, estado y datos
de la FIFO de JPEG, tiempos de cálculo, cabeceras de programa SA (`SaProgHdr`) y handles
de unidad/DMM. **La sigla no se expande en ningún byte** → **sin desarrollar** (NO VERIFICADO).
* Las 45 cadenas están en **3 bloques** de `.rodata` (no contiguas): A `0x43ce546b`–`0x43ce54bb`
  (3), B `0x43ce55bc`–`0x43ce5618` (3), C `0x43ce564c`–`0x43ce59d1` (39); entre ellos, una
  tabla de índices ajena al módulo (256 B) y las 3 cadenas de programa SA.
* Fichero fuente propio: **NO VERIFICADO** (las 5 funciones no imprimen `file=%s`). Vecinos:
  `ScalarInfraSequenceSa.cpp` `0x43ce6c15` (10 sitios), `ScalarInfraSequenceSaStage.cpp`
  `0x43ce6e16` (6), `ScalarInfraAsyncMain.cpp` `0x43ce59fd` (3).
* Canal de log **propio**: impresor `0x439a10f0` (id `0x93`, tamaño `0x9a`,
  `osal_try_valloc_msg` `0x435612d0`), frente al logger global `0x435ab880` de `[SFRA]`/`[SFRS]`.

## Cifras (124 tests, `tests/test_s167_sad.py` 106 + `tests/test_s167_sad_indep.py` 18)
**45** cadenas `[SAD]` (44 con mensaje + el token suelto `[SAD] ` `0x43ce56b3`) ·
**49** sitios de emisión · **5** emisores (`0x43998578` 3, `0x4399d464`/`0x4399d528`/
`0x4399d618` 1 cada uno, despachador `0x439a119c` **43**) · **0** sin referencia ·
**49/49** pares PIC verificados a mano · **0** discrepancias con el mapa global del repo.

## Contenido
* `0x43998578` — recorre dos tablas de *u16* (**255** entradas `0x43f84bfe`, **32** en
  `0x43f85932`), invalida la coincidencia con `0xFFFF`; contadores `0x43f31368` (u32) y
  `0x43f84bfc` (u16); usa `bl 0x43b61cb2` → **`[CAM_DMM]` (S113)**.
* `0x4399d464`/`0x4399d528`/`0x4399d618` — validadores de cabecera SA (`CdcSaPrg`/`NmlSaPrg`/
  `RsdSaPrg`); error `0x0d` (`0x0c` en el tercero); 12 / 5 / 4 llamadores `bl`.
* `0x439a119c` — volcado por comando: exige `ldrh [r0+2] == 0x9548` (`movw r3,#0x9548`
  `0x439a119e`), `byte [r0+4] == 1`, `byte [r0+5] ∈ 1..6` (tabla `tbh` `0x439a11d0` → casos
  `0x439a11dc`, `0x439a126c`, `0x439a13f2`, `0x439a14ae`, `0x439a14c0`, `0x439a1536`):
  `CfgStatePrt`, `FifoStatePrt`/`FifoDataPrt`, `CalcTimePrt`/`CalcTimeSum`, `DdsDataAdd`,
  `SaProgHdr`, recuento de handles. Errores: `bhi`→`data1=other` `0x43ce59af`,
  `bne`→`SelCodeErr` `0x43ce59c1`. Único llamador `bl` `0x4399b5ac` (dispatcher padre
  `0x4399b074`, registrado como handler en `0x43fd2a88`).
* Programas SA: `SA_PREINSTALLED_PRG:` `0x43ce561f`, `SA_JPEG_ENC` `0x43ce5634`,
  `SA_JPEG_DEC` `0x43ce5640`; tabla de versiones `0x43ce5402`–`0x43ce5445` (SA0/SA1/SA5/
  ZMA0/ZMA1, todos `V1.0`), comparada 16 B contra `0x43f2ef7c`/`0x43f2ef6e`/`0x43f2ef5c`/
  `0x43f2ef8c`.

## Diferencial (A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01)
* `[SAD]`: **45 | 0 | 0**. Contenido (`DbgPrt`, `CfgStatePrt`, `FifoStatePrt`, `SaProgHdr`,
  `CdcSaPrg`, `JpgNrm`, `SelCode`, `DdsDataAdd`, …): presente | **0** | **0** → **adición
  de la fw3.21 de la A6000**, no un renombrado.
* Infraestructura SA (`SA_PREINSTALLED_PRG:`, `SA_JPEG_ENC/DEC`, `ScalarInfraSequenceSa*.cpp`):
  1 | 1 | 1 → la biblioteca SA es común; lo propio es la instrumentación.
* **Hallazgo de bytes**: la tabla de 300 B que en A7S (`0x43cda6ef`) y A6300 (`0x43df89bc`)
  ocupa el hueco tiene en la A6000 (`0x43ce5445`) la **cabecera de 27 B idéntica** y la
  **tabla de 25 índices `0x03`–`0x1b` idéntica byte a byte** (`0x43ce54bc`–`0x43ce55bb` frente
  a `0x43cda716`–`0x43cda816`), pero las **44 cadenas `[SAD]` están intercaladas** en ella,
  partiéndola en 3 bloques → la instrumentación se ha **insertado** en el driver SA.
* Salvedad S130 §4: la comparación mezcla versión y modelo.

## Línea del obturador
**Negativo verificado**: 0 de `shutter`/`silent`/`obtur`/`expos`/`imager`/`sensor`/`readout`/
`drive`/`brack`/`sweep`/`interval`/`still`/`movie`/`focus`/`aperture`/`iso` en las 45 cadenas.
Lo único del dominio de imagen es `jpg` (`JpgNrm`/`JpgSrt` = **índices de la cola FIFO**, no
capturas). **Sin efecto en S51 (A/B/C = NO).**

## Entregables / NO VERIFICADO
`analysis/s167_sad/sad.md` · `sad.json` · `s167_*.py` · `tests/test_s167_sad.py` (106) +
`tests/test_s167_sad_indep.py` (18). **NO VERIFICADO**: expansión de la sigla "SAD"; fichero
fuente propio; sentido de `Cdc/Nml/RsdSaPrg`, `DdsDataAdd`, `SelCode`, `ZmCfg`/`SaCfg`; qué
es la «unit» y el «Dmm»; semántica de los 6 subcomandos y quién envía el mensaje `0x9548`;
código homólogo en A7S/A6300 (las direcciones homónimas contienen otra cosa).