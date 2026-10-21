# S119 — el módulo `[APL]`: la capa de aplicación sobre HW y SA

**Hito de la línea de ingeniería inversa general** (A6000 fw3.21). No toca la línea del obturador
electrónico: **0** mensajes de obturador en las 42 trazas.
Informe: [analysis/s119_apl/apl.md](../../analysis/s119_apl/apl.md) · Datos: `apl.json` ·
Test: `tests/test_s119_apl.py` (47 tests, verdes).

## Hallazgo central

Las **42 trazas `[APL]`** **no son un módulo con prefijo propio**: son un **sub-bloque `[APL]`
dentro de las cadenas `[CAMERA_SA]:`** (S108). Cadenas completas `0x43cebde1`–`0x43cec4fe`
(contiguas); la etiqueta `[APL]` va 13 bytes más dentro, `0x43cebdee`–`0x43cec50b`.
Las emite **5 funciones** del driver de cámara, con 42/42 trazas referenciadas por PIC (1:1):
`0x439cea30` Open (7 trazas), `0x439cebe4` Close (9), `0x439cedd0` Free & Close (4),
`0x439ceeb8` Open + ejecución (20), `0x439cf3b8` SA open/close (2). Los 10 sub-bloques (partición
exacta, suma 42) van de "HW Open/Close" (3) a "GetMemInfo" (5); detalle en el informe.

## Qué abre y qué cierra

* **HW** (el firmware **no da nombre** a estas funciones): `0x43b7db64` open / `0x43b7dbd6`
  close / `0x43b7dc74` GetCoreNum / `0x43b7dc26` SetMode / `0x43b5ea54` MmuMakeParam /
  `0x43a2ff38` abort.
* **SA** (driver `Camera::SaFuncDrv`, S84/S108): `0x43b6d796`→`0x439d143c` `ExecuteOpenMSG`,
  `0x43b6d77c`→`0x439d133c` `ExecuteCloseMSG`, `0x43b6d7a8`→`0x439d185c` `ExecuteCalcStartMSG`.
* **Parámetros**: `0x439d0f58` = **`CallocCamSaParam`** (la traza la llama "InputPrm"; reserva vía
  el DMM, `AsyncAllocNew` `0x439037c0`), `0x439d1bd0` = **`GetMemInfo`** (5 llamadas),
  `0x439d168c` = **`GetExecUnit`** (la traza la llama "GetZimaNo"). Las tres se autoidentifican
  pasando su nombre como `%s` del formato de traza.
* **`unit_hndl` = handles de unidad del DMM** (`[CAM_DMM]`, S113): open `0x43903280`, close
  `0x43903414`, free `0x43902fbc` (thunks `0x43b6d598`/`0x43b6d5ac`/`0x43b6d5b4`); se validan 6
  direcciones del mapa del HW: `HME_BaseTar_Addr`, `HME_BaseRef_Addr`, `Work_Addr`, `Vec_Addr`,
  `Result_Addr`, `HME_BaseTar_LineAddAddr`.

## Consumidor: `[CAMERA_MAIN_TC]` ("ApolloSA")

Cada una de las 5 funciones tiene **un único** llamador, todos en `[CAMERA_MAIN_TC]`
(`SA Preload %d` `0x43cb700e`, `SA Acquire %d` `0x43cb703a`, `SA Start %d %d` `0x43cb7092`,
`SA release1 %d` `0x43cb70bf`, `SA release2 %d` `0x43cb714d`, `ApolloSA_Main(start)` `0x43cb6ac7`).
Es el pipeline de *time compression* / movie: **la APL es su coprocesador de imagen**. **No** lo
llama el gestor de captura `[IMAGING_CAP]` (S106) ni `Camera::CamCore` (S107): ambos son *clientes*
del mismo SA, no clientes de `[APL]`.

## Diferencial A7S fw3.20

**42/42 cadenas comunes texto a texto, 0 exclusivas en ningún sentido**, y **la misma estructura
de 5 funciones** (`0x439bcd80` 7, `0x439bcea0` 9, `0x439bcfc8` 4, `0x439bd05c` 20, `0x439bd3a4` 2).
Lo único que cambia es que la A7S **no lleva el prefijo `"[CAMERA_SA]: "`** (sus cadenas están en
`0x43ce1588`–`0x43ce1a90`). El A6300 fw2.01: 42/42 también.

## Nota de método y abierto / NO VERIFICADO

- La regla PIC canónica del repo (todos los `ldr` del registro en 4 KB) da **67** pares (traza,
  sitio) frente a los **42** de la regla estricta: **25 falsos positivos** comprobados
  desensamblando (p.ej. `0x439b1eea` referencia en realidad un mensaje de `[SFRS]`).
- Significado de `APL`, `HW`, `SA`, `HME`, `MMU`, `Zima` (el firmware no expande ninguna sigla;
  el único nombre de negocio es "ApolloSA"), y layout/tamaño de `InputPrm`.
- Identidad y fichero fuente del bloque HW: **el módulo no registra ningún fichero de origen**
  (0 referencias `.cpp` desde `0x439ce900`–`0x439cf430`).
- Por qué la traza dice "GetZimaNo" cuando la función se llama `GetExecUnit`.
- El módulo `[CAMERA_MAIN_TC]` (el consumidor) **no** está reconstruido: hito pendiente.
