# Darwin: entradas verificadas para investigar el obturador

Continuación vigente: [máquina de estados, notificaciones y control](darwin-state-machine.md).
Las cuatro entradas TBB ya fueron recuperadas de los bytes originales.
La advertencia de Ghidra conservada más abajo es histórica; no sigue siendo
un bloqueo para reconstruir sus destinos. El bit `0x80` del bloque de callback
retiene la etapa del planificador, no certifica finalización de movimiento.

Se incorporan las dos imágenes auxiliares oficiales `0640_darwin/darwin_core.bin`.
Todavía **no se ha demostrado que Darwin sea el receptor del paquete CAIF**
descrito en [silent-caif-transport.md](silent-caif-transport.md).

| Imagen | Tamaño | SHA-256 |
|---|---:|---|
| A6000 3.21 | 157 276 | `5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4` |
| A6300 2.01 | 181 040 | `6249d4b7f70d31c50048c85ca39e61c1872b547a26fd4b4ad0343ca9811433ac` |

Las tablas iniciales son compatibles con vectores Cortex-M: pila en SRAM
`2000....`, reset Thumb `45c9` / `45f9`. Se analizaron con lenguaje
`ARM:LE:32:Cortex`, sin ejecutar el firmware. Los proyectos
iniciales con ROM en cero son una **hipótesis descartada**. La ROM correcta
se carga en **`4200`**; los proyectos vigentes son
`analysis/ghidra/a6000-darwin-rom.gpr` y `a6300-darwin-rom.gpr`.

La corrección no se basa solamente en que aparezcan instrucciones válidas:
el vector reset A6300 `45f9` corresponde a archivo `3f8`; el vector siguiente
`4601` coincide con el manejador de excepción en archivo `400`, seguido de
los demás manejadores en los desplazamientos indicados por los vectores.
Además, la tabla absoluta `2b534`, referida desde la entrada de arranque,
contiene callbacks válidos en archivo `27334`: `768d,7839,78ab,78c5`.
Interpretarla con base cero producía enteros que no eran callbacks.
Los exports anteriores sin campo `rom_base:4200` se conservan como auditoría
del intento; **no usarlos para resolver punteros absolutos o llamadas indirectas**.

## Lectura ShutPI

| Función | A6000 | A6300 |
|---|---|---|
| Cadena `[ERR] ShutPIAdValue` | `1b5c0` | `1d518` |
| Referencia ADR16 a cadena | `1b422` | `1d37e` |
| Lector identificado | `1b400` | `1d35c` |
| Consulta de variante de hardware | `5ec4(2)` | `62f8(2)` |

Direcciones de esta tabla con base corregida; restar `4200` para offsets de archivo.

Si la consulta de variante devuelve cero, ambos lectores aceptan el canal 8,
leen un valor de 16 bits y lo desplazan dos bits a la derecha. Otros canales
devuelven cero y pueden emitir el error indicado. La variante alternativa
utiliza la ruta ADC genérica del firmware. El nombre y el acceso ADC aportan
una entrada para estudiar la posición del mecanismo; **no son una orden de
motor ni evidencia de una cortina trasera electrónica**.

En el primer proyecto A6300 el autoanálisis no había definido el lector; se verificaron prólogo,
dos retornos y salto a ADC genérico con LLVM. `SeedDarwinAdc.java` define
únicamente los límites del lector. En los proyectos correctos, Ghidra había
incluido el lector en un wrapper que fija canal 8 y salta a él:
A6000 `2109c → 1b400`, A6300 `24da2 → 1d35c`. Se separaron solamente
esas definiciones inferidas y se reconstruyeron los wrappers de seis bytes,
sin borrar instrucciones ni modificar los originales. Los exports vigentes
son `a6000-darwin-rom-adc-separated.json` y
`a6300-darwin-rom-adc-separated.json`, ambos con campo `rom_base:4200`.
El export inicial `a6300-darwin-shutter-adc-verified.json` usa offsets base cero;
debe reemplazarse por la consulta en el proyecto con ROM `4200`.
El primer intento `...-corrected.json` no creó función: una guarda rechazó
una suposición errónea de solapamiento con `19066`, sin modificarla.
La función A6000 ya estaba definida: `a6000-darwin-shutter-adc-inventory.json`.

## Monitor de posición y configuración del controlador

Se siguió el lector hasta las comparaciones que marcan tres fases. En A6300,
`23752` lee fase `+153` de la estructura `200034e4`; compara ADC canal 8
con umbrales de configuración `+34/+36` y marca bits `10/20/40` en `+154`.
En A6000 se observa el mismo patrón con estructura `200036d8` y bits `2/4/8`.
La consulta A6000 resuelve a una función contenedora `ce88` por una cola
compartida; las instrucciones de comparación están en `2065c..206e0`.
No confundir la dirección de esa función contenedora con el inicio local
del monitor. Export: `*-darwin-shutter-position-consumers.json`.

Los inicializadores de fase son `20734` en A6000 y `23af4` en A6300.
Los consumidores de las fases están en `2089c` / `23e16` y usan saltos TBB
de cuatro entradas que todavía no recuperó bien el decompilador. Por ello
no se atribuye una semántica de cortina a cada fase a partir del pseudocódigo
incompleto. Exports: `*-darwin-shutter-phase-writers-seeded.json`.

A6300 acepta además un valor 4 en el selector `24700`; A6000 `20c74`
normaliza a cero cualquier valor distinto de 1, 2 o 3. **No es el enum
Silent 2 ni se ha demostrado que 4 signifique Silent.** Ambos selectores
leen los tres bits inferiores de un byte de configuración: `20000000+50`,
si su indicador de presencia en `200002c0` lo permite. El acceso se hace
por `1cf34(0)` en A6300 y `1b080(0)` en A6000. La inicialización contiene
una ruta de actualización de la copia de backup en SRAM mediante comando
`12`; esto es distinto de haber seguido el byte Silent del paquete CAIF.
Evidencia: `*-darwin-shutter-driver-selectors.json` y
`*-darwin-shutter-config-source.json`.

## Comunicaciones pendientes de asociar

Se localizaron callbacks A6300 con diagnósticos `mss-sync` y `mss-async`,
offsets de archivo `df54` / `e41c`. Un manejador de ajuste está en archivo `245d0`.
`a6300-darwin-serial-handlers.json` conserva las consultas. El helper
offset de archivo `a920`, usado por el ajuste, también prepara registros de eventos; su
presencia no basta para llamarlo despachador del protocolo CAIF.
Las consultas de referencias registradas a las direcciones Thumb impares
están vacías; no se interpretan como ausencia de callbacks.

`SeedDarwinVectors.java` verifica ambos hashes y siembra vectores 1..63.
El primer intento A6300 encontró conflicto al reescribir TMode ya analizado;
se corrigió conservando el modo Thumb predeterminado del lenguaje Cortex.
La ejecución posterior y la importación A6000 terminaron correctamente.
`QueryDarwin.java` exige base `4200` y exporta hash y entradas canónicas;
permite candidatos explícitos con `candidate:` que deben verificarse con
instrucciones. Las vistas ELF derivadas conservan los bytes de las ROM;
las primeras con base cero representan offsets de archivo, no direcciones de ROM.

**ACEPTO**: existen entradas concretas para continuar el análisis del
obturador en ambos firmwares auxiliares.
**RECHAZO**: atribuirles la recepción CAIF o una función Silent aún no seguida.
**VEREDICTO: CAMBIOS**. Identificar el protocolo de entrada y los actuadores.
