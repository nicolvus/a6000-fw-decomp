# ¿Puede un YC de Live View llegar a EncodeStill? — sesión 13

Alcance: análisis estático. Direcciones ELF (Ghidra = ELF + 0x10000). Contrato en `encodestill-yc-contract.md`; origen de la orden en `encodestill-command-origin.md`.

**Veredicto: NO DEMOSTRADO y NO DESCARTADO.** No hay evidencia de incompatibilidad de tipo, pero tampoco se localizó un productor que entregue un YC de Live View al pin YC del recorder. El único antecedente nativo comprobado es PbCap/edición (YC de reproducción).

## Tabla comparativa

| Propiedad | YC de Live View | EncodeStill / Execute | Compatible |
|---|---|---|---|
| Tipo de memoria | Unidad SDS de YC entregada por pines EE/Rec (`PinSend` LIRO `0x439abbfe`, «Send EEPin/RecPin») — VERIFICADO (cadenas, sfra-electronic-frame-source.md) | Handle DMM u16 + `unitType` + `unitPhyAddr`; Execute lo abre con DmmOpen — VERIFICADO | **Plausible** (ambos «YC SDS»; INFERENCIA por `InfStillEncoder/InfDecoder`). No confirmado. |
| Formato | Implícito en la unidad SDS; NO VERIFICADO | Sin campo de formato; implícito en `unitType` — VERIFICADO | Pendiente |
| Dimensiones | SFRA abre el path EE con anchos 320/640/1024 (VERIFICADO en sesiones previas); ancho/alto exactos del YC NO VERIFICADOS. Los modos del sensor (2000×570, 1996×1124…) son lectura del IMX210, **no** tamaño del YC | Canvas {w,h} u16 + región opcional; PbCap tiene cadenas 1920×1080/640×360/640×480 — relación NO verificada | Pendiente |
| Stride | NO VERIFICADO | No es un campo; NO VERIFICADO si se deriva del canvas | Pendiente |
| Colorimetría / rango Y | NO VERIFICADO | 0..3 y 0/1 obligatorios | Pendiente |
| Vida útil | El productor (ISP/dataflow) reutiliza buffers; `PinSend` libera con `FUN_43b63566(handle,-1,-1)` — VERIFICADO | Execute abre y cierra el handle al preparar; FEA lee después — NO VERIFICADO | **Riesgo**: sin copia o referencia propia, el buffer podría reciclarse |
| Quién lo entrega | EE/Rec pins | pin YC del recorder (`this+0x60`) por `PlayData` `0x2001/0x1003` | Pendiente: falta el eslabón productor→pin |

## Lo que sí se sabe de los productores

- **ObjRenderer** tiene una captura YUV propia (`MSGID_YUV_CAPTURE_START/STOP`): usa una «YUV Capture Pin», una unidad `YCC_CAP`, remuestreo SDF (`MID_SDF_REP_RESIZE_ROTATE_ACK`) y devuelve dirección, canvas, colorimetría, rango Y, offset y tamaño destino (`PARAMID_YUV_CAPTURE_*`). Son exactamente los campos del `PlayData` (VERIFICADO las cadenas; que alimente el pin del recorder es INFERENCIA).
- **ObjScalar::SequenceRecordStillImageCmd** (ruta «recordStillImage» de ScalarDaemon) empaqueta un YC de un canal STM en un `PlayData` anidado (`MakePlayDataMsg 0x3ee314`) y arma el recorder con `0x1027`. Es el único camino ya identificado que registra una imagen **externa** a través del recorder (VERIFICADO el código; fuente del canal STM NO verificada).
- **ObjScalar** también tiene `SequenceSfrSetPathJpegCmd`/`SequencePin{Open,Connect,Deliver,Notify}` (sesión anterior): puede abrir el path de SFRA como cliente interno. Que pueda recibir el YC del EE para dárselo al recorder NO está verificado.

## Preguntas del encargo

1. **Buffer exacto del frame del visor**: unidad SDS entregada por el pin EE; dirección/handle NO localizados en `libObj`.
2. **Handle**: llega dentro del mensaje de pin (`PinSend` emite `0x2009/0xb012`). NO VERIFICADO el campo.
3. **Tipo de unidad**: «YC SDS» por INFERENCIA.
4. **Compatible con `ycBufferInfo`**: plausible; sin prueba.
5. **Geometría y stride**: NO VERIFICADO.
6. **¿Se puede retener mientras MPR lo procesa?** Hay mecanismos de congelado en LIRO (`ycc_freeze`, `sds_ycc_freeze` en `SeqStillCap`), pero no para el EE de Linux. NO VERIFICADO.
7. **Reutilización del buffer por el productor**: `PinSend` lo libera tras enviar; riesgo real.
8. **Copia/referencia existente**: la captura YUV de `ObjRenderer` (`YCC_CAP` + SDF resize) es el mecanismo de copia más cercano. NO verificado en modo disparo.
9. **¿En modo foto sin Wi-Fi?** NO VERIFICADO (misma pregunta que SFRA: quién emite `SystemCmdPinConnect` para EE).
10. **¿Sin Stage_SACC ni adquisición fotográfica?** Sí en la ruta PbCap/edición (no pasa por LIRO). En disparo, NO VERIFICADO.

