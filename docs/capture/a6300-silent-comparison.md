# Comparación estática A6300 2.01 / A6000 3.21

Investigación en curso, 16-10-2026. Referencia seleccionada por instrucción
del usuario: A6300, sin utilizar A7S. Origen y huellas en
`analysis/a6300-source.json`. No hay modificación ni prueba sobre cámara.

## Estado y selección de lectura

En A6300, el receptor `437ef610` del comando `40e3` guarda el estado en
`44018c00+264`. El conversor `438c41c8` transforma 0/1 en tipo 0/2.
`438a5d90` guarda ese tipo en `captura+804`, con inhibiciones por otros
campos de captura y una anulación diagnóstica. El tipo 2 también activa
`captura+7a4`.

`438be6f0` llama a `438be684(modo, captura+724, captura+804)` y almacena
el resultado en `captura+4e0`. La función tiene estas ramas verificadas:

| Condición | Resultado lógico |
|---|---|
| Primer argumento = 5 | `0x0c`, antes de evaluar Silent |
| Primer argumento = `0x1b` | `0x1b`, antes de evaluar Silent |
| Tipo Silent = 2, segundo argumento = 1 | `0x4f` |
| Tipo Silent = 2, segundo argumento = 0 | `0x4e` |
| Tipo normal, segundo argumento = 0/1/2 | `0x0b` / `0x35` / `0x17` |

Otros valores del segundo argumento producen diagnóstico y un valor por
defecto; no se les asigna una configuración fotográfica sin evidencia.
El callback Silent de la primera tabla (`43bda462`) construye el argumento
con `43803c78(captura+4e0, ...)` y llama a `43717dbc` → método virtual
`+20`, SetMode. La llamada está en el tramo posterior al switch, alcanzado
por el estado 2; otros estados retornan antes. Se ha unido la selección al
controlador estáticamente, sin afirmar ejecución ni éxito físico.

En IMX284, SetMode `4371949c` busca el modo lógico en una tabla de 21
palabras en `441afd10`. `0x0b` tiene índice 0 y `0x4e` índice 3.
`0x4f` no está en esta tabla concreta; no asumir que lo acepta esta variante.
La búsqueda `43b8f3cc` devuelve `0xff` si no encuentra el modo.

SetMode aplica el índice mediante el método virtual `+c0`, `43718c2c`.
Este recorre registros de 28 bytes en `441aecd0`: puntero de destino seguido
de valores por índice. Hay 124 registros antes del puntero nulo; 51 valores
cambian entre índices 0 y 3. Son escrituras a estructuras de configuración,
todavía no prueba de transferencia física. La tabla opcional `43ffbdf8`
tiene puntero inicial nulo. No interpretar el significado eléctrico de los
registros a partir de sus números.

## No confundir los dos números 2

**RECHAZO**: «tipo Silent = 2 implica ExpRsvParam.selector = 2».
SetExposure del IMX284 (`4371917c`) admite 0, 1, 3 y 4; rechaza 2.
El IMX210 de A6000 sí tiene una rama de exposición 2, pero eso no establece
su semántica. No hay base para activarla como parche SilentShutter.

La política A6300 `4391d150` contiene una rama adicional concreta frente
a la política EFCS de A6000: con los bits `0xe0` de configuración `+50c`
apagados, si `configuración+430 == 2`, deja la clase en **0**. Sin Silent,
evalúa EFCS en `+45c` y selecciona 1/3, con más condiciones. Los flags
previos pueden producir 1/5; el diagnóstico `+7e` y la anulación `+36/+37`
pueden reemplazar el resultado. Silent también pone a cero otra salida
`44097928`, cuyo significado físico aún no se ha establecido.

Transporte identificado: `4391d440` devuelve la clase de `44097924`;
`43918ed0` la guarda en `44096d68`; `4391a6f4` la escribe en el banco de
fotograma `+f5`. `4391bd40` copia 16 bytes desde banco `+ec` a
`captura+674` (rama alternativa `+17c`, selector `+185`). El selector normal
queda en `captura+67d`. `438b5364` lo entrega a SetExposure `43717de4`
si el contador `+4f98` es cero; para clases de dispositivo 2/3 lo sustituye
antes por cero. Se debe conservar esta distinción entre selección y entrega.

El wrapper real empieza en `43717de4`; `43717df8` era una instrucción
interior consultada por error, corregida mediante la reparación puntual.
Los exports anteriores con entrada `43717df8` no prueban límites ni callers.

`438bfcd8` entrega `captura+20` como segundo argumento de `4391a6f4`:
el campo `+7e4` de ese argumento es exactamente `captura+804`.
`4391a6f4` lo copia a la configuración `+430` evaluada por `4391d150`.
Esto cierra el enlace de Silent con la selección de clase 0. El preámbulo
PIC empieza seis bytes antes del push; el primer export `438bfcde` omitía
esos bytes y sus argumentos adicionales eran un artefacto del análisis.
La consulta corregida tiene una sola entrada `438bfcd8(int captura)`.

