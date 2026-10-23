# S135 — el subsistema `ElecShutter` del A6300 como control positivo

**Hito de la línea de ingeniería inversa general** con relevancia directa para la **línea del
obturador electrónico**.

Informe: [analysis/s135_elec_shutter/elec_shutter_scan.md](../../analysis/s135_elec_shutter/elec_shutter_scan.md) ·
Datos: `elec_shutter_scan.json` · Test: `tests/test_s135_elec_shutter.py`.

## Hallazgo central

Buscando en los tres `av-cam.bin` disponibles las huellas de un subsistema de **obturador
electrónico**, aparece una asimetría inequívoca:

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---:|---:|---:|
| `ElecShutter` | **0** | **0** | 4 |
| `EC_ElecShutter_Main.cpp` | **0** | **0** | 1 (`0x43dcfa41`) |
| `EC_NonlinearElecShutter_MechShutterTable.cpp` | **0** | **0** | 1 (`0x43dcfa65`) |
| `SilentShutterMode` / `CheckSetSilentShutterMode` | **0** | **0** | 2 / 1 |
| `front_eshutter` / `CheckSetFrontEshutter` | **0** | **0** | 1 / 1 |
| `shutterType` / `CheckSetShutterType` | **0** | **0** | 1 / 1 |
| `SET Silent Shutter Type` | **0** | 1 (`0x43ca4b6b`) | 1 (`0x43dc4f43`) |
| `efcs`/`EFCS`, `electronic`, `curtain`, `mechanical`, `flicker` | **0** | **0** | **0** |

La única coincidencia de la A7S es el *diagnóstico* del convertidor `0x4379ec04`, ya documentado
en `work/claude/a7s_silent_execution_trace.md`.

**La ausencia en la A6000 es selectiva**: la A6000 **sí** tiene el motor de control de exposición
`EC` (`EC::EcTagData` `0x43ca91ce`, `EC::EcEncryptedTagData` `0x43ca9227`,
`api_EC_GetApolloLapNum()` `0x43caa193`), lo que falta es **exactamente** la sub-rama
`ElecShutter/`.

Las 15 apariciones de `shutter`/`Shutter` de la A6000 son del **obturador mecánico**: el
silenciador (`VDF::ShutterMuteOffExecutor` `0x43c851d8`, `[SFRS][PINSEND] shutter mute thru`
`0x43ce956e`, `[VPH_API]<shutter_mute_param>` `0x43ce3634`) y el disparo táctil
(`[CAMERA_MAIN_FC]: ReplyForTouchShutter` `0x43ca6a85`).

## Lectura para la línea del obturador

**Control positivo**: cuando un firmware de Sony trae obturador electrónico en esta capa, deja
huellas inequívocas. La A6000 fw3.21 **no tiene ninguna** → su HAL **no implementa** un
subsistema de obturador electrónico. Refuerza la conclusión vigente de S51 (A/B/C = NO) y
complementa a S101 (allí el selector de tipo de mecanismo `0x4379316a` tenía valor 0 por
defecto y sin escritor; aquí se ve que tampoco existe el módulo que lo interpretaría).

**Límite**: la ausencia estática no demuestra que el hardware no pueda dar lectura sin cortina;
solo que esta fw3.21 no lo implementa en el HAL. La prueba física (plan P0–P8) sigue siendo la
que decide.

## Abierto / NO VERIFICADO

- Si el módulo `ElecShutter` del A6300 se ejecuta y con qué efecto físico.
- Si la política **EFCS** de la A6000 en `libObj.so` (E012) es el mismo concepto que
  `ElecShutter` del A6300 en `av-cam.bin`: son binarios y capas distintas, no enlazados.
- Si una fw anterior de la A6000 tuvo ese módulo (no hay más blobs de la A6000 en el repo).

## Corrección posterior (hito S172, 22-10-2026)

1. **El bloque de 128 bytes en `0x43dcfa9e` NO es una tabla de velocidad de obturación.**
   Verificado: **0 referencias PIC** (no está en el mapa global del A6300) y **0 punteros
   absolutos de 4 B**; además es una tabla byte→byte **no decreciente** (`54 54`, `60 60`,
   `66 66`, `6a 6a`, `6e 6e`, `71 71`, `74 74`, `77 77`, `7b 7b`, `7d 7d`, `7f 7f`), más
   compatible con una tabla de **caracteres imprimibles**. La tabla real de velocidades se
   indexa **por fila, con 32 bits por entrada**, y la consume el código de
   `EC_NonlinearElecShutter_MechShutterTable.cpp`.
2. **El módulo ha sido localizado y caracterizado** (S172): `EC_ElecShutter_Main.cpp`
   (`0x4391d67c`) devuelve un **código de modo de obturador** (`0x80` → 3, `0x100` → 4) y
   `EC_NonlinearElecShutter_MechShutterTable.cpp` implementa la **equivalencia no lineal entre
   velocidad electrónica y mecánica** (interpolación por tramos con escalas 10000/1000 y
   búsqueda en punto fijo 16.16 con escala `0x8000`).

**Lo que S135 acertó se mantiene**: la existencia del módulo `ElecShutter/` en el A6300 fw2.01
y su ausencia en la A6000 fw3.21 y la A7S fw3.20, con los ajustes `SilentShutterMode` /
`shutterType` / `front_eshutter`. **S51 no cambia** (A=NO, B=NO, C=NO).

Detalle: [S172](../../analysis/s172_elec_shutter_a6300/elec_shutter_a6300.md).
