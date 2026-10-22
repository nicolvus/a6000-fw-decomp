# S135 — el subsistema `ElecShutter` del A6300 como control positivo: la A6000 fw3.21 y la A7S fw3.20 no lo tienen

> Hito de la **línea de ingeniería inversa general** con **relevancia directa para la línea del
> obturador electrónico**. Se compara, **byte a byte**, el `av-cam.bin` de los tres firmware
> disponibles (A6000 fw3.21, A7S fw3.20, A6300 fw2.01) buscando las huellas de un subsistema
> de **obturador electrónico**. Convención **vaddr = 0x43541000 + file_offset**. No se ha
> ejecutado firmware ni se ha usado la cámara.

## 1. Por qué este hito

El proyecto ya tiene bastante trabajo sobre el obturador electrónico (S53, S56, S57, S58, S101 y
la comparación con el A6300 en `docs/capture/a6300-silent-comparison.md`, toda ella sobre
`libObj.so`). Lo que **no** estaba hecho era el **control positivo** en la capa del HAL
(`av-cam.bin`): ¿qué huellas deja en `av-cam.bin` un firmware de Sony que **sí** tiene
obturador electrónico? El A6300 fw2.01 sirve de ese control.

## 2. Método

Búsqueda literal de una batería de términos en los tres blobs (`bytes.count()` + extracción del
contexto de cada coincidencia), sin heurísticas:

`ElecShutter`, `EC_ElecShutter`, `EC_NonlinearElecShutter`, `ElecShutter_Main`,
`MechShutterTable`, `SilentShutterMode`, `CheckSetSilentShutterMode`, `front_eshutter`,
`CheckSetFrontEshutter`, `shutterType`, `CheckSetShutterType`, `SET Silent Shutter Type`,
`efcs`, `EFCS`, `electronic`, `Electronic`, `curtain`, `rolling`, `mechanical`, `Mechanical`,
`flicker`, `silent`, `Silent`, `SILENT`, `shutter`, `Shutter`.

## 3. Resultado

### 3.1 El A6300 fw2.01 **sí** tiene un subsistema de obturador electrónico

(Las direcciones de la tabla son el **inicio de la cadena**; el subtexto entre corchetes aparece
unas posiciones más adelante dentro de la misma cadena.)

| cadena | vaddr (A6300) |
|---|---|
| `ElecShutter/EC_ElecShutter_Main.cpp` | `0x43dcfa41` |
| `ElecShutter/EC_NonlinearElecShutter_MechShutterTable.cpp` | `0x43dcfa65` |
| `SET Silent Shutter Type: %d\n` | `0x43dc4f43` |
| `LiroSeq ParamCheckErr@%s[SilentShutterMode] cur:%d req:%d` | `0x43dc9a14` |
| `CheckSetSilentShutterMode` | `0x43dca9ad` |
| `LiroSeq ParamCheckErr@%s[shutterType] cur:%d req:%d` | `0x43dca61f` |
| `CheckSetShutterType` | `0x43dcb09c` |
| `LiroSeq ParamCheckErr@%s[front_eshutter] cur:%d req:%d` | `0x43dc821d` |
| `CheckSetFrontEshutter` | `0x43dca84a` |

Además, el módulo **EC** (motor de control de exposición) del A6300 incluye:
`job_EC_move_iris error:[%x]` `0x43dcf97d`, `CapRawDSLR::ECShare is NULL![%d]` `0x43dcf9cd`,
`EC::ISO Range Error : ForMemory %x  MinCap %x` `0x43dcf9ee`,
`EC::CapISO Error : ISO %x  MinCap %x` `0x43dcfa1c`, `EC_ERR_PRINT %s:%d Pga Drv Manager …`
(×5), `EC_MEMORYPOOL_ERROR` `0x43dcf5e1`, y la tabla de **índices de velocidad de obturación**
justo detrás de `EC_NonlinearElecShutter_MechShutterTable.cpp` (`0x43dcfa9e`:
`00 01 03 04 05 06 08 09 0a 0b 0d 0e 0f 10 12 13 14 16 17 18 19 1b 1c 1d 1e 1f 21 22`, es decir, los
códigos de velocidad **no lineales** con su equivalente mecánico).

### 3.2 La A6000 fw3.21 y la A7S fw3.20 **no** lo tienen

| término | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---:|---:|---:|
| `ElecShutter` | **0** | **0** | 4 |
| `EC_ElecShutter` / `EC_NonlinearElecShutter` | **0** | **0** | 1 / 1 |
| `ElecShutter_Main` / `MechShutterTable` | **0** | **0** | 1 / 1 |
| `SilentShutterMode` | **0** | **0** | 2 |
| `CheckSetSilentShutterMode` | **0** | **0** | 1 |
| `front_eshutter` / `CheckSetFrontEshutter` | **0** | **0** | 1 / 1 |
| `shutterType` / `CheckSetShutterType` | **0** | **0** | 1 / 1 |
| `SET Silent Shutter Type` | **0** | **1** | 1 |
| `efcs` / `EFCS` | **0** | **0** | **0** |
| `electronic` / `curtain` / `mechanical` / `flicker` | **0** | **0** | **0** |

