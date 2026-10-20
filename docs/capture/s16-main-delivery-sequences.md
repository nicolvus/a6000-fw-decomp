# Rama principal — secuencias 0x3900/0x600D vs 0x3900/0x6013 (sesión 16)

Alcance: análisis estático de `libObj.so` fw 3.21. Direcciones **ELF** salvo indicación "Ghidra VA" (= ELF + 0x10000). Evidencia propia de esta sesión (distinta de la de Rama A/Rama B sesión 16, y distinta de la ya registrada en sesión 15): nuevo hallador gemelo de `0x600d` en ELF `0x1f25d8` y decompilado de la factoría de secuencias `0x17b004`.

## Hallazgo nuevo 1 — segundo handler gemelo que construye `0x3900/0x600d` (ELF `0x1f25d8`)

Búsqueda de literales `movw #0x600d` / `movw #0x6013` en todo `libObj.so` (4.4M líneas de desensamblado completo, `llvm-objdump -d --triple=thumbv7-linux-gnueabi`): solo **dos** sitios construyen cada literal.

- `0x600d`: ELF `0x1e9be8` (dentro del parser REQ_DELIVER ya conocido, `0x1e9880`, sesión 15/Rama A) y ELF `0x1f25d8` (**nuevo**, función independiente, ~0x9d58 bytes más adelante).
- `0x6013`: ELF `0x17b01e` (factoría de secuencias, `0x17b004`) y ELF `0x1e96c0` (handler conocido, sesión 15).

Decompilado de la función nueva (ELF `0x1f25d8`, Ghidra `0x2025d8t`), **VERIFICADO (decompilado propio)**:

```c
void FUN_0x1f25d8(this) {
  if (tipo_submensaje(this+0xc) != 0x29 /* 0x1003 */) { log(0x6d); return; }
  submsg = leer_msgid(...);                         // iVar2
  (**(this+0x14)->vtbl[0x3c])(this+0x14, 1);          // GetSubState(block,1) = acceso al holder de modo
  modo = GetMode();                                   // func_0x15011c, getter genérico
  campo_0x100a = 0xe;  // valor por defecto
  leer_submensaje(iVar1, 0x100a, &campo_0x100a);
  if (campo_0x100a != 0 && campo_0x100a != 0xa) {
     if (modo == 0xe)      msg = 0x6053;
     else if (modo == 0xf) msg = 0x6052;
     else if (modo == 1) {
        msg = 0x6051;
        if (submsg == 0x1011) msg = 0x600d;          // ÚNICA condición para 0x600d
     }
     else goto default;
  } else default: msg = 0x6051;
  func_0xef454(this+0xc, 0x3900, msg);
  func_0xbd3208(this+0x5c, this+0xc, this+4);          // misma cola que el handler de sesión 15
}
```

**Confirma de forma independiente**, con una función distinta a la de sesión 15, exactamente la misma condición ya documentada por Rama A: `EffectInternalMode==1` y submensaje `0x1011` ⇒ `0x3900/0x600d`. Doble verificación cruzada (dos funciones distintas, misma regla).

**Hallazgo adicional no documentado antes**: existe una familia de mensajes hermanos no catalogada — `0x6051` (caso general/default), `0x6052` (modo `0xf`), `0x6053` (modo `0xe`). Estos NUNCA se habían registrado en sesiones previas. Su significado semántico es **NO VERIFICADO**, pero su existencia muestra que el "modo 1" no es la única rama con mensaje propio: cada modo "especial" (`1, 0xe, 0xf`) tiene su propio código de notificación, y `0x600d` es solo el caso en que, además, el submensaje entrante coincide con `0x1011`.

## Hallazgo nuevo 2 — la factoría `0x17b004` SÍ distingue 0x6013 de 0x600d: una es una Sequence con estado, la otra no

Decompilado de la factoría (ELF `0x17b004`, Ghidra `0x18b004t`), **VERIFICADO (decompilado propio)**:

```c
undefined4 FUN_0x17b004(ctx, uint tipo) {
  switch (tipo) {
    case 0x300b: /* ... */ return new(0x54 B); // ctor 0x1bdedc
    case 0x3003: return new(0x54 B);           // ctor 0x182f38
    case 0x3004: return new(0x70 B);           // ctor 0x184354
    case 0x603b: return new(0x70 B);           // ctor 0x184354 (mismo ctor reusado)
    case 0x6013: return new(0xd4 B);           // ctor 0x1861a8  ← SaveStillEditCmd
    default: return 0;
  }
}
```

