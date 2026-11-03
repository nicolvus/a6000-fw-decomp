# S178 — inventario de etiquetas pendientes y descartadas

Generado por `audit_pending.py`; direcciones, textos completos y referencias por ocurrencia en [pendientes_auditados.json](pendientes_auditados.json). Prioridad 0: captura/sensor; 1: sincronización/visor; 2: resto. Dentro de cada grupo: cadenas contenedoras con PIC candidato descendentes y etiqueta. La prioridad expresa una hipótesis de selección, no identidad funcional.

ACEPTO acepta un candidato a módulo; no cierra su decodificación. RECHAZO se contabiliza fuera de cobertura. NO_VERIFICADO conserva la investigación abierta. Las referencias PIC son candidatas hasta contrastar instrucciones y pools.

| Etiqueta | Prioridad | Cadenas contenedoras con PIC candidato | Candidato | Estado | Motivo |
|---|---:|---:|---|---|---|
| `[EXL]` | 0 | 20 | ACEPTO | pendiente | Prefijo de diagnóstico initCamdcv con referencia PIC comprobada; relación con muestreo de imagen sugerida por el texto, semántica funcional pendiente. |
| `[SFR]` | 0 | 16 | ACEPTO | pendiente | Prefijo de diagnóstico Recieve CpuSelectComp con referencia PIC comprobada; identidad funcional y relación con [SFRA]/[SFRS] pendientes. |
| `[SYS_SENSER_CA_PUTS]` | 0 | 0 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[CMDMLTSYNC]` | 1 | 11 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[EVF]` | 1 | 6 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[SYNCSETMODE]` | 1 | 6 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[PANELEVF]` | 1 | 3 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[PNLEVF]` | 1 | 2 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[DECMODEMGR]` | 2 | 30 | ACEPTO | pendiente | Prefijo de diagnóstico SetState con referencia PIC comprobada; se prioriza por sus 30 cadenas históricas, sin demostrar función ni relación con obturador. |
| `[AVCDPRMCHK]` | 2 | 26 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[DECVIDDISP]` | 2 | 26 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[MC]` | 2 | 25 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[ZIMA_AVCD]` | 2 | 25 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[DECAUDSPDI]` | 2 | 24 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[EXCDCENCMP]` | 2 | 22 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[VIDDECSTAT]` | 2 | 21 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[NG]` | 2 | 18 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[OPTION]` | 2 | 18 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[AUDDECCTRL]` | 2 | 17 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[MPGPINSUPL]` | 2 | 16 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[VIDDECZIMA]` | 2 | 16 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[DECAUDSTAT]` | 2 | 13 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[UART]` | 2 | 13 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[VIDDECCTRL]` | 2 | 13 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[AG]` | 2 | 12 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[AUDDECSTAT]` | 2 | 12 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[BASE]` | 2 | 12 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[BIN_BUFFER]` | 2 | 12 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[DECVESAUGI]` | 2 | 11 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[ES_BUFFER]` | 2 | 10 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[MCCMDSENDR]` | 2 | 10 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[OK]` | 2 | 10 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[AVC]` | 2 | 9 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[RDY]` | 2 | 9 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[DECAUDMUTE]` | 2 | 8 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[EXCODECDEC]` | 2 | 8 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[EXCODECENC]` | 2 | 7 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[AVSCCTLYCC]` | 2 | 6 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[DECMODEERR]` | 2 | 6 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[PBX]` | 2 | 6 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[VIDDECPRAM]` | 2 | 6 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[CYCLE]` | 2 | 5 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[INCDCIFCTRL]` | 2 | 5 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[MPEG2]` | 2 | 5 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[SPC]` | 2 | 5 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[DECAUDLPCM]` | 2 | 4 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[DECSEQCTRL]` | 2 | 4 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[DFE_INT]` | 2 | 4 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[ENCUSDTMGR]` | 2 | 4 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[EXDFSENDER]` | 2 | 4 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[FFLSH]` | 2 | 4 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[MAIN]` | 2 | 4 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[VFX]` | 2 | 4 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[AVIO]` | 2 | 3 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[AVSCCTLEFCT]` | 2 | 3 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[DBG]` | 2 | 3 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[DECAUDPAUS]` | 2 | 3 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[ENCODE_JPEG_WITH_WORK]` | 2 | 3 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[LGA]` | 2 | 3 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[MCBBDLYCLC]` | 2 | 3 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[MCIFINFACC]` | 2 | 3 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[PROC]` | 2 | 3 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[SIO]` | 2 | 3 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[STK_AUTO_SAL]` | 2 | 3 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[AVCMODEMGR]` | 2 | 2 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[BIN_LIMITER]` | 2 | 2 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[CBA_FIFO]` | 2 | 2 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[CORE]` | 2 | 2 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[DECAUDSMPL]` | 2 | 2 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[DECVIDPARM]` | 2 | 2 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[DEC]` | 2 | 2 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[DMMYSIOCOM]` | 2 | 2 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[HDMAC]` | 2 | 2 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[IMCIF]` | 2 | 2 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[MCUSRDEDT]` | 2 | 2 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[NTF]` | 2 | 2 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[PCPSTATDRM]` | 2 | 2 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[RCV]` | 2 | 2 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[STK_COLOR_SIM]` | 2 | 2 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[STK_TOUCH_SIM]` | 2 | 2 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[STOPG]` | 2 | 2 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[TOP]` | 2 | 2 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[VIDEOCOLOR]` | 2 | 2 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[ABB]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[ANNOUNCE]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[AVCDECAUDES]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[AVIF]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[AVSCEVTSND]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[AVSC]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[BBDELAY]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[CDCCTRL]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[CDM]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[CLKCTRL]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[CODE]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[D0]` | 2 | 1 | RECHAZO | no-modulo | Campo de dato :%04x dentro de una traza [CAM_UTIL_ADJ]; no es prefijo de módulo. |
| `[D1]` | 2 | 1 | RECHAZO | no-modulo | Campo de dato :%04x dentro de una traza [CAM_UTIL_ADJ]; no es prefijo de módulo. |
| `[D2]` | 2 | 1 | RECHAZO | no-modulo | Campo de dato :%04x dentro de una traza [CAM_UTIL_ADJ]; no es prefijo de módulo. |
| `[D3]` | 2 | 1 | RECHAZO | no-modulo | Campo de dato :%04x dentro de una traza [CAM_UTIL_ADJ]; no es prefijo de módulo. |
| `[D4]` | 2 | 1 | RECHAZO | no-modulo | Campo de dato :%04x dentro de una traza [CAM_UTIL_ADJ]; no es prefijo de módulo. |
| `[D5]` | 2 | 1 | RECHAZO | no-modulo | Campo de dato :%04x dentro de una traza [CAM_UTIL_ADJ]; no es prefijo de módulo. |
| `[D6]` | 2 | 1 | RECHAZO | no-modulo | Campo de dato :%04x dentro de una traza [CAM_UTIL_ADJ]; no es prefijo de módulo. |
| `[D7]` | 2 | 1 | RECHAZO | no-modulo | Campo de dato :%04x dentro de una traza [CAM_UTIL_ADJ]; no es prefijo de módulo. |
| `[DAAUGICONV]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[DECSEQVIF]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[DIRECTCOMMAND]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[DVAUGICONV]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[DVFC]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[ENCAUDLPCM]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[ENCAUDUTIL]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[EXEC]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[GPE]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[INF]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[LIF_ERROR]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[MANU]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[MC32BTCNTR]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[MCCOUNTMGR]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[MCMSGPINIF]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[MCMSGSTATE]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[MCS]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[MODIFY1]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[MOJITO_ERROR]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[MPGMSGSEND]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[MPGPINCONV]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[PCIE]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[PCP1]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[PCPSTATINI]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[PERI]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[RC1]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[RC2]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[RCH]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[RDM]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[REN]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[RESET]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[RING_DIAL]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[SA1]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[SCN]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[SCN_ENCODE]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[SET_DIAG_MODE]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[SE]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[SONLYAUDIO]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[SPC1]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[SRC1]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[SRC2]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[SRC3]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[SRC4]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[STK_C_SIM]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[STK_T_SIM]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[THM]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[VFX1]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[VIDENCPARAM]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[VPINFO]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[WSX0]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[WSX1]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[ZIMA1]` | 2 | 1 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[MAGIC]` | 2 | 0 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[PFHS]` | 2 | 0 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[SND]` | 2 | 0 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[SYSTEM]` | 2 | 0 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
| `[WRAP]` | 2 | 0 | NO_VERIFICADO | pendiente | Sin revisión individual de instrucciones: token y referencias PIC no prueban un módulo. |
