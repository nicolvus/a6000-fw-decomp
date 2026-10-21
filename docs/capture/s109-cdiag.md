# S109 — `[CDIAG]`: el banco de diagnóstico del códec de la A6000

**Línea de ingeniería inversa general** (no afecta al obturador electrónico: S51 sigue con
A/B/C = NO — en las 270 trazas no aparece ni una vez `shutter`, `silent`, `EFCS`, `curtain`,
`mechan`, `imager`, `sensor` ni `dmm`).

Informe: [analysis/s109_cdiag/cdiag.md](../../analysis/s109_cdiag/cdiag.md) · Datos:
`analysis/s109_cdiag/cdiag.json` · Diferencial: `cdiag_diff.json` ·
Test: `tests/test_s109_cdiag.py` (22 tests).

## Hallazgo central

`[CDIAG]` es el **subsistema de diagnóstico del códec**: por comando remoto pide al
codificador (AVC HD/SD y JPEG) que codifique o decodifique datos de prueba guardados en
fichero y comprueba **byte a byte** que el resultado coincide con el esperado.

- **270 apariciones** del token `[CDIAG]` en `0x43c3b0d4`–`0x43c3e86a` (255 empiezan por
  `[CDIAG]`, 15 llevan `[ERR][CDIAG]`).
- **16 clases** (`CdCtrlIf`, `CdCtrlCore`, `CdCtrl{HdDec,HdRec,JpgDec,JpgEnc,JpgEncDec,
  SdDec,SdRec}`, `CdMemCtrl`, `CdUtil{ClkCtrl,CmpData,SysvMsg}`, `CdMsgIf`, `CdMsgCore`,
  `CdTskCore`) y **2 ficheros fuente**: `cdCtrlIf.cpp` (`0x43c3b1a8`), `cdCtrlCore.cpp`
  (`0x43c3b86c`).
- **7 escenarios**: `HD REC`, `HD DEC`, `SD REC`, `SD DEC`, `JPEG ENC`, `JPEG DEC`,
  `JPEG ENCDEC`; **8 operaciones**: `DbgDiagAvc`, `ConfirmDoneCodec`, `CmpData`, `RunCodec`,
  `RelMemArea`, `SetMemArea`, `SetData`, `SetDiagMode`.
- Comparador de 3 pasos (`0x43c3e6dc`–`0x43c3e86a`), memoria (`CdMemCtrl`:
  `MEM ALLOC/SHARE/FREE`, `unitHandle`, `unitType`), reloj (`CdUtilClkCtrl`: `ClkState
  IDLE->OPEN`…`CLOSE->IDLE`, `PAL(50i)/NTSC(60i) MODE Clk`) y sincronismo vertical
  (`CdUtilSysvMsg`: `Reg/UnReg SysV`, `[VSYNC] RUN CODEC INIT`).

## Qué se ha reconstruido (verificado contra bytes)

1. **Sub-bloques**: `[TSK]`(1), `[TSKCORE]`(1), `[CTRLIF]`(19), `[CTRLCORE]`(49),
   `[CTRLHDDEC]`(26), `[CTRLHDREC]`(27), `[CTRLJPGDEC]`(21), `[CTRLJPGENC]`(21),
   `[CTRLJPGENCDEC]`(22), `[CTRLSDDEC]`(26), `[CTRLSDREC]`(27), `[CMPDATA]`(16).
2. **27 firmas de función** embebidas (`CDIAGER CdCtrlCore::CmpData(...)`); el tipo
   `DIAGINFO*` lleva `fileId`, `memIdx`, `unitHandle`, `unitType` y `size`.
3. **Tabla de registro de clases**: `0x43fda6a0`, 16 pares `{vptr, nombre}`; la **misma**
   tabla está en la A7S en `0x43fdb6ec`; en la A6300 en `0x4419b094` con **20** entradas.
4. **Transporte**: `OsalRequestPacket`/`OsalResponsePacket`, mensaje propio
   `CdCtrlIf::MSG_SENS_COMMAND*`, **15 nombres `SENS_*`** y la infra `DataflowInfra*`.
5. **API OSAL** (por las trazas de error de `[CLK_CTRL]`): `osal_try_valloc_msg` `0x435612d0`,
   `osal_snd_msg` `0x4356120c`, `osal_free_msg` `0x435612ec`, `osal_rcv_msg` `0x43561260`;
   el núcleo de la tarea (`0x435a1318`) llega a `osal_rcv_msg` vía `0x435a9f4c`.
6. **Escritor de trazas**: formateador variádico `0x435ab880` (310 llamadas), búfer de
   128 B, `vsnprintf` (`bl 0x439c5004`), nivel `0xbe` e id de módulo `0xbad`.
7. **Referencias** (esquema **PIC**, `destino = literal + (add + 4)`): **226 de las 255**
   cadenas referenciadas; las **29** restantes sin referencia PIC **ni puntero absoluto**
   → cadenas muertas (25 `ClkState`/`ClkType` de los controladores JPEG + 4 `MEM SHARE err`).
8. **Diferencial A7S fw3.20**: **idéntico** — las **270 cadenas coinciden literalmente**
   (0 exclusivas), mismas 16 clases, 2 ficheros y 27 firmas. La A6300 fw2.01 tiene 310
   tokens = las 270 comunes + **40 de 4K** (`[CDIAG][CTRL4KREC]`, `CdCtrl4KDec/Rec`, `CdExt*`).

## Abierto / NO VERIFICADO

Fichero fuente de las clases de códec y de las utilidades · formato binario de
`MSG_SENS_COMMAND`, `DIAGINFO` y los mensajes `SENS_*` · codificación numérica de `cmd`,
`mode` y `func` · quién emite los comandos `SENS_*` · si `[CodecSeq]` (`0x43c3e8bb`) forma
parte de `[CDIAG]`. Scripts: `analysis/s109_cdiag/` (`scan_cdiag.py`, `scan_diff.py`,
`scan_class_table.py`, `scan_cdiag_refs.py`, `scan_unreferenced.py`, `disasm.py`).
