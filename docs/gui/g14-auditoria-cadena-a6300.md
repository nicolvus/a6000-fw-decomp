# G14 — Auditoría de la cadena completa de los ajustes exclusivos de la A6300 (estático, 08-11-2026)

**Alcance**: los 81 ajustes que solo tiene la A6300 ([G13](g13-barrido-ajustes-a6000-a6300.md) §3), menos los que la A6000 ya
tiene con otro nombre o equivalente (Dial Lock, NTSC/PAL, Zoom Setting/Speed, Priority Set AF-S/AF-C = mismo parámetro
`@M00F 76/76` que «Priority setup», APS-C/Super 35mm = `@M00B 134/147` de «APS-C Size Recording», Zebra, Record Setting, Panorama
Direction, Focus Area de fase, Version, Custom Key(Shoot./PB), HDMI Info Display = respaldo `0x1070a47` de
«NoOsdOutputThroughHdmi», Aperture/ShutterSpeed internos) y los duplicados.

**Método** (scripts de trabajo y datos en `analysis/gui/g14/`, se ejecutan desde la raíz con el directorio como primer argumento, en este orden: `f6300b.py` (con los argumentos de G14 §método), `measure.py`, `calls.py`, `desc.py`, `pairs.py`, `params.py`, `cls_params.py`; resultado combinado en `analysis/gui/a6300-only-audit.json`):

| Eslabón | A6300 2.01 (`viewUnified2.so`, sin símbolos) | Comprobación en la A6000 |
|---|---|---|
| 1. Nodo → ProcessId | `CautionConfig.so` (`settings_sweep.py`) | — |
| 2. ProcessId → clase | `getElement` `0x208a84` (`pid ≤ 0x15a`) → `factoryElement` `0x1bcae8` (243 casos); nombre de clase por RTTI (vtable → typeinfo) | ¿existe la clase en `cmn_view_processDataMgr.so`? |
| 3. Código propio | métodos de la vtable que no hereda de `CustomBase`/`Normal`, bytes y llamadas (cota baja: corta en el primer `pop pc`) | — |
| 4. Datos | descriptor `setProcessId` (`0x3c9860`, mismo formato que la A6000): modelos `@Mxxx` + parámetros, ids NVRAM | ¿mismo modelo+parámetro / mismo id NVRAM en algún descriptor o librería? |
| 5. Dependencias | cadenas `@Mxxx` y `view/…`, funciones importadas | ¿existen esa vista y esos símbolos? |
| 6. Negocio | ids de `ParamList::add`/`PrmNumberList::GET` del código propio | ¿algún código de la A6000 usa ese id? |

Validación: EFCS da el mismo descriptor en ambas (`@M00F 84/79`); las clases salen con nombre en 243/243 casos. **Límites**: no se
ha seguido el lado del modelo/`av-cam` (qué hace cada mensaje); los ids de parámetro solo se capturan cuando se cargan como
inmediato (varias clases salen sin ninguno); «id usado en la A6000» puede ser coincidencia de número; los tamaños son cota baja.

## Resultado

Escala: **Media** = datos + ampliar la tabla de ProcessIds (`cmp r1,#0xe8`) y el negocio de la A6000 ya conoce el parámetro.
**Alta** = portar la clase (Thumb, 250–800 B) y/o una vista nueva y/o ayudantes que la A6000 no tiene, con parámetros que ningún
código de la A6000 usa. **Muy alta** = varias clases + procesado de imagen. **No** = hardware.

