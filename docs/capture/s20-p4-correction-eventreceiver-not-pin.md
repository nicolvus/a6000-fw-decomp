# S20 — atribución histórica de `ctx+0x4c` corregida en S30

> **RECHAZADO por S30:** el constructor y offsets atribuidos aquí mezclan
> `ObjStillRecorderThread` con `StillConverter`. En StillConverter el
> constructor real `0x920c8c` crea **EventSender en `+0x4c`**, EventReceiver
> en `+0x50`, Handler en `+0x54` y thread en `+8`. Enlace local verificado
> en `0x920d0e`; `0x91618c` pertenece a ObjStillRecorderThread. El cuerpo se
> conserva como historial, no como contrato vigente. Véase [S30](s30-pipelines-capture-encode.md).

Continuación directa de `s20-p4-stillconverter-encodestill-dispatch.md`,
que dejó como pregunta abierta "el destino del pin en `ctx+0x4c`". Al
localizar el constructor real de la clase (antes no encontrado), el
resultado **corrige** la inferencia de esa tarea: no es un pin de
dataflow, es un mecanismo de notificación local. Alcance: `libObj.so`,
`llvm-objdump` directo. Sin Codex, sin subagentes.

## Hallazgo: constructor real localizado (offset `0x916140`, `libObj.so`)

Buscando los escritores de `+0x4c` dentro del bloque `StillConverter`
(`grep` sobre el volcado completo de `[0x91395c, 0x921d56)`), el primero
cronológicamente es un constructor real:

```asm
r4+0x50 = new EventHandlerWrapper()        ; _ZN19EventHandlerWrapperC1Ev
r4+0x48 = new MWF::EventSender()            ; _ZN3MWF11EventSenderC1Ev
r4+0x4c = new MWF::EventReceiver()          ; _ZN3MWF13EventReceiverC1Ev
EventReceiver::GenerateEventId(r4+0x4c, 0x2f)
EventReceiver::SetEventHandler(r4+0x4c, r4+0x50)
EventSender::SetEventReceiver(r4+0x48, r4+0x4c)   ; conecta Sender->Receiver LOCAL
r4+0x44 = new MWF::ObjThread(fn, arg, prio=8, nombre, flags)
ObjThread::StartThread(r4+0x44)                    ; arranca el hilo propio
```

**VERIFICADO**: `ctx+0x4c` es una instancia de `MWF::EventReceiver`
(constructor real `_ZN3MWF13EventReceiverC1Ev` llamado explícitamente, no
inferido). `ctx+0x48` es su `MWF::EventSender` emparejado, conectado al
receptor del **mismo objeto** (no a un objeto externo). `ctx+0x44` es un
`MWF::ObjThread` propio, arrancado en construcción — **StillConverter es
un objeto activo con su propio hilo trabajador**, consistente con el
patrón ya visto en otras clases MWF del proyecto (`ObjActiveBase`).

## Corrección sobre `s20-p4-stillconverter-encodestill-dispatch.md`

Aquella tarea interpretó la llamada `ldr r3,[r0]; ldr r3,[r3,#0xc]; blx r3`
sobre `*(ctx+0x4c)` como "patrón consistente con `ObjPin::Send`, no
verificado el layout exacto" — **se corrige**: el objeto en `ctx+0x4c` es
un `EventReceiver`, no un `ObjPin`; el slot de vtable `+0xc` es un método
virtual de `EventReceiver` (su identidad exacta —p. ej. `Notify`/`Post`—
no se decompiló en esta tarea, pero su clase ya no es ambigua). El mensaje
`ObjMsg(0x3a48,...)` que construyen las ramas de `"Receive
CBID_ENCODE_STILL"` y su rama hermana **no se envía a un pin externo de la
topología de objetos**; se entrega al `EventReceiver` **del propio
objeto**, que (vía `SetEventReceiver`) está conectado únicamente a su
`EventSender` hermano del mismo `StillConverter`.

## Implicación

**Este camino (`ctx+0x4c`) no lleva hacia DCF/MPR (P5) ni hacia ningún
objeto corriente abajo** — es un mecanismo de **auto-notificación /
auto-encolado** típico de un objeto activo: el manejador construye un
mensaje y lo entrega a su propio `EventReceiver`, que probablemente
despierta/reencola trabajo para su propio `ObjThread` (cruzando el límite
de hilo de forma segura), no reenvía datos a otra etapa del pipeline. Por
tanto, **se cierra negativamente** la pista "seguir el pin hacia su
destino" planteada ayer: no hay un "destino" externo que seguir por esta
vía. El verdadero destino final de un `EncodeStill` completado (JPEG →
DCF → catálogo) debe buscarse en otro punto, no en este mecanismo de
despacho interno.

## Clasificación

- **VERIFICADO**: `ctx+0x4c` = `MWF::EventReceiver`; `ctx+0x48` =
  `MWF::EventSender` emparejado (loopback local); `ctx+0x44` =
  `MWF::ObjThread` propio, arrancado en construcción.
- **DESCARTADO**: la inferencia previa de que el slot vtable `+0xc` sobre
  `ctx+0x4c` fuera `ObjPin::Send` — es un método de `EventReceiver`.
- **NO_VERIFICADO**: identidad exacta del método de `EventReceiver` en el
  slot `+0xc`; qué hace el `ObjThread` propio con el evento una vez
  despierto; si ese hilo, más adelante, sí alcanza DCF/MPR por otra vía no
  relacionada con `ctx+0x4c`.

## Archivos

```sh
llvm-objdump -d --triple=thumbv7-linux-gnueabi \
  --start-address=0x916140 --stop-address=0x916260 libObj.so
```

SilentShutter no se declara funcional.
