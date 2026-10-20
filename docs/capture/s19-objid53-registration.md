# S19-03 — ObjId 53 y topología `0xb4`

**Estado: PARCIAL — CORREGIDO en sesión 20 (ver `s20-s19-corrections.md`, C1).** La fila `0xb4` tiene `ObjId 53` como objeto **origen** (`src_obj`, pin de salida 2) y `ObjId 11 (0x0b)` como objeto **destino** (`dst_obj`, pin de entrada 0). La clase corroborada por constructor real (`ObjStillRecorder_Create` → `0x9178f0`) es la del **destino, ObjId 11**, no la de ObjId 53. La clase real de ObjId 53 sigue **NO_VERIFICADA**: no se localizó su constructor ni el sitio de auto-registro que asocia el entero 53 con una clase concreta.

## Hallazgos

| Estado | Hallazgo | Dirección / archivo | Método |
|---|---|---|---|
| VERIFICADO | La fila `0xb4` de la tabla de topologías contiene `[0,6,0x35,1,2,0xb,0,0]`: conecta la salida 2 del objeto 53 al pin de entrada 0 de StillRecorder, con `StsId=6`. | `libObj.so:.rodata 0xcc5830..0xcc584f` | Volcado little-endian de `.rodata`; índice `(0xb4 * 0x20) + 0xcc4210`. |
| VERIFICADO | `ObjStillRecorder_Create` reserva `0x148` B y llama al constructor `0x9178f0`; la API exportada proporciona una identidad de clase independiente para el extremo StillRecorder. | `libObj.so:0x91391c..0x913936` | `readelf -sW`; `llvm-objdump -d --triple=thumbv7-linux-gnueabi`. |
| VERIFICADO | El constructor de `ObjStillRecorder` inicializa `MWF::ObjActiveBase` con el literal `0x2f`, instala su vtable y crea objetos `MWF::ObjPin` junto a `ConnectPinWrapper`. | `libObj.so:0x9178f0..0x917a68` | LLVM; seguimiento de argumentos y asignaciones. |
| INFERENCIA | El **destino** de la fila `0xb4` (ObjId 11, 0x0b) es la instancia topológica de la clase `ObjStillRecorder`: el objeto destino nombrado por la fila coincide con la clase cuya construcción y pines se verificaron. ObjId 53 es el objeto **origen** de esa misma fila; su clase real no se recuperó y la asociación numérica 53→constructor sigue sin localizarse. | `libObj.so:0xcc5830..0xcc584f`, `0x91391c`, `0x9178f0` | Correlación de topología y API/clase, sin tabla de registro localizada. |
| VERIFICADO | `TM::createLifeCycles` obtiene dos participantes mediante `0x41920c`; cuando falta una entrada, esta rutina reserva `0x30` B y construye un placeholder genérico en `0x446e60`. Luego crea el `LifeCycle` de `0x14` B en `0x41b6c0` y lo registra por `0x419028`. | `libObj.so:0x41920c..0x4192e4`, `0x4195c0..0x4196f0` | LLVM; flujo de registros. |
| DESCARTADO | `0x41920c` no es un constructor de ObjId ni una factoría estática por ID: sólo busca una entrada existente y crea el placeholder genérico al no hallarla. | `libObj.so:0x41920c..0x4192e4` | LLVM; tamaño de asignación `0x30` y llamada a `0x446e60`. |
| VERIFICADO | `libObj.so` tiene `.init_array` con 263 entradas, todas `R_ARM_RELATIVE`; no hay `.ctors`. Ninguna entrada apunta al rango de `ObjStillRecorder_*` (`0x913900..0x913966`). | `libObj.so:.init_array 0xfd25a4..0xfd29bf`, secciones ELF | `readelf -SW/-rW`; decodificación de las 263 palabras. |
| VERIFICADO | No hay puntero a `ObjStillRecorder_Create` ni a las cinco APIs exportadas `ObjStillRecorder_*` en secciones asignables de datos; los únicos valores hallados son sus propias entradas `.dynsym`. | `libObj.so:.dynsym` y secciones asignables | Escaneo de palabras little-endian de todas las secciones asignables. |
| NO_VERIFICADO | No se identificó un inicializador global, tabla/mapa o llamada que registre explícitamente `0x35` con `ObjStillRecorder_Create` antes de `main`. La ausencia anterior excluye las formas directas inspeccionadas, no todos los registros indirectos posibles. | `libObj.so:.init_array`, `.data.rel.ro`, `.data`, `.rodata` | Inventario de init-array, relocaciones, punteros y desensamblado dirigido. |
| DESCARTADO | El literal `0x35` en `0x4172d6` no identifica ObjId 53: aparece en una rutina que emite diagnóstico para un `ObjStatusViewer` cuyo estado no es 1. | `libObj.so:0x417268..0x417322` | LLVM; flujo de control y argumentos a logging. |

## Topología y ciclo de vida

```text
fila 0xb4: ObjId 53.out2 ──> ObjStillRecorder.in0   (StsId 6)
                     │
                     └─ clase corroborada: ObjStillRecorder_Create
                                            └─ ctor 0x9178f0

TM::createLifeCycles 0x4195c0
  ├─ lookup/placeholder 0x41920c (0x30 B si no existe)
  └─ LifeCycle 0x41b6c0 (0x14 B) → registro 0x419028
```

La línea superior identifica la clase del extremo por la semántica ya establecida de la fila y por el constructor exportado. No prueba una instancia runtime concreta, la ejecución de `Connect`, ni que la topología se active durante una captura.

## Inicialización y límites

La entrada `.init_array` que cubre el subsistema (`0x40e621`) sí contiene el flujo que posteriormente puede llamar `TM::createLifeCycles` (`0x41a1fa → 0x4195c0`), pero no contiene una inscripción explícita de `0x35` con la API de StillRecorder. El constructor público `ObjStillRecorder_Init` tampoco es una entrada de `.init_array` y no tiene una referencia directa recuperada desde dicho arreglo.

Por tanto el mecanismo de registro puede ser indirecto, externo a `libObj.so`, o depender de datos inicializados en tiempo de carga que no codifican directamente la dirección de la API exportada. Es **NO_VERIFICADO**, no una prueba de que no exista.

## Seguridad y siguiente tarea

Análisis estático, local y de sólo lectura sobre A6000 FW 3.21. No se modificó ningún binario, no se abrió ni eliminó ningún proyecto Ghidra y no se conectó ni flasheó una cámara. Nada de este análisis declara SilentShutter funcional.

Siguiente: `S19-04`, seguir el registro indirecto/consumidor de la instancia ObjStillRecorder y la activación efectiva de la topología `0xb4`.
