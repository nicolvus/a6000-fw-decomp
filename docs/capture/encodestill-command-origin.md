# Origen de la orden 0x10000005 (Execute / EncodeStill) — sesión 13

Alcance: análisis estático de `libObj.so` fw 3.21. Direcciones ELF (Ghidra = ELF + 0x10000). Datos estructurados en `analysis/encodestill-command-flow.json`.

## Resultado central

**No existe un remitente externo de `0x10000005`.** La orden `MSGID_RECORD_IMAGE_CALL` la crea `ObjStillRecorder` *a sí mismo* cuando su pin YC recibe un `PlayData`. Lo que pone en marcha todo es otra orden, `MSGID_RECORD_IMAGE_CMD` (categoría `0x3500`, id `0x3001`, parámetro `0x1005` = modo), que emiten **modelos de UI de reproducción y edición** (`ModelPbCap`, `ModelPaint`) o la consola de mantenimiento.

Consecuencia: `Execute`/`EncodeStill` es la ruta de **PbCap (captura de fotograma en reproducción) y de edición** (Trim, RedEye, Focus, Paint, Art, Beauty). **No** es la ruta de captura normal, que sigue siendo LIRO → `0x1006` → Pool (arquitectura A).

## Cadena completa

| # | Actor | Dirección ELF | Qué hace | Estado |
|---|---|---|---|---|
| 1 | `ModelPbCap` | `0x6137b0` | `ObjMsg(0x3500,0x3001){0x1005=0}` y `MWF::ObjIf::IssueCommandAsync(*(this+0x9c),msg)` (`0x6137ec`) | VERIFICADO |
| 1 | `ModelPaint` | `0x611074` | mismo mensaje con `0x1005=4`; lo pasa al ayudante `0x6104f6(this,msg,0xb)` | VERIFICADO |
| 1 | consola `ObjStillRecorderMcmd` | `0x901504` | `RecordImage <Pbcap/Trim/RedEye/Focus/Paint/Art/Beauty>` → mismo mensaje con índice 0..6 | VERIFICADO |
| 2 | MWF (`libMWF.so`) | — | enruta por categoría `0x3500` = `CATEID_STILL_RECORDER` | VERIFICADO (tabla `libSysDef`) / INFERENCIA (el enrutado) |
| 3 | `ExecFuncPoint` | `0x90d7e8`, caso `0x3001` en `0x90dd6c` | comprueba (`0x91939c`) y llama a `YcPinReqDeliver` | VERIFICADO |
| 4 | `YcPinReqDeliver` | `0x90a668` | `ObjMsg(0x2000,0x1011){0x1022=true,0x1024=false,0x1025,0x1026,0x131a}` por el pin YC (`this+0x60`) | VERIFICADO (código) / INFERENCIA (semántica: «pide que me entregues un YC») |
| 5 | **productor del YC** | — | entrega `ObjMsg(0x2001,0x1003)` = `PlayData` | **NO VERIFICADO quién** |
| 6 | manejador de pin | `0x919ca0`, rama `0x919f1a` | `GetMessageId==0x1003` → `ObjMsg(0x3500,0x10000005){0x10000006=msg recibido, 0x1000, 0x1012}` y lo publica en `this+0x18` | VERIFICADO |
| 7 | tabla de estados | fila `0x101f118` (id `0x10000005`) | `ExecFuncPoint` caso `0x90de1e` → `Execute` | VERIFICADO |
| 8 | `Execute` | `0x90b248` | reserva salidas, `EncodeStill`, Pool, `RecordStill` → `WriteStill` | VERIFICADO (sesión 12) |

Modos (`this+0x128`, parámetro `0x1005`): `0 Pbcap`, `1 Trim`, `2 RedEye`, `3 Focus`, `4 Paint`, `5 Art`, `6 Beauty`. El orden sale de la ayuda de consola (INFERENCIA fuerte); `ModelPbCap` envía 0 y `ModelPaint` envía 4 (VERIFICADO).

## Respuestas a las diez preguntas

