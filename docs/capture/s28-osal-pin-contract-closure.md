# S28 — receptor OSAL, propietarios y contrato de conexión YC

Fecha: 2026-10-17. A6000 3.21; análisis local estático, sin cámara ni instalaciones.
Orden de investigación: 3 → 1 → 2 → 4. Los cuatro puntos quedan resueltos en
su alcance de mensajería y compatibilidad de contratos. No se acredita una
captura electrónica funcional.

## 3. Receptor OSAL identificado

**ACEPTO:** `libBizFw.so:0x33348` y `0x33470` delegan en
`DataflowInfraSender::SendASync` y `DataflowInfraReceiver::ReceiveASync`,
respectivamente. Sus implementaciones están en `dataflowInfraFramework.so`:

| Paso | Dirección ELF | Comportamiento comprobado |
|---|---|---|
| Envío | `0x1bc70`, llamada `0x1bcde` | Reserva mensaje OSAL, copia el payload desde `DataflowInfraMsg+0x10`, añade origen y llama `osal_snd_msg(destination, message)` |
| Recepción | `0x1b968` | Llama `osal_rcv_msg_tmo`, obtiene tamaño/origen, copia el mensaje y libera el bloque OSAL |
| Receptor de Imaging | av-cam `0x4379744c` | Bucle `ReceiveASync(0x50004, ..., UINT32_MAX)`; diagnóstico `InfraImaging.cpp` |
| Dispatcher | misma función | Opcode `u16 +0 = 0x1000`; suboperación `u16 +2` |

El binario LIRO contiene su implementación de recepción en `0x435a9f4c`;
llama al wrapper OSAL `0x43561260`, que despacha por la interfaz instalada
en `DAT_440205c0+0x14`, slot `0x1e0`. La arquitectura Linux/LIRO y
`osal_uipc.ko` se documentó en S20. Aquí la identidad del consumidor se
demuestra por su propia espera sobre `0x50004`; no se deduce del nombre
del objeto que emite la petición.

Suboperaciones recuperadas: `0` GET, `1` REQUEST_CONNECT,
`2` REQUEST_DISCONNECT, `0x100` CONNECT, `0x101` DISCONNECT,
`0x8100` CONNECT_COMP y `0x8101` DISCONNECT_COMP. GET responde con
`0x8000`. El dispatcher busca por tres campos, no por una dirección de callback.
Si no encuentra el pin, responde `-0x20`; no inventa un descriptor.

## 1. Quién registra y sirve `0x00050004`

**ACEPTO:** el propietario efectivo es **InfraImaging**, en `av-cam.bin`.
ObjEffect es un cliente que modifica conexiones; no es el propietario de
la cola por aparecer en el llamador de `infraGetPin`.

`0x43797c34` construye cinco `DataflowInfraPin` mediante `0x435a97f0`.
Su tabla de punteros está en `0x43ff3714`; el GOT
`[0x44025f2c] = 0x43ff3714` permite al receptor recorrerlos.

| Objeto pin | Propiedades ROM | Tupla `{categoría, dirección, índice, OSAL}` |
|---|---|---|
| `0x43e9de9c` | `0x43ff3728` | `{0,2,0,0x50004}` |
| `0x43e9de64` | `0x43ff3738` | `{0,2,1,0x50004}` |
| `0x43e9dee0` | `0x43ff36e4` | `{0,2,2,0x50004}` |
| `0x43e9df18` | `0x43ff36f4` | `{0,2,3,0x50004}` |
| `0x43e9de2c` | `0x43ff3704` | `{3,2,0,0x50004}` |

La categoría `0` corresponde a los pines YC de esta ruta. Las direcciones
`1/2` son salida/entrada; `CheckConnectParam` exige emparejar `1↔2` y admite
`3↔3`. El índice distingue pines dentro de categoría y dirección.

El constructor copia las cuatro propiedades a `pin+0x18..+0x24` y fija
estado inicial `pin+0x28 = 1`. `GetSelfPin` (`0x43a49986`) devuelve las
propiedades; `0x43a49980` devuelve el estado. Las implementaciones coinciden
con los símbolos C++ de `dataflowInfraFramework.so:0x1ada8/0x1b2fe`.

