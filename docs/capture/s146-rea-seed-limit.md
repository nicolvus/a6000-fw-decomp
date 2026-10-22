# S146 — REA no puede sembrar procedimientos en el hueco actual

**VERIFICADO como límite de herramienta:** el selector `file-offset:` de
`procedure_pseudo_code` resuelve correctamente offset→VA, pero exige que la
dirección ya pertenezca a un procedimiento observado. No crea ni siembra una
entrada. `procedure_info`, `procedure_assembly` y `analyze_function` rechazan
ese selector. Por tanto, el siguiente paso de S145 de «sembrar» las entradas no
está disponible en la superficie REA actual; no debe repetirse como si fuera
una operación soportada.

## Evidencia y corrección de coordenadas

La dirección candidata `0x43843a44` corresponde al offset `0x302a44`; REA
resuelve ese mapeo y falla porque no hay procedimiento que empiece o contenga
la dirección (Evidence `ev_ea22a2182a4e3d23312394b402b358789ae6a158f2c91f4dd012453fd50de7ed`).
El mensaje observado fue:

> File offset 0x302a44 maps to analysis address 0x43843a44, but no procedure starts at or contains that address in the current Ghidra analysis.

El caller candidato `0x437b617e` tiene offset correcto `0x27517e`. La consulta
del offset `0x27617e` fue un error de coordenada y mapea a `0x437b717e`, que
cae dentro de un procedimiento no relacionado `FUN_4380a4c4` (cuerpo no
contiguo; Evidence `ev_b0d6874334a9baa4823bb7b150b77290a5434ef146c37fcd58858065b1babd63`).
Su pseudocódigo no es evidencia sobre el caller candidato
(`ev_b0f83d8206f65a014ebfad1dd74c5428aa1aa66ff8fe6cb7067cfa007f94e20b`).
Las conversiones se recalculan contra el blob con el script de este hito.

REA no ofrece una operación de crear función/entry en la sesión Ghidra
disponible. `open_binary.entry_point` solo define dónde se mapea el offset 0,
así que moverlo para alcanzar una de estas entradas rompería el mapeo de
direcciones de todo el firmware. No se cambió la sesión ni se anotó el target.

## Consecuencia técnica

Esto bloquea solo la **decompilación REA** del bloque sin función. No prueba
ausencia, ejecución o propósito físico; las instrucciones positivas de S145
siguen vigentes. La continuación viable es recuperar bytes por REA y recorrer
el Thumb de forma estática/reproducible, manteniendo explícita la limitación
de CFG y no abriendo una línea nueva de Ghidra. Si esa reconstrucción no puede
cerrar los gates, registrar el límite y escoger otro eslabón independiente.

```sh
python3 analysis/s146_rea_seed_capability/verify_offsets.py
python3 -m unittest tests.test_s146_rea_seed_capability -v
```
