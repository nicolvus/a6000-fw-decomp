# E25-22 — Protocolo para validar el transporte físico de exposición

**Estado: preparado, no ejecutado.** El 28-10-2026, en este entorno, las conexiones TCP normales a `192.168.1.29:23` (Telnet) y `:8080` (RemoteShutter) devolvieron `PermissionError: [Errno 1] Operation not permitted`; no se sabe si la cámara está conectada. `ip route get` también fue bloqueado. No se solicitó ni eludió acceso adicional; no se disparó, no se leyó ni se modificó la cámara.

## Primera dependencia para observar el bus

La RAM P2S `0xfc088340…` es una ventana **MMIO**: no conocemos el mapa físico, la semántica de lectura, si una lectura tiene efectos laterales, ni si los datos sobreviven a cada transferencia. `dd /dev/mem` leyendo esa dirección virtual no está justificado. Incluso una lectura segura y consistente de esa RAM demostraría preparación, no que los bits lleguen al sensor. La primera dependencia precisa para comprobar la **entrega al sensor** es una captura pasiva y sincronizada de las señales serie entre BIONZ y sensor, con puntos de acceso, tensión, polaridad y conexión verificados. No se conocen puntos de prueba accesibles sin abrir la cámara: su apertura sigue fuera de la autorización de esta sesión.

Según texto extraído del esquema, **a confirmar visualmente en el esquema original y en el equipo**: CN0400 pin 7 `XCE` / `CIS0_XCS`, 9 `SCK`, 10 `SDO` / `CIS0_SI`, 2 `XVS` / `CIS0_VD`, 6 `XPI` / `CIS0_SHT_RST`. La denominación SDO/SI indica nombres desde extremos distintos y no demuestra dirección sin revisar el esquema. Existe `SDI` en pin 8: no asumir que sea irrelevante. No asignar tensión ni un punto de masa por el nombre. Fuente y límites: [S57-E](s57-xpi-shutter-reset.md), [S56-B](s56-cisif-dfe-controller.md). El texto del PDF no es netlist ni prueba de acceso físico.

## Experimento propuesto

1. En banco, obtener autorización específica para acceder físicamente a las redes y definir recuperación; confirmar numeración y puntos alternativos no invasivos en el esquema, tensión de alimentación, masa, impedancia/capacitancia de sondas y ancho de banda. No conectar al conector basándose solo en el texto anterior. Analizador con canales XCS/SCK/SI/SDI/VD/XPI y, si existe acceso seguro, una señal de referencia de cortina o de lectura; registrar configuración, frecuencia de muestreo y capturas crudas. El muestreo debe superar el reloj observado con margen suficiente para resolver cada flanco; no se conoce a priori su frecuencia ni modo SPI.
2. Con el dispositivo íntegro y estable, obtener referencia sin captura y varias fotos normales a 1/1000 s, 1/4 s y 4 s, sin modificar ajustes distintos del tiempo ni ejecutar parches. Para cada una guardar estado/tiempo, configuración de cortina y, si se tiene acceso de lectura permitido, muestras con hora de `cap+0x64c..655`, `cap+0x504` y `cap+0x4b9c`. Identificar el objeto `cap` en cada disparo; no reutilizar una dirección física histórica sin verificarla.
3. Capturar señales antes, durante y después del disparo, incluyendo todo el lote y el período largo. Determinar polaridad, flanco y agrupación a partir de la traza; comparar campos de dirección/datos con las sombras y el plan. **`81 | len | 81` es formato del buffer P2S, no se ha demostrado que aparezca tal cual en el cable.** No aplicar `frames()` directamente a bits de bus sin identificar la conversión hardware. Comprobar direcciones 3–8 y el doble envío de ID1 si aparecen, incluyendo orden y valores efectivos. Una lectura de sombras es una instantánea no atómica, no una traza ni un envío probado.
4. Comparar secuencias de XPI, VD y línea de referencia entre tiempos y modos de cortina disponibles sin alterar ShutMode mediante RAM. Conservar RAW y tiempos de captura para relacionar el evento de lectura. Comparar ShutMode 0 y 3 únicamente si se **observan de forma natural** en un modo identificado; no forzar ni atribuir semántica al selector por correlación sola. Para más de un cuadro, medir la secuencia de VD, parámetros efectivos y fin de lectura en una exposición normal larga; una fotografía correcta con cortina no prueba integración electrónica continua.

## Lecturas de software complementarias

Los seis registros sombra son objetos `{u16 id, u8 valor, u8 ...}`. Para esta imagen, el mapeo obtenido de GOT y tabla es:

| ID | Virtual objeto | Física candidata del objeto | Byte de dato |
|---:|---:|---:|---:|
| 3 | `0x4401c7e0` | `0x8401c7e0` | `+2` |
| 4 | `0x4401c678` | `0x8401c678` | `+2` |
| 5 | `0x4401c744` | `0x8401c744` | `+2` |
| 6 | `0x4401c684` | `0x8401c684` | `+2` |
| 7 | `0x4401c698` | `0x8401c698` | `+2` |
| 8 | `0x4401c764` | `0x8401c764` | `+2` |

La conversión `física = virtual + 0x40000000` procede de la ruta RAM usada en E25-19, no es prueba de validez de estas seis páginas en ejecución. Antes de leer, comprobar versión/hash, punteros GOT y encabezados ID de cada objeto en cámara; detenerse ante discrepancias. Usar exclusivamente el lector de RAM normal `scripts/e25_19_readonly.py`, no leer MMIO ni escribir. `cap+0x504==1` puede anular temporalmente svd antes de SetExposure y luego restaurarlo: lecturas antes/después no garantizan observar el valor aplicado. Repetir muestras y registrar latencia, pero no interpretar ausencia como evidencia negativa.

## Criterios de resultado

- **Transporte confirmado:** al menos una transacción identificada en el bus, con direcciones y bytes 3–8 consistentes con una muestra temporalmente compatible y sin errores de decodificación; guardar trama cruda y alineación. Diferencias entre foto y sombra exigen comprobar concurrencia, mapeo, velocidad y modo antes de concluir pérdida.
- **Inicio/fin:** solo se consideran localizados con correlación temporal reproducible y evidencia independiente de su función; cambios en XPI, ID1 o VD son candidatos, no prueba causal.
- **Lectura RAW:** identificar una señal de salida/recepción o marcador trazado hasta datos RAW; VD o duración del archivo por sí solos no la localizan.
- **Multicuadro:** contar VD y correlacionar datos y exposición efectiva sin asumir integración continua. El plan `svd` o una foto mecánica larga no bastan.

Sin el analizador y acceso físico verificado no se puede comprobar llegada al sensor. Telnet/RemoteShutter por sí solos permiten como máximo estudiar las sombras; el acceso fue bloqueado en esta sesión.
