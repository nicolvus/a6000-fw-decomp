# S634 — etiquetas pendientes de la familia OTROS: evidencia medida de cadenas, funciones y referencias

**03-11-2026.** Documenta las 146 etiquetas del censo S178 que seguían pendientes (todas las que quedaban fuera de las familias con tres o más etiquetas). Mide, para cada una y sobre `av-cam.bin` (A6000 fw3.21, base `0x43541000`), lo que se puede comprobar con bytes; no atribuye significado a ninguna sigla ni módulo. Es el mismo criterio que los informes de evidencia de cadenas S605–S631.

Datos: [otros.json](../../analysis/s634_otros/otros.json). Generador: `analysis/camera_closure/labels.py` y `analysis/s634_otros/build_otros.py`. Prueba: [test_s634_otros.py](../../tests/test_s634_otros.py).

## Método (VERIFICADO contra bytes)

- **Cadenas:** todas las cadenas NUL-terminadas de `av-cam.bin` que contienen el token `[ETIQUETA]`.
- **Sitios:** cargas `ldr rX,[pc,#imm]` + `add rX,pc` (regla estricta del repo) cuyo destino cae en la cadena, antes o en el token.
- **Función contenedora:** primer `push {…,lr}` hacia atrás (≤ 0x2000 B). **Llamadores:** `bl`/`blx`/`b.w` directos, por patrón de halfwords. **Punteros:** literal de 32 bits (con o sin bit Thumb) / `ldr`+`add pc` en la misma función / `movw`+`movt`.
- **Fuentes:** cadenas `.cpp/.h/.c` desnudas cargadas dentro de esas funciones. **Obturador:** alcance por `bl` directo hasta profundidad 3 a las 7 funciones de obturador conocidas (C3-B, productor de `r5`, `SetExposure`, `SetRead`, constructor normal, EFCS, BULB).
- **Modelos:** coincidencias exactas del token en `av-cam.bin` de A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01.

## Resultados

