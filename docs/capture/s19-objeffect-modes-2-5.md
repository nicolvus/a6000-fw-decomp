# S19-11 — Modos 2–5 de ObjEffect ante la entrada Camera

Alcance: Sony A6000 FW 3.21, análisis estático local de
`libObj.so` SHA-256 `8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a`.
Direcciones: offsets ELF. Método: `llvm-objdump -d --triple=thumbv7-linux-gnueabi`.
No se modificó firmware, no se usó Ghidra, ni se conectó o flasheó una cámara.

## Veredicto

**S19-11: PARCIAL.** El enum efectivo en este recorrido es exactamente el rango
`2..5`: el valor se obtiene dinámicamente del proveedor/holder y se guarda en
`Sequence+0x50`. Las cuatro cifras llegan al mismo pre-despacho, pero sólo el
valor **3** supera el filtro interno y prepara/envía `ObjMsg(0x3900, 0x0002)`.
Los valores **2, 4 y 5** retornan por la rama de error sin construir esa orden.

Este `0x3900/0x0002` no es la ruta PbCap/SDF ya verificada, que usa
`0x3900/0x3000` y asigna los DMM raster/SDS en `0x15fa74`; tampoco hay llamada
desde este dispatcher a `0x15ebfc` (publicación `PlayData` condicionada a
`0x111`). Por ello ningún modo 2–5 queda verificado como productor de un buffer
apto para `EncodeStill` o PbCap. Aunque la topología estática previa enlaza
`Camera.out0 → Effect.in0`, no se recuperó una arista de ejecución ni la
identidad del holder que entrega el modo: las conclusiones son condicionales a
que dicha entrada alcance esta secuencia.

## Despacho y valores reales

| Estado | Dirección, archivo, método | Hallazgo |
|---|---|---|
| VERIFICADO | `0x1761a8..0x1761c8`, `libObj.so`, LLVM | El constructor de la secuencia inicializa a cero el byte `this+0x50`; no fija un modo 2–5 por constante. |
| VERIFICADO | `0x176ae8..0x176bc0`, `libObj.so`, LLVM | Tras validar holder (`+0x14`) e interfaz (`+0x8`), invoca la ranura virtual con selector 1, transforma el resultado por `0x14011c` y guarda el byte resultante en `this+0x50`. El nombre semántico del enum sigue NO_VERIFICADO. |
| VERIFICADO | `0x176cc6..0x176cce`, `libObj.so`, LLVM | El código carga `this+0x50`, resta 2 y acepta sólo si el resultado sin signo es `<=3`. Es un rango real e inclusivo: **2, 3, 4 y 5**, no una numeración asumida. |
| VERIFICADO | `0x176cd0..0x176ce2`, `libObj.so`, LLVM | Para esos cuatro valores llama `0x176294`; el resultado, incluso de error, se entrega después a `0x176994`. Los demás valores saltan a la misma finalización de error. |

## Diferencia por modo

| Valor efectivo | Procesamiento observado | Compatibilidad EncodeStill/PbCap | Mecánica |
|---|---|---|---|
| 2 | VERIFICADO: entra al filtro `2..5`, pero en `0x176550..0x176562` no es 3 y salta a `0x17676a`; registra/retorna error. No construye `ObjMsg(0x3900, 0x0002)`. | DESCARTADO para este recorrido: no llega a la reserva/publicación PbCap. | NO_VERIFICADO: este código no llama a control de cámara/obturador. |
| 3 | VERIFICADO: `0x176550..0x176566` toma la rama especial. `0x1765cc..0x1766c0` consulta el objeto en `+0xc0`, construye `ObjMsg(0x3900, 0x0002)` con parámetros `0x1000..0x1004`, y lo envía a la interfaz en `this+0x8`. | NO_VERIFICADO: no hay DMM raster/SDS, `0x111`, `0x15ebfc`, `EncodeStill` ni PbCap. INFERENCIA: es una operación distinta de la SDF PbCap por el command-id `0x0002` frente a `0x3000`. | NO_VERIFICADO: enviar una orden a una interfaz no demuestra ni evita cortinas. |
| 4 | VERIFICADO: mismo filtro de entrada y la misma rama de error que 2; no hay orden `0x3900/0x0002`. | DESCARTADO para este recorrido. | NO_VERIFICADO. |
| 5 | VERIFICADO: mismo filtro de entrada y la misma rama de error que 2; no hay orden `0x3900/0x0002`. | DESCARTADO para este recorrido. | NO_VERIFICADO. |

`0x176994` sólo propaga el resultado recibido por el pin/objeto de salida 7 y
añade parámetros de estado; no asigna DMM ni demuestra píxeles, JPEG o
finalización de captura.

## Límites y descartes

- **DESCARTADO**: denominar 2–5 por nombres de enum no recuperados. Sólo los
  valores numéricos y sus ramas se verificaron.
- **DESCARTADO**: equiparar `0x3900/0x0002` con SDF PbCap. La ruta PbCap
  conocida es `0x15fa74`, con `0x3900/0x3000`, DMM propios y posterior
  `0x15ebfc`.
- **NO_VERIFICADO**: que Camera sea el holder/proveedor dinámico de modo o que
  `Camera.out0` ejecute esta secuencia; la topología estática no prueba ello.
- **NO_VERIFICADO**: que el modo 3 produzca un buffer apto para EncodeStill,
  PbCap, JPEG o DCF; tampoco se verifican formato, geometría ni ownership.
- **NO_VERIFICADO**: que cualquiera de estos modos suprima, habilite o evite
  la secuencia mecánica. No hay una arista desde este dispatcher a los
  controladores/estados físicos de obturador.

SilentShutter no se declara funcional.

## Siguiente tarea propuesta

**S19-12 (h): condiciones para evitar captura mecánica.** Los modos de Effect
no contienen una decisión física de obturador. Seguir las condiciones que
seleccionan/omiten la secuencia de captura mecánica desde la ruta Camera/S2 es
la continuación más directa y útil; debe mantenerse separada de la mera
compatibilidad de buffers.