El enlace del trabajo receptor se instala en `0x437970d4`: recupera
`[0x4402005c] = 0x4379744d`, construye un delegado con esa función y lo guarda
en `0x43e9d790` con identificador interno de trabajo `0x47`.
El delegado ejecuta la función almacenada en `+8` mediante `0x43acabec`.
`0x47` es el identificador del trabajo observado, no el ID OSAL `0x50004`.
No se afirma haber observado la asignación de la cola Linux en ejecución.

**RECHAZO:** el supuesto bloqueo de S25–S27 por un registro imposible de
reconstruir estáticamente. Estos cinco pines sí tienen inicialización estática.

## 2. Semántica de los otros endpoints y del recableado

**ACEPTO:** `0x005a0048` es el endpoint de **VEF::SubsystemMain**.
`0x436a4b8c` lo usa como origen de `SendCommandOsal`; el diagnóstico conserva
el nombre C++ completo en `0x43c8c1fd`. Su inicializador `0x436a4b1c` copia
12 filas desde `0x43bb2928` y construye seis salidas YC y seis entradas YC,
índices `0..5`, en `0x43e73674` con stride `0x38`.

**ACEPTO:** `0x01670464` es el endpoint de **ScalarInfra / SFRA**.
`ScalarInfraAsyncMain.cpp`, en el handler `0x439a1864`, lo utiliza al enviar
respuestas. Su inicializador `0x439a6104` convierte ocho filas de
`0x43bd4ae0` en cuatro salidas YC y cuatro entradas YC, índices `0..3`,
en `0x43f342e8`, también con stride `0x38`.

Ambas tablas fuente usan `{índice, categoría, dirección, OSAL}`; sus
inicializadores las reordenan a `PIN_PROPERTY`. No interpretar sus palabras
directamente con el orden del constructor de Imaging. Los buscadores
`0x436a7490/0x439a9b90` comparan categoría, dirección e índice.

El ensamblador de `libObj.so:0x15d6c0..0x15d7c4` determina exactamente:

| Vuelta | Desconecta VEF | Desconecta ScalarInfra | Nueva conexión |
|---|---|---|---|
| 0 | YC salida 0 | YC salida 0 | VEF YC salida 0 → Imaging YC entrada 0 |
| 1 | YC salida 2 | YC salida 1 | VEF YC salida 2 → Imaging YC entrada 1 |

No conecta ScalarInfra a Imaging en esta transición: desmonta sus salidas
0/1 y restaura el par VEF→Imaging. Los nombres SFRA/JPEG no autorizan a
llamar raster JPEG a las cuatro propiedades de un pin YC.

## 4. Los cuatro campos y `ObjStillRecorderCore::WriteStill`

**RECHAZO:** llamar a los cuatro valores de S23 «campos retornados de imagen».
Son parámetros de entrada `ParamStd<unsigned int>` de `ObjMsg`, conservados
en `PinParserYcOut0+0x34/+0x38/+0x3c/+0x40`. Tras GET del pin local, el parser
los copia a la segunda propiedad de `_MSG_PIN_REQUEST_CONNECT`:

| Parámetro ObjMsg | Campo de la propiedad remota | ¿Equivale a una entrada de imagen de WriteStill? |
|---|---|---|
| `0x1000` | Categoría del pin | No: no es dirección de buffer ni UniqueId de imagen |
| `0x1001` | Dirección del pin | No: no es ancho ni identificador DMM |
| `0x1002` | Índice del pin | No: no es alto ni pitch |
| `0x1003` | Endpoint OSAL del propietario | No: enruta mensajes; no identifica un raster |

`libObj.so:0x143472` construye esa petición con cabecera
`{0x1000,1,0x28,2}`; `0xa1516c` envía sus **40 bytes**.
El dispatcher de Imaging compara la primera propiedad y llama
`DataflowInfraPin::RequestConnect` con la petición y el destino de respuesta.
Esto asigna semántica a los cuatro valores mediante su consumidor, no por
parecido con una estructura gráfica.

**ACEPTO:** GET usa una petición de 20 B y una respuesta de **32 B**:

| Offset de respuesta | Contenido |
|---|---|
| `+0..+7` | Cabecera `{0x1000,0x8000,0x20,2}` |
| `+8/+0xc/+0x10/+0x14` | Categoría, dirección, índice, endpoint OSAL |
| `+0x18` | Estado del pin |
| `+0x1c` | Resultado firmado: 0 si encontrado, `-0x20` si ausente |

