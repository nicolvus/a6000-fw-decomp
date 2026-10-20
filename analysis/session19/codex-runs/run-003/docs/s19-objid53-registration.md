# S19-03 — ObjId 53 y topología `0xb4`

**Estado: PARCIAL.** La clase del extremo identificado como ObjId 53 en la fila de topología `0xb4` queda corroborada como `ObjStillRecorder` por su API exportada y constructor real. No se localizó el sitio de auto-registro que asocia el entero 53 con esa clase; no se presupone una tabla estática de constructores.

| Estado | Hallazgo | Dirección / archivo | Método |
|---|---|---|---|
| VERIFICADO | La fila `0xb4` contiene `[0,6,0x35,1,2,0xb,0,0]`: salida 2 de ObjId 53 a entrada 0 de StillRecorder, `StsId=6`. | `libObj.so:.rodata 0xcc5830..0xcc584f` | Volcado little-endian; índice `(0xb4 * 0x20) + 0xcc4210`. |
| VERIFICADO | `ObjStillRecorder_Create` reserva `0x148` B y llama al constructor `0x9178f0`. | `libObj.so:0x91391c..0x913936` | `readelf -sW`; LLVM. |
| VERIFICADO | El constructor inicializa `MWF::ObjActiveBase` con `0x2f`, instala vtable y crea `MWF::ObjPin` junto a `ConnectPinWrapper`. | `libObj.so:0x9178f0..0x917a68` | LLVM; flujo de registros. |
| INFERENCIA | ObjId 53 es la instancia topológica de `ObjStillRecorder`; la asociación numérica 53→constructor no se recuperó. | `0xcc5830..0xcc584f`, `0x91391c`, `0x9178f0` | Correlación de topología y clase. |
| VERIFICADO | `0x41920c` construye placeholder genérico de `0x30` B vía `0x446e60` sólo en fallo de lookup. | `libObj.so:0x41920c..0x4192e4` | LLVM. |
| DESCARTADO | `0x41920c` no es tabla/factoría estática por ObjId. | `libObj.so:0x41920c` | LLVM. |
| VERIFICADO | `.init_array` tiene 263 entradas `R_ARM_RELATIVE`; no hay `.ctors` ni entradas a `ObjStillRecorder_*`. | `0xfd25a4..0xfd29bf` | `readelf`; decodificación de palabras. |
| VERIFICADO | No hay punteros a las cinco APIs exportadas `ObjStillRecorder_*` en datos asignables fuera de `.dynsym`. | `libObj.so` | Escaneo de palabras little-endian. |
| NO_VERIFICADO | No se identificó auto-registro explícito `0x35→ObjStillRecorder_Create`; puede ser indirecto o externo. | `.init_array/.data.rel.ro/.data/.rodata` | Inventario dirigido. |
| DESCARTADO | El `0x35` de `0x4172d6` es diagnóstico de `ObjStatusViewer`, no registro ObjId. | `0x417268..0x417322` | LLVM. |

La entrada `.init_array` `0x40e621` cubre código que puede llegar a `0x41a1fa → 0x4195c0`, pero no una inscripción explícita de ObjId 53. Nada prueba instancia runtime, activación de la fila, ejecución de `Connect` ni SilentShutter funcional. Análisis estático local, sin modificación de binarios ni cámara.
