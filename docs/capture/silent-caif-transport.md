# Señal Silent en el transporte de captura CAIF

Reconstrucción estática del firmware ILCE-6300 2.01, 16-10-2026.
Direcciones del programa LIRO con base `43541000`.
Direcciones y desplazamientos de las tablas de este documento son hexadecimales.

## Construcción y entrega del paquete

`438bfcd8(captura)` llama a `4391a6f4`, pasando como quinto argumento
`*(captura+4ed0)+40`, si ese objeto existe. La construcción está condicionada
también a la existencia del cuarto argumento obtenido del objeto `+20`.

En la rama sin anulación diagnóstica (`*pbRam441fe1e0==0`), el byte `+12`
del paquete recibe `20` si `*(captura+804)==2` y cero en caso contrario,
con un incremento adicional de uno según otro indicador. Por tanto el bit
`20` representa explícitamente la selección Silent en este paquete.
Con anulación diagnóstica activa se toma otra rama; no generalizar el valor.
El byte `+0d` también cambia: la selección Silent fuerza el componente
`cVar11` a 2 antes de empaquetarlo en los bits altos.

No confundir este paquete con la clase de exposición del controlador:
Silent normal usa clase 0 y el modo de sensor `4e` descritos en
[la comparación de controladores](a6300-silent-comparison.md).

| Tramo comprobado | Función / estructura |
|---|---|
| Configuración Silent a bytes del paquete | `4391a6f4`, quinto argumento |
| Paquete alojado en objeto de captura | `*(captura+4ed0)+40` |
| Evento CAIF 1 entrega ese paquete | `437e0508 → 436f9714` |
| Copia de 31 bytes a buffer estable | `44147b18`, longitud `1f` |
| Encolado de parámetros | `436fa784(10300,1f,44147b18)`, cola `1502c7` |
| Recepción, copia y despacho | `436fa630 → 436fc6c8` |
| Mensaje tipo 2 a handler dependiente de estado | tabla `441ad85c` |
| Conservación en anillo de diez registros | `436fb7d8`, base `43ff1fb0` |
| Cabecera de ocho bytes para el transporte | `436fb974`, buffer `44105548` |
| Descriptor del cuerpo | `436fb860 → 436fa9f8`, base `43ff1cb0` |
| Finalización y avance de anillo | `436fad78 → 436fa934` |

El registro OSAL contiene tipo 2, código `10300` en `+4`, longitud en `+8`
y puntero en `+0c`. `436fa784` devuelve error si la tabla de aceptación
`436fa99c` no admite la categoría/operación o falla la reserva/envío.
El wrapper superior no convierte su retorno constante en prueba de recepción.

## Diferencia comprobada en A6000

El constructor equivalente `43841070` recibe el quinto argumento desde
`437f87ac`: `*(captura+4ad8)+40`. En la rama normal del campo `+12`,
escribe **solamente 0 o 1** según otro indicador; la rama de anulación
diagnóstica también escribe 1. En esas asignaciones no añade el bit `20`
que A6300 deriva de Silent. El campo `+0d` de A6000 tampoco contiene la
condición Silent de A6300: su sobrescritura explícita a 2 depende del modo
de captura `19`. Evidencia previa reutilizada:
`efcs-algorithm-arguments.json` y `efcs-capture-sequence-switch.json`.

Esto identifica otra diferencia de construcción, además de modo y secuencia.
No demuestra por sí solo si el receptor A6000 aceptaría ese bit o qué haría.

**Diferencia de longitud verificada:** el evento 1 A6000
`437db858 → 436b8a50` copia y encola **22 bytes (`16`)** desde objeto `+40`
a `43f91e32`; la operación sigue siendo `10300`. A6300 envía **31 (`1f`)**.
El bit Silent situado en `+12` cabe en ambas longitudes, pero los nueve bytes
finales adicionales de A6300 no se transmiten por esta función A6000.
No se ha probado que el receptor acepte otra longitud ni que esos nueve bytes
sean todos necesarios para Silent. Exports:
`a6000-caif-event-dispatch.json`, `a6000-caif-parameter-payload.json`.

## Continuación del transporte

La tabla de estados tiene cinco entradas principales verificadas; no leer
los datos posteriores como estados adicionales. Para estado 2/subestado 1,
mensaje tipo 2, el handler es `436fb974`. Este copia código y longitud del
anillo a una cabecera de ocho bytes y usa la cola de dispositivo `740017`.
Para estado 2/subestado 2, los handlers `436fb860` y `436fab68` coordinan
dos indicadores antes de entregar el descriptor del cuerpo.

`436fa9f8` divide el cuerpo en bloques de hasta 128 bytes. En estado 2
coloca el puntero de origen en el primer campo del descriptor. Para el
paquete `1f` basta un descriptor: origen `44147b18`, longitud 31.
Se observan parámetros numéricos de temporización del transporte, pero
todavía no se ha identificado de forma independiente el dispositivo ni
el receptor físico que interpreta el bit Silent.