La **única** coincidencia de la A7S es `SET Silent Shutter Type: %d\n` (`0x43ca4b6b`), que ya
estaba documentada en `work/claude/a7s_silent_execution_trace.md` (es el *diagnóstico* del
convertidor `0x4379ec04` de la A7S, no un módulo de obturador electrónico).

### 3.3 Matiz importante: la A6000 **sí** tiene el motor `EC`

La A6000 fw3.21 **no** carece del motor de control de exposición: tiene `EC::HS_M S`
`0x43ca315e`, `EC::EcTagData` `0x43ca91ce`, `EC::EcEncryptedTagData` `0x43ca9227`,
`EC::EcAmcTagData` `0x43ca931b`, `EC::api_EC_GetApolloLapNum()` (dentro de
`[IMAGING_CAP]: %s: warning EC::api_EC_GetApolloLapNum() Over LimitNum [%d] -> [%d]`
`0x43caa193`) y `Camera::EC::job_EC_CalcCaptureGamma` (en el RTTI). Lo que **no** tiene es la
**sub-rama `ElecShutter/`**.

→ La ausencia es **selectiva**, no un simple recorte de build: en la A6000 falta exactamente
la parte del obturador electrónico, y el resto del motor de exposición está.

### 3.4 Qué sí dice la A6000 sobre el obturador

Las 15 apariciones de `shutter`/`Shutter` de la A6000 son **del obturador mecánico**:

- `VDF::ShutterMuteOffExecutor::OtherFunctionOn(...)` `0x43c851d8` y `ShutterMuteOffExecutor.cpp`
  `0x43c8521b` (el silenciador del obturador);
- `N3VDF25VdfInputCmdSetShutterMuteE` `0x43c881a3` y `N3VDF28VdfInputCmdShutterMuteOffPinE`
  `0x43c88455`;
- `[SFRS][PINSEND] shutter mute thru: file=%s line=%d` `0x43ce956e` (S118);
- `[VPH_API]<shutter_mute_param>` `0x43ce3634` y `>shutter_mute_status<o/f:%d` `0x43ce3dfc`
  (S131, API **nueva** en esta fw3.21);
- `[CAMERA_MAIN_FC]: ReplyForTouchShutter ERROR - NULL cb_func` `0x43ca6a85` (disparo táctil).

## 4. Lectura para la línea del obturador

1. **Control positivo**: cuando un firmware de Sony trae obturador electrónico en esta capa, deja
   huellas inequívocas (directorio `ElecShutter/`, ajustes `SilentShutterMode`/`shutterType`/
   `front_eshutter`, tabla de velocidad no lineal con equivalente mecánico).
2. **La A6000 fw3.21 no tiene ninguna de ellas** → **su HAL no contiene un subsistema de
   obturador electrónico**. Esto **refuerza** la conclusión vigente de S51 (A/B/C = NO) y es
   **complementario** de S101: allí se vio que el selector de tipo de mecanismo
   (`0x4379316a`, `tbb` sobre `[G+0x808]&7`) tiene valor 0 por defecto y ningún escritor directo;
   aquí se ve que **tampoco existe el módulo que lo interpretaría**.
3. **Límite de la inferencia (regla del proyecto)**: la ausencia estática de un módulo en un
   firmware **no** demuestra que el hardware no pueda obtener lectura sin cortina; solo
   establece que **esta fw3.21 no lo implementa en el HAL**. La prueba física sigue siendo la
   que decide (plan P0–P8 de `docs/capture/physical-test-plan.md`, ninguna ejecutada).

## 5. Verificaciones hechas

| afirmación | cómo se comprueba |
|---|---|
| recuento de cada término en los tres blobs | `bytes.count()` sobre los tres `av-cam.bin` |
| direcciones del A6300 | extracción del contexto de cada coincidencia (vaddr = base + offset) |
| ausencia en la A6000 y la A7S | los mismos recuentos, a 0 |
| la A6000 sí tiene el motor EC | presencia de `EC::EcTagData` `0x43ca91ce`, `api_EC_GetApolloLapNum` `0x43caa193`, RTTI `Camera::EC::job_EC_CalcCaptureGamma` |
| las 15 apariciones de `shutter` de la A6000 son del obturador mecánico | listado completo de los contextos |
| la coincidencia de la A7S ya estaba documentada | `work/claude/a7s_silent_execution_trace.md` (convertidor `0x4379ec04`) |

## 6. NO VERIFICADO / abierto

- Si el módulo `ElecShutter` del A6300 se ejecuta en algún modo y con qué efecto físico.
- Si la política **EFCS** de la A6000 en `libObj.so` (E012, `docs/capture/shutter-investigation.md`)
  es el mismo concepto que `ElecShutter` del A6300 en `av-cam.bin`: son binarios y capas
  distintas, y no se ha enlazado.
- Si una fw anterior de la A6000 tuvo ese módulo (no hay más blobs de la A6000 en el repositorio).
- Nada de esto **modifica** S51 (A/B/C = NO): lo único que hace es **añadir un control positivo**
  a la ausencia ya documentada.

## 7. Ficheros de este hito

| fichero | contenido |
|---|---|
| `elec_shutter_scan.md` | este informe |
| `elec_shutter_scan.py` | script reproducible del barrido de términos en los tres blobs |
