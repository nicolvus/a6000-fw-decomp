# Proyecto LIRO persistente

S29: `QueryLibraryExisting.java salida.json VA...` consulta bibliotecas del
proyecto `a6000-libs` con `-readOnly`. Usa la función contenedora y conserva
su entrada en el export; no cambia TMode de instrucciones existentes.
Evita `ContextChangeException` de DecompAt al consultar funciones conocidas.
Las VA del proyecto de bibliotecas tienen sesgo `+0x10000` frente a ELF.
Una consulta interior o una advertencia PIC no confirma un límite de función;
el cierre WriteStill de S29 usa LLVM, tablas y relocaciones para esas aristas.

Continuación 16-10: [fases y control Darwin](../../docs/capture/darwin-state-machine.md).
`*-darwin-phase-table-verified.json` se reproduce con `python3 -m src.darwin`
sobre cada ROM original; exige SHA-256 conocido y preserva las ventanas de bytes.
`darwin-phase-caif-independent-disassembly.txt` contiene el contraste LLVM.
Los exports `a6300-nfc-sio[-message]-rea.json` añaden un productor serie
independiente; no identifican el receptor remoto CAIF.

Darwin se analiza en `a6000-darwin-rom.gpr` y `a6300-darwin-rom.gpr`,
lenguaje `ARM:LE:32:Cortex`, base **`4200`** comprobada con reset,
excepciones y tabla de callbacks. Los proyectos anteriores `*-darwin.gpr`
con base cero se conservan como hipótesis descartada: no usar sus punteros
absolutos. `SeedDarwinVectors.java` verifica ambos hashes; `QueryDarwin.java`
exige base4200 y diferencia entradas registradas de candidatos explícitos.
Las vistas `*-darwin-rom-analysis-view.elf` tienen `.text` idéntica al
original, verificado byte a byte, con dirección virtual4200.
Detalles y límites: [Darwin](../../docs/capture/darwin-shutter-entrypoints.md).

`silent-liro.gpr` contiene el av-cam.bin original con base lógica 0x43541000.
`a6300-liro.gpr` contiene separadamente ILCE-6300 2.01, sin autoanálisis amplio.
`a6300-libObj.gpr` contiene su `libObj.so`, importado sin autoanálisis amplio
tras agotar REA/search_strings el plazo de 300 segundos. REA abrió y verificó
la identidad del ELF; no se obtuvo evidencia de esa consulta fallida.
`QueryA6300Library.java` verifica la huella del archivo y del ELF importado,
exporta el sesgo de carga (`0x10000`) y consulta direcciones virtuales ELF.
Las entradas `.ARM.exidx` corroboran límites, pero pueden agrupar funciones:
`960294` cubre también otra función que empieza en `96034c`. La primera
traduce comando `40e4`; la segunda, comprobada con LLVM, traduce Silent `40e3`.
El prefijo `candidate:` permite consultar una división verificada o un destino
de llamada/vtable; el export distingue ese fundamento del registro de unwind.
Origen y hashes: [a6300-source.json](../a6300-source.json). A7S excluida por
instrucción del usuario. No mezclar direcciones, estados ni conclusiones físicas.
Comparación incremental: [A6300 Silent](../../docs/capture/a6300-silent-comparison.md).
`RepairA6300Sequence.java` corrige solamente metadatos inferidos concretos,
con huella estricta: sin argumento, la fusión errónea de `438afc0c` con su
helper/thunk; con `exposure-interior`, la entrada interior `43717df8`.
El wrapper SetExposure correcto comienza en `43717de4`, verificado con LLVM.
El argumento `capture-prelude` repara otra entrada incompleta: el constructor
de configuración empieza en `438bfcd8`, seis bytes antes del push de
`438bfcde`. La consulta corregida recupera el preámbulo PIC y un solo argumento.
Las consultas anteriores se conservan como historial, no como entradas válidas.
La reparación no se vuelve a ejecutar una vez corregida: exige el estado
erróneo original y falla si no existe. No borra instrucciones ni cambia bytes.