**`0x600d`, `0x6051`, `0x6052`, `0x6053` NO aparecen en ningún caso de esta factoría.** Solo `0x6013` (y `0x300b/0x3003/0x3004/0x603b`, no relacionados con esta pregunta) instancian un objeto de secuencia con estado propio (bloque de `0xd4` bytes). El constructor `0x1861a8` decompilado es un stub trivial (`*param_2 = param_4`, instala un puntero de vtabla) — la lógica real de ejecución vive en los métodos virtuales de esa clase, no en el constructor; no se localizó su `Execute()`/`BeginExecCommand` en el tiempo disponible de esta sesión (candidato razonable: la cadena ya documentada en sesión 14, `analysis/yc-pin-delivery-flow.json` paso 4, `0x15fa74`/`0x15fd50`/`SequencePinDeliverExecWriteStillCmd`, que sí hace `AllocMem`+resize SDF+`PinConnect`; **NO VERIFICADO** que sea la misma instancia, solo es plausible por continuidad temática).

## Respuestas a las 8 preguntas del encargo

| # | Pregunta | Respuesta | Clasificación |
|---|---|---|---|
| 1 | ¿Qué clase ejecuta cada secuencia? | Ambas rutas (`0x600d` y `0x6013`) se construyen dentro del **mismo tipo de manejador de comando de pin de ObjEffect** (el mismo layout `this` que el parser REQ_DELIVER, confirmado en dos funciones gemelas: `0x1e9880` y, nuevo esta sesión, `0x1f25d8`). La diferencia está en lo que generan: `0x6013` pasa por la factoría `0x17b004` e instancia una **clase Sequence real** de `0xd4` bytes (ctor `0x1861a8`); `0x600d` (y sus hermanos `0x6051/0x6052/0x6053`) **no instancian ningún objeto** — se postean como `ObjMsg` crudo vía `func_0xbd3208`, sin pasar por la factoría. | VERIFICADO (decompilado propio, factoría + 2 handlers) |
| 2 | ¿Qué pin de entrada utiliza? | Ninguna de las dos funciones fija un número de pin: el campo "nº de pin" (`this+0x50`) llega en el propio mensaje `REQ_DELIVER` entrante (ver `0x173158`, sesión 15). El código es **genérico por pin**: la misma lógica de modo/mensaje se ejecuta sin importar si la petición es sobre la salida `#0` (fila `0x07`, hacia Renderer) o la salida `#1` (fila `0x2a`, hacia Recorder) — cuál de las dos está en juego lo decide el **emisor** de la petición, no este código. | VERIFICADO (ausencia de check de nº de pin en ambas funciones) |
| 3 | ¿Cómo selecciona el frame de origen? | No se encontró selección de frame dentro de estos dos despachadores: solo deciden **qué mensaje de control** mandar, no qué datos adjuntar. La selección real del frame (si ocurre) debe vivir en el método `Execute()`/`BeginExecCommand` de la clase Sequence `0xd4` B instanciada por `0x6013`, no localizado en esta sesión. | NO VERIFICADO (no es parte del despachador; pendiente en la clase Sequence) |
| 4 | ¿Qué diferencia funcional existe entre las dos secuencias? | Diferencia real y nueva en esta sesión: `0x6013` crea un objeto con estado (una Sequence completa, memoria propia, probablemente con pasos múltiples); `0x600d` es un **mensaje plano sin objeto de estado**, estructuralmente más parecido a un *acuse/eco* que a una entrega de imagen. Esto es consistente con que PbCap (modos 2–5, verificado en sesión 15) sí mueve datos (DMM/SDF, sesión 14), mientras que el camino de modo 1 (`0x600d`) no tiene, hasta donde se ha mirado, ninguna llamada a asignación DMM ni a SDF en el propio despachador. | VERIFICADO la asimetría de instanciación; INFERENCIA que "0x600d no mueve imagen" (ausencia de evidencia, no prueba de ausencia) |
| 5 | ¿Cuál utiliza resize/rotate? | Ninguna de las dos funciones de despacho llama directamente a SDF. La única llamada a `ObjMsg(0x3900,0x3000)` (resize/rotate SDF) catalogada hasta ahora sigue siendo la de sesión 14 (`0x15fa74`, dentro de la cadena de escritura de still de PbCap). Si esa cadena es la continuación de la Sequence `0xd4`B de `0x6013` es **plausible pero no verificado** en esta sesión (mismo bloque temático, sin xref directa confirmada). | NO VERIFICADO el enlace directo; la ruta `0x6013` es la única candidata razonable |
| 6 | ¿En qué condiciones construye `PlayData`? | No se observó construcción de `PlayData` en ninguno de los dos despachadores (`0x1e9880`/`0x1f25d8`) ni en la factoría (`0x17b004`) ni en el stub del constructor (`0x1861a8`). Sigue siendo, como en sesiones previas, un hallazgo de la cadena de sesión 14 (`ObjScalar::MakePlayDataMsg`), no reproducido aquí. | NO VERIFICADO en esta sesión (fuera del alcance de las funciones inspeccionadas) |
| 7 | ¿`0x600D` depende de reproducción o puede operar con entrada Camera? | La única condición de disparo verificada es `EffectInternalMode==1` + submensaje entrante `== 0x1011` — ninguna de las dos condiciones menciona el origen del pin de entrada (Camera vs Player). Dado que **no se encontró ninguna llamada a DMM/SDF** en el propio despacho de `0x600d`, es razonable (INFERENCIA) que esta ruta no mueva realmente un frame y por tanto sea indiferente al origen (Camera o Player) — pero esto no se puede confirmar sin encontrar el consumidor final de `0x3900/0x600d` en la cola de pines (`this+0x5c`→`vtbl+0x44`→slot 8), que no se decompiló en esta sesión. | NO VERIFICADO el consumidor final; INFERENCIA de que es indiferente al origen |
| 8 | ¿Qué respuesta/evento autoriza continuar hacia el Recorder? | Para `0x6013`: la única "autorización" encontrada es la construcción exitosa de la Sequence (factoría `0x17b004` devuelve puntero no nulo) — no hay un paso de aprobación adicional visible en el despachador ni en el constructor. Para `0x600d`: no hay Sequence que "continúe" nada; es un mensaje terminal en sí mismo según la evidencia disponible. Ninguno de los dos casos muestra, en el código inspeccionado esta sesión, una comprobación explícita de que el Recorder esté conectado (fila `0x2a`) antes de proceder — coincide con la ausencia de guard de exclusión ya reportada por sesión 15 y por Rama A de esta sesión. | VERIFICADO la ausencia de guard explícito en estas funciones; NO VERIFICADO si existe en capas más internas (pin manager, no inspeccionado) |

