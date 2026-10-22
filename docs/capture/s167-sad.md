# S167 — el módulo `[SAD]` (45 cadenas / 44 trazas) — fw3.21 de la A6000
> Línea de RE general. Sólo bytes; vaddr = `0x43541000 + file_offset`.
> Regla de referencias: **PIC estricta** (canónica del repo, S106).

## Qué es
`[SAD]` es el **rótulo de diagnóstico de la biblioteca "SA driver"** del subsistema
`NS_SCALAR_INFRA` (el mismo de `[SFRA]`/`[SFRS]`, S118/S116). **La sigla no se expande en
ningún byte** → **sin desarrollar** (NO VERIFICADO).
* Emisor en `0x43990000`–`0x439a1800`: allí sólo se emiten `[SIO]` (3) y `[SAD]` (45).
* RTTI vecinos: `…ScalarInfraSequenceIf` `0x43ce59d2`, `…ScalarInfraSequenceSa` `0x43ce6bea`,
  `…ScalarInfraSequenceSaStageAutoexec_sadone` `0x43ce7004`; ficheros de la capa de **secuencia**
  (por encima): `ScalarInfraSequenceSa.cpp` `0x43ce6c15` (10 sitios),
  `ScalarInfraSequenceSaStage.cpp` `0x43ce6e16` (6). **El fichero propio de `[SAD]` no está
  embebido** (verificado con regla estricta *y* ancha).
* Canal de log **propio**: impresor `0x439a10f0`, id de mensaje OSAL `0x93` (147), frente al
  logger global `0x435ab880` de `[SFRA]`/`[SFRS]` → módulo independiente.

## Cifras
**45** cadenas `[SAD]` (`0x43ce546b`–`0x43ce59c1`; bloques 3+3+39, con 3 cadenas de programa
SA intercaladas; 44 con texto + el token suelto `[SAD] ` `0x43ce56b3`) · **49** sitios de
emisión · **5** emisores (`0x43998578` 3, `0x4399d464` 1, `0x4399d528` 1, `0x4399d618` 1,
`0x439a119c` **43**) · **0** sin referencia · **49/49** pares PIC verificados a mano ·
**0** discrepancias con el mapa global del repo.

## Contenido
* `0x43998578` — `Same Unit Handle Get`/`same hndl get_cnt`/`alloc_cnt`: recorre dos tablas
  de *u16* (`0x43f85932`: 32 entradas; `0x43f84bfe`: 255) e invalida la coincidencia
  (`0xFFFF`); contadores `0x43f84bfc`, `0x43f84bf4`, `0x43f31368`, `0x43f31364`. Usa el gestor
  de memoria (`bl 0x43b61cb2`) → **`[CAM_DMM]` (S113)**.
* `0x4399d464`/`0x4399d528`/`0x4399d618` — validadores de cabecera de programa SA
  (`CdcSaPrg`/`NmlSaPrg`/`RsdSaPrg`): error `0x0d` (13) (`0x0c`=12 en el tercero) y byte
  "informar una sola vez" compartido `0x43e211c8`.
* `0x439a119c` — **volcado de estado** por comando: exige `ldrh [r0+2] == 0x9548`
  (`movw r3,#0x9548` en `0x439a119e`), `byte [r0+4] == 1`, `byte [r0+5] ∈ 1..6` (`tbh`
  `0x439a11cc`, tabla `0x439a11d0` → 6 casos en `0x439a11dc`, `0x439a126c`, `0x439a13f2`,
  `0x439a14ae`, `0x439a14c0`, `0x439a1536`): `CfgStatePrt` (ZmCfg/SaCfg), `FifoStatePrt`/
  `FifoDataPrt` (FIFO JPEG: punteros escritura/lectura y nº en cola; colas `JpgNrm`,`JpgSrt`),
  `CalcTimePrt`/`CalcTimeSum`, `DdsDataAdd`, `SaProgHdr` (PrgID + 4 palabras) y recuento de
  handles del DMM; `bhi`→`data1=other` (`0x43ce59af`), `bne`→`SelCodeErr` (`0x43ce59c1`).
  Puntero embebido: `ldr r3,[pc,#0x3e4]` (`0x439a11ac`) → `0x43ce5644` = `"PEG_DEC"`
  (`SA_JPEG_DEC`+4), para comparar el nombre del programa recibido.
* Programas/versiones SA: `SA_PREINSTALLED_PRG:` `0x43ce561f` (`0x4399ee6a`), `SA_JPEG_ENC`
  `0x43ce5634` (`0x4399eefa`), `SA_JPEG_DEC` `0x43ce5640` (`0x4399ef0e`); tabla de versiones
  `0x43ce5402`–`0x43ce5445` (SA0, SA1, SA5, ZMA0, ZMA1, todos `V1.0`), comparada 16 bytes
  contra `0x43f2ef58`/`0x43f2ef68`/`0x43f2ef78`.

## Diferencial (A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01)
* `[SAD]`: **45 | 0 | 0**; tokens `SaProgHdr`, `CdcSaPrg`, `NmlSaPrg`, `RsdSaPrg`,
  `JpgNrm/Srt`, `OpnCmd`, `SelCode`, `DdsDataAdd`, `Hdr Err`, `DbgPrt`: presentes | **0** | **0**.
* Infraestructura "SA" (`SA_PREINSTALLED_PRG:`, `SA_JPEG_ENC/DEC`, `SA_EXEC_PROGRAM_*`,
  `ScalarInfraSequenceSa*.cpp`): 1 | 1 | 1. → La **capa de diagnóstico `[SAD]` es una adición
  de la fw3.21 de la A6000**; en la A7S el código equivalente (`0x4398ecd0`/`0x43986100`) es
  **otro código**, no el mismo sin trazas. Salvedad S130 §4: la comparación mezcla versión y
  modelo (no hay fw anterior de la A6000).

## Línea del obturador
**Negativo verificado**: 0 apariciones de `shut`, `silent`, `electro`, `mech`, `sensor`,
`imager`, `expo`, `readout`, `drive`, `focus`, `iso` en las 45 trazas (y en las 65 cadenas de
la biblioteca). Lo único del dominio de imagen es `jpg` (`JpgNrm`/`JpgSrt`).
**Sin efecto en S51 (A/B/C = NO).**

## Entregables / NO VERIFICADO
`analysis/s167_sad/sad.md` · `sad.json` · `s167_*.py` · `tests/test_s167_sad.py` (104 tests) +
`tests/test_s167_sad_indep.py` (17 tests, bytes). **NO VERIFICADO**: expansión de la sigla
"SAD"; fichero fuente propio; sentido de `DdsDataAdd`/`SelCode`/`ZmCfg`; `0x9548`/`0x93`.