| Etiqueta | Cadenas | Sitios | Funciones | `bl` | Punteros lit/pic/movw | Token A6000/A7S/A6300 | Fuentes citadas | Obturador |
|---|---:|---:|---:|---:|---|---|---|---|
| `[DECMODEMGR]` | 30 | 37 | 11 | 8 | 1/0/0 | 30/30/37 | `mcAvcDecModeMgr.cpp` | — |
| `[AVCDPRMCHK]` | 26 | 31 | 2 | 2 | 0/0/0 | 26/26/24 | `seqctrl/mcAvcDecCmdParamCheck.cpp` | — |
| `[DECVIDDISP]` | 26 | 61 | 26 | 32 | 39/0/0 | 26/26/28 | `seqctrl/video/mcAvcDecVDisplayBase.cpp` | — |
| `[ZIMA_AVCD]` | 26 | 152 | 53 | 60 | 1/0/0 | 26/26/28 | — | — |
| `[MC]` | 25 | 43 | 24 | 30 | 1/0/0 | 25/25/24 | `mcAvCtrlIf.cpp` | — |
| `[DECAUDSPDI]` | 24 | 51 | 26 | 31 | 8/0/0 | 24/24/24 | `seqctrl/audio/esAugiBuffCtrl/ac3OutOn/mcAvcDecAudioAc3Parser.cpp`, `seqctrl/audio/esAugiBuffCtrl/ac3OutOn/mcAvcDecAudioEsAugiBuffCtrlAc3OutOn.cpp`, `seqctrl/audio/esAugiBuffCtrl/ac3OutOn/mcAvcDecAudioEsSender.cpp` | — |
| `[EXCDCENCMP]` | 23 | 22 | 22 | 43 | 0/0/0 | 23/23/31 | — | — |
| `[EXL]` | 22 | 25 | 11 | 16 | 0/0/0 | 22/22/22 | — | — |
| `[VIDDECSTAT]` | 21 | 27 | 18 | 41 | 7/0/0 | 21/21/23 | `video/dec/avcDecVideoState.cpp`, `video/dec/avcDecVideoStateDecFastFlush.cpp`, `video/dec/avcDecVideoStateReady.cpp` | — |
| `[MPGPINSUPL]` | 18 | 20 | 13 | 20 | 0/0/0 | 18/18/18 | `src/common/pinSupplier/MpgPinSupplier.cpp` | — |
| `[NG]` | 18 | 24 | 7 | 8 | 0/0/0 | 18/13/13 | — | — |
| `[OPTION]` | 18 | 18 | 1 | 1 | 0/0/0 | 18/18/18 | — | — |
| `[SFR]` | 18 | 18 | 14 | 6 | 5/0/0 | 18/22/44 | `SubsystemMain.cpp` | — |
| `[AUDDECCTRL]` | 17 | 18 | 2 | 11 | 0/0/0 | 17/17/17 | `audio/dec/avcDecAudioModuleIf.cpp` | — |
| `[AG]` | 16 | 13 | 4 | 2 | 2/0/0 | 16/16/16 | — | — |
| `[VIDDECZIMA]` | 16 | 34 | 20 | 59 | 0/0/0 | 16/16/16 | `video/dec/avcDecVideoZimaAccessor.cpp` | — |
| `[CMDMLTSYNC]` | 13 | 19 | 7 | 9 | 0/0/0 | 13/13/13 | `mcCmdMultiSync.cpp` | — |
| `[DECAUDSTAT]` | 13 | 14 | 9 | 21 | 11/0/0 | 13/13/17 | — | — |
| `[UART]` | 13 | 13 | 5 | 8 | 2/0/0 | 13/0/0 | — | — |
| `[VIDDECCTRL]` | 13 | 16 | 3 | 24 | 0/0/0 | 13/13/13 | `video/dec/avcDecVideoCtrl.cpp`, `video/dec/avcDecVideoCtrlIf.cpp` | — |
| `[AUDDECSTAT]` | 12 | 18 | 9 | 3 | 6/0/0 | 12/12/22 | `audio/dec/avcDecAudioModuleStateDecNormal.cpp`, `audio/dec/avcDecAudioModuleStateDecPause.cpp`, `audio/dec/avcDecAudioModuleStateNonActive.cpp`, `audio/dec/avcDecAudioModuleStateReady.cpp` | — |
| `[BASE]` | 12 | 12 | 3 | 23 | 1/0/0 | 12/5/5 | — | — |
| `[BIN_BUFFER]` | 12 | 12 | 1 | 0 | 0/0/0 | 12/12/12 | — | — |
| `[DECVESAUGI]` | 11 | 14 | 2 | 1 | 0/0/0 | 11/11/14 | — | — |
| `[OK]` | 11 | 11 | 4 | 5 | 0/0/0 | 11/10/10 | `still_seq_panoramaStitch.cpp` | — |
| `[ES_BUFFER]` | 10 | 10 | 1 | 0 | 0/0/0 | 10/10/10 | — | — |
| `[MCCMDSENDR]` | 10 | 10 | 8 | 112 | 0/0/0 | 10/10/10 | — | — |
| `[AVC]` | 9 | 9 | 1 | 1 | 0/0/0 | 9/9/9 | `video/dec/avcDecVideoZimaAccessor.cpp` | — |
| `[EXCODECENC]` | 9 | 7 | 2 | 1 | 1/0/0 | 9/9/51 | `cdcIf/ExCodecEnc.cpp` | — |
| `[RDY]` | 9 | 10 | 6 | 13 | 2/0/0 | 9/9/11 | `video/dec/avcDecVideoStateReady.cpp` | — |
| `[DECAUDMUTE]` | 8 | 9 | 4 | 3 | 1/0/0 | 8/8/8 | — | — |
| `[EXCODECDEC]` | 8 | 16 | 14 | 22 | 8/0/0 | 8/8/12 | `cdcIf/ExCodecDec.cpp` | — |
| `[MAGIC]` | 7 | 0 | 0 | 0 | 0/0/0 | 7/7/7 | — | — |
| `[AVSCCTLYCC]` | 6 | 7 | 4 | 3 | 0/0/0 | 6/6/6 | `mcAvCtrlYcCamData.cpp` | — |
| `[DECMODEERR]` | 6 | 7 | 4 | 2 | 2/0/0 | 6/6/6 | `mcAvcDecStateDecErr.cpp` | — |
| `[EVF]` | 6 | 9 | 4 | 0 | 0/0/0 | 6/2/2 | — | — |
| `[PBX]` | 6 | 6 | 1 | 2 | 0/0/0 | 6/6/6 | — | — |
| `[SND]` | 6 | 0 | 0 | 0 | 0/0/0 | 6/6/6 | — | — |
| `[SYNCSETMODE]` | 6 | 6 | 4 | 12 | 0/0/0 | 6/6/6 | `mcSyncSetMode.cpp` | — |
| `[VIDDECPRAM]` | 6 | 8 | 5 | 5 | 0/0/0 | 6/6/6 | `video/dec/avcDecVideoParam.cpp` | — |
| `[CYCLE]` | 5 | 5 | 1 | 0 | 0/0/0 | 5/5/5 | — | — |
| `[INCDCIFCTRL]` | 5 | 5 | 3 | 8 | 0/0/0 | 5/5/5 | `cdcIf/InCdcIfCtrl.cpp` | — |
| `[MPEG2]` | 5 | 5 | 1 | 0 | 0/0/0 | 5/5/5 | — | — |
| `[SPC]` | 5 | 12 | 12 | 56 | 0/0/0 | 5/0/0 | — | — |
| `[DECAUDLPCM]` | 4 | 4 | 4 | 7 | 0/0/0 | 4/4/12 | — | — |
| `[DECSEQCTRL]` | 4 | 9 | 5 | 11 | 1/0/0 | 4/4/4 | `seqctrl/mcAvcDecSeqCtrl.cpp` | — |
| `[DFE_INT]` | 4 | 4 | 2 | 0 | 0/0/0 | 4/4/4 | — | — |
| `[ENCUSDTMGR]` | 4 | 4 | 3 | 12 | 0/0/0 | 4/4/4 | `seqCtrl/mcAvcEncUserDataMgr.cpp` | — |
| `[EXDFSENDER]` | 4 | 4 | 1 | 2 | 0/0/0 | 4/4/4 | — | — |
| `[FFLSH]` | 4 | 5 | 4 | 1 | 3/0/0 | 4/4/4 | `video/dec/avcDecVideoStateDecFastFlush.cpp` | — |
| `[MAIN]` | 4 | 8 | 7 | 7 | 0/0/0 | 4/0/0 | — | — |
| `[VFX]` | 4 | 8 | 3 | 32 | 0/0/0 | 4/4/5 | — | — |
| `[AVIO]` | 3 | 3 | 2 | 2 | 0/0/0 | 3/92/92 | — | — |
| `[AVSCCTLEFCT]` | 3 | 3 | 2 | 2 | 0/0/0 | 3/3/3 | — | — |
| `[DBG]` | 3 | 3 | 3 | 0 | 0/0/0 | 3/3/3 | — | — |
| `[DECAUDPAUS]` | 3 | 3 | 3 | 0 | 3/0/0 | 3/3/3 | — | — |
| `[ENCODE_JPEG_WITH_WORK]` | 3 | 3 | 2 | 0 | 2/0/0 | 3/3/3 | — | — |
| `[LGA]` | 3 | 3 | 2 | 3 | 0/0/0 | 3/3/3 | — | — |
| `[MCBBDLYCLC]` | 3 | 3 | 3 | 4 | 0/0/0 | 3/3/3 | — | — |
| `[MCIFINFACC]` | 3 | 3 | 3 | 2 | 0/0/0 | 3/3/3 | `mcIfInfoAccessor.cpp`, `mcIfInfoLogger.cpp` | — |
| `[PANELEVF]` | 3 | 3 | 1 | 0 | 0/1/0 | 3/3/3 | — | — |
| `[PROC]` | 3 | 3 | 2 | 1 | 0/0/0 | 3/3/3 | — | — |
| `[SIO]` | 3 | 3 | 1 | 0 | 0/1/0 | 3/3/3 | — | — |
| `[AVCMODEMGR]` | 2 | 3 | 3 | 23 | 0/0/0 | 2/2/2 | `mcAvcModeMgr.cpp` | — |
| `[BIN_LIMITER]` | 2 | 2 | 1 | 0 | 0/0/0 | 2/2/2 | — | — |
| `[CBA_FIFO]` | 2 | 2 | 1 | 0 | 0/0/0 | 2/2/2 | — | — |
| `[CORE]` | 2 | 6 | 2 | 2 | 0/0/0 | 2/2/2 | `amSensCtrlIf.cpp` | — |
| `[DECAUDSMPL]` | 2 | 2 | 1 | 5 | 0/0/0 | 2/2/2 | — | — |
| `[DECVIDPARM]` | 2 | 3 | 3 | 4 | 0/0/0 | 2/2/2 | `seqctrl/mcAvcDecParam.cpp` | — |
| `[DEC]` | 2 | 2 | 2 | 0 | 1/0/0 | 2/2/2 | — | — |
| `[DMMYSIOCOM]` | 2 | 2 | 1 | 1 | 0/0/0 | 2/2/2 | `mcDummySioCom.cpp` | — |
| `[HDMAC]` | 2 | 3 | 3 | 0 | 0/0/0 | 2/2/2 | — | — |
| `[IMCIF]` | 2 | 2 | 2 | 2 | 0/0/0 | 2/2/2 | — | — |
| `[MCUSRDEDT]` | 2 | 2 | 1 | 1 | 0/0/0 | 2/2/2 | — | — |
| `[MPGPINCONV]` | 2 | 12 | 8 | 19 | 0/0/0 | 2/2/2 | `src/common/pinSupplier/pinConverter/MpgPinConverter.cpp` | — |
| `[NTF]` | 2 | 2 | 2 | 2 | 0/0/0 | 2/2/2 | `mcPinAudioEditor.cpp` | — |
| `[PCPSTATDRM]` | 2 | 6 | 2 | 1 | 1/0/0 | 2/2/2 | `pcpCtrl/pcpCtrlStateDormant.cpp` | — |
| `[PNLEVF]` | 2 | 2 | 2 | 0 | 0/1/0 | 2/2/2 | — | — |
| `[RCV]` | 2 | 2 | 2 | 1 | 0/0/0 | 2/2/2 | — | — |
| `[STOPG]` | 2 | 2 | 2 | 0 | 1/0/0 | 2/2/2 | — | — |
| `[SYSTEM]` | 2 | 0 | 0 | 0 | 0/0/0 | 2/2/2 | — | — |
| `[TOP]` | 2 | 2 | 2 | 1 | 1/0/0 | 2/2/2 | — | — |
| `[VIDEOCOLOR]` | 2 | 3 | 3 | 9 | 0/0/0 | 2/2/2 | `seqctrl/video/mcAvcDecVideoColor.cpp` | — |
| `[WRAP]` | 2 | 0 | 0 | 0 | 0/0/0 | 2/2/2 | — | — |
| `[ABB]` | 1 | 1 | 1 | 12 | 0/0/0 | 1/1/1 | — | — |
| `[ANNOUNCE]` | 1 | 1 | 1 | 1 | 0/0/0 | 1/1/1 | `bgm/BGM.cpp` | — |
| `[AVCDECAUDES]` | 1 | 1 | 1 | 2 | 0/0/0 | 1/1/1 | — | — |
| `[AVIF]` | 1 | 3 | 3 | 72 | 0/0/0 | 1/1/1 | — | — |
| `[AVSCEVTSND]` | 1 | 1 | 1 | 8 | 0/0/0 | 1/1/1 | `mcAvscUtil/mcAvscUtilEventSender.cpp` | — |
| `[AVSC]` | 1 | 9 | 9 | 1011 | 0/0/0 | 1/1/1 | — | — |
| `[BBDELAY]` | 1 | 1 | 1 | 1 | 1/0/0 | 1/1/1 | `cdcIf/ExCodecEnc.cpp` | — |
| `[CDCCTRL]` | 1 | 1 | 1 | 3 | 0/0/0 | 1/1/1 | — | — |
| `[CDM]` | 1 | 1 | 1 | 1 | 0/0/0 | 1/1/1 | `Stage_BOKS.cpp` | — |
| `[CLKCTRL]` | 1 | 1 | 1 | 0 | 1/0/0 | 1/1/1 | `seqCtrl/video/onlyaudio/support/mcAvcEncVideoOnlyAudioSeqCtrl.cpp` | — |
| `[CODE]` | 1 | 1 | 1 | 6 | 0/0/0 | 1/1/1 | — | — |
| `[DAAUGICONV]` | 1 | 1 | 1 | 0 | 1/0/0 | 1/1/2 | — | — |
| `[DECSEQVIF]` | 1 | 1 | 1 | 1 | 0/0/0 | 1/1/1 | — | — |
| `[DIRECTCOMMAND]` | 1 | 1 | 1 | 1 | 0/0/0 | 1/1/1 | — | — |
| `[DVAUGICONV]` | 1 | 1 | 1 | 0 | 1/0/0 | 1/1/1 | — | — |
| `[DVFC]` | 1 | 1 | 1 | 5 | 0/0/0 | 1/1/1 | — | — |
| `[ENCAUDLPCM]` | 1 | 1 | 1 | 1 | 0/0/0 | 1/1/1 | `mcAvcEncLpcmBufIf.cpp` | — |
| `[ENCAUDUTIL]` | 1 | 1 | 1 | 1 | 0/0/0 | 1/1/1 | — | — |
| `[EXEC]` | 1 | 1 | 1 | 0 | 0/0/0 | 1/1/1 | — | — |
| `[GPE]` | 1 | 1 | 1 | 12 | 0/0/0 | 1/1/1 | — | — |
| `[INF]` | 1 | 1 | 1 | 4 | 0/0/0 | 1/1/1 | — | — |
| `[LIF_ERROR]` | 1 | 1 | 1 | 0 | 0/0/0 | 1/0/0 | — | — |
| `[MANU]` | 1 | 1 | 1 | 6 | 0/0/0 | 1/1/1 | — | — |
| `[MC32BTCNTR]` | 1 | 2 | 1 | 0 | 0/0/0 | 1/1/1 | — | — |
| `[MCCOUNTMGR]` | 1 | 3 | 2 | 7 | 0/0/0 | 1/1/1 | `mcUtil32BitCountMgr.cpp` | — |
| `[MCMSGPINIF]` | 1 | 2 | 2 | 2 | 0/0/0 | 1/1/1 | `mcPinIf.cpp` | — |
| `[MCMSGSTATE]` | 1 | 1 | 1 | 2 | 0/0/0 | 1/1/1 | — | — |
| `[MCS]` | 1 | 1 | 1 | 2 | 0/0/0 | 1/1/2 | — | — |
| `[MODIFY1]` | 1 | 1 | 1 | 3 | 0/0/0 | 1/1/1 | — | — |
| `[MOJITO_ERROR]` | 1 | 1 | 1 | 0 | 0/0/0 | 1/1/1 | — | — |
| `[MPGMSGSEND]` | 1 | 2 | 1 | 1 | 0/0/0 | 1/1/1 | `src/common/MpgDataFlowInfraMsgSend.cpp` | — |
| `[PCIE]` | 1 | 1 | 1 | 12 | 0/0/0 | 1/1/1 | — | — |
| `[PCP1]` | 1 | 1 | 1 | 12 | 0/0/0 | 1/1/1 | — | — |
| `[PCPSTATINI]` | 1 | 2 | 2 | 0 | 2/0/0 | 1/1/1 | `pcpCtrl/pcpCtrlStateInitialize.cpp` | — |
| `[PERI]` | 1 | 1 | 1 | 12 | 0/0/0 | 1/1/1 | — | — |
| `[PFHS]` | 1 | 0 | 0 | 0 | 0/0/0 | 1/0/0 | — | — |
| `[RC1]` | 1 | 1 | 1 | 12 | 0/0/0 | 1/1/1 | — | — |
| `[RC2]` | 1 | 1 | 1 | 12 | 0/0/0 | 1/1/1 | — | — |
| `[RCH]` | 1 | 1 | 1 | 1 | 0/0/0 | 1/1/1 | — | — |
| `[RDM]` | 1 | 1 | 1 | 1 | 0/0/0 | 1/1/1 | `Stage_BOKS.cpp` | — |
| `[REN]` | 1 | 1 | 1 | 1 | 0/0/0 | 1/1/1 | `Stage_BOKS.cpp` | — |
| `[RESET]` | 1 | 1 | 1 | 1 | 0/0/0 | 1/1/1 | — | — |
| `[RING_DIAL]` | 1 | 2 | 2 | 4 | 0/0/0 | 1/0/0 | — | — |
| `[SA1]` | 1 | 1 | 1 | 12 | 0/0/0 | 1/1/1 | — | — |
| `[SCN]` | 1 | 1 | 1 | 2 | 0/0/0 | 1/1/1 | — | — |
| `[SCN_ENCODE]` | 1 | 2 | 2 | 1 | 0/0/0 | 1/1/1 | `ModuleOnePassScnEncode.cpp`, `ModuleOnePassScnEncodeWithThm.cpp` | — |
| `[SET_DIAG_MODE]` | 1 | 1 | 1 | 1 | 0/0/0 | 1/1/2 | — | — |
| `[SE]` | 1 | 1 | 1 | 0 | 1/0/0 | 1/1/1 | — | — |
| `[SONLYAUDIO]` | 1 | 1 | 1 | 0 | 1/0/0 | 1/1/1 | `seqCtrl/video/onlyaudio/support/mcAvcEncVideoOnlyAudioSeqCtrl.cpp` | — |
| `[SPC1]` | 1 | 1 | 1 | 12 | 0/0/0 | 1/1/1 | — | — |
| `[SRC1]` | 1 | 1 | 1 | 12 | 0/0/0 | 1/1/1 | — | — |
| `[SRC2]` | 1 | 1 | 1 | 12 | 0/0/0 | 1/1/1 | — | — |
| `[SRC3]` | 1 | 1 | 1 | 12 | 0/0/0 | 1/1/1 | — | — |
| `[SRC4]` | 1 | 1 | 1 | 12 | 0/0/0 | 1/1/1 | — | — |
| `[SYS_SENSER_CA_PUTS]` | 1 | 0 | 0 | 0 | 0/0/0 | 1/1/1 | — | — |
| `[THM]` | 1 | 1 | 1 | 2 | 0/0/0 | 1/1/1 | — | — |
| `[VFX1]` | 1 | 1 | 1 | 12 | 0/0/0 | 1/1/1 | — | — |
| `[VIDENCPARAM]` | 1 | 5 | 5 | 11 | 0/0/0 | 1/1/1 | `video/enc/avcEncVideoParam.cpp` | — |
| `[VPINFO]` | 1 | 1 | 1 | 133 | 0/0/0 | 1/1/1 | — | — |
| `[WSX0]` | 1 | 1 | 1 | 12 | 0/0/0 | 1/1/1 | — | — |
| `[WSX1]` | 1 | 1 | 1 | 12 | 0/0/0 | 1/1/1 | — | — |
| `[ZIMA1]` | 1 | 1 | 1 | 12 | 0/0/0 | 1/1/1 | — | — |

Etiquetas con cadenas pero sin ningún sitio de carga: `[MAGIC]`, `[PFHS]`, `[SND]`, `[SYSTEM]`, `[SYS_SENSER_CA_PUTS]`, `[WRAP]`. Ninguna de las 146 alcanza por `bl` directo (profundidad ≤ 3) una de las 7 funciones de obturador conocidas: se cumple; [S51](s51-decision.md) se mantiene.

## Alcance

Los nombres de las etiquetas son texto del firmware. Este informe no afirma qué hace cada módulo, ni expande siglas, ni compara cuerpos de función entre modelos (solo la presencia del token), ni sigue llamadas indirectas (vtable, tablas indexadas o registros calculados). No se ejecutó firmware.

## Reproducción

```bash
.venv/bin/python analysis/camera_closure/run_labels.py
.venv/bin/python analysis/s634_otros/build_otros.py
.venv/bin/python -m pytest -q tests/test_s634_otros.py
```
