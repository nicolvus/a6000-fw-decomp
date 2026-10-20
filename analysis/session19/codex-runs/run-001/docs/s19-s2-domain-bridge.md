# S19-01 — puente S2 entre dominios de mensajes

**Resultado:** PARCIAL. Se localizó el mecanismo estático de registro indirecto de `0x43807f4c`, pero no hay evidencia estática que lo conecte con la cola CamUser `0x40193` ni con los mensajes ObjMsg `0x3011/0x3013/0x3015`. Por tanto, no se declara funcional `SilentShutter`.

## Evidencia nueva

| Estado | Hallazgo | Dirección / método | Fuente |
|---|---|---|---|
| VERIFICADO | El dispatcher local lee el primer `u32` de `r1`, discrimina `0x100..0x207` (más `0x8201..0x8306`) y para `0x100` llama a `0x43807d80`. | `0x43807f4c`; `llvm-objdump -d --triple=thumbv7-none-eabi`. | `analysis/av-cam-analysis-view.elf` (base `0x43541000`). |
| VERIFICADO | `0x43807f4c` está registrado como puntero Thumb `0x43807f4d` en la palabra `0x43fcd5d0`; no hay `bl` directo a su entrada. | lectura cruda de palabras y búsqueda de patrón little-endian. | `analysis/av-cam-analysis-view.elf`. |
| INFERENCIA | El bloque que empieza en `0x43fcd5b4` es un registro/tabla de handlers, no una vtable C++ convencional: incluye un descriptor `0x43fffd94`, callbacks Thumb y entradas hermanas en `0x43fcd5f4`. La presencia de la entrada prueba registro declarativo, no ejecución. | agrupación de palabras contiguas; puntero GOT `0x44022c04 -> 0x43fcd468` que referencia la familia de tablas. | `analysis/av-cam-analysis-view.elf`. |
| VERIFICADO | La ruta local `0x100` puede llegar a `CaptureStart`: `0x43807f4c` → `0x43807d80` → llamadas directas a `0x43809ed8`; este último arma el callback con `0x439018b0` y termina llamando a `0x43b0172c` sobre el objeto recibido. | LLVM en `0x43807d80`, `0x43809ed8`. | `analysis/av-cam-analysis-view.elf`. |
| VERIFICADO | `RelMgr` emite las transiciones ObjMsg previas: `0x3013` y `0x3015`; en la ruta de disparo emite tipo 2, id `0x3011`, mediante `0x43aeaf18` hacia `0x40193`. | LLVM en `0x4379ea40`, `0x4379eb0c`, `0x4379eba8` y la evidencia C2 heredada. | `analysis/av-cam-analysis-view.elf`; `docs/capture/shutter-trigger-chain-0x3011.md`. |
| VERIFICADO | El tratamiento de `0x3011` ya recuperado es una tabla de permiso/estado: fila `{0x437fd0e1, 0x3011, 2, 0x3010}` en `0x43ffdd30`; no contiene el callback local ni `CaptureStart`. | reconstrucción C2 conservada, contrastada con su fuente. | `docs/capture/shutter-trigger-chain-0x3011.md`. |
| NO_VERIFICADO | El receptor OSAL/ObjMsg de la cola `0x40193`, su registro y su adaptación desde `0x3011/0x3013/0x3015` al mensaje local `0x100` no se localizaron. | búsquedas de puntero, xrefs literales y seguimiento de tabla; no existe una arista de llamada/registro demostrable. | `analysis/av-cam-analysis-view.elf`. |
| DESCARTADO | Considerar el puntero de tabla como prueba de que el callback se ejecuta o de que recibe `0x40193`. | separación explícita entre registro declarativo y entrega dinámica. | evidencia anterior. |

## Cadena que sí queda sustentada

```text
RelMgr 0x4379d838
  ├─ 0x3013 / 0x3015 → ObjMsg → cola 0x40193     [VERIFICADO]
  └─ tipo 2, 0x3011 → ObjMsg → cola 0x40193      [VERIFICADO]
       └─ receptor/adaptador desconocido          [NO_VERIFICADO]

tabla estática 0x43fcd5b4
  └─ slot 0x43fcd5d0 = 0x43807f4d (Thumb)         [VERIFICADO]
       └─ dispatcher local 0x43807f4c
            └─ caso 0x100 → 0x43807d80 → 0x43809ed8 → CaptureStart [VERIFICADO]
```

La topología de ambos extremos es ahora más concreta, pero sigue faltando la arista central. Los dominios no deben tratarse como equivalentes: `0x3011/0x3013/0x3015` son IDs ObjMsg de CamUser; `0x100..0x207` son códigos del mensaje local que recibe el dispatcher registrado.

## S1, S2, estados, cancelación y liberación

- **S1/S2:** INFERENCIA heredada: RelMgr conserva sus estados/índices de tecla antes de emitir los ObjMsg. Esta ejecución no demuestra qué evento físico equivale a S2 ni que `0x3011` sea por sí solo el borde eléctrico de S2.
- **Transición de captura:** VERIFICADO solo desde la rama local: un evento local `0x100` puede invocar el instalador `0x43809ed8`; el instalador no prueba que sea invocado por `0x3011`.
- **Cancelación/liberación:** NO_VERIFICADO para el cruce. El dispatcher local contiene ramas de limpieza y las filas LIRO conocidas tienen callbacks de retry/cancel, pero no se demostró que consuman la cancelación asociada a una liberación de `0x3015`.

## Método y límites

Se empleó `llvm-objdump` y lectura cruda del ELF de vista; una invocación dirigida de Ghidra no produjo JSON, por lo que no se usó como evidencia. No se modificaron binarios ni se ejecutó hardware. La ausencia de una arista estática no refuta una conexión de runtime: queda como **NO_VERIFICADO**, no como ausencia funcional.

## Siguiente tarea

`S19-02`: seguir el consumidor de la familia de tabla `0x43fcd5b4` hasta el registro OSAL/ObjMsg y buscar la conversión de estructura, no sólo comparaciones literales de `0x3011`.
