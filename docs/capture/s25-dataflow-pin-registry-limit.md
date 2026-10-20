# S25 — límite estático del registro Dataflow para `0x50004`

Actualización S28: [registro y receptor identificados](s28-osal-pin-contract-closure.md).
InfraImaging construye los cinco pines estáticamente y sirve la cola en
`0x4379744c`. La copia correcta es `reply+0x1c → out+0x1c`, dentro de 32 B.
Este cierre supera el límite histórico y corrige el offset descrito abajo.

Fecha: 2026-10-17. Análisis estático de `libBizFw.so` y `libObj.so` de A6000
FW 3.21.

## Resultado

**VERIFICADO:** la configuración ObjEffect de S24 no obtiene el pin de
`0x50004` desde una tabla local `endpoint → callback`. Llama
`OBJAVBBCBASECLASS::DataflowInfraCh::infraGetPin` en `libBizFw.so` ELF
`0x35a74`.

`infraGetPin` construye `_MSG_PIN_GET` con opcode interno `0x1000`, empaqueta
los campos de `INFRA_GET_PIN_COMP` y el identificador solicitado, y llama:

```c
DataflowInfraCh::sndRcvAsyncDataflowMsg(
    channel, request_component, request_size, request, reply_size, ...);
```

Tras retorno exitoso copia campos de la **respuesta** al destino que recibe el
llamador, incluido el valor de `reply+0x20` a `out+0x1c`. Por tanto, el
`DataflowInfraPin` que entrega `infraGetPin` se materializa por respuesta de
un registro/servicio en ejecución.

**VERIFICADO:** no hay, en el constructor `PinParserYcOut0` ni en el tramo
`ObjEffect 0x15d6c0..0x15d7a2`, un puntero estático al callback que consume el
payload `0x1000`; sólo existen la consulta de endpoint `0x50004` y las
operaciones de conexión del pin retornado.

**INFERENCIA:** el mapeo endpoint→pin/callback se puebla durante el ciclo de
vida Dataflow. Esta inferencia se limita al mecanismo observado: no identifica
qué componente realiza el registro ni afirma que sea imposible reconstruirlo
buscando su inicializador en otro módulo.

## Consecuencia para la ruta YC

```text
Camera.YC0 → PinParserYcOut0
          → endpoint constante 0x50004
          → infraGetPin request/reply
          → pin/callback resuelto en tiempo de ejecución
```

Esto explica por qué el análisis de los constructores no revela el receptor
final del request `0x1000`. No demuestra que el registro sea necesariamente
dinámico en todas las fases ni que el flujo llegue a StillRecorder.

**NO_VERIFICADO:** inicializador del registro, receptor de `0x50004`, formato
de respuesta/píxeles, descriptor DMM, caché, ownership, sincronización, vida
útil, o lectura electrónica completa. SilentShutter sigue **NO_VERIFICADO**.

## Reproducción

```sh
python3 -I analysis/session22/evidence/s25_dataflow_registry_audit.py
```

El auditor desensambla únicamente `libBizFw.so:0x35a74..0x35ba4`.

## Veredicto

**VEREDICTO: PARCIAL.** El bloqueo de resolución de callback quedó demostrado:
la frontera es un request/reply de registro, no una tabla local que pueda
seguirse desde Camera.YC0. Aún existe una ruta estática alternativa: localizar
el inicializador que registra `0x50004` en los módulos Dataflow/ObjEffect.

**Única siguiente investigación recomendada:** buscar el alta de endpoint
`0x50004` o su `INFRA_GET_PIN_COMP` en inicializadores de `libObj.so`,
`libBizFw.so` y `dataflowInfraFramework.so`.