1. **¿Quién crea el mensaje?** `0x3001`: `ModelPbCap`/`ModelPaint`/consola. `0x10000005`: el propio recorder (`0x919f1a`).
2. **¿En qué estado de cámara?** Reproducción/edición (PbCap, Paint). INFERENCIA por nombres de modelo (`[M_PbCap]`, `M_PanoramaPb`, `UnreadyPbCap`).
3. **¿Qué evento?** La acción del usuario en la UI de PbCap/Paint. El disparador de `0x6137b0` (vtable o acción de estado) NO está localizado.
4. **¿Qué proceso lo envía?** `libObj` por `MWF::ObjIf::IssueCommandAsync/Sync`; el recorder responde a su cliente por `this+0x18`.
5. **¿De dónde sale el handle YC?** Del `PlayData` que entrega el par conectado al pin YC. En PbCap el candidato es la captura YUV de `ObjRenderer` (devuelve dirección, canvas, colorimetría, rango Y, offset y tamaño destino) — INFERENCIA, no confirmada.
6. **¿Cómo se fijan las dimensiones?** Canvas/región vienen en `0x1036/0x1037/0x1038` del `PlayData`. El recorder además pide una clase de tamaño con `0x1026 = tabla[this+0x12c]` (≤4).
7. **¿De dónde vienen CamInfo y EXIF?** Del grupo `0x1041` del `PlayData` (`0x1042` Exif, `0x1043` GPS, `0x1044` CamInfo, `0x1046` fecha). Quién lo rellena NO está verificado.
8. **¿Qué se prepara antes?** `0x2001` hacia `0x3500` (activar recorder, INFERENCIA), comando previo a `CntMgr` (`0x3700/0x102a`) en PbCap, ajuste de medios.
9. **¿Qué respuesta espera?** `0x3500/0x3002` con `0x1001` = resultado (ruta `0x90ddcc`), y al final de `Execute` otra `0x3500/0x3002` con `0x1001` y `0x100f`.
10. **¿Depende de una captura mecánica previa?** No en esta ruta: ni LIRO ni `SeqStillCap` intervienen (VERIFICADO por ausencia en la cadena). Sí depende de que haya un productor de YC y de que el medio no esté en `None`.

## Correcciones a sesiones anteriores

- El «modo 4» de `this+0x128` (sesiones 10–11) es `RecordImageMode = Paint`, y lo fija `0x1027` de `ObjScalar::SequenceRecordStillImageCmd`. Es distinto de `MediaMgr+0x2C = 4` (`None`).
- La sesión 12 decía «remitente no encontrado»: no hay remitente externo del `0x10000005` porque no viaja entre objetos; el que sí tiene remitente es el `0x3001`.

## Otras observaciones útiles

- `ObjScalar::SequenceRecordStillImageCmd::Begin` (`0x3d2ef8`) arma `ObjMsg(0x2001,0x1027){0x131f ticket, 0x1320 PlayData anidado}` por el pin 6; el recorder lo trata en `0x919ca0` y devuelve `0x3500/0x1000000f`. `MakePlayDataMsg` (`0x3ee314`) construye `ObjMsg(0x2001,0x1003)` con subobjetos `0x1007→0x1031`, `0x1008→0x1017`, `0x1009→0x1041`.
- Constructores de `PlayData` (`0x2001/0x1003`) hay en objetos Infra* (`0x14c388…0x209e00`), `ObjMovieRecorder` (`0x88bb7a…0x8eeef0`) y `ObjScalar` (`0x3ee474`); **no** en `ObjRenderer`, `ObjCamera` ni `ObjDisplay` por inmediatos.

## NO VERIFICADO

- Objeto productor del `PlayData` en PbCap (topología ObjHandover id `0x2a`; no está en `libSysDef`).
- Quién llama a `0x6137b0` y bajo qué precondiciones de UI.
- Si `Execute` corre en `ExecFuncPoint` o en el hilo `DispatchCommand` (`0x9162d0`).
- Si la captura YUV de `ObjRenderer` admite el modo de disparo (EE).

## Corrección sesión 14
- «Topología ObjHandover `0x2a`» era una etiqueta errónea: `ObjHandover` es NFC/Wi-Fi. `0x2a` = fila de la tabla del TopologyManager (ObjEffect salida nº1 → ObjStillRecorder entrada YC). Productor y traza en `objhandover-2a-topology.md` y `analysis/yc-pin-delivery-flow.json`.
