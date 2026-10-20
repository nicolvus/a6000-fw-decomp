# S30 — captura, origen YC y cierre de EncodeStill

Firmware A6000 3.21; análisis estático local. Direcciones `libObj`, `libmpr`
y `libBizFw`: VA ELF; Ghidra las representa con `+0x10000`. Direcciones
`av-cam.bin`: VA con base `0x43541000`. No se ejecutó nada en la cámara.

## Resultado de los tres requisitos

| Requisito | Resultado comprobado | Estado |
|---|---|---|
| 1. Captura nueva sin movimiento de cortinas | La ruta fija conocida continúa por CAIF/Darwin. `0x437f7ff0` selecciona drive/relación de tamaño; no inicia una adquisición independiente. | **NO CERRADO** |
| 2. Sensor/DMA → YC válido | Se resolvió el origen de `ctx+0x4b54`: es CaptureId. Esa ruta no entrega el raster. Falta identificar el productor real y su terminación DMA. | **NO CERRADO** |
| 3. YC → EncodeStill → Pool | Se recuperó el servicio receptor, secuencia, destino SDF y retorno bloqueante hasta la continuación de Execute/Pool. | **Flujo de control recuperado; contrato de caché/reciclaje del YC de captura abierto** |

Estos resultados no equivalen a tres pipelines funcionales ni a SilentShutter
demostrado. El cierre software de WriteStill documentado en S29 sigue vigente.

## 1. Dos falsos puentes descartados

**RECHAZO:** `0x436d6118` como terminación de lectura/DMA. Sus instrucciones
solo cargan un puntero mediante GOT y retornan. `0x437f7ff0` lo pasa a
`0x43ad908e`, que consulta dos modos por el slot `+0x24`, calcula su relación
de tamaño en escala `0x1000` y escribe salidas auxiliares a cero. El diagnóstico
es `getDriveModeSizeRatio Error`. No hay aquí registro ni llamada de completion.

**RECHAZO:** `ctx+0x4b54/+0x4b58/+0x4b5c` como descriptor YC. En la rama
de `Stage_Notify`, si `+0x4b54 == -1`, `0x4372a3c4` solicita `0xd008`
a `0x40193`. El receptor es `0x4381d16c`; la tabla `0x44000174` tiene
35 registros de **12 bytes**. La fila `0x4400024c` resuelve
`0xd008 → 0x43aea99b` (Thumb `0x43aea99a`).

Ese handler genera evento interno `0x15` para RelMgr `0x4379d838`, que llama
`0x4381c6cc`: la cadena original identifica `CapIdTblMgr) GetCaptureID`.
El constructor de respuesta `0x4379d6cc` devuelve el ID, estado y ocho bytes
auxiliares; `0x4372a3c4` copia el ID a `+0x4b54`, el byte de estado a
`+0x4b94` y los ocho bytes a `+0x4b58/+0x4b5c`. `0x4372a45c` envía después
`0xd001`, evento interno `0x16`, que llega a `0x4381c568`, identificado como
`CapIdTblMgr) IncrementRP`. Es consumo de una tabla de identificadores.

## 2. Receptor efectivo de EncodeStill

```text
ObjStillRecorderCore::Execute 90b248
  → reserva de salida 90a810 → preparación RegionInfo 90ad20
  → MprAcsr 8fe6f8 → MprIf::EncodeStill 71cf58
  → FeaIf::EncodeStill 44f834
      copia 0x78 bytes a FeaCore+0x11c mediante 429764
      encola comando 4000007c
  → rama del worker 42a1dc..42a210 → FeaCore 4406d4
  → 717ebc → 718848
      registra callback 71c8a8 mediante 2c2d78
      configura con 2c5db4, solicita encode con 2c5cbc
      solicitud: familia 1500, operación 2, payload 0x48 bytes
  → 2c0c18: osal_snd_msg(55001f, cabecera de 0x24 bytes)
```

**ACEPTO:** `0x55001f` corresponde al receptor de `InfraAvbbcIf`, creado en
`libObj:0x26e8fc`. Su hilo usa `0x26e438`, resuelto por GOT
`0x102f4d8=0x26e439`; slot virtual `+8` en `0xff7238=0x26e5d1`.
El helper de recepción es `0x49cd0c`. Para familia `0x1500` y operación 2,
`0x26e6e6..0x26e750` reenvía a **`0x550123`**.

