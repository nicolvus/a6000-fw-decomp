# S31 — subsistema CAMERA_MAIN_SYNC/DFECore: cadenas no exploradas (18-10-2026)

Firmware ILCE-6000 3.21, `av-cam.bin`, SHA-256
`b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`. Hallazgo
por búsqueda literal de cadenas (`strings`), no decompilación todavía.
Base lógica de análisis `0x43541000` (ver E016); VA aproximada = base +
offset de archivo para una imagen plana.

## Motivación

Las sesiones S16–S30 (ver `s22-sensor-to-yc.md`, `s30-pipelines-capture-encode.md`)
buscaron el productor sensor/DMA del YC y el fin electrónico de exposición
exclusivamente en la capa de servicio (`libObj.so`, `libBizFw.so`,
`dataflowInfraFramework.so`, wrappers `C_Imager` de `av-cam.bin`). Ninguna
sesión previa había buscado cadenas de depuración del propio motor de
temporización del sensor dentro de `av-cam.bin`. Tampoco se había revisado
si el control físico vive en un módulo `.ko` separado: se comprobó que
**ningún** `.ko` del firmware (`dmm.ko`, `mcmn_drv.ko`, `stream.ko`, etc.)
contiene cadenas `IMX210`, `exposure`, `SilentShutter` o `EFCS` — descarta un
driver V4L2/kernel separado para el sensor en esta imagen.

## VERIFICADO: cadenas literales y offset de archivo

| Cadena | Offset archivo | Comentario |
|---|---:|---|
| `[DFECore]: camIntHandler0: fact=%x` | `0x750ff0` | handler de interrupción con factor/causa |
| `[DFECore]: camIntHandler1: fact=%x num=%d` | `0x750e75` | segundo handler de interrupción, con número |
| `[CAMERA_MAIN_SYNC]: No Read. cause:no expose` | `0x761637` | log de omisión de lectura por "no expose" |
| `[CAMERA_MAIN_SYNC]: No Read. cause:1st expose` | `0x7616e7` | log de omisión de lectura durante 1ª exposición |
| `VD_Drive S` / `VD_Drive E` | `0x761e3d` / `0x761f01` | marcas de inicio/fin de `Imaging::VD_Drive` |
| `EC_VD_Post S` / `EC_VD_Post E` | `0x761f48` / `0x761f55` | marcas de inicio/fin de `EC_VD_Post` |
| `VD_Post S_OF` / `VD_Post E_OF` | `0x76276a` / `0x7627ed` | variante "overflow" de `VD_Post` |
| `[CAMERA_MAIN_SYNC]: int_LM_Send1st_Handler: EC_VD_Post had been still running.` | `0x7627fa` | handler de interrupción que depende del estado de `EC_VD_Post` |

Cadenas adicionales confirmadas por `strings` (mismo binario, no listadas con
offset): `Imaging::VD_Drive: overflow`, `EC_VD_Post timing error %d, vd:%d`,
`CamV[%10d] CamOutV[%10d] Blank[%10d] eeStart[%10d] idtDriver[%10d]`,
`SyncResMgr::Get: IMAGER0, DFE_ERR:0x%02x`, `No Read. cause:clamp`,
`exp:%d, read:%d, clampinit:%d`, `shut:%d, svd:%d, shd:%d, spl:%d, sint:%d, gs:%d`,
`int_ADC_Handler`, `int_BONOBO_INT_REQ_Handler`, `int_BONOBO_start_Handler`.

**INFERENCIA, no VERIFICADO:** por el vocabulario (`VD_Pre`/`VD_Drive`/`VD_Post`/
`VD_Sequence`, "expose", "Read", "clamp", "IMAGER0") esta tarea `CAMERA_MAIN_SYNC`
parece ser el motor real de temporización de línea vertical (VD) y exposición
del sensor — justo el nivel por debajo de los wrappers `C_Imager::SetMode/
SetExposure/SetRead` ya documentados en `silent-imager-consumers.md`, y no
analizado por ninguna sesión anterior. "EC_VD_Post" podría corresponder a un
post-procesado de "End Capture"/cortina electrónica sobre VD, pero el nombre
por sí solo no prueba esa semántica.

## NO_VERIFICADO — qué falta

- Las funciones que emiten cada cadena (dirección de código, no solo el
  literal), su máquina de estados `VD_Pre → VD_Drive → VD_Post → VD_Sequence`,
  y si alguna rama corresponde a lectura sin cortinas mecánicas.
- Si `int_LM_Send1st_Handler`/`camIntHandler0/1` leen un registro de
  interrupción físico real o solo un contador software.
- Si esta tarea termina produciendo el buffer YC/raster buscado desde S18, o
  solo coordina temporización sin tocar memoria de imagen.

## Decompilación de las 8 funciones del motor VD (18-10-2026)

30 funciones decompiladas (headless `-readOnly -noanalysis`, SHA-256 del blob
confirmado antes de exportar). Nombres por cadena/comportamiento, no por
símbolo original.

