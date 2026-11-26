# G113 — Opengate en vídeo: parche estático (3:2 real + raster 1440×960) y velocidad de lectura (25-11-2026)

Implementación estática tras [G112](g112-opengate-video-3-2.md). Cuatro cambios en `av-cam.bin`, un módulo de
parche (`scripts/gui/og_avcam_patch.py`), siete pruebas Unicorn/datos (`tests/test_g113_opengate.py`) y una build
`--funciones og`. **Nada instalado ni ejecutado en la cámara.**

## 1. Qué queda implementado

| # | Cambio | Dirección | Antes → después |
|---|---|---|---|
| OG-A | Alto activo del modo de sensor `0x19` (24p): lectura 3:2 de altura completa | `0x43bc1a30` (fila 11 de 72 B de `0x43bc16dc`, campo `+0x3c`) | `1124` → **`1333`** |
| OG-B | El codificador acepta el raster 3:2 | `0x4361255c` (`cmp.w r3,#0x438; bne error`) → `bl` a cueva en `0x43fb8480` (`ZONA_G18+0x600`) | 1440×**1080** → 1440×**1080 o 960** |
| OG-C | Raster del perfil 1 del codificador | `0x43a7bfba` (`mov.w r3,#0x438`) | alto **1080** → **960** |
| OG-D (opcional) | Opengate a 59,94 Hz en los modos `0x10`/`0x1a` | filas 3 y 10 (`+0x3c`) y tablas A/B `0x43bc1ae8`/`0x43bc1b84` | alto 1124 → 1333; línea `693→676` ciclos, cuadro `1300→1333` |

`apply_bytes()` aplica OG-A/B/C (24p); `apply_60p()` añade OG-D. Ambas son idempotentes y validan los bytes
originales.

**Por qué 1440×960 y no 1920×1280.** `FUN_4391c540` exige, para anchos distintos de 1920, que ancho de entrada =
ancho de salida y alto de entrada = alto de salida, y su lista blanca de anchos es `{640, 800, 1280, 1440, 1920}`
con alto 1080 obligatorio a 1920. `FUN_436124b8` elige perfil por coincidencia exacta de (ancho, alto) contra
cinco rasters; el único 3:2 de la lista es 1440×1080 (perfil 1, ctor `0x43a7bf56`). 1440×960 pasa los dos.

**Por qué no hay que tocar la marca de aspecto.** Con lectura `1996×1333` y salida `1440×960` la escala es
0,7214 horizontal y 0,7202 vertical: 0,2 % de diferencia ⇒ píxel cuadrado, el 3:2 del fichero sale solo. No hace
falta el enum de aspecto de la orden `0x4000` (que no tiene 3:2) ni `emAspectRatio` de `libmpr`.

**Lo que NO se toca.** El camino entrelazado (`0x4361254a`, `+0x4e` = 0 → perfil 4 = 1440×540) queda intacto para
no romper AVCHD 1440×1080i; el perfil 6/7 (1920×1080) y el 2/5 (720p) conservan su comportamiento, con pruebas de
regresión.

## 2. ¿Se puede leer el sensor más rápido que 66,7 ms/cuadro?

**Período = a·b / 54,054 MHz** (tablas A `0x43bc1ae8` y B `0x43bc1b84`, 12 B por modo: `a` = ciclos de línea,
`b` = líneas de cuadro). Es un dato, no una estimación: los 33 modos dan exactamente 900 900 (59,94 Hz) o
1 080 000 (50 Hz) salvo los de 48 Hz y la foto.

| Modo | lectura | a·b | período | px/ciclo | Mpx/s |
|---|---|---|---|---|---|
| foto `0x0b`/`0x2f` | 6000×4000 | 864·4176 = 3 608 064 | **66,75 ms (14,98 Hz)** | **6,94** | **375** |
| vídeo `0x05/0x10/0x18/0x1a` | 1996×1124 | 693·1300 = 900 900 | 16,67 ms | 2,88 | 156 |
| `0x19` (24p) | 1996×1124 | 693·1625 = 1 126 125 | 20,83 ms | 2,88 | 156 |
| `0x0f` | 1024×684 | 858·1050 = 900 900 | 16,67 ms | 1,19 | 64 |

**El límite no es el blanking, es la tasa de columna.** En foto hay 176 líneas de blanking vertical (4,2 %) y
ningún hueco horizontal apreciable (6000 px en 864 ciclos = 6,94 px/ciclo); en vídeo la tasa de columna es 2,4×
menor. La tasa máxima que ejerce cualquier modo del firmware es **375 Mpx/s** (foto). Con eso:

| Palanca | Cálculo | Ganancia |
|---|---|---|
| Quitar el blanking vertical (`b` 4176 → 4000) | 864·4000 = 3 456 000 → 63,94 ms | **+4,4 %** (15,64 Hz) |
| Acortar la línea a 858 ciclos (lo que ya usa `0x0f`) | 858·4176 = 3 583 008 → 66,29 ms | +0,7 % |
| Ambas | 858·4000 = 3 432 000 → 63,50 ms | **+5,1 %** (15,74 Hz) |
| 24 fps a 24 MP | 41,7 ms / 4000 líneas = 10,4 µs/línea = **563 ciclos** ⇒ **10,7 px/ciclo** | imposible sin subir el reloj |