`InfraStillEncoder`, constructor `0x46bed0`, atiende esa segunda cola.
Worker `0x46bb60 → 0x49cde4`; slot virtual `+0x18`, tabla
`0x1008230=0x46bcc5`, despacha `0x1500/2` y crea `SeqResizeEnc`
en `0x464200`. La secuencia registra quince estados y elige bloques de
resize/encode para las tres salidas habilitadas.

El estado de encode `0x465fac` prepara un mensaje de `0x50` bytes,
con `0x48` de parámetros, y lo envía a **SDF `0x56000f`**. En
`libBizFw`, `ConvertCid(3)=0x2000` (tabla `0x46340`) y
`ConvertCmdMidToSdf(0x304)=4` (fila `0x4752e`).
Por tanto el mensaje efectivo es **`0x2000/4`**, no el índice interno `0x304`.

**ACEPTO:** receptor SDF `av-cam:0x43638308`: espera indefinidamente en
`0x435a9f4c`, que llama a `Receive/Free` OSAL, y analiza en `0x43639c78`.
La rama `0x2000` de `0x436399d8` pasa por `0x43a8aa00`; comando 4 usa
el método `0x4363a1cc` de `SdfMsgAnalyzerRcv`, que obtiene el trabajo con
`0x4363ca28` y lo procesa con `0x4363a78c`. La ejecución del motor y su
coherencia de memoria requieren seguir ese trabajo; no se deducen del envío.

El selector `0x4363c378`, para comando 4, devuelve una de dos instancias
en `0x43e51450 + índice*0x10c`. Su inicialización en `0x4363d156..0x4363d16e`
llama `0x43653c2c` con IDs 4 y `0x24`. GOT `0x44021f98` apunta a la tabla
virtual `0x43fc4e10`. La rama de ejecución diferida `0x4363a668` envía el
trabajo de `0xe8` bytes al executor **`0x560010`**.

### Ejecución y fin real del motor JPEG

El executor es `0x43638474`, con su propia espera OSAL y analyzer.
Comando 4 pasa por `0x43a8ac06 → 0x4363a12c`. El trabajo contiene el
puntero de instancia; el despacho normal usa el slot `+8`. La API de encode
selecciona la ruta de ejecución de pines en `0x43a9d2d0` bajo su condición
de estado 7, y `0x43a8fbaa` prepara, ejecuta y notifica mediante slots.
El slot `+0x78`, tabla `0x43fc4e90`, es **`0x43a9d320`**.

La ruta de encode llega a `0x4365b6ec → 0x43aa1930 → 0x43aa1746`
→ `0x43a94a10 → 0x43a949c8 → 0x43b4c46e → 0x43936f34`.
`0x43aa1930` es un wrapper con argumentos adicionales de pila; su
decompilación auxiliar como `void(void)` no describe su ABI efectivo.

Dentro de `0x43936f34` se establece la pareja concreta de inicio/fin:

- `0x43937246..0x4393724a` instala **`0x43936b35`** como callback
  en el bloque de comando. La dirección se construye relativa a PC.
- `0x43937286` fija máscara 4; `0x439332e4` limpia esa condición.
- `0x43933874`, operación `0x31`, llama `ddl_saJpegCalcStart`
  (`0x43b5e832`, request DDL `0x101`, bloque de `0x18` bytes).
- `0x43933300(4,unit)` espera **SAFIN** mediante `0x43560de0`, plazo
  `10000`; tabla `0x43bd2de8` selecciona flag OSAL `0xc` o `8` según unidad.
- Callback `0x43936b34` resuelve unidad y comando, escribe el estado del
  reporte en `+0x3c` y llama `0x439332b0(4,unit)`, que señaliza el mismo
  flag con `0x43560da8`.
- Después de la espera se comprueba el reporte y se calcula el tamaño
  codificado en `param+0x14c`; `0x43a949c8` lo devuelve al llamador.

El slot de completitud `0x4363bb3c` construye el mensaje y lo devuelve al
destino conservado por la API. `0x43639fbc` comunica también el resultado
del trabajo del executor al receiver. Desde allí continúa SeqResizeEnc y
el retorno a MPR descrito abajo. El cierre estático incluye el callback
registrado y la espera efectiva; no es prueba de ejecución en una cámara.

