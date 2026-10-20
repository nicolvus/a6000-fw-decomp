# S23 — frontera Dataflow de los pines YC de ObjCamera

Actualización S28: [receptor y contrato resueltos](s28-osal-pin-contract-closure.md).
El helper envía 20 B pero copia **32 B** de respuesta; los cuatro enteros son
propiedades del pin remoto que se usan en REQUEST_CONNECT, no campos gráficos.
Esta corrección prevalece sobre las descripciones históricas siguientes.

Fecha: 2026-10-17. Alcance: `libObj.so` de A6000 FW 3.21, sólo lectura
estática. SHA-256 comprobado: `8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a`.

## Hallazgo

**VERIFICADO:** el parser del pin topológico `ObjCamera.out0` (`PIN_YC#0`),
`CamUser::PinParserYcOut0`, no entrega sus mensajes directamente al siguiente
objeto. Su método virtual de slot `+8`, ELF `0xa279c8`, usa un puente Dataflow
síncrono común en `0xa14f88`. La misma función es llamada por los parsers
`YcOut0`, `YcOut1`, `YcOut2`, `YcOut3` y `YcOut5`.

Esto identifica una frontera concreta entre la mensajería `MWF::ObjPin` y el
servicio Dataflow que procesa las operaciones YC. No identifica todavía el
productor sensor/DMA ni acredita que cualquiera de sus mensajes contenga un
raster YC válido para `StillRecorder`.

## Entrada y despacho de YC0

La RTTI coloca `0xa279c8` en la tercera entrada de la vtable primaria de
`CamUser::PinParserYcOut0` (`0x1021fb8`). El método obtiene el ID del mensaje
entrante y separa `0x1000`, `0x1003`, `0x3000` y `0x3001`.

Para la rama `0x1000` se comprueban cuatro `ParamStd<unsigned int>`:
`0x1000`, `0x1001`, `0x1002` y `0x1003`. Sus valores se guardan, en este
orden, en `this+0x34`, `+0x38`, `+0x3c` y `+0x40`. No hay en esta rutina una
interpretación estática que permita nombrarlos como dirección, ancho, alto o
formato.

```c
// 0xa27b22..0xa27c44, simplificado y VERIFICADO por ensamblador
if (msg->id == 0x1000) {
    p[0] = msg->GetParam(0x1000);
    p[1] = msg->GetParam(0x1001);
    p[2] = msg->GetParam(0x1002);
    p[3] = msg->GetParam(0x1003);
    if (!p[0] || !p[1] || !p[2] || !p[3]) return status_error;

    this->field34 = u32(p[0]);
    this->field38 = u32(p[1]);
    this->field3c = u32(p[2]);
    this->field40 = u32(p[3]);
    dataflow_roundtrip(this->field10, request20, reply40);
}
```

**VERIFICADO:** después de esta rama, el parser crea un sobre
`MWF::ObjMsg(0x2001, 0x1001)`, copia los parámetros comunes de relay y emite
por su pin (`this+8`) mediante `ObjPin::Send(0x1003, &out)`, en `0xa27f3c`.
En las rutas vistas, el sobre agrega `0x1005` o `0x132e`; no agrega los grupos
`0x1017/0x1031/0x1041` exigidos por el `PlayData` de `ObjStillRecorder`.

**RECHAZADO:** describir `PinParserYcOut0` como el productor del raster o
confundir su sobre `0x2001/0x1001` con el `PlayData` conocido
`0x2001/0x1003`.

## Contrato Dataflow recuperado

`0xa14f88` toma `(destination, request20, reply_buffer)` y ejecuta:

```c
DataflowInfraMsg m;
m.SetDataflowMsg(request20, 0x14);
m.SetReplyId(0x0002015d);
m.SetSrcId(0x0002015d);
DataflowInfraSender{}.SendASync(destination, &m);
DataflowInfraReceiver{}.ReceiveASync(0x0002015d, &m, UINT32_MAX);
if (m.GetMsgType() == 1)
    memcpy(reply_buffer, m.GetMsg(/* hasta 0x50 B */), 0x14);
```

El tercero de esos argumentos queda en una estructura de 40 bytes creada por
el llamador; el helper sólo copia los primeros 20 bytes de la respuesta.
`UINT32_MAX` hace que la espera sea indefinida en el código observado.

El solicitante YC0 construye los 20 bytes así, antes de llamar:

```c
struct DataflowRequest20 {
    u16 opcode;       // 0x1000
    u16 flags;        // 0
    u16 byte_count;   // 0x14
    u16 version;      // 2
    u32 field0;       // this+0x10
    u32 field1;       // this+0x14
    u32 field2;       // this+0x18
};
```

Los seis primeros campos son fijados por `0x143428`; las tres palabras finales
son escritas por `0xa27c06..0xa27c1e`. Los nombres semánticos de `field0..2`,
la identidad del `destination` guardado en `this+0x10`, y el handler que recibe
`0x1000` siguen **NO_VERIFICADOS**.

Existen dos helpers hermanos para contratos de 40 y otros tamaños (`0xa1516c`,
`0xa15350`), usados también desde las ramas de parsers YC. Eso confirma una
familia Dataflow compartida; no prueba compatibilidad con DMM/EncodeStill.

## Impacto sobre la cadena objetivo

| Tramo | Estado tras S23 |
|---|---|
| LIRO 0x78 → selector IMX210 | VERIFICADO antes de S23 |
| Terminación de lectura/DMA → mensaje YC0 | NO_VERIFICADO |
| Mensaje YC0 `0x1000` → estado interno del parser | VERIFICADO |
| Parser YC0 → solicitud/respuesta Dataflow | VERIFICADO |
| Respuesta Dataflow → descriptor DMM `ycBufferInfo` para EncodeStill | NO_VERIFICADO |
| Dirección, caché, ownership, barrera y vida útil | NO_VERIFICADO |
| Lectura electrónica sin mecánica | NO_VERIFICADO; SilentShutter no cambia |

## Reproducción

```sh
python3 -I analysis/session22/evidence/s23_yc_dataflow_audit.py
```

El auditor desensambla sólo `0xa27b22..0xa27c44`, `0xa14f88..0xa15110` y
`0x143428..0x143470` con `llvm-objdump`; no modifica el ELF.

## Veredicto y siguiente paso

**VEREDICTO: PARCIAL.** La frontera de transporte YC quedó cerrada
estáticamente hasta un request/reply Dataflow y se descarta que el parser sea,
por sí solo, el productor de píxeles. Falta el handler del destino guardado en
`PinParserYcOut0+0x10`: es la arista que puede revelar el significado de los
cuatro enteros y si produce/abre un DMM compatible con `EncodeStill`.

**Única siguiente investigación recomendada:** recuperar el constructor o
registro que asigna `PinParserYcOut0+0x10` y localizar el receptor Dataflow del
opcode `0x1000` para enlazarlo —o descartarlo— como productor de YC de captura.