Es decir: **24 MP a 24 fps exigiría 1,54× la tasa de columna actual** (≈83 MHz de referencia en vez de 54,054, o
el doble de carriles). Eso no está en `av-cam`: el reloj de 54 MHz es la referencia del bloque imager (manual de
servicio, `CL6013`) y lo único que cambia por modo en el sensor son los registros `0x011–0x014` de la matriz de
59 filas (`0x43fe9b74`), con valores `0x014c/0x0474` en los modos de vídeo, `0x0694/0x02c4` en `0x0f` y `0` en
foto (valores por defecto). Sin datasheet del IMX210, tocar esos pares para subir la tasa es una apuesta, no una
optimización: no hay ninguna ruta estática que los relacione con el período, que ya viene dado por `a·b`.

**Lo que sí se puede acelerar es el opengate, y mucho.** El 3:2 con binning 3 tiene 1333 líneas y hoy usaría la
línea de 12,83 µs (48 Hz como máximo, modo `0x19`). Con línea de **676 ciclos** el cuadro dura
676·1333 = 901 108 ciclos = **59,986 Hz**, el mismo 60p que ya hace el vídeo actual pero con 3:2 completo:

| Variante | período | fps de lectura | frente a la foto |
|---|---|---|---|
| 3:2 en modo `0x19` (OG-A) | 693·1625 = 1 126 125 | 48,0 | 3,5× más rápido |
| 3:2 a 60p (OG-D) | 676·1333 = 901 108 | **59,99** | **4,0×** |
| 24 MP (foto, sin tocar) | 864·4176 = 3 608 064 | 14,98 | 1× |

Conclusión: **no hay forma estática de bajar de 66,7 ms a resolución plena** (sólo ~5 % quitando blanking, y con
la incógnita de si el imager acepta 4000 líneas de cuadro), pero **el opengate 3:2 sí llega a 60p** porque su
límite es el número de líneas (1333), no la tasa de columna.

## 3. Estado del build y de las pruebas

- `python3 -m pytest tests/test_g113_opengate.py -q` → **7 passed**: idempotencia, alto 3:2 sin cambiar el
  período, aceptación 1440×960 (perfil 1), conservación de 1440×1080 y 1440×1080i, conservación de 1080p/720p/480p,
  rechazo de alturas no soportadas y aritmética del 60p.
- Build `--funciones og` (base Silent + opengate) y su auditoría: ver §4.

## 4. Build 3.94 `og` y auditoría (MEDIDO)

`python3 scripts/gui/build_cfw_film.py build/og113 --version 3.94 --funciones og` → base 3.38 + Silent
(`patch_silent_r5`) + opengate; 27 ficheros, 465 bloques recompuestos, `darwin_v3`, `--sin-wbi`.
`firmware_packed.dat` sha256 **`daaaf81fda7107b85bb419d0985c925867f17670902dcfba46e56d40116dd129`**,
tar `6560a15aae68c35387667cf7468cd97e43229b81f5ca8d1e28b5b70596eec9f7`.

`audit_package_nflasha15.py … --darwin-v3 --sin-wbi --bionz-g22` → **`todo_ok: true`, 29/29 comprobaciones** y 65
sumas verificadas. Para que la comprobación `g22.bionz_es_3.38_mas_patch_tristate` reconozca la build se añadió la
rama `{"og"}` a `bionz_g22_checks` (sin ella, el `av-cam` parcheado se veía como «no es el esperado», que es
exactamente lo que debía pasar hasta ahora).

**Nada instalado**: la cámara no se toca en esta fase.

## 5. Lo que falta para «funcionalidad completa» (y dónde está el riesgo)

1. **Que la cámara pida 1440×960.** Hoy el formato de película pide 1920×1080; el parche hace que el raster 1440
   exista y que el codificador acepte 960, pero el pedido sale del bloque de formato (`obj+0x404`, 0x84 B) y de la
   orden LIRO `0x4000` (tamaño `0xf`, aspecto `0x11`), cuyo emisor no está resuelto. Es el paso pendiente OG-6.
2. **El ISP** debe aceptar 1333 líneas de entrada y escalarlas a 960: no se puede comprobar estáticamente (el
   arnés no emula MCAVC ni graba, E2E-15).
3. **El imager** debe aceptar la ventana de 1333 líneas activas sin cambio de registros (la matriz de 59 filas no
   codifica alto: el alto sale de la fila de 72 B). Es la hipótesis central y sólo se valida en cámara.
4. Riesgo de fallo mudo: si el imager rechaza el modo, el resultado esperado es cuadro con líneas basura o cuelgue
   del imager, sin diagnóstico por software; la recuperación es el actualizador por SWD (R48).
