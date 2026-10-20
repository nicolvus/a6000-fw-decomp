# S58-D/E — Diferencias Silent efectivas y petición de ganancia

20-10-2026. Fuente: ejecución original A7S 3.20 con [cobertura y stubs](s58-imx235-full-emulation.md). Datos completos, por dispositivo, etapa y orden: `analysis/s58/out/a7s_effective_diff.json` y `a7s_scenarios.json`.

## Corrección de la comparación S57

**CORRECCIÓN (VERIFICADO) de [s57-imx235-silent-register-diff.md](s57-imx235-silent-register-diff.md):** paso real 0x14 B, 69 filas y selección indirecta de 15 columnas para 34 modos. SetMode emulado reproduce las 69 filas para los seis modos. Los pares 0x000C 0x20→0x10 y 0x000A 0x02→0x01 de S57 procedían de interpretar 35 filas de 40 B con 34 columnas directas.

| Comparación | Columna SetMode | Último valor transmitido, bus completo |
|---|---:|---:|
| 0x4c→0x4e | 14 registros | 14 |
| 0x4d→0x4f | 11 | 11 |
| 0x4e→0x4f | 4 | 4 |
| 0x4c→0x4d | 0 | 0 para las entradas ensayadas |
| 0x0b→0x4e | 45 | **43** |
| 0x0b→0x35 | 4 | 4 |

La diferencia 45→43 muestra por qué la columna estática no sustituye al estado transmitido. Se comparan entradas numéricas iguales, **sin afirmar tiempos de integración físicamente equivalentes**.

## Valores transmitidos 0x4c→0x4e

Todos al dispositivo 0x81. En los escenarios estudiados, estas diferencias ya están en SetMode y sobreviven a SetExposure/SetRead/Execute:

| Dirección | 0x4c | 0x4e |
|---|---|---|
| 0x01 | 01 | 00 |
| 0x08 | 92 | 00 |
| 0x09 | 02 | 00 |
| 0x0a | 16 | 00 |
| 0x0b | 03 | 00 |
| 0x0c | 0a | 64 |
| 0x11 | 00 | 03 |
| 0x1f | 08 | 0c |
| 0x28 | 29 | 01 |
| 0x3c | 1b | 28 |
| 0x50 | 78 | 1c |
| 0x51 | 03 | 02 |
| 0x55 | e8 | d0 |
| 0x9a | 85 | aa |

Para 0x4d→0x4f desaparecen las diferencias en 0x01/0x09/0x0b y 0x0a pasa 0x16→0xa8. Silent 0x4e→0x4f cambia `{0x01:00→01,0x09:00→02,0x0a:00→a8,0x0b:00→03}`. Es el mismo conjunto y valores que foto 0x0b→0x35; su relación con submodo de lectura es **INFERENCIA**, su función eléctrica no se deduce del número de registro.

## Registros 0x0c y 0x0a

0x0c=0x64 en modos 0x0b/0x37/0x35/0x38/0x4e/0x4f/0x50/0x51; 0x0a en 0x32/0x34/0x33/0x4c/0x4d. Otros valores existentes: 02,0c,14,18. No es exclusivo de Silent. No se puede descartar que participe en una combinación necesaria para Silent; sí queda refutada la premisa de un bit Silent exclusivo 0x20→0x10.

0x0a=0xa8 en 0x35/0x38/0x4f/0x51; 0 en 0x0b/0x37/0x01/0x03/0x0a/0x36/0x12/0x44/0x4e/0x50/0x08; 0x16 en 0x32/0x34/0x33/0x4c/0x4d. Valores restantes: 24,5e,72,78,b0,b4. La matriz JSON incluye los 34 modos para ambos registros y los demás campos.

SetExposure modifica 0x02–0x07 y control; SetRead no cambia 0x0a/0x0c en los escenarios guardados. La coocurrencia con resolución, frecuencia y configuración SIF **no se recuperó**: falta el vínculo entre descriptores de modo, inicialización real y receptor. No se asignan unidades ni significado óptico por correlación de columnas.

## Diferencias fuera de la matriz

Los cambios incrementales de SetExposure/SetRead en 0x4c y 0x4e son iguales para las entradas ensayadas; no aparece una orden adicional exclusiva Silent. H58-6 se descarta **solo en esta cobertura**. Execute emite mensajes 0x1000/0x1001 mediante `0x438f6864` en foto 0x0b/0x35 y no en 0x4c/0x4d/0x4e/0x4f con estado inicial cero. El receptor y su efecto no se conocen; la diferencia puede depender del estado no inicializado.

No aparecen destinos P2S adicionales por seleccionar Silent: los 100 destinos y su orden son iguales en los doce escenarios. La escritura 0x83:0x17=0x4a también existe en foto, no constituye una función Silent nueva.

## Umbral 0x1000 y consumo

**CORRECCIÓN (VERIFICADO) de [S57-B](s57-ssb-pulse-analysis.md):** el productor `0x436f4b10` está dentro de **SetRead**. Compara el código AGC con 0x1000; cuando AGC>0x1000, fija O+0x3d7 y transforma el código; en el otro caso borra la petición. No se ha convertido este código a duración de exposición ni probado que el umbral corresponda a un fotograma.

Consumidor `0x436f459c`: lee O+0x3d7, pone el bit 4 de **0x81:0x5f** y borra la petición; la siguiente llamada sin petición borra ese bit. Test con código original en los cinco modos obligatorios: mismo comportamiento foto/Silent. El escenario Execute ensayado no demuestra haber consumido esa petición; el test llama explícitamente al helper. No se confunde esa llamada aislada con orden físico de transmisión.

SetExposure, por separado, modifica el bit 3 de 0x00. **Petición de ganancia, bit 3 y fin electrónico no son operaciones intercambiables.** La semántica eléctrica de 0x5f sigue desconocida; ganancia es interpretación respaldada por el contexto AGC, no por un datasheet.

## Equivalencia IMX210 y siguiente prueba

Hay un paralelo estructural verificable: tripleta de tiempos, ShutMode, sombra y Execute/P2S. No se demuestra equivalencia eléctrica de registros ni de valores entre IMX235 e IMX210. Para comprobarla: recuperar inicialización real y descriptores de modo, seguir el llamador del consumidor 0x436f459c y el receptor de mensajes Execute. Ninguno de estos resultados justifica copiar registros o parchear.
