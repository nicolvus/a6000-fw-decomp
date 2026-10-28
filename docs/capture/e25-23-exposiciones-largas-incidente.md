# E25-23 — Exposiciones largas e interrupción (28-10-2026)

**Estado: interrumpida.** Tras solicitar 30 s, RemoteShutter informó `speed=65535.0` y permaneció en `shooting` más de 90 s sin callback; el usuario informó que la cámara se bloqueó y la reinició. No se conoce la causa del bloqueo ni se ha demostrado qué significa 65535. **No repetir el disparo** hasta resolver la selección y comprobar el valor efectivo antes de solicitar captura. El procedimiento usado debió detenerse al observar el valor discrepante: la aceptación `ss-ok` no bastaba. No se atribuye automáticamente el bloqueo a la velocidad, a BULB ni a una pieza concreta.

## Condiciones y comprobaciones

El usuario indicó ambiente muy oscuro, cámara inmóvil, flash integrado inoperante y ausencia de flash externo; la configuración consultada indicaba `flash-mode=on`, que no acredita por sí misma si hubo destello. ISO 100, f/3.5, RAW+JPEG, modo manual y reducción de ruido de exposición larga desactivada; enfoque y balance blancos automáticos. La focal, la temperatura, batería y estabilidad real de la iluminación no se midieron. La sesión no controla el efecto de AF, balance, temperatura ni escena sobre las comparaciones. Oscuridad extrema no prueba integración fotoeléctrica lineal.

Antes de disparar: RemoteShutter v8b sin ráfaga, MD5 `/system/av-cam.bin` `ef2e3003ddad7185b5398cb76287c5aa`, dos originales T050 y seis GOT del lector coincidentes; seis GOT de sombras e IDs comprobados; RAM contrastada con `/proc/iomem`. No acredita integridad completa, ni la versión de Darwin. Tras el reinicio informado, `/info` y `/status` respondieron, se repitió el MD5 y coincidieron los dos sitios T050 y las seis GOT. Esto acredita respuesta de esos servicios y controles puntuales, no estabilidad global.

## Solicitudes y resultados

| Pedido | `/ss` | `/info` tras ajuste | Callback | Archivos en tarjeta |
|---|---|---|---|---|
| 5 s | `ss-ok 5.0` | 5.0 | 7,231 s | DSC03362.ARW/JPG |
| 15 s | `ss-ok 15.0` | 20.0 | 22,092 s | DSC03363.ARW/JPG |
| 30 s | `ss-ok 30.0` | 65535.0 | no recibido en 90 s | no identificado |

Los tiempos de callback incluyen procesamiento; no miden el intervalo efectivo de integración. `/ss` puede informar un valor transitorio: su código no garantiza que el valor permanezca después de retornar. Los dos JPEG de callback se guardaron localmente, así como las muestras y respuestas completas en [evidencia](../../analysis/e25-23/20261028-evidence.json). Los dos RAW se copiaron por Telnet y sus MD5 coinciden con los calculados en la tarjeta. Se conservan en `analysis/camera-dumps/20261028-201843-E25-23/`, fuera de Git. Los JPEG originales también se recuperaron por Telnet con MD5 coincidente: `6d729b71bebb0a611565a365e71f5974` y `ce7fd10d5503add8049bb53bbac8d572`. El estado observado antes del reinicio era `shooting`; el contador seguía en 2. No se dispone de captura terminada de 30 s.

## Parámetros y límites

En las muestras `record_a` por GOT, se observó `shd=1, svd=0, spl=0, ShutMode=3`; también ceros durante cinco muestras de la primera solicitud. `record_b` fue cero en los campos examinados. No se ha demostrado que cada lectura corresponda al plan nativo activo de la fotografía; la persistencia y los ceros no prueban transferencia de parámetros. En copias `cap` localizadas por gestor → nodo → M → `[M]`, los valores observados fueron `cap+0x504=1`, `shd=1, svd=0, spl=0, ShutMode=3`. Los IDs 3–8 fueron frecuentemente `00 00 01 00 00 00` durante las tres solicitudes; también se captaron otras combinaciones. Cada lectura tiene tiempos de inicio y fin en los datos; las sombras se leen secuencialmente y las combinaciones pueden mezclar instantes. Muestras: 13, 33 y 117; estas cifras no establecen cobertura de transiciones breves.