`EmulateImagerMode.java` comprueba el selector de modo de ambos originales
mediante ejecución acotada de instrucciones. Usa `-readOnly`; solo escribe su
JSON de resultados. El modo Thumb se fija en cada paso conservando el resto
del contexto. Se detiene ante los epílogos POP-to-PC verificados con LLVM y
comprueba R0 y el retorno guardado en pila. No ejecuta la transición de ISA
del retorno, que produjo errores del emulador en los primeros intentos.
Los archivos `*-mode-emulation-verified.json` son las comprobaciones válidas;
los intentos anteriores con `passed=false` documentan fallos del arnés y no
constituyen fallos del firmware. No emula sensor, MMIO ni fotografía.
Última continuación: [EFCS hasta captura y DFE](../../docs/capture/efcs-capture-selector.md).
Se conservan también docs/capture/silent-imager-consumers.md e
docs/capture/imager-exposure-p2s.md. Hash original verificado en cada export
de funciones; más de37000 funciones registradas, sin garantía de cobertura completa.
El autoanálisis amplio alcanzó el límite de300s y se guardó como parcial.

Usar `QuerySilentLiro.java`: argumentos salida JSON y direcciones Thumb.
Prefijo `@0x...` consulta la función contenedora existente sin crear una entrada.
El export distingue `query`, `entry` y `status`; no confundir la dirección
consultada con un límite de función demostrado. `QuerySilentReferences.java`
exporta las referencias registradas con su tipo y función contenedora.

QuerySilentLiro acepta únicamente los tamaños y SHA-256 conocidos de A6000
3.21 y A6300 2.01, y exporta `firmware_profile`/`source_size`. Prueba inicial:
el script anterior rechazó A6300 por hash; después, consultas A6300 y regresión
A6000 correctas. La hipótesis readonly termina en 0x43bc0000 para A6000 y
0x43d00000 para A6300; no representa permisos físicos observados.

Los scripts se ejecutan con analyzeHeadless, `-process av-cam.bin -noanalysis`,
`-scriptPath analysis/ghidra`, reutilizando el proyecto. El comando completo
está en el informe E019. No ejecutar `ExportSilentLiro.java`: es el script
histórico que limpiaba metadatos y recreaba solo ocho candidatos iniciales.

`SeedSilentLiro.java` incorpora los handlers de las 220 filas del receptor.
`RepairImagerEntries.java` corrige dos entradas mediante la vtable IMX210.
`RemoveInteriorQueries.java` retira tres definiciones provisionales sin prueba
de entrada ABI. Sus consultas permanecen en exports históricos y se enumeran
en `rejected-queries.json`; no usarlas como funciones válidas.

QuerySilentLiro marca 0x43541000–0x43bc0000 como no escribible en el proyecto
y activa RespectReadOnly en el decompilador. Es una hipótesis de constantes
de código/pools, no un mapa de permisos observado. Los datos posteriores
siguen escribibles y el script comprueba todos los bytes antes de operar.

Validación final: `silent-final-integrity.json` (cinco consultas decompiladas)
y `silent-final-reference-coverage.json`. Los exports son resultados nativos
Ghidra separados de los bundles REA de ../rea; no tienen IDs de evidencia REA.

E020 agrega las familias `efcs-frame-*`, `efcs-exposure-*`, `efcs-capture-*`,
`efcs-dfe-*`, `shutter-source-bank-*` y `capture-exposure-*`. Las consultas
`@` sin función se conservan como fallidas; no equivalen a código inexistente.
0x437ea8cc y 0x437ebed8 se incorporaron después de verificar sus prólogos
Thumb. El segundo inicializa las tablas de secuencias con helpers; no se deben
leer las tablas BSS inicialmente vacías como valores de ejecución.
