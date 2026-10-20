# S19-02 — LifeCycle y `ObjPin::Connect`

**Estado: PARCIAL.** Se verificó el punto de llamada efectivo a la implementación MWF y el comportamiento de `UObjPin::Connect`. No se verificó una arista de ejecución desde el `LifeCycle` creado por `TM::createLifeCycles` hacia aquel punto; por ello no existe todavía una cadena demostrada `createLifeCycles → Activate → Connect`.

## Hallazgos

| Estado | Hallazgo | Dirección / archivo | Método |
|---|---|---|---|
| VERIFICADO | `AVBIZ::UNIVERSE::UObjPin::Connect` ajusta `this+8` como `MWF::ObjPin*`, conserva `r1=dst` y `r2=ObjStatusViewer*`, y llama al PLT de `MWF::ObjPin::Connect`. El cuarto argumento sólo habilita trazas antes/después de la llamada; no es una precondición adicional del enlace. | `libBizFw2.so:0x2be8c`, llamada `0x2bf1c → 0x20588@plt`; relocación `0x43ee4 R_ARM_JUMP_SLOT`. | `llvm-objdump -d --triple=thumbv7-linux-gnueabi`, `readelf -rW`. |
| VERIFICADO | La implementación MWF rechaza destino nulo/igual, `PinType` diferente y direcciones incompatibles; para direcciones válidas asigna el destino y registra el `ObjStatusViewer` si se entregó. No comprueba que el destino estuviera previamente conectado. | `libMWF.so:0x29588..0x296d6`. | Desensamblado LLVM y flujo de registros. |
| VERIFICADO | `ConnectPinWrapper::Connect` de `libInfraCacheMgr.so`, `libInfraScalarMpr.so` y `libmprctrl.so` carga el pin envuelto de `this+4` y ejecuta `blx` al PLT MWF cuando su bandera diferida `this+0x15` es cero. Con la bandera activa guarda los argumentos y marca pendiente (`+0x16`), sin ejecutar `Connect` en esa invocación. | `0x1c0d0→0xca40`, `0x2a174→0x1540c`, `0x1f580→0xef3c`, respectivamente. | LLVM; seguimiento `r0/r1/r2`. |
| VERIFICADO | `BizObjPin::Connect` adapta `this` a `this+4` y hace salto de cola al PLT importado de MWF. | `libBizFw.so:0x42b5e..0x42b68`; `R_ARM_JUMP_SLOT 0x57eb4`. | LLVM y relocación dinámica. |
| VERIFICADO | `TM::createLifeCycles` reserva 0x14 bytes, invoca el constructor `0x41b6c0`, conserva el objeto y lo inserta/registrar mediante `0x419028`. | `libObj.so:0x419652..0x41969c`. | LLVM, seguimiento de `r9` y de argumentos. |
| VERIFICADO | El constructor escribe la vtable Itanium cuyo address point es `0xcc6698`; los tres slots Thumb son `0x41b605`, `0x41b649` y `0x41b65d` (restado el bit 0 para desensamblar). El slot de evento `0x41b65c` sólo registra/diagnostica el evento en el intervalo observado. | `libObj.so:0x41b6d4`, `.rodata:0xcc6694..0xcca0`, `0x41b65c..0x41b6b6`. | Palabras crudas, `R_ARM_RELATIVE`, LLVM. |
| INFERENCIA | `0x416faa → 0x41b728` es una activación o despacho posterior del objeto de ciclo: es el único caller directo localizado para esa rutina de estado. No se le asigna el nombre `Activate` al no conservarse símbolo. | `libObj.so:0x416f9e..0x416fae`, `0x41b728..0x41b75a`. | LLVM; relación directa de llamada. |
| NO_VERIFICADO | No aparece en el constructor, sus tres slots ni la rutina de despacho observada una llamada al PLT de `UObjPin::Connect` o `MWF::ObjPin::Connect`, ni una carga de puntero que resuelva a esos destinos. La arista de ejecución `LifeCycle → Connect` no queda demostrada. | Ventana `libObj.so:0x4195c0..0x4196f0`, `0x41b604..0x41b75a`, `0x416f9e..0x416fae`. | LLVM y seguimiento de punteros/vtable. |
| DESCARTADO | La vtable del LifeCycle como evidencia suficiente de una conexión de pines o de ejecución del callback. Define comportamiento posible, no prueba despacho runtime ni destino de pin. | `libObj.so:.rodata:0xcc6694`. | Separación entre tabla estática y ejecución. |

## Cadena sustentada y corte

```text
TM::createLifeCycles 0x4195c0
  → ctor LifeCycle 0x41b6c0 [VERIFICADO]
  → registro 0x419028 [VERIFICADO]
  → despacho posterior 0x416faa → 0x41b728 [INFERENCIA: rol Activate]
  └─ Connect de pin: sin arista demostrada [NO_VERIFICADO]

UObjPin::Connect 0x2be8c
  → ObjPin::Connect@plt 0x20588
  → MWF::ObjPin::Connect 0x29588 [VERIFICADO]
```

`UObjPin::Connect` no añade una restricción de compatibilidad distinta a MWF en el camino de enlace: instrumenta con `Uc` y delega. Los `ConnectPinWrapper` sí pueden **diferir** una llamada por su bandera local, pero eso no prueba que un LifeCycle sea su productor ni su ejecutor posterior.

## Límites

Se examinó exclusivamente la extracción FW 3.21 y no se modificaron binarios. Una relocación `JUMP_SLOT` y una llamada PLT prueban la ruta de enlace de código, no que una instancia concreta haya ejecutado la llamada en runtime. Nada de lo anterior demuestra que SilentShutter funcione.

## Siguiente tarea

`S19-03`: seguir el registro de `0x419028` y el caller `0x416faa` hasta su origen/evento, y contrastar los objetos de pin usados en ese despacho con los callers de `UObjPin::Connect`/`ConnectPinWrapper`.