El registro de control IMX284 está en `441ed9bc` (dirección almacenada 1,
valor inicial `0x20`); la tabla de modos pone su byte de valor a `0x04`
tanto para `0x0b` como `0x4e`. SetExposure clase 0 aplica máscara `0xd4`
→ `0x40`, igual en ambos casos. Por tanto, **ese registro por sí solo no
identifica el modo Silent**: hacen falta las diferencias de lectura,
temporización y secuencia ya identificadas. No atribuir semántica física
idéntica a direcciones de registros de sensores distintos.

Exports: `a6300-silent-exposure-selector.json`,
`a6300-exposure-class-producer.json`, `a6300-exposure-class-writers.json`,
`a6300-exposure-packet-copy.json`, `a6300-exposure-source.json` y
`a6300-silent-exposure-callers.json`.
Se añade `a6300-exposure-policy-capture-link-corrected.json`.

El programador de temporización `4380447c` llama a `43804c50`, que siempre
devuelve 1. La rama heredada `if (resultado == 0)` no es la ruta demostrada.
El helper activo entrega a `43712a38` el indicador `(selector == 3)` y
a `43712a54` 41 valores temporales ajustados. No se ha asignado significado
eléctrico de cortina trasera a ese indicador.
La ruta del indicador continúa `43712a38 → 43b8c8aa → 43b8c62e`, que
escribe 32 bits en `base+0xa1b80`. La base se obtiene del campo `+4` del
objeto `43ffa16c` (GOT `441fe5d4`), inicialmente cero en el archivo.
La llamada en `43710be2`, comprobada con LLVM, entrega ese objeto y argumento
0 a `43714910`; este escribe `0xfc000000` en `objeto+4` mediante `43b8b1e6`.
El destino lógico queda en **`0xfc0a1b80`**, igual al destino reconstruido
independientemente para A6000. Otra instancia usa `0xfc001000`.
La base no se ha supuesto por equivalencia entre cámaras. El export del
inicializador `437109c8` tiene 72 avisos por llamadas no delimitadas; no se
utiliza como flujo completo. La prueba de esta llamada usa sus instrucciones
y literales, junto al constructor y setter delimitados por separado.

En A6300 Silent con clase 0 este indicador vale 0; también vale 0 con clase
1. **El indicador no basta para distinguir EFCS de Silent**. No hay prueba
eléctrica de que sea un selector de cortina trasera.

Las funciones `437e0508`/`437e0628` identifican explícitamente CaifCom
SndEvent/RcvEvent. Sus comandos y esperas no se deben etiquetar como acciones
mecánicas sin seguir sus receptores. La presencia de eventos no demuestra
que una cortina haya completado su movimiento ni que un fotograma sea válido.

## Secuencias de captura

Con `captura+79e == 0` y `captura+804 == 2`, los selectores
`438af40c` y `438afa10` eligen filas 9 y 15 respectivamente, salvo sus
ramas previas de excepción. Las tablas están en `4407ee78` y `4407fa8c`;
sus bytes originales son cero y se inicializan en ejecución.

El inicializador `438afc0c` llama a `43bbaf2e` → `438a7b58`, que coloca
el callback en `registro+8` y pone `registro+4` a cero. Resueltos:

| Tabla / fila | Ranura GOT del callback | Puntero Thumb |
|---|---|---|
| Primera / 8 | `441ff420` | `43bda3b3` |
| Primera / 9, Silent | `44200800` | `43bda463` |
| Segunda / 14 | `441fd8e8` | `43bdc7ed` |
| Segunda / 15, Silent | `44201af4` | `43bdc8e5` |

Los nombres y las acciones físicas de estos callbacks siguen pendientes.

En A6000, la fila 9 de la tabla equivalente (`43eddd08`) apunta a `43b1b0c8`.
El selector `437ea8cc` la elige con `+73a=0`, `+4b84!=0` y `+4b80=1`.
La selección equivalente de A6300 usa la fila 10; la fila 9 Silent se
intercala antes de evaluar esa política. Copiar el índice 9 entre versiones
seleccionaría rutas distintas.

La etapa normal con etiqueta `0x5c` se identifica en A6000 como
`Stage_NotifyLongExpNRCapturing`, y el código equivalente aparece en A6300
normal. No se ha interpretado como acción de cortina. Silent A6300 omite
esa etapa y usa un estado 9 que puede repetir `438b5364`/SetExposure según
`captura+678` y el contador `+4f98`. La equivalencia completa con todas las
secuencias A6000 se está auditando.

## Diferencia concreta en el firmware A6000