La llamada paralela `436fa350(122,...)` usa una tabla y una ruta distinta;
no debe sustituir al seguimiento del cuerpo encolado por `436fa784`.

Exportaciones en `analysis/ghidra/`: `a6300-caif-silent-payload.json`,
`a6300-caif-command-transport.json`, `a6300-caif-queue-receiver.json`,
`a6300-caif-state-dispatch.json`, `a6300-caif-payload-handlers.json`,
`a6300-caif-payload-framing.json`, `a6300-caif-header-completion.json`
y `a6300-caif-payload-descriptor.json`. Revisar entrada canónica en cada
export: algunos selectores son thunks y resuelven a otro nombre de entrada.

## Nueve bytes adicionales: productores recuperados

**VERIFICADO, 16-10-2026:** se reutilizó `a6300-exposure-class-writers.json`
(`4391a6f4`) y se contrastaron las escrituras `4391acd4..4391ad58` y la
rama `4391b092` con LLVM. Fuente LIRO A6300 SHA-256
`6a5a25728dc378c99d5b883c9743b69faa5f719ff844b4e1788e73bd5ae7be16`.
Ventanas en `darwin-phase-caif-independent-disassembly.txt`.

Sea X el objeto apuntado por la global `442017f8`:

| Byte de paquete | Productor/condición comprobada |
|---|---|
| `+16/+17` | Entero little endian de X: `+d6a` si X[`+61`]=1 y X[`+64`]=2; si no, `+66e` con X[`+5f`]=1 y X[`+63`]=2; si no, `+bf8` con X[`+5e`]=1 y X[`+62`]=2; si ninguna, cero |
| `+18/+19` | Cero en este bloque |
| `+1a` | Inicialmente `80` si una condición anterior se cumple, cero en caso contrario; OR con byte global `4415af72` si objeto de `44201b74`, campo `+178`, vale 1 |
| `+1b..+1e` | Copia `4415af73..4415af76` bajo esa última condición; este bloque no los asigna en la rama contraria |

**NO VERIFICADO:** significado físico de los campos de X, productores de
las cinco globales y valores retenidos/inicialización del paquete cuando
no se copian `+1b..+1e`. No aparecen aquí como una copia directa del enum
Silent. Esto caracteriza su construcción, sin probar que sean necesarios
para Silent ni que el receptor A6000 entienda el formato de 31 bytes.

## ABI de comunicación serie: evidencia independiente con REA

**VERIFICADO:** `nfc.ko` A6300, 14 872 bytes, SHA-256
`5c7942c9839e9bb24f05eb7480da80c08b391a82baa7ed3f2ff6dd0516142684`,
también **envía** mensajes de 64 bytes a `740017`. Su helper `.text+0`
(REA `1002c`) coloca un puntero a descriptores en `+38` y un callback
`sio_comm_cb` en `+3c`; usa `+4` como número de bloques y `+2c` como
operación. `nfc_rsrc_dev_send_data`, `.text+4d4` (REA `10500`), divide
en bloques de 128 bytes y llama al helper con operación 6; recepción
`.text+5a0` (REA `105cc`) usa 5. La variante de configuración del helper
convierte 6 en 2 y recepción en 1, compatible con el valor 2 del cuerpo CAIF.

Son coincidencias de estructura y llamadas con símbolos independientes de
los nombres inferidos en LIRO. **INFERENCIA:** CAIF utiliza el mismo ABI de
servicio serie. **NO VERIFICADO:** implementación receptora de `740017`,
tipo eléctrico del bus, canal seleccionado, dispositivo remoto y parser
`10300`. Encontrar el literal de cola en NFC no identifica NFC como destino
del paquete CAIF: en las funciones analizadas NFC es otro productor.

REA/Ghidra recuperó cuatro funciones, sin errores:
`a6300-nfc-sio-rea.json` y `a6300-nfc-sio-message-rea.json`.
Evidencias `ev_0883f51c18e11b4cbaa838a9f16d96a1ae91b41e7f3f08b914d0d320c8f9584b`
y `ev_0d92b70fc282d8fc7e0c98c9a11ab37f2c99cc66e4cb31dcef2270f00f8d9788`.
Las direcciones `.text+...` son relativas a sección ELF; no mezclarlas con
ROM Darwin ni LIRO. La consulta conservada `a6300-sio-queue-candidates.json`
no encontró funciones previamente registradas en cinco posiciones candidatas;
no las creó ni demuestra ausencia de receptor.

**ACEPTO**: el paquete de captura de A6300 transporta una selección Silent
distinta del número de modo del sensor y de la clase de exposición.
**RECHAZO**: que localizar ese bit baste para activar obturación electrónica
en A6000, o que un evento CAIF confirme una cortina física concreta.
**VEREDICTO: CAMBIOS**. Falta identificar el receptor del cuerpo y comparar
su interpretación con A6000 antes de proponer un cambio funcional.