La cadena estática [E25-21](e25-21-setexposure-p2s.md) y la relación de Darwin con `ExposureReady` [E25-19c](e25-19c-fin-exposicion-mensaje-temporizador.md) no prueban que `SetExposure` o `Execute(1)` se hayan ejecutado en estas tomas, que el bus haya entregado datos al sensor, ni cuál fue el fin electrónico de integración. Una imagen válida o el callback tampoco demuestran ausencia de cortina. No se hizo lectura MMIO, hook, parche ni escritura directa de RAM.

## Próximo paso seguro

Conservar y analizar los dos RAW si se recuperan, con hashes y EXIF. Investigar offline cómo `adjustShutterSpeed`, la actualización asíncrona y `speed()` pueden dar `ss-ok 30` seguido de `65535`, y cómo verificar de modo no intrusivo un ajuste estable; no volver a solicitar un disparo largo ni seleccionar BULB para probarlo sin resolver el incidente y contar con autorización adecuada. La señal de 30 s, la ausencia de cortina, inicio/fin de integración y entrega P2S siguen sin demostrar.

## RAW recuperados

Ambos RAW se decodifican con rawpy y tienen área visible 6024 × 4024 (24,24 MP), valores representados en `uint16`, nivel negro 512 por canal y blanco 16383. EXIF: ILCE-6000 v3.21, ISO 100, f/3.5, 16 mm, modo manual, flash no disparado y balance automático. EXIF registra **5 s y 20 s**, no 15 s. El MD5 coincide con el archivo presente en la tarjeta, lo que verifica la copia, no que el contenido sea una captura físicamente correcta. SHA-256: `48f753191e7f7b95e4fecd9392bb5bd40fb76c40238e841dc71a53438c86fcde` y `ba99d5fe642784c9daf6733b1173c509fcf29242e7e6a98c5b1ce2c9c7fa6372`.

La media Bayer tras restar 512 por canal fue aproximadamente 10,41 y 44,95 unidades, respectivamente; razón 4,32 frente a 4 esperada de 5 a 20 s. Valores medios por canal R/G1/G2/B: 3,90/14,21/14,34/9,21 y 19,18/60,12/60,25/40,27. Medianas respectivas 4/8/8/8 y 12/36/36/28. No hay píxeles en el blanco ni por encima del 99 % del blanco. En la primera toma, 12–46 % de muestras por canal están en o bajo el negro; cuantización visible y escena muy oscura limitan el análisis. Estos datos son compatibles con más señal a 20 s pero **no demuestran duración efectiva ni linealidad fotométrica**: no se separaron luz, señal oscura, píxeles defectuosos, temperatura o ruido, ni se cuenta con réplicas para estimar incertidumbre. No existe RAW de 30 s para comparar.

La media por filas sin restar negro varió entre 512,73–537,63 y 519,48–617,62, respectivamente. Las diferencias espaciales incluyen contenido de escena y canales alternados; no identifican una causa de sensor o cortina. [Estadísticas por canal y perfiles](../../analysis/e25-23/raw_stats.json) · [gráfico de filas](../../analysis/e25-23/row_means.png) · [respuesta observada](../../analysis/e25-23/raw_response.png). La compresión o procesamiento Sony no quedan caracterizados por esta lectura; no se supone linealidad del RAW.

### Criterios de 30 s

A solicitud: **DEMOSTRADO**. B aceptación: **COMPATIBLE, PERO NO DEMOSTRADO** (`ss-ok` contradice la posterior lectura 65535). C EXIF, D RAW, E plan de 30 s, F parámetros en record atribuibles a ese plan, G transferencia a cap, I entrega al sensor, J fotometría, K ausencia de cortina, L inicio/fin electrónicos y M vuelta normal sin reinicio: **NO DEMOSTRADO**. H preparación en sombras: **COMPATIBLE, PERO NO DEMOSTRADO**; se observaron bytes en RAM pero no su procedencia ni envío. La recuperación posterior con reinicio es una observación distinta de M.