### Descriptores que consume el motor

`0x43a96c70 → 0x43a975d8` resuelve el **handle** con `0x436519c0`,
copia un descriptor de **`0x44` bytes** y cierra el acceso con `0x43651694`.
El adaptador `0x43aa8558` acepta un contador hasta 8 y copia ocho pares
de palabras al contrato del driver. Esto no identifica ocho planos de
píxeles: falta asignar la semántica completa de esas entradas y verificar
que un YC nuevo de captura cumple el formato y su sincronización de caché.

## 3. Retorno hasta Execute y Pool

`SeqResizeEnc` prepara su retorno en `0x464154`: familia `0x4e0`,
operación `0x2002`, destino conservado en la secuencia. El callback de
respuesta registrado por `libmpr:0x2c0c94` es `0x2c82f0` para `0xc70047`.
No se confunde ese endpoint de **respuesta** con `0x55001f` de solicitud.
`0x2c7d60` traduce `0x4e0/0x2002` a evento interno `0x3001`;
`0x2c3e3c` lo encola y el worker `0x2c3f5c` invoca el callback guardado
en `0xa4b14c`: `0x71c8a8`.

Para `0x3001`, ese callback guarda el resultado y señaliza el objeto en
`0xad38e8` mediante `0x5fdc84`. Es el mismo objeto que `0x718848` espera
con `0x5fe58a(...,-1)`. Al terminar se desregistra el callback; el
resultado vuelve por `0x4406d4` como **`0x4000007c`, 12 bytes**:

| Offset | Contenido consumido por MprAcsr |
|---|---|
| `+0` | código de resultado u32 |
| `+4/+6` | primer par de dimensiones u16 |
| `+8/+a` | segundo par de dimensiones u16 |

`libObj:0x900648`, rama `0x900974`, copia esos 12 bytes a un `Struct`
en `ObjMsg(0x3500,0)`. `0x8febaa` invoca EncodeStill;
`0x8febd0` hace **`WaitEvent(-1)`**; después extrae el `Struct`.
**RECHAZO:** afirmar que `Execute` continúa al mero retorno de FeaIf.
FeaIf encola, pero su llamador exterior sí espera el retorno completo.

Con éxito, Execute continúa hacia `0x912b4c`, registro de imagen en Pool,
y la ruta de recording ya documentada en S29. Su epílogo libera los handles
de entrada `0x1018/0x1032` mediante `DmmCloseAndFree` (PLT `0xdc180`) y
emite `0x3500/0x3002`. Esto fija el orden de vida útil del camino nativo;
**no garantiza** que un productor alternativo deje de reciclar un anillo ni
que una escritura CPU sea visible al motor antes del encode.

## 4. Corrección de StillConverter

La atribución de S20 a un constructor `0x916140` era incorrecta:
`0x91618c` inicia `ObjStillRecorderThread`. El constructor de StillConverter
es `0x920c8c`, ya identificado también en `record-still-image-route.md`:
`+0x4c=EventSender`, `+0x50=EventReceiver`, `+0x54=EventHandlerWrapper`,
`+8=ObjThread`. Sender y Receiver quedan enlazados en `0x920d0e`.
El callback `0x91eb60` usa el Sender `+0x4c`; no es un pin YC.

## Evidencia y validación

`analysis/session22/evidence/s30_pipeline_audit.py`: instrucciones, hashes,
tablas, traducción SDF, callback, espera y campos de retorno.
`s30-native-verified.json`: doce ventanas nativas con hashes de los originales.
Los archivos `s30-*.json` conservan decompilaciones auxiliares; consultas
interiores con registros `unaff_*` no se usan como prueba de ABI o de función.

Validación: S30 **12/12**, S28 **6/6**, S29 **6/6**; ruff y mypy del auditor
nuevo PASS. `mypy --ignore-missing-imports src`: PASS. `ruff check src tests`
conserva los nueve avisos previos en cuatro tests no modificados. Sin commit:
el directorio no contiene repositorio Git.

Quedan pendientes exactamente: adquisición nueva sin cortinas; productor y
terminación DMA del YC; contrato de formato/planos/pitch y caché/reciclaje
de ese YC. Los RPC de pines, CaptureId y completion de encode no los sustituyen.

**VEREDICTO: CAMBIOS.** No están cerrados los tres requisitos funcionales.