## Conclusión

La entrada de `EncodeStill` es un YC SDS normal; no hay un campo que un frame de Live View incumpla. Lo que falta es (a) el productor que lo entregue al pin YC del recorder en modo disparo y (b) garantizar su vida útil. Hasta verificar ambos, **no se declara compatibilidad**.

## NO VERIFICADO

Dimensiones reales del YC del EE, disposición de planos, quién conecta el EE a un consumidor local, retención del buffer, topología ObjHandover `0x2a`.

## Sesión 14 — actualización del veredicto
**Sigue NO DEMOSTRADO y NO DESCARTADO**, pero ahora con cadena concreta (`analysis/yc-pin-delivery-flow.json`).

| Eslabón | Hallazgo | Estado |
|---|---|---|
| Productor del pin YC del recorder | ObjEffect (ObjId 9) salida nº1, topología `0x2a` | VERIFICADO fila; identidad INFERENCIA fuerte |
| Quién crea `0x2a` | ModelPbCap (`0x6135dc`), RedEye, Trimming, FocusRevision; **ningún modelo de disparo localizado** | VERIFICADO |
| Entrada de ObjEffect en EE | Camera(8) o0→Effect i0 (`0xa`), o1→i1 (`0xb`); Live View solo crea `{0xa,7}` | VERIFICADO tabla |
| Formato entregado | dos unidades DMM nuevas (`0x50b3f` 1920×1080, `0xe0b00` SDS) rellenadas por SDF; cabecera SDS 0x800 B con colorimetría/yRange | VERIFICADO |
| Retención | copia dedicada del productor; el recorder no retiene; `EncodeStill` asíncrono | VERIFICADO |
| Secuencia WriteStill con entrada de Camera | no demostrado (cadena adyacente a `SequenceFactoryComponentMoviePlay`; tamaños `movieSrcSize/movieDstSize`) | NO VERIFICADO |

Respuestas a la tabla de sesión 13 que cambian: (1) **tipo de unidad**: el visor no se entrega tal cual; ObjEffect fabrica unidades `0x50b3f/0xe0b00`. (6)(7)(8) la «copia estable» existe en ObjEffect. (5) geometría: clase de tamaño ∈ {640×360, 640×480, 1920×1080}; mayor resolución respaldada **1920×1080** (solo para el destino de PbCap, no para el YC del visor). El YC del EE (320/640/1024 en SFRA) sigue sin geometría ni tipo conocidos.

## Sesión 15 — investigación en paralelo (Claude + Codex), veredicto sin cambios de fondo

Detalle completo: `docs/capture/liveview-encodestill-parallel-verdict.md`, `analysis/liveview-encodestill-crosscheck.json`.

- **NUEVO VERIFICADO**: identidad del objeto 8 = ObjCamera, antes INFERENCIA fuerte, ahora confirmada por su constructor real (ELF `0x98c380`): sus 9 pines son todos de **salida** (6 YC + STILL_DATA + SOUND + CAMERA_STATUS), cero entradas. Camera no puede recibir `YcPinReqDeliver`.
- **NUEVO VERIFICADO**: tamaños reales de los extents DMM: `0x50b3f`→`0x3fc000` B, `0xe0b00`→exactamente `0x800` B (confirma que es solo la cabecera SDS, nunca el raster), `0x220b2e`→`0x96000` B.
- **NUEVO VERIFICADO**: estructura real de `EffectInternalMode` — es un holder detrás de `GetSubState(block,1)`, no `this+0x14+4` directo. Escritor localizado (`0x173158`) con tabla `0x1025→modo`; solo los modos `{1,2,3,4,5}` producen acción real sobre `REQ_DELIVER`.
- **Sigue NO VERIFICADO**: cualquier relación entre `EffectInternalMode` y `ModelBootEE`/Live View (no se encontró ningún escritor activado desde ahí); qué modelo crea la topología `0x2a` en disparo; `unitType`/formato del YC de Camera.
- **Veredicto sin cambios**: sigue **NO DEMOSTRADO y NO DESCARTADO**. La identidad de Camera y la estructura de `EffectInternalMode` son ahora terreno firme, pero los tres bloqueos de sesión 14 (modelo que cree `0x2a` en disparo, modo de Effect compatible con entrada de Camera, tipo/formato del YC del visor) persisten.