| Estado | Función | Dirección | Hallazgo |
|---|---|---|---|
| VERIFICADO | `VD_Drive` | `0x4378f410` | Emite S/E, espera evento `0x1a/0x80`, comprueba el VD actual y ejecuta trabajos pendientes |
| VERIFICADO | `EC_VD_Post` | `0x4378f848` | Emite S/E, evita reprocesar un VD ya hecho; al terminar guarda su número en `0x43e992dc` |
| VERIFICADO | Predicado «No Read» | `0x4378e6a0` | Falso cuando `arg1+0x18==0`; también para 1ª exposición, con ramas clamp y 1ª lectura HS |
| VERIFICADO | `VD_Pre` | `0x43792a0c` | Prepara estado y callbacks; señala evento `0x1a/0x40` |
| VERIFICADO | `VD_Sequence` | `0x4379155c` | Espera evento `0x40`, ejecuta la secuencia y señala `0x100` |
| VERIFICADO | `VD_Post` | `0x4379210c` | Espera `0x100`, después encola `VD_Drive`; contiene las marcas S_OF/E_OF |
| VERIFICADO | `int_LM_Send1st_Handler` | `0x43792750` | Compara `0x43e992dc` con el VD actual; si coincide reprograma un callback temporal, si no registra EC pendiente |
| VERIFICADO | `camIntHandler0` / `camIntHandler1` | `0x436cf954` / `0x436cf780` | Handler0 acumula causas con máscara `0x03380000` y despacha 4 slots de callback; Handler1 cuenta llamadas (log cada 1000) |

**Secuencia real (asíncrona y condicionada, no lineal):** `VD_Pre` —evento
`0x40`→ `VD_Sequence` —evento `0x100`→ `VD_Post` —cola→ `VD_Drive`.
`0x43791a7c` encola `VD_Pre`; `0x437918ac` encola `VD_Sequence` según modo.
La variante EC llega por `0x437926fc` o el callback `0x43791454`, condicionado
al predicado `0x4378e90c`.

**VERIFICADO — acceso MMIO real:** la programación temporal llega a
`0x436ccd9c → 0x43ad6006`, que escribe registros físicos entre `0xf3c30110` y
`0xf3c3015c`. Prueba acceso estático a hardware mapeado en memoria; su efecto
físico no se ha observado (no hay cámara conectada).

**PARCIAL — conexión YC:** `VD_Sequence → 0x43796954 → 0x4379bb90`
(diagnóstico `SyncYCout.cpp`) prepara parámetros y los envía por
`0x43797afc/0x7b10/0x7b24/0x7b38 → 0x435a9928`; aquí vive la cadena «YC out
window overflow». **No identifica dirección de píxeles, planos, pitch ni
finalización DMA** — es el candidato más cercano al productor YC buscado
desde S22/S30, pero no lo cierra.

**NO_VERIFICADO:** si estos handlers marcan fin de lectura/DMA o solo
temporización; `VD_Drive`/`VD_Post` recorren listas de trabajo con llamadas
indirectas vía `0x43ad6034` cuyos destinos concretos no se resolvieron.
Dato que falta y procedimiento no destructivo: resolver estáticamente quién
construye esas listas de callback (siguiente paso recomendado, ver abajo);
para comportamiento físico haría falta una captura pasiva correlacionada de
VD/lectura/interrupciones en hardware real, sin flashear.

Exports: `analysis/ghidra/camera-main-sync-final-decompilation.c` (pseudocódigo),
`camera-main-sync-final-decompilation.json`, `camera-main-sync-final-evidence.json`
(callsites/ensamblador), `camera-main-sync-string-xrefs.json`,
`camera-main-sync-entry-xrefs.json`. 30/30 decompilaciones sin error, SHA-256
verificado, proyecto Ghidra sin modificar (solo lectura).

## Siguiente paso recomendado

**Actualización S32:** este paso se realizó en
[S32 — callbacks VD y SyncYCout](s32-vd-callbacks-sync-ycout.md).
CORRECCIÓN: `0x43ad6034` es código de despacho y `0x43ad6052` su thunk;
las listas y seis destinos concretos ya están resueltos. El log de ventana YC
está en `0x4379bb90`, callsite `0x4379cb2e`, no en `0x435a9928`.
La rama ampliada referencia handles DMM compartidos mediante `0x4379b44c`,
pero todavía no identifica un contrato completo de píxeles/pitch/formato/fin DMA.
La recomendación siguiente se conserva como estado previo de S31.

Resolver los destinos concretos de las llamadas indirectas vía `0x43ad6034`
desde las listas de trabajo de `VD_Drive`/`VD_Post`, y seguir
`0x4379bb90`/`0x435a9928` (rama YC de `VD_Sequence`) para ver si alguno
produce o referencia un descriptor YC/DMM con dirección de buffer real.
