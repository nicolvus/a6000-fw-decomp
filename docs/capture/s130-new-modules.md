# S130 — los 20 módulos "NUEVO/PROPIO": ¿contenido nuevo o solo otra etiqueta?

> **Aviso D4 (25-10-2026):** [S170](../../analysis/s170_illumi/illumi.md) rectifica la lectura de `[ILLUMI]` como contenido nuevo: el subsistema de iluminación tiene las mismas RTTI en los tres modelos; lo propio de la A6000 son las trazas. Que sea el mismo código en los tres sigue NO_VERIFICADO.

**Hito de la línea de ingeniería inversa general**: cierra la pregunta abierta por S128.

Informe: [analysis/s130_new_modules/new_modules.md](../../analysis/s130_new_modules/new_modules.md) ·
Datos: `new_modules.json` · Test: `tests/test_s130_new_modules.py`.

## Método

Para cada prefijo `NUEVO/PROPIO` de S128 se extrae el **núcleo** de cada mensaje (lo que sigue a
`"[PREFIX]: "`) y se busca como subcadena en la A7S fw3.20 y el A6300 fw2.01, anotando con qué
etiqueta aparece allí.

## Resultado

| clase | nº | prefijos |
|---|---|---|
| **ETIQUETADO** | 2 | `[IDT_OPD]` (270/273 núcleos, todos como `[IDT]`), `[DFE]` (11/11) |
| PARCIAL | 1 | `[JPEG]` (4/17) |
| **CONTENIDO NUEVO** | 17 | `[MOUNT_DEBUG]`, `[CAMERA_MAIN_LC]`, `[ACCY]`, `[VPH_API]`, `[CLK_CTRL]`, `[SAD]`, `[ILLUMI]`, `[CAM_UTIL_ADJ]`, `[CAM_UTIL_SENS]`, `[TP_R]`, `[CAMERA_IS]`, `[DEPTH]`, `[JOG]`, `[ADC_DEBUG]`, `[LIF_DEBUG]`, `[PANDA]`, `[CAMERA_MAIN_FC]` |

Los tokens `ACCY`, `VPH_API`, `CLK_CTRL`, `CAMERA_MAIN_LC`, `MOUNT_DEBUG`, `ILLUMI` y `PANDA`
**no aparecen ni una vez** en la A7S ni en el A6300.

## Detalle para la línea del obturador

El módulo `[VPH_API]` (la API de cámara, 106 trazas) incluye una **API de silenciador de
obturador nueva** en esta fw3.21: `<shutter_mute_param>` `0x43ce3634`,
`<shutter_mute_param_sub>` `0x43ce3b5a`, `>shutter_mute<` `0x43ce3de4` y
`>shutter_mute_status<o/f:%d` `0x43ce3dfc`. Las 4 cadenas `shutter_mute*` **no existen** en la
A7S fw3.20 ni en el A6300 fw2.01, mientras que la traza del silenciador en sí
(`shutter mute on/off`, `[SFRS][PINSEND]`, S118) **sí** está en los tres → la fw3.21 **añade el
parámetro de API**, no el mecanismo. El silenciador es del obturador **mecánico**: sin efecto en
S51.

## Advertencia

A6000-fw3.21 ↔ A7S-fw3.20 ↔ A6300-fw2.01 mezcla **versión y modelo**: lo que se mide es
«presente en la A6000 fw3.21 y ausente en los otros dos», y no se puede separar «nuevo en la
fw3.21» de «propio de este modelo» (no hay una fw anterior de la A6000 en el repositorio).
