# S26 — seis microprocesos cerrados alrededor de `Camera.YC0`

Fecha: 2026-10-17. Alcance: análisis estático, de sólo lectura, de los ELF
originales de A6000 FW 3.21. Este informe cierra procesos **acotados**; no
declara cerrado el trayecto sensor → descriptor YC → `StillRecorder`.

## Base de direcciones

**VERIFICADO:** `libObj.so` y `libBizFw.so` son ELF32 ARM `ET_DYN`; las
direcciones siguientes son VAs ELF usadas directamente por `llvm-objdump` con
`--triple=thumbv7-linux-gnueabi`. Los auditores S23--S25 ya validaron el
SHA-256 de `libObj.so` y los símbolos/rangos empleados. No se modificó ningún
binario.

## Procesos cerrados estáticamente

| Nº | Proceso y frontera | Evidencia cerrada | Límite explícito |
|---:|---|---|---|
| 1 | Instanciación `ObjCamera` → parser YC0 | `0x987eb6..0x987ec8`: reserva `0x54`, pasa `ObjCamera+0x58` al ctor `0xa281dc`, guarda el resultado en `ObjCamera+0xa0`. | No demuestra quién publica el primer mensaje YC. |
| 2 | Admisión de mensaje `0x1000` → estado del parser | `0xa27b22..0xa27c06`: obtiene `0x1000..0x1003`, exige que existan y escribe `+0x34/+0x38/+0x3c/+0x40`. | Los cuatro `u32` no tienen semántica de raster probada. |
| 3 | Estado del parser → request de 20 B | Helper `0x143428..0x143470` fija `{opcode=0x1000, flags=0, size=0x14, version=2}`; YC0 escribe después sus tres palabras de destino. | No identifica el significado de las tres palabras. |
| 4 | Request → respuesta Dataflow | `0xa14f88..0xa15110`: `SetDataflowMsg(…,0x14)`, `srcId=replyId=0x2015d`, `SendASync`, `ReceiveASync(..., UINT32_MAX)` y copia condicionada al tipo `1`. | No identifica el manejador ni convierte la respuesta en DMM/YC. |
| 5 | Consulta de endpoint → pin resuelto | `libBizFw.so:0x35a74..0x35ba4`: construye `_MSG_PIN_GET` opcode `0x1000`, llama `sndRcvAsyncDataflowMsg` y copia `reply+0x20` a `out+0x1c`. | El alta de `0x50004` y su callback siguen sin localizar. |
| 6 | Parser → emisión `ObjPin` | `0xa279e8..0xa27f3c`: crea `ObjMsg(0x2001,0x1001)`, copia relay-common y lo envía por `ObjPin::Send(0x1003, &out)`. | No es el `PlayData(0x2001,0x1003)` de `StillRecorder`. |

Los seis tienen una entrada, una transformación y una salida delimitadas por
instrucciones verificables; por ello se marcan **CERRADO ESTÁTICAMENTE sólo en
la frontera de la tabla**.

## Pseudocódigo consolidado

```c
// 1--4, simplificado; campos semánticos no inferidos
yc0 = new PinParserYcOut0(camera, camera->pin_yc0); // camera+0xa0
if (in.id == 0x1000 && params[0..3] != NULL) {
    yc0->u32_34_40 = values(params[0..3]);
    request20 = { 0x1000, 0, 0x14, 2, yc0->u32_10, yc0->u32_14, yc0->u32_18 };
    reply20 = dataflow_roundtrip(yc0->u32_10, request20, 0x2015d);
}
out = ObjMsg(0x2001, 0x1001);
out.CopyCommonRelayParam(in);
yc0->pin->Send(0x1003, &out);

// 5, dentro de la infraestructura
pin = sndRcvAsyncDataflowMsg(_MSG_PIN_GET{0x1000, endpoint}, ...).reply_pin;
```

## Reproducción

```sh
python3 -I analysis/session22/evidence/s26_closed_microprocesses_audit.py
```

El auditor desensambla exactamente los seis intervalos anteriores; no ejecuta
firmware ni escribe los ELF.

## Estado que no queda cerrado

**NO_VERIFICADO:** productor de YC de una adquisición nueva, terminación
sensor/DMA, direcciones, geometría, formato, caché, ownership, sincronización,
metadatos y vida útil del descriptor; compatibilidad de esa posible salida con
`ObjStillRecorderCore::WriteStill(0x909a84)`; y una ruta de lectura electrónica
sin accionamiento mecánico. **RECHAZADO:** que el cierre de estos seis
microprocesos pruebe cualquiera de esos puntos. SilentShutter sigue
**NO_VERIFICADO**.

## Veredicto

**VEREDICTO: PARCIAL.** Se alcanzan seis procesos cerrados estáticamente, pero
todos se sitúan en el transporte/configuración de `Camera.YC0`, aguas abajo de
la adquisición aún desconocida y antes de una compatibilidad no demostrada con
Recorder.

**Única siguiente investigación recomendada:** localizar el inicializador que
registra el endpoint `0x50004` y recuperar el callback que recibe su request
`0x1000`; es la arista con mayor probabilidad de revelar si entra un YC de
captura y bajo qué contrato.