## Consecuencia para la arquitectura E

Este hallazgo **no mejora ni empeora** la viabilidad de la arquitectura E: refuerza con una segunda fuente independiente que el modo 1 (`0x600d`) es un camino real y simple del parser, pero añade evidencia nueva de que, a diferencia de `0x6013`, **no parece transportar datos de imagen** (ausencia de instanciación de Sequence/DMM/SDF). Si eso se confirmara, el modo 1 dejaría de ser un candidato razonable para portar un frame de Camera — habría que centrarse en los modos 2–5 (mismos que ya usa PbCap), que siguen sin tener un escritor conocido activado desde Live View (bloqueo ya reportado en sesión 15).

## Clasificación resumen

| Afirmación | Clasificación |
|---|---|
| Existe un segundo handler gemelo (ELF `0x1f25d8`) con la misma regla modo1+0x1011→0x600d | VERIFICADO (decompilado propio) |
| Familia de mensajes hermanos 0x6051/0x6052/0x6053, antes no catalogada | VERIFICADO (existencia); NO VERIFICADO (semántica) |
| La factoría 0x17b004 solo instancia Sequence con estado para 0x6013 (y 0x300b/0x3003/0x3004/0x603b), nunca para 0x600d | VERIFICADO (decompilado propio) |
| 0x600d no transporta imagen (ausencia de DMM/SDF en su despacho) | INFERENCIA (ausencia de evidencia) |
| Ningún pin de entrada ni comprobación de origen (Camera/Player) en estos despachadores | VERIFICADO (ausencia de checks) |
| Enlace entre la Sequence de 0x6013 y la cadena SDF de sesión 14 (0x15fa74/0x15fd50) | NO VERIFICADO (plausible por continuidad temática) |

## NO VERIFICADO (pendiente)

Método `Execute()`/`BeginExecCommand` real de la clase Sequence `0xd4`B (ctor `0x1861a8`); consumidor final de la cola `this+0x5c→vtbl+0x44[8]` para ambos mensajes; significado semántico de `0x6051/0x6052/0x6053`; si la cadena SDF de sesión 14 es literalmente la misma instancia que dispara `0x6013`.