La función equivalente `437f7f98` (`GetImagerDriveMode`) de A6000 solo
selecciona `0x0b`, `0x35` y `0x17` por el segundo argumento, con excepciones
5 → `0x0c` y `0x1b` → `0x1b`. No recibe ni evalúa un tercer argumento
Silent. Su llamador `437f7ff0` escribe `captura+4d0` y permite una anulación
diagnóstica; esa anulación no añade soporte de sensor.

El SetMode IMX210 `436d6b50` rechaza valores mayores de `0x47` y busca
únicamente 13 modos en `43fea070`:
`0b,01,05,10,07,12,03,0a,0f,18,1a,19,2f`.
En particular, el modo silencioso A6300 `0x4e` se rechaza antes de buscarlo.
El escritor de tablas A6000 `436d6570` usa registros de 20 bytes, frente a
28 bytes en A6300. **No se pueden trasladar el número ni los bytes de la
tabla de IMX284 al IMX210 como si fueran una opción oculta compatible.**
Esto demuestra una diferencia de implementación, no una imposibilidad del
silicio IMX210. Sigue abierta una implementación distinta usando capacidades
del IMX210 que todavía deben demostrarse.

Un dato que impide inferir imposibilidad por comparación superficial: la primera
fila de la tabla IMX210 pone `0x0c` para modo `0x0b`; la primera fila IMX284
pone `0x04` para `0x0b` y `0x0c` para Silent `0x4e`. Sus destinos tienen
un campo previo de dirección cero. La coincidencia de valor **no prueba que
los bits signifiquen lo mismo**; tampoco permite declarar que IMX210 carezca
de la capacidad por no tener el número lógico `0x4e`. Se necesitan la semántica
de registros del IMX210 o medidas sobre hardware para decidir esa hipótesis.

Exports adicionales: `a6300-silent-sequence-callbacks.json`,
`a6300-silent-mode-apply.json`, `a6000-vs-a6300-drive-mode.json` y
`a6000-drive-mode-caller.json`.

## Reproducibilidad y corrección de metadatos

También se siguió una [selección Silent en el paquete CAIF](silent-caif-transport.md):
`4391a6f4` activa bit `20` en byte `12`, que el evento 1 entrega a
`436f9714`; se copia un cuerpo de 31 bytes y se sigue hasta el descriptor
del transporte. Falta comprobar su interpretación en el receptor físico.

La ruta `43919c04 → 43ba72ba → 4380fc78`, omitida por Silent, quedó
identificada como **registro KikiLog**, con receptor `kikilog.ko` y contador
`record_acm`. No es prueba de accionamiento de cortina. Véase
[la reconstrucción del receptor](silent-kikilog.md).

Comprobación adicional de instrucciones: `EmulateImagerMode.java` ejecutó
**7 casos por firmware, 14 correctos**, en Ghidra con los proyectos abiertos
en modo de lectura. Con entrada modo=1 y recorte 0/1, A6300 devuelve `4e/4f`
para tipo Silent 2; A6000 devuelve `0b/35` con el mismo valor en R2.
Los casos normales, recorte 2 y excepciones modo 5/1b también coinciden con
las ramas reconstruidas. Resultados: `a6300-mode-emulation-verified.json` y
`a6000-mode-emulation-verified.json`.

El arnés limita cada caso a 512 instrucciones, selecciona Thumb conservando
el resto del contexto en cada paso y verifica R0 al llegar al epílogo,
además del retorno guardado en pila. Los primeros intentos revelaron que
el contexto se perdía en los saltos y que el emulador rechazaba el cambio de
ISA al retornar. Se conservan como intentos fallidos; la comprobación válida
se detiene antes del POP-to-PC. No es emulación del sensor ni validación
de una fotografía electrónica.

Exportaciones `analysis/ghidra/a6300-silent-mode-selector.json`,
`a6300-imx284-mode-map.json`, `a6300-imx284-mode-program.json` y
`a6300-capture-sequence-init-repaired.json`. Todos identifican la huella
del original; las regiones constantes son hipótesis de análisis.

El primer análisis del inicializador fusionó funciones y produjo 375 avisos
PIC; no se usa como evidencia de flujo. `RepairA6300Sequence.java` valida
la huella y elimina únicamente la definición errónea de esa función,
conservando instrucciones y bytes. Tras sembrar el helper y el thunk
verificados independientemente con LLVM, la consulta repetida recuperó
las tres entradas distintas y cero avisos PIC. Se conservan ambos exports.

**ACEPTO**: A6300 tiene selección Silent diferenciada de modo y secuencia.
**RECHAZO**: equivalencia numérica directa con el selector 2 de A6000.
**VEREDICTO: CAMBIOS**. Falta conectar la selección con la programación
completa, reconstruir la secuencia mecánica y demostrar una ruta equivalente
viable en IMX210. No hay parche funcional validado.