Correcciones a S23/S25: `0xa14f88` copia **ocho palabras/32 B**, comprobadas
por dos pares LDM/STM en `0xa150c8..0xa150d2`; no copia 20 B.
`infraGetPin` conserva `response+0x1c → out+0x1c`; la afirmación histórica
`response+0x20 → out+0x1c` era incorrecta. La respuesta no contiene un
puntero DMM, callback, geometría o formato de imagen.

`ObjStillRecorderCore::WriteStill` está en ELF `0x909a84`, Ghidra
`0x919a84` por sesgo de carga `+0x10000`. El export S22 que lo decodificó
en ARM con `halt_baddata` no es evidencia válida de su contrato.
La nueva decompilación Thumb se contrasta con LLVM y con diagnósticos de
`ObjStillRecorderCore.cpp`:

- Obtiene `MediaComInfo` y consulta/prepara el Pool antes de escribir.
- Lee hasta dos UniqueId desde parámetros `0x10000011/0x10000012`.
- El parámetro compuesto `0x10000003`, cuyo mensaje interno tiene ID
  `0x1000`, incluye CaptureId (`0x1000`), CapDate
  (`0x1001`, 10 B), GPS (`0x1007`, `0x90` B), y campos opcionales
  RepresentativeImageInfo (`0x1008`) y StillRecCtrlInfo (`0x100e`).
- `0x90f698` prepara la información efectiva de las imágenes desde el Pool;
  el llamador maneja `StillInfo` de `0x6b0` B y `WriteStillParam` de `0x40` B.
- `0x90a172 → 0x8fe0a0` entrega esos bloques y el número de imágenes a MPR.
  No entrega una `PIN_PROPERTY` ni interpreta sus cuatro palabras como YC.

**RECHAZO:** compatibilidad directa `PIN_PROPERTY → WriteStill`. Son contratos
distintos y el código recuperado no implementa una conversión entre ellos.
Esto cierra negativamente esa equivalencia, no demuestra que sea imposible
crear un adaptador y un productor de imagen válidos por otra ruta.

## Evidencia y validación

Evidencia en `analysis/session22/evidence/`: `s28-osal-callers.json`,
`s28-imaging-registration.json`, `s28-imaging-static-init.json`,
`s28-thread-bind-execute.json`, `s28-peer-pin-constructors.json`,
`s28-peer-pin-services.json`, `s28-other-endpoints.json`,
`s28-pin-property-types.json`, `s28-getpin-layout.json`,
`s28-yc-parser-contract.json`, `s28-yc-connect-contract.json` y
`s28-writestill-contract.json`. Direcciones de bibliotecas del texto son ELF;
sus exports Ghidra muestran `ELF+0x10000`.

Consultas exploratorias con `function_not_created` y entradas interiores no
definen límites ABI. En particular `s28-yc-parser-contract.json:0xa37b22`
es una rama interior: sus accesos se contrastan con LLVM; no se afirma que
sus registros `unaff` representen argumentos de una función independiente.
La cobertura incompleta de referencias Ghidra no se usa como prueba negativa.

Reproducir: `python3 -I analysis/session22/evidence/s28_dataflow_contract_audit.py`.
El auditor verifica cuatro SHA-256, tablas originales, construcción, recepción
OSAL, copia de respuesta y contrato WriteStill sin ejecutar firmware.
El primer pase detectó que VEF tiene **6 salidas + 6 entradas**, corrigiendo
la hipótesis inicial de 12 salidas, además de detectar la falta de este cierre.

Resultado final: **6/6 pruebas PASS**; `ruff` del auditor PASS; `mypy` de
`src` y el auditor PASS (6 archivos). `ruff check src tests` conserva nueve
avisos en cuatro tests ajenos, sin modificar esos archivos ni añadir avisos.
README, índice de captura, CONTEXT y notas históricas afectadas actualizados.
No hay repositorio `.git` en este checkout: cambios sin commit y sin push.

**VEREDICTO: APROBADO**, para los cuatro puntos investigados. El receptor,
registro, recableado y diferencia de contratos quedan determinados.
Productor sensor/DMA, raster válido, caché/ownership y fin electrónico de
exposición permanecen fuera de lo demostrado; SilentShutter sigue sin validar.
