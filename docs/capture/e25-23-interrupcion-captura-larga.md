# E25-23 — Interrupción de una captura larga de 30 s (28-10-2026)

Informe redactado el 31-10-2026 **a partir de la evidencia versionada**, sin repetir pruebas (cierre de D13). Registro: [T055](registro-pruebas-camara.md).
Firmware instalado: 3.23 (`av-cam.bin` MD5 `ef2e3003…` medido en la cámara; Darwin no verificado). Sin parches: los sitios T050 y las GOT T052-A coincidieron antes, después de cada foto y al final.

Etiquetas: **MEDIDO** (JSON y RAW de la sesión) · **TESTIMONIO** (usuario) · **HIPÓTESIS**.

## 1. Evidencia

| Carpeta | Contenido |
|---|---|
| [`20261028-201822-E25-23`](../../analysis/camera-dumps/20261028-201822-E25-23/) | Primer intento (23:18:22–23:18:33 UTC): línea base y controles; abortado por `AssertionError()` antes de disparar. 0 fotos |
| [`20261028-201843-E25-23`](../../analysis/camera-dumps/20261028-201843-E25-23/) | Sesión (23:18:43–23:21:08 UTC): `evidence.json` (13/33/117 muestras de `record_a/b`, 6 sombras, colas g1/g9), `raw_stats.json`, `row_means.png`, JPEG reducidos `5s.jpg` y `15s.jpg`. RAW no versionados (SHA-256 en `raw_stats.json`) |

Condiciones: RAW+JPEG, ISO 100, f/3.5, 16 mm, exposición manual, WB auto, flash configurado pero físicamente inoperante (usuario). Escena e iluminación no controladas.

## 2. Resultado por disparo (MEDIDO)

| Petición `/ss` | `/info` tras seleccionar | EXIF | `done` (ms) | Archivo | Muestreo |
|---|---|---|---|---|---|
| 5 s | 5.0 | 5 s | 7 231 | `DSC03362` | 13 muestras en 8,9 s |
| 15 s | **20.0** | 20 s | 22 092 | `DSC03363` | 33 muestras en 24,5 s |
| 30 s | **65535.0** | — | nunca | — | 117 muestras en 90,7 s; estado `shooting` al final |

- La app respondió `ss-ok 30.0`, pero la cámara quedó con velocidad `65535`. El disparo no terminó en 90 s y la sesión se cortó con `captura o muestreo incompletos`. Después el usuario informó que la cámara estaba bloqueada y la reinició (**TESTIMONIO**).
- 15 s se convirtió en 20 s: la selección de velocidad no es exacta en esa zona.
- Sombras: ID5 y ID6 cambian durante las capturas (p. ej. `0x73→…`, `0xa4→0x03`, `0x01→0x00`). Son lecturas no atómicas y no demuestran qué se envió al sensor.
- RAW: media por canal (sin el negro 512) de 3,9/14,2/14,3/9,2 a 5 s y de 19,2/60,1/60,3/40,3 a 20 s. La razón es de ≈ 4,2–4,9, compatible con 4× de exposición, pero la escena es muy oscura (cerca del suelo de ruido) y no está controlada: **no mide la integración electrónica**.

## 3. Interpretación

- **HIPÓTESIS:** `65535` es un valor centinela (fuera de tabla o BULB). Una captura en modo BULB espera a que se suelte el disparador y no termina sola, lo que encajaría con `shooting` indefinido. No se demostró en binario ni en la cámara.
- No se demostró causa del bloqueo ni relación con el parche B1a del 3.23. Con 3.21 no se probó 30 s en la misma sesión.

## 4. Límites y recomendación

- Sin captura de bus, sin RAW de 30 s y sin control de iluminación.
- No repetir 30 s ni BULB con firmware modificado sin antes resolver en estático qué representa `65535` en `getShutterSpeed`/`setShutterSpeed`. Hoy la cámara está bloqueada por el 3.25 ([E26](e26-recovery.md)), así que el punto queda solo para análisis offline (fila E25-23 de [PENDIENTES](../PENDIENTES.md)).
