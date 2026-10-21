# S118 — `[SFRA]`: el módulo de control del escalar en la cámara

Hito de la línea de RE general. Conecta con el framework `NS_SCALAR_INFRA` (`[SFR]`/`[SFRS]`, S116),
el motor YC (S110), el gestor de memoria (S113) y el resource controller. Sin efecto directo en la
línea del obturador electrónico. Informe completo (catálogo de comandos, ids decodificados, mapa
función→traza, ficheros fuente): [analysis/s118_sfra/sfra.md](../../analysis/s118_sfra/sfra.md) ·
Datos: `sfra.json`, `func_map.json`, `command_table.json` · Test: `tests/test_s118_sfra.py`
(22 tests, verdes).

## Hallazgo central

`[SFRA]` es la **fachada de cámara del framework `NS_SCALAR_INFRA`** (nombre del framework
**verificado por el firmware**: `NS_SCALAR_INFRA::SubsystemFactory::ExecCmd` `0x43ce79ec`,
`NS_SCALAR_INFRA::WaitQueue::Enqueue` `0x43ce7bad`). **100 trazas** (100 textos distintos) en
`0x43ce5a16`–`0x43ce7723`, **118 sitios de referencia** y **47 funciones**
(`0x439a1864`–`0x439a7bd4` + copia aislada en `0x439ae838`). Núcleo: `ScalarInfraAsyncMain`
(`0x439a1864`, fichero `ScalarInfraAsyncMain.cpp` `0x43ce59fd`).

## Protocolo

17 comandos con marcadores `***…***`: **8 `[CMD]`** (petición) + **9 `[CMP]`** (finalización) —
`GET_INFO`, `SET_PATH(OPEN/CLOSE)`, `SET_SA_NOTIFY`, `GET_SA_RESULT`, `SET_JPEG_PARAM`, `GET_JPEG`,
`LiveView SET_JPEG` y sus `_CMP`. Los **ids están decodificados de los bytes**: cada comando lo
protege un predicado de la familia `0x43b63xxx` que compara el **tipo de mensaje** (16 bits en
`+0x02`) y, para la clase `0x0100`, el **id de sub-comando** (8 bits en `+0x0f`): `0x0100`/`0x10`
GET_INFO, `0x0100`/`0x20` GET_JPEG, `0x0100`/`0x22` SET_JPEG_PARAM, `0x0100`/`0x30` GET_SA_RESULT,
`0x0100`/`0x32` SET_SA_NOTIFY, `0x0100`/`0x42` LiveView SET_JPEG, `0x8110` SET_PATH(CLOSE), `0x8120`
SET_PATH(OPEN), `0x9010` GET_INFO_CMP. Sub-bloques (11): `RATECONTROL` 26, sin etiqueta 21,
`ERROR` 14, `BUF` 11, `CMP` 9, `CMD` 8, `ERR` 4, `RC` 4, `NOTIFY` 1, `SFR_ERR_NOTREADY` 1,
`WARNING` 1. Ficheros fuente del módulo (11, contiguos en el blob): `ScalarInfraAsyncMain.cpp`
`0x43ce59fd`, `SfrJpegBuffer.h` `0x43ce5e45`, siete `ScalarInfraSequence*.cpp` `0x43ce6320`–
`0x43ce7126`, `SfrYc.cpp` `0x43ce73ec`, `DrvCallRc.cpp` `0x43ce76fb`.

## Subsistemas y diferencial

Relacionado con `NS_SCALAR_INFRA` (`[SFR]`/`[SFRS]`), el acelerador escalar «SA», el motor YC
(`SfrYc.cpp`, `stdYc2sfrYc_*`), el **DMM** (`DrvCallDmm::UtilityGetAddr` `0x43ce75d8`), el resource
controller (`DrvCallRc.cpp`, `[SFRA][RC]`), el anillo JPEG (`SfrJpegBuffer.h`, `[BUF]`) y LiveView.
Censo de llamadas: 58 llamadas a 31 destinos, **ninguna directa al imager ni al codificador**.

**Diferencial A7S fw3.20 — el módulo es idéntico.** La A7S fw3.20 **sí lleva el prefijo `[SFRA]`**
(100 apariciones): los **100/100 mensajes coinciden texto a texto**, en el **mismo orden**, con
**118 sitios** y **47 funciones** en ambas cámaras; sólo cambia la posición en el blob. La A6300
fw2.01 tiene **108** trazas: las 100 de la A6000 más 8 con nomenclatura antigua (`CMD_JPEG`,
`CMD_LIVEVIEW`, `SET_PATH_CMP(JPEG CLOSE)`, `LiveViewStageIdle::exec openReq/closeReq`,
`getCloseSeq() Invalid Seq!!!`).

## Aviso metodológico (afecta a hitos anteriores)

La regla canónica del repo (todos los `ldr` del registro en 4 KB) da **186** pares (cadena, sitio)
frente a los **118** reales: 68 son falsos positivos por reutilización del registro (`0x4398f06a`
resuelve a una tabla de contadores, no a `SET_PATH(CLOSE)`; `0x439a17e8`/`0x439a1808` están en una
tabla de punteros, no en código). S118 usa *kill analysis* (`analysis/s118_sfra/pic_dataflow.py`).
**Recomendación: revisar los recuentos de sitios de S110/S112/S113/S115.**

## Abierto / NO VERIFICADO

Significado funcional de los ids; correspondencia de los 5 casos del `TBB` (`0x439a1640`, tabla
`0x439a1654`) con los nombres `[CMP]`; 5 ids de sub-comando sin traza propia (`0x34`, `0x40`,
sub-ids `0x8120`); `SFRA`, `SA` y `RC` no están expandidas por el firmware; enlace con el imager
(S115) y con el gestor de captura (S106) **indirecto**, vía `[SFR]`/`[SFRS]`.