| Ajuste (ProcessId A6300) | Qué hace | Cadena en la A6300 | Qué falta en la A6000 | Complejidad |
|---|---|---|---|---|
| Shutter Type (319) | mecánico / electrónico / auto | `CustomStillShutterType` 292 B; `@M00B 167/188`; param `0x4ce` | clase, parámetro y `0x4ce` (no usados en la A6000) | Alta portado; **Media reutilizando EFCS (3.54, hecho)** |
| Selftimer during Brkt (321) | autodisparador antes del horquillado | `CustomSelfTimerOnBracket` 358 B; `@M0E9`; params `0x2b0/0x2b3` | **vista `view/SELFTIMERONBRACKET`**, `CmnModelAndTreeId`, `backupWrite`; params **sí** usados en la A6000 | Media-alta |
| Bracket Settings (320) | contenedor: Bracket order + Selftimer | `Normal`; Bracket order = `@M00F 22/13` | Bracket order ya existe igual en la A6000 | Baja (contenedor) + la de Selftimer |
| RAW File Type (5) | RAW comprimido / sin comprimir | `CustomRawFileType` 262 B; `@M00F`; param `0x2bc` | clase y ayudantes (`CmnModelAndTreeId`, `isSlowRecMovie/isHFRMode`); `0x2bc` **sí** aparece en la A6000; el codificador sin comprimir NO_VERIFICADO | Alta |
| Release w/o Card (73) | disparar sin tarjeta | `CustomReleaseWOCard` 386 B; `@M00A`, `@M0E9` | clase + `CmnModelAndTreeId`, `backupRead`, `CmnViewModelWrpMediaType` | Alta |
| ISO AUTO Min. SS (325) | velocidad mínima en ISO Auto | `CustomIsoAutoMinShutterSpeed` 464 B; `@M00B`, `@M0E9` | **vista `view/ISO_AUTO_MIN_SS`**, `CmnViewisoAutoMinShutterSpeedDataMgr`, `backupRead`; lógica de AE en `av-cam` NO_VERIFICADO | Alta |
| AF in Focus Mag. (340) | AF con la imagen ampliada | `CustomFocusMagnifAF` 274 B; `@M00B 173/195`; param `0x4f0` | clase; parámetro y `0x4f0` desconocidos | Alta |
| AF Area Auto Clear (69) | ocultar el recuadro AF | `Normal`; NVRAM `0x1070ee7` | nadie en la A6000 lee `0x1070ee7` (falta el consumidor que dibuja) | Alta |
| Wide AF Area Disp. (70) | puntos AF en «Wide» | `Normal`; NVRAM `0x1070b4f` | ídem, `0x1070b4f` sin consumidor | Alta |
| Marker Display / Settings (291–295) | marcas de centro, aspecto, zona segura, guía | `CustomMarkerDisplay` 248 B + 4 `Normal`; NVRAM `0x10704b6–0x10704ba` | ninguno de esos ids existe en la A6000 (falta la capa de dibujo) | Alta |
| Video Light Mode (285) | control de la luz de la zapata | `Normal`; `@M00B 159/178` | parámetro desconocido en la A6000 | Media si el modelo lo admite; si no, Alta |
| Lens Ring Setup (122) | función del anillo (zoom/enfoque) | `CustomLensRingSetup` 330 B; `@M00B`, `@M0E9` | clase; parámetros no capturados | Alta |
| Zoom Ring Rotate (308) | sentido del anillo de zoom | `CustomZoomRingRotate` 406 B; param `0x4b0` | clase; `0x4b0` desconocido | Alta |
| Rng. of Zoom Assist (343) | tamaño de la ayuda de zoom | `Normal` **sin modelo ni NVRAM** | todo: el comportamiento vive en otro sitio | Alta |
| Copyright Info (314–318) | escribir autor/copyright en EXIF | `CustomWriteCopyrightInformation` 276 B, `@M00F 93/111`; 3 `Normal` sin enlace (entradas de texto) | clase, parámetro y pantallas de texto | Alta |
| Set File Name (338) | prefijo del nombre de archivo | `Normal` sin enlace (pantalla de texto) | pantalla y lógica de nombres | Alta |
| HDMI: TC Output (302), 24p/60p (254), Audio Out (310) | salida de timecode, cadencia y audio por HDMI | `CustomHdmiTCOutput` 328 B, `CustomHdmiOutputSwitch` 480 B, `Normal @M008 9/5` | clases y parámetros | Alta |
| TC/UB Settings (299) | timecode / user bit | `CustomTCUBSettings` 316 B | clase + `isSlowRecMovie/isHFRMode`; timecode en el códec NO_VERIFICADO | Alta |
| Auto Pwr OFF Temp. (346) | umbral térmico de apagado | `Normal`; `@M007 3/8` | parámetro desconocido; riesgo térmico | Alta (riesgo) |
| AF System (335) | AF con adaptador LA-EA3 | `CustomAFSystem` 270 B | clase | Alta |
| Picture Profile (255 + 13 subajustes) | gamma, knee, color, detalle, S-Log | 14+ clases `CustomPictureProfile*` (274–756 B) + `CmnViewPictureProfileCommon`; Gamma param `0x214` **sí** usado en la A6000 | todas las clases y el ayudante común; soporte del pipeline de imagen NO_VERIFICADO | Muy alta |
| Gamma Disp. Assist (337) | vista normal con S-Log | `CustomSLogDispAssist` 346 B; `@M006` | **vista `view/SLOGDISPASSIST`**; depende de Picture Profile | Muy alta |
| Photo Creativity (341) | modo creativo guiado | `Custom4kPhotoCapture` 156 B | clase (de otro modelo) | N/A |
| 4K HDMI, Super 35, HFR, S&Q, Dual Rec, SteadyShot en cuerpo, Finder Frame Rate, LPF, Function for VF close | — | clases `CustomHDMI4kOutput`, `CustomHFRExpoMode`, `CustomSlowQuickFrameRate`, `CustomDualVideoRecording`, `CustomSteadyShot*`, `CustomFinderFrameRate`, `CustomLPFilter`… (+ vistas `AUTO_DUAL_REC`, `FINDER_FRAMERATE`) | hardware | No |

## Conclusiones
1. **Ninguno de los exclusivos es «solo datos»**: todos tienen o una clase propia que la A6000 no tiene, o un id NVRAM/parámetro que
   ningún código de la A6000 lee. Además, cualquier ProcessId nuevo exige ampliar la tabla llena de la A6000 (`0xe8`).
2. Lo más barato de portar: **Selftimer during Brkt** (sus parámetros ya existen en la A6000; falta una vista y 3 ayudantes),
   **Video Light Mode** (solo datos si el modelo admite el parámetro) y **RAW File Type** (parámetro conocido; falta la clase).
3. **ISO AUTO Min. SS**, **Release w/o Card** y **AF in Focus Mag.** son las de más valor, con dificultad Alta: clase + vista o
   ayudantes + verificación del lado del modelo.
4. Lo que no se puede saber sin seguir el modelo/`av-cam` (siguiente nivel): si la A6000 ejecuta de verdad los parámetros nuevos.